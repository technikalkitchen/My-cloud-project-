"""U06.5 Unit 7 — Reliability-weighted multi-exchange reference price engine.

MAD-based robust outlier filtering, dynamic reliability scoring with missing-
feature denominator renormalization, correct weight validation, reliability-
weighted price aggregation, minimum cross-exchange confirmation gate, and
source/evidence traceability.

All functions are deterministic: no randomness, no live network calls inside
the engine itself. Evidence is supplied by the caller (Units 4/5/6).
"""
from __future__ import annotations

import math
import statistics
from datetime import timedelta
from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.core.u06_5 import (
    deep_copy,
    parse_timestamp,
    safe_float,
    safe_int,
    timestamp_age_seconds,
    utc_now,
)
from app.config.quality import (
    EXCHANGE_KLINE_INTERVAL,
    FRESHNESS_THRESHOLD_SECONDS,
    QUALITY_CONFIG,
    TARGET_EXCHANGE_COUNT,
)
from app.config.exchanges import (
    MIN_VALIDATED_EXCHANGE_COUNT,
)

OUTLIER_ENGINE_VERSION = "OUTLIER_ENGINE_V2"
PRICE_AGGREGATOR_VERSION = "PRICE_AGGREGATOR_V2_RELIABILITY_WEIGHTED"
REFERENCE_ENGINE_VERSION = "REFERENCE_PRICE_ENGINE_V1"

REQUIRED_RELIABILITY_COMPONENTS = (
    "data_integrity",
    "freshness",
    "volume",
    "near_depth",
    "far_depth",
    "spread",
    "price_impact",
    "cross_exchange_consistency",
)

_WEIGHT_SUM_EPSILON = 1e-6


def validate_reliability_weights() -> Dict[str, Any]:
    """Validate the reliability-component weights declared in QUALITY_CONFIG.

    Checks:
      * every required component name is present
      * every weight is a finite, non-negative number
      * all weights together sum to 1.0 (within epsilon)

    Returns a dict with ``valid`` (bool), ``failures`` (list[str]) and
    ``weights`` (deep copy of the configured weights).
    """
    weights = QUALITY_CONFIG.get("reliability_component_weights", {})
    failures: List[str] = []

    for name in REQUIRED_RELIABILITY_COMPONENTS:
        if name not in weights:
            failures.append(f"missing component: {name}")

    for name, weight in weights.items():
        value = safe_float(weight)
        if value is None or not math.isfinite(value):
            failures.append(f"invalid weight for {name}: {weight!r}")
            continue
        if value < 0:
            failures.append(f"negative weight for {name}: {value}")

    declared_sum = sum(
        safe_float(w) for w in weights.values() if safe_float(w) is not None
    )
    if abs(declared_sum - 1.0) > _WEIGHT_SUM_EPSILON:
        failures.append(
            f"weight sum {declared_sum:.6f} != 1.0"
        )

    return {
        "valid": not failures,
        "failures": failures,
        "weights": deep_copy(weights),
        "weight_sum": declared_sum,
        "required_components": list(REQUIRED_RELIABILITY_COMPONENTS),
    }


# ---------------------------------------------------------------------------
# Bounded helpers
# ---------------------------------------------------------------------------

def _bounded01(x: Optional[float]) -> Optional[float]:
    if x is None or not math.isfinite(x):
        return None
    return max(0.0, min(1.0, x))


def _relative_log_score(
    value: Optional[float],
    peer_values: Sequence[float],
) -> Optional[float]:
    """Peer-normalized score. Zero/negative values are unavailable, not zero-quality."""
    if value is None or value <= 0 or not peer_values:
        return None
    vals = [v for v in peer_values if v is not None and v > 0 and math.isfinite(v)]
    if not vals:
        return None
    lo, hi = min(vals), max(vals)
    if hi <= lo:
        return 1.0
    a, b = math.log1p(lo), math.log1p(hi)
    return _bounded01((math.log1p(value) - a) / (b - a))


def _freshness_score(age_seconds: Optional[float]) -> Optional[float]:
    if age_seconds is None:
        return None
    if age_seconds < 0:
        return None
    half_life = max(1.0, float(QUALITY_CONFIG["max_source_age_seconds"]) / 2.0)
    return _bounded01(math.exp(-math.log(2.0) * age_seconds / half_life))


def _spread_score(spread_bps: Optional[float]) -> Optional[float]:
    if spread_bps is None or spread_bps < 0:
        return None
    limit = max(1e-9, float(QUALITY_CONFIG["spread_soft_limit_bps"]))
    return _bounded01(math.exp(-spread_bps / limit))


def _impact_score(impact_pct: Optional[float]) -> Optional[float]:
    if impact_pct is None or impact_pct < 0:
        return None
    return _bounded01(1.0 / (1.0 + impact_pct / 0.10))


# ---------------------------------------------------------------------------
# Market observation model
# ---------------------------------------------------------------------------

def make_market_observation(
    *,
    exchange: str,
    exchange_id: str,
    asset: str,
    base_asset: str,
    quote_asset: str,
    market_id: str,
    market_type: str,
    price: Any,
    volume_usd_24h: Any,
    timestamp: Any,
    retrieved_at: str,
    provider: str,
) -> Dict[str, Any]:
    """Create a portable market observation record with traceable source fields."""
    source_timestamp = timestamp
    return {
        "exchange": exchange,
        "exchange_id": exchange_id,
        "asset": asset,
        "base_asset": base_asset,
        "quote_asset": quote_asset,
        "market_id": market_id,
        "market_type": market_type,
        "price": safe_float(price),
        "volume_usd_24h": safe_float(volume_usd_24h),
        "volume_usd_recent": None,
        "trade_count_recent": None,
        "timestamp": source_timestamp,
        "retrieved_at": retrieved_at,
        "age_seconds": timestamp_age_seconds(
            source_timestamp, retrieved_at
        ),
        "provider": provider,
        "quality_status": "UNVALIDATED",
        "rejection_reason": None,
    }


def normalize_quote_to_usd(
    observation: Dict[str, Any],
    conversion_prices: Optional[Dict[str, float]] = None,
) -> Tuple[Optional[float], Dict[str, Any]]:
    """Normalize a quote-currency price to USD using real conversion prices.

    USD/USDT/USDC are already USD-equivalent. BTC and ETH quotes are converted
    only when a real conversion price is supplied. No synthetic rates are invented.
    """
    quote = str(observation.get("quote_asset") or "").upper()
    price = safe_float(observation.get("price"))
    if price is None or price <= 0:
        return None, {"status": "INVALID_PRICE"}

    conversion_prices = conversion_prices or {}

    if quote in {"USD", "USDT", "USDC"}:
        return price, {
            "status": "VALIDATED",
            "chain": [quote, "USD"],
            "conversion_rate": 1.0,
        }

    if quote == "BTC":
        btc_usd = safe_float(conversion_prices.get("BTC"))
        if btc_usd:
            return price * btc_usd, {
                "status": "VALIDATED",
                "chain": ["BTC", "USD"],
                "conversion_rate": btc_usd,
            }

    if quote == "ETH":
        eth_usd = safe_float(conversion_prices.get("ETH"))
        if eth_usd:
            return price * eth_usd, {
                "status": "VALIDATED",
                "chain": ["ETH", "USD"],
                "conversion_rate": eth_usd,
            }

    return None, {
        "status": "UNAVAILABLE",
        "chain": [quote, "USD"],
        "reason": "NO_VALID_CONVERSION_RATE",
    }


def validate_market_observation(
    observation: Dict[str, Any],
    now: Optional[str] = None,
) -> Tuple[bool, str]:
    """Validate a single market observation for inclusion in aggregation."""
    now = now or observation.get("retrieved_at") or utc_now()

    if str(observation.get("market_type") or "").upper() != "SPOT":
        return False, "WRONG_MARKET_TYPE"

    price = safe_float(observation.get("price"))
    if price is None or price <= 0:
        return False, "PRICE_INVALID"

    volume = observation.get("volume_usd_24h")
    if volume is not None:
        volume = safe_float(volume)
        if volume is None or volume < float(QUALITY_CONFIG["min_volume_usd_24h"]):
            return False, "INSUFFICIENT_LIQUIDITY"

    freshness_timestamp = observation.get("freshness_timestamp") or observation.get("timestamp")
    age = timestamp_age_seconds(freshness_timestamp, now)
    if age is not None and age > float(QUALITY_CONFIG["max_source_age_seconds"]):
        return False, "STALE_DATA"

    if not observation.get("asset"):
        return False, "ASSET_IDENTITY_MISSING"

    if not observation.get("market_id"):
        return False, "MARKET_ID_MISSING"

    return True, "VALID"


# ---------------------------------------------------------------------------
# MAD-based robust outlier filtering
# ---------------------------------------------------------------------------

def median_abs_deviation(values: Sequence[float]) -> float:
    """Median Absolute Deviation (MAD) — robust dispersion estimator."""
    if not values:
        return 0.0
    med = statistics.median(values)
    deviations = [abs(x - med) for x in values]
    return statistics.median(deviations)


def outlier_filter_v1(
    observations: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    """MAD-based robust outlier rejection.

    Rejects observations whose price deviates too far from the median
    (percentage deviation) or whose robust z-score exceeds the threshold.
    All decisions and evidence are deterministic.
    """
    values = [
        safe_float(x.get("normalized_usd_price"))
        for x in observations
    ]
    valid_values = [x for x in values if x is not None]

    if not valid_values:
        return {
            "status": "DATA_UNAVAILABLE",
            "accepted": [],
            "rejected": [],
            "median": None,
            "mad": None,
            "config": deep_copy(QUALITY_CONFIG),
            "version": OUTLIER_ENGINE_VERSION,
        }

    med = statistics.median(valid_values)
    mad = median_abs_deviation(valid_values)

    accepted: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []

    for obs in observations:
        price = safe_float(obs.get("normalized_usd_price"))
        if price is None:
            rejected.append({
                "observation": deep_copy(obs),
                "reason": "PRICE_INVALID",
            })
            continue

        pct_dev = (
            abs(price - med) / abs(med) * 100.0
            if med else float("inf")
        )

        if mad > float(QUALITY_CONFIG["mad_epsilon"]):
            robust_z = 0.6745 * (price - med) / mad
        else:
            robust_z = 0.0 if price == med else float("inf")

        if (
            pct_dev > float(QUALITY_CONFIG["max_price_deviation_pct_from_median"])
            or abs(robust_z) > float(QUALITY_CONFIG["max_robust_z"])
        ):
            rejected.append({
                "observation": deep_copy(obs),
                "reason": "ROBUST_OUTLIER",
                "percentage_deviation": pct_dev,
                "robust_z": robust_z,
            })
        else:
            item = deep_copy(obs)
            item["outlier_percentage_deviation"] = pct_dev
            item["outlier_robust_z"] = robust_z
            accepted.append(item)

    return {
        "status": "VALIDATED" if accepted else "DATA_UNAVAILABLE",
        "accepted": accepted,
        "rejected": rejected,
        "median": med,
        "mad": mad,
        "config": deep_copy(QUALITY_CONFIG),
        "version": OUTLIER_ENGINE_VERSION,
    }


# ---------------------------------------------------------------------------
# Reliability scoring (7 scored components + 1 fixed data_integrity constant)
# ---------------------------------------------------------------------------

def _build_reliability_scores(
    observations: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Compute dynamic observation-level reliability from real, timestamped evidence.

    Seven scored components (freshness, volume, near_depth, far_depth, spread,
    price_impact, cross_exchange_consistency) plus data_integrity (fixed 1.0).
    Missing feature evidence is excluded from the denominator and reported
    explicitly; it is never fabricated.
    """
    valid = [x for x in observations if x.get("quality_status") == "VALIDATED"]
    volume_peers = [safe_float(x.get("volume_usd_24h")) for x in valid]
    near_peers: List[float] = []
    far_peers: List[float] = []
    for x in valid:
        q = x.get("market_quality") or {}
        bands = q.get("depth_bands", {})
        near_peers.append(safe_float(bands.get("0.10%", {}).get("total_usd")))
        far_peers.append(safe_float(bands.get("1.00%", {}).get("total_usd")))
    volume_peers = [x for x in volume_peers if x is not None and x > 0]
    near_peers = [x for x in near_peers if x is not None and x > 0]
    far_peers = [x for x in far_peers if x is not None and x > 0]

    prices = [safe_float(x.get("normalized_usd_price")) for x in valid]
    prices = [x for x in prices if x is not None and x > 0]
    consensus = statistics.median(prices) if prices else None

    component_weights = QUALITY_CONFIG["reliability_component_weights"]
    result: List[Dict[str, Any]] = []
    for obs in valid:
        q = obs.get("market_quality") or {}
        bands = q.get("depth_bands", {})
        impact = q.get("price_impact", {})
        impact_values = [
            v.get("worst_pct") for v in impact.values()
            if isinstance(v, dict) and v.get("worst_pct") is not None
        ]
        representative_impact = min(impact_values) if impact_values else None
        price = safe_float(obs.get("normalized_usd_price"))
        deviation = (
            abs(price - consensus) / consensus * 100.0
            if price and consensus else None
        )

        components = {
            "data_integrity": 1.0,
            "freshness": _freshness_score(q.get("age_seconds", obs.get("age_seconds"))),
            "volume": _relative_log_score(safe_float(obs.get("volume_usd_24h")), volume_peers),
            "near_depth": _relative_log_score(
                safe_float(bands.get("0.10%", {}).get("total_usd")), near_peers
            ),
            "far_depth": _relative_log_score(
                safe_float(bands.get("1.00%", {}).get("total_usd")), far_peers
            ),
            "spread": _spread_score(safe_float(q.get("spread_bps"))),
            "price_impact": _impact_score(representative_impact),
            "cross_exchange_consistency": _bounded01(
                1.0 / (1.0 + (deviation or 0.0) / 0.25)
            ),
        }
        numerator = 0.0
        denominator = 0.0
        component_details: Dict[str, Any] = {}
        for name, base_weight in component_weights.items():
            value = components.get(name)
            if value is None:
                component_details[name] = {
                    "status": "NOT_AVAILABLE", "weight_excluded": True
                }
                continue
            numerator += float(base_weight) * value
            denominator += float(base_weight)
            component_details[name] = {
                "status": "AVAILABLE", "score": value, "base_weight": base_weight
            }
        score = numerator / denominator if denominator > 0 else 0.0
        item = deep_copy(obs)
        item["reliability"] = {
            "score": _bounded01(score),
            "components": component_details,
            "consensus_price": consensus,
            "price_deviation_pct": deviation,
            "model": "RELIABILITY_MODEL_V1_DYNAMIC",
            "fixed_exchange_rank": False,
        }
        result.append(item)
    return result


# ---------------------------------------------------------------------------
# Reliability-weighted price aggregation
# ---------------------------------------------------------------------------

def price_aggregate_v1(
    observations: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    """Reliability-weighted reference-price engine.

    Accepts already-normalized observations and optional real market-quality
    evidence. If order-book evidence exists it contributes to reliability; if it
    does not, the missing component is reported and the remaining observed
    components are re-normalized. No synthetic depth is created.

    Outlier rejection runs before reliability scoring. A minimum number of
    cross-exchange confirmations is required before a reference price is emitted.
    """
    quality_accepted: List[Dict[str, Any]] = []
    quality_rejected: List[Dict[str, Any]] = []
    for observation in observations:
        ok, reason = validate_market_observation(observation)
        if not ok:
            item = deep_copy(observation)
            item["quality_status"] = "REJECTED"
            item["rejection_reason"] = reason
            quality_rejected.append(item)
            continue
        item = deep_copy(observation)
        item["quality_status"] = "VALIDATED"
        quality_accepted.append(item)

    outlier_result = outlier_filter_v1(quality_accepted)
    accepted = outlier_result["accepted"]
    rejected = quality_rejected + outlier_result["rejected"]
    if len(accepted) < int(QUALITY_CONFIG["min_markets_for_aggregate"]):
        return {
            "status": "DATA_UNAVAILABLE",
            "accepted_markets": accepted,
            "rejected_markets": rejected,
            "weights": {},
            "aggregate_formula": "NO_VALID_MARKETS",
            "aggregate_version": PRICE_AGGREGATOR_VERSION,
            "reference_price": None,
            "confidence": 0.0,
            "outlier": outlier_result,
        }

    scored = _build_reliability_scores(accepted)
    if len(scored) < int(QUALITY_CONFIG["min_reference_exchanges"]):
        return {
            "status": "INSUFFICIENT_CROSS_EXCHANGE_CONFIRMATION",
            "accepted_markets": scored,
            "rejected_markets": rejected,
            "weights": {},
            "aggregate_formula": "MINIMUM_CROSS_EXCHANGE_CONFIRMATION_NOT_MET",
            "aggregate_version": PRICE_AGGREGATOR_VERSION,
            "reference_price": None,
            "confidence": 0.0,
            "outlier": outlier_result,
        }

    raw_weights: List[float] = []
    weights: Dict[str, float] = {}
    for index, obs in enumerate(scored):
        rel = safe_float(obs.get("reliability", {}).get("score")) or 0.0
        near_depth = safe_float(
            (obs.get("market_quality") or {}).get("depth_bands", {})
            .get("0.10%", {}).get("total_usd")
        )
        volume = safe_float(obs.get("volume_usd_24h"))
        liquidity_signal = (
            math.sqrt(max(0.0, (math.log1p(volume or 0.0)) * (math.log1p(near_depth or 0.0))))
            if (volume or near_depth) else 1.0
        )
        weight = max(1e-12, rel * liquidity_signal)
        key = f"{obs.get('exchange')}::{obs.get('market_id')}::{index}"
        weights[key] = weight
        raw_weights.append(weight)

    total_weight = sum(raw_weights)
    reference_price = (
        sum(safe_float(o["normalized_usd_price"]) * w for o, w in zip(scored, raw_weights)) / total_weight
    )
    normalized_weights = [w / total_weight for w in raw_weights]
    for obs, nw in zip(scored, normalized_weights):
        obs["final_weight"] = nw

    reliability_values = [
        safe_float(o.get("reliability", {}).get("score")) for o in scored
    ]
    reliability_values = [x for x in reliability_values if x is not None]
    agreement = 1.0
    if reference_price and scored:
        deviations = [
            abs(safe_float(o["normalized_usd_price"]) - reference_price) / reference_price
            for o in scored
        ]
        agreement = _bounded01(
            1.0 / (1.0 + (statistics.median(deviations) if deviations else 0.0) / 0.002)
        ) or 0.0
    coverage = min(1.0, len(scored) / max(1, TARGET_EXCHANGE_COUNT))
    confidence = _bounded01(
        0.55 * (statistics.mean(reliability_values) if reliability_values else 0.0)
        + 0.25 * agreement
        + 0.20 * coverage
    ) or 0.0

    return {
        "status": "CALCULATED",
        "accepted_markets": scored,
        "rejected_markets": rejected,
        "weights": weights,
        "normalized_weights": {k: v / total_weight for k, v in weights.items()},
        "aggregate_formula": "SUM(normalized_usd_price * dynamic_reliability_score * liquidity_signal) / SUM(dynamic_reliability_score * liquidity_signal)",
        "aggregate_version": PRICE_AGGREGATOR_VERSION,
        "reference_price": reference_price,
        "confidence": confidence,
        "confidence_components": {
            "mean_reliability": statistics.mean(reliability_values) if reliability_values else 0.0,
            "cross_exchange_agreement": agreement,
            "exchange_coverage": coverage,
        },
        "outlier": outlier_result,
        "methodology": {
            "fixed_exchange_ranking": False,
            "volume_is_not_sole_weight": True,
            "orderbook_depth_is_used_when_available": True,
            "missing_features_are_not_fabricated": True,
            "single_exchange_is_not_cross_exchange_confirmed": len(scored) < 2,
        },
    }


def build_live_reference_price_from_multi_exchange(
    multi_exchange: Dict[str, Any],
) -> Dict[str, Any]:
    """Build the canonical current BTC reference price from real exchange evidence.

    This is intentionally symbol-scoped. It does not pretend that one BTC probe
    represents all Top-125 assets. Historical scans can call the same engine on
    symbol/time-aligned observations when real provider evidence exists.
    """
    observations: List[Dict[str, Any]] = []
    per_exchange = multi_exchange.get("per_exchange") or {}
    for provider, evidence in per_exchange.items():
        rows = evidence.get("ohlcv") or []
        if not rows:
            continue
        row = sorted(rows, key=lambda x: x.get("timestamp", ""))[-1]
        price = safe_float(row.get("close"))
        if not price or price <= 0:
            continue
        quote_volume = safe_float(row.get("quote_volume"))
        if quote_volume is None:
            base_volume = safe_float(row.get("volume"))
            quote_volume = base_volume * price if base_volume is not None else None
        obs = make_market_observation(
            exchange=provider,
            exchange_id=provider,
            asset="BTC",
            base_asset="BTC",
            quote_asset="USDT",
            market_id=row.get("market_id") or provider,
            market_type="SPOT",
            price=price,
            volume_usd_24h=None,
            timestamp=row.get("timestamp"),
            retrieved_at=evidence.get("retrieved_at") or utc_now(),
            provider=provider,
        )
        obs["volume_usd_recent"] = quote_volume
        obs["volume_source"] = row.get("volume_source")
        obs["timeframe"] = row.get("timeframe")
        obs["market_quality"] = evidence.get("orderbook_quality") or {"status": "NOT_AVAILABLE"}
        observations.append(obs)

    if not observations:
        return {
            "status": "NOT_AVAILABLE",
            "symbol": "BTC",
            "reason": "NO_VALID_EXCHANGE_PRICE_OBSERVATIONS",
            "observations": [],
        }

    for obs in observations:
        obs["volume_usd_24h"] = safe_float(obs.get("volume_usd_recent"))
        obs["volume_metric_used"] = (
            "RECENT_5M_QUOTE_TURNOVER" if obs.get("volume_usd_recent") is not None
            else "UNAVAILABLE"
        )
        normalized_price, usd_meta = normalize_quote_to_usd(obs)
        obs["normalized_usd_price"] = normalized_price
        obs["usd_normalization"] = usd_meta
        candle_ts = parse_timestamp(obs.get("timestamp"))
        if candle_ts is not None:
            obs["freshness_timestamp"] = (candle_ts + timedelta(minutes=5)).isoformat()

    aggregate = price_aggregate_v1(observations)
    return {
        "status": aggregate.get("status"),
        "symbol": "BTC",
        "timeframe": EXCHANGE_KLINE_INTERVAL,
        "reference_price": aggregate.get("reference_price"),
        "confidence": aggregate.get("confidence"),
        "aggregate": aggregate,
        "observation_count": len(observations),
        "validated_observation_count": len(aggregate.get("accepted_markets", [])),
        "source_policy": "DYNAMIC_RELIABILITY_WEIGHTED_MULTI_EXCHANGE",
        "not_global_market_cap": True,
        "engine_version": REFERENCE_ENGINE_VERSION,
    }


# ---------------------------------------------------------------------------
# Order-book quality metrics (consumed by reliability scoring)
# ---------------------------------------------------------------------------

def _depth_usd(
    book: Dict[str, Any], mid: float, band_pct: float, side: str
) -> float:
    if not book or mid <= 0:
        return 0.0
    bound = band_pct / 100.0
    levels = book.get("bids", []) if side == "bid" else book.get("asks", [])
    total = 0.0
    for level in levels:
        if not isinstance(level, (list, tuple)) or len(level) < 2:
            continue
        price, qty = safe_float(level[0]), safe_float(level[1])
        if price is None or qty is None:
            continue
        distance = abs(price - mid) / mid
        if distance <= bound:
            total += price * qty
    return total


def _slippage_for_notional(
    book: Dict[str, Any],
    mid: float,
    notional_usd: float,
    side: str,
) -> Optional[float]:
    if not book or mid <= 0 or notional_usd <= 0:
        return None
    levels = book.get("asks", []) if side == "buy" else book.get("bids", [])
    remaining = float(notional_usd)
    spent = 0.0
    acquired = 0.0
    for level in levels:
        if not isinstance(level, (list, tuple)) or len(level) < 2:
            continue
        price = safe_float(level[0])
        qty = safe_float(level[1])
        if price is None or qty is None or price <= 0 or qty <= 0:
            continue
        level_notional = price * qty
        take = min(remaining, level_notional)
        if take <= 0:
            continue
        acquired += take / price
        spent += take
        remaining -= take
        if remaining <= 1e-9:
            break
    if remaining > 1e-6 or acquired <= 0:
        return None
    avg_price = spent / acquired
    if side == "buy":
        return max(0.0, (avg_price - mid) / mid * 100.0)
    return max(0.0, (mid - avg_price) / mid * 100.0)


def orderbook_quality_metrics(book: Dict[str, Any]) -> Dict[str, Any]:
    """Compute market-quality evidence from a normalized order book.

    Expects a book dict with ``status``, ``mid_price``, ``spread_pct``,
    ``bids`` and ``asks`` (lists of [price, qty] tuples/lists),
    ``source_timestamp`` and ``retrieved_at``.
    """
    if book.get("status") != "VALIDATED":
        return {"status": "NOT_AVAILABLE"}
    mid = safe_float(book.get("mid_price"))
    if not mid:
        return {"status": "NOT_AVAILABLE"}
    bands: Dict[str, Any] = {}
    for band in QUALITY_CONFIG["depth_bands_pct"]:
        bids = _depth_usd(book, mid, band, "bid")
        asks = _depth_usd(book, mid, band, "ask")
        bands[f"{band:.2f}%"] = {
            "bid_usd": bids,
            "ask_usd": asks,
            "total_usd": bids + asks,
        }
    impacts: Dict[str, Any] = {}
    for notional in QUALITY_CONFIG["price_impact_notional_usd"]:
        buy = _slippage_for_notional(book, mid, notional, "buy")
        sell = _slippage_for_notional(book, mid, notional, "sell")
        impacts[str(int(notional))] = {
            "buy_pct": buy,
            "sell_pct": sell,
            "worst_pct": max(
                [x for x in (buy, sell) if x is not None], default=None
            ),
        }
    age = timestamp_age_seconds(
        book.get("source_timestamp"), book.get("retrieved_at")
    )
    return {
        "status": "VALIDATED",
        "mid_price": mid,
        "spread_pct": safe_float(book.get("spread_pct")),
        "spread_bps": (
            safe_float(book.get("spread_pct")) * 100.0
            if safe_float(book.get("spread_pct")) is not None
            else None
        ),
        "depth_bands": bands,
        "price_impact": impacts,
        "age_seconds": age,
        "level_count_bid": book.get("level_count_bid"),
        "level_count_ask": book.get("level_count_ask"),
    }
