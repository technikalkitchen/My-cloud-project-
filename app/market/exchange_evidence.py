"""U06.5-A exchange-layer acquisition.

Binance Spot Public is primary; Coinbase Exchange Public is fallback only
when Binance fails to provide valid requested data for that symbol.
Provider-supplied traded volume is preserved exactly; no synthetic volume,
close*volume, interpolation, or silent resampling is allowed.

Layer A only: acquisition + normalization. No ranking, no reference price,
no indices, no dominance, no lock gate.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.u06_5 import safe_float, safe_int, utc_now
from app.config.quality import (
    EXCHANGE_KLINE_INTERVAL,
    EXCHANGE_KLINE_LIMIT,
    MULTI_EXCHANGE_PROBE_SYMBOL,
    MULTI_EXCHANGE_SPECS,
    ORDERBOOK_SPECS,
    PROVIDER_PRIORITY,
    TARGET_EXCHANGE_COUNT,
    MIN_VALIDATED_EXCHANGE_COUNT,
    U05_EXCHANGE_SYMBOLS,
    QUALITY_CONFIG,
)
from app.market.http import http_json


def _valid_binance_kline_row(row: Any) -> bool:
    if not isinstance(row, list) or len(row) < 7:
        return False
    numeric_positions = (1, 2, 3, 4, 5, 6)
    try:
        values = [float(row[i]) for i in numeric_positions]
        return (
            all(math.isfinite(v) for v in values)
            and values[5] > 0
            and values[4] >= 0
        )
    except Exception:
        return False


def _valid_coinbase_candle_row(row: Any) -> bool:
    if not isinstance(row, list) or len(row) < 6:
        return False
    try:
        values = [float(row[i]) for i in range(1, 6)]
        return (
            all(math.isfinite(v) for v in values)
            and values[1] > 0
            and values[4] >= 0
        )
    except Exception:
        return False


def acquire_exchange_symbol_ohlcv(symbol: str) -> Dict[str, Any]:
    if symbol not in U05_EXCHANGE_SYMBOLS:
        return {
            "symbol": symbol,
            "status": "NOT_AVAILABLE",
            "selected_provider": None,
            "fallback_used": False,
            "attempts": [],
            "ohlcv": [],
        }

    attempts: List[Dict[str, Any]] = []
    binance = http_json(
        "https://api.binance.com/api/v3/klines",
        params={
            "symbol": symbol,
            "interval": EXCHANGE_KLINE_INTERVAL,
            "limit": EXCHANGE_KLINE_LIMIT,
        },
    )
    binance_valid = (
        binance.ok
        and isinstance(binance.payload, list)
        and len(binance.payload) >= 1
        and all(_valid_binance_kline_row(x) for x in binance.payload)
    )
    attempts.append({
        "provider": "binance",
        "provider_mode": "PUBLIC_SPOT",
        "endpoint": "/api/v3/klines",
        "symbol": symbol,
        "interval": EXCHANGE_KLINE_INTERVAL,
        "http_status": binance.status,
        "ok": binance.ok,
        "valid": binance_valid,
        "retrieved_at": binance.retrieved_at,
        "error_class": binance.error_class,
        "error_message": binance.error_message,
    })

    if binance_valid:
        rows = []
        for row in binance.payload:
            rows.append({
                "exchange": "binance",
                "market_id": symbol,
                "timestamp": datetime.fromtimestamp(
                    float(row[0]) / 1000, tz=timezone.utc
                ).isoformat(),
                "open": safe_float(row[1]),
                "high": safe_float(row[2]),
                "low": safe_float(row[3]),
                "close": safe_float(row[4]),
                "volume": safe_float(row[5]),
                "quote_volume": safe_float(row[7]) if len(row) > 7 else None,
                "volume_source": "PROVIDER_SUPPLIED_TRADED_BASE_VOLUME",
                "timeframe": EXCHANGE_KLINE_INTERVAL,
                "provider_timestamp_ms": safe_int(row[0]),
            })
        return {
            "symbol": symbol,
            "status": "VALIDATED",
            "selected_provider": "binance",
            "selected_provider_mode": "PUBLIC_SPOT",
            "fallback_used": False,
            "attempts": attempts,
            "ohlcv": rows,
        }

    product_id = U05_EXCHANGE_SYMBOLS[symbol]
    coinbase = http_json(
        f"https://api.exchange.coinbase.com/products/{product_id}/candles",
        params={"granularity": 300},
    )
    coinbase_valid = (
        coinbase.ok
        and isinstance(coinbase.payload, list)
        and len(coinbase.payload) >= 1
        and all(_valid_coinbase_candle_row(x) for x in coinbase.payload)
    )
    attempts.append({
        "provider": "coinbase",
        "provider_mode": "PUBLIC_SPOT_FALLBACK",
        "endpoint": f"/products/{product_id}/candles",
        "symbol": symbol,
        "interval": EXCHANGE_KLINE_INTERVAL,
        "http_status": coinbase.status,
        "ok": coinbase.ok,
        "valid": coinbase_valid,
        "retrieved_at": coinbase.retrieved_at,
        "error_class": coinbase.error_class,
        "error_message": coinbase.error_message,
    })

    if coinbase_valid:
        rows = []
        # Coinbase candle schema: [time, low, high, open, close, volume].
        for row in sorted(coinbase.payload, key=lambda x: x[0]):
            rows.append({
                "exchange": "coinbase",
                "market_id": product_id,
                "timestamp": datetime.fromtimestamp(
                    float(row[0]), tz=timezone.utc
                ).isoformat(),
                "open": safe_float(row[3]),
                "high": safe_float(row[2]),
                "low": safe_float(row[1]),
                "close": safe_float(row[4]),
                "volume": safe_float(row[5]),
                "quote_volume": None,
                "volume_source": "PROVIDER_SUPPLIED_TRADED_BASE_VOLUME",
                "timeframe": EXCHANGE_KLINE_INTERVAL,
                "provider_timestamp_seconds": safe_int(row[0]),
            })
        return {
            "symbol": symbol,
            "status": "VALIDATED",
            "selected_provider": "coinbase",
            "selected_provider_mode": "PUBLIC_SPOT_FALLBACK",
            "fallback_used": True,
            "fallback_reason": "BINANCE_UNAVAILABLE_OR_INVALID",
            "attempts": attempts,
            "ohlcv": rows,
        }

    return {
        "symbol": symbol,
        "status": "NOT_AVAILABLE",
        "selected_provider": None,
        "fallback_used": True,
        "fallback_reason": "BINANCE_AND_COINBASE_UNAVAILABLE_OR_INVALID",
        "attempts": attempts,
        "ohlcv": [],
    }


def acquire_exchange_evidence() -> Dict[str, Any]:
    """Acquire real U05-compatible exchange OHLCV with deterministic fallback."""
    symbols = list(U05_EXCHANGE_SYMBOLS.keys())
    per_symbol = {
        symbol: acquire_exchange_symbol_ohlcv(symbol) for symbol in symbols
    }
    validated = [x for x in per_symbol.values() if x.get("status") == "VALIDATED"]
    return {
        "primary_provider": "binance",
        "fallback_provider": "coinbase",
        "timeframe": EXCHANGE_KLINE_INTERVAL,
        "volume_definition": "PROVIDER_SUPPLIED_TRADED_BASE_VOLUME",
        "requested_symbols": symbols,
        "per_symbol": per_symbol,
        "validated_symbol_count": len(validated),
        "coverage_ratio": len(validated) / len(symbols) if symbols else 0.0,
        "market_pair_engine": {
            "status": (
                "VALIDATED" if len(validated) == len(symbols) else "PARTIAL"
            ),
            "primary": "binance",
            "fallback": "coinbase",
            "fallback_only_on_primary_failure": True,
            "selection_used_for_current_top125": False,
        },
    }


# ---------------------------------------------------------------------------
# U06.5 Unit 4 — Independent 8-exchange OHLCV acquisition + 7-of-8 gate.
# ---------------------------------------------------------------------------

def _valid_kline_row(row: Any, min_len: int) -> bool:
    if not isinstance(row, list) or len(row) < min_len:
        return False
    try:
        values = [float(row[i]) for i in range(1, min_len)]
        return (
            all(math.isfinite(v) for v in values)
            and values[0] > 0
            and values[3] >= 0
        )
    except Exception:
        return False


def _normalize_exchange_payload(
    exchange: str,
    spec: Dict[str, Any],
    result: Any,
) -> Dict[str, Any]:
    """Normalize one exchange's raw HTTP payload into the U06.5-A OHLCV contract.

    Each exchange is probed independently. No failover between exchanges.
    Provider-supplied traded volume is preserved exactly; no synthetic volume.
    """
    retrieved_at = result.retrieved_at if result is not None else utc_now()

    if result is None or not result.ok or not isinstance(result.payload, list):
        return {
            "exchange": exchange,
            "status": "NOT_AVAILABLE",
            "selected_provider": exchange,
            "attempts": [{
                "provider": exchange,
                "provider_mode": spec.get("mode"),
                "endpoint": spec.get("url", "").split("/api")[-1],
                "http_status": getattr(result, "status", None),
                "ok": bool(result and result.ok),
                "valid": False,
                "retrieved_at": retrieved_at,
                "error_class": getattr(result, "error_class", None),
                "error_message": getattr(result, "error_message", None),
            }],
            "ohlcv": [],
        }

    rows: List[Dict[str, Any]] = []
    for row in result.payload:
        if not _valid_kline_row(row, 7):
            continue
        rows.append({
            "exchange": exchange,
            "market_id": spec.get("symbol"),
            "timestamp": datetime.fromtimestamp(
                float(row[0]) / 1000, tz=timezone.utc
            ).isoformat(),
            "open": safe_float(row[1]),
            "high": safe_float(row[2]),
            "low": safe_float(row[3]),
            "close": safe_float(row[4]),
            "volume": safe_float(row[5]),
            "quote_volume": safe_float(row[7]) if len(row) > 7 else None,
            "volume_source": "PROVIDER_SUPPLIED_TRADED_BASE_VOLUME",
            "timeframe": EXCHANGE_KLINE_INTERVAL,
            "provider_timestamp_ms": safe_int(row[0]),
        })

    if not rows:
        return {
            "exchange": exchange,
            "status": "NOT_AVAILABLE",
            "selected_provider": exchange,
            "attempts": [{
                "provider": exchange,
                "provider_mode": spec.get("mode"),
                "endpoint": spec.get("url", "").split("/api")[-1],
                "http_status": result.status,
                "ok": result.ok,
                "valid": False,
                "retrieved_at": retrieved_at,
                "error_class": result.error_class,
                "error_message": result.error_message,
            }],
            "ohlcv": [],
        }

    return {
        "exchange": exchange,
        "status": "VALIDATED",
        "selected_provider": exchange,
        "selected_provider_mode": spec.get("mode"),
        "fallback_used": False,
        "attempts": [{
            "provider": exchange,
            "provider_mode": spec.get("mode"),
            "endpoint": spec.get("url", "").split("/api")[-1],
            "http_status": result.status,
            "ok": result.ok,
            "valid": True,
            "retrieved_at": retrieved_at,
            "error_class": result.error_class,
            "error_message": result.error_message,
        }],
        "ohlcv": rows,
    }


def acquire_multi_exchange_evidence() -> Dict[str, Any]:
    """Probe all 8 core exchanges in parallel and apply the 7-of-8 gate.

    Each exchange is an independent probe. No failover between exchanges.
    The gate requires at least MIN_VALIDATED_EXCHANGE_COUNT of
    TARGET_EXCHANGE_COUNT exchanges to return VALIDATED status.
    """
    specs = MULTI_EXCHANGE_SPECS
    per_exchange: Dict[str, Dict[str, Any]] = {}
    for exchange, spec in specs.items():
        result = http_json(spec["url"], params=spec.get("params"))
        per_exchange[exchange] = _normalize_exchange_payload(
            exchange, spec, result
        )

    validated = [
        x for x in per_exchange.values() if x.get("status") == "VALIDATED"
    ]
    validated_count = len(validated)
    total_count = len(specs)
    gate_passed = validated_count >= MIN_VALIDATED_EXCHANGE_COUNT

    return {
        "probe_symbol": MULTI_EXCHANGE_PROBE_SYMBOL,
        "timeframe": EXCHANGE_KLINE_INTERVAL,
        "volume_definition": "PROVIDER_SUPPLIED_TRADED_BASE_VOLUME",
        "requested_exchanges": list(specs.keys()),
        "per_exchange": per_exchange,
        "validated_exchange_count": validated_count,
        "target_exchange_count": TARGET_EXCHANGE_COUNT,
        "min_validated_exchange_count": MIN_VALIDATED_EXCHANGE_COUNT,
        "coverage_ratio": (
            validated_count / total_count if total_count else 0.0
        ),
        "gate": {
            "name": "U06_5_UNIT_4_EXCHANGE_COVERAGE",
            "required": MIN_VALIDATED_EXCHANGE_COUNT,
            "target": TARGET_EXCHANGE_COUNT,
            "actual": validated_count,
            "passed": gate_passed,
            "status": "PASSED" if gate_passed else "FAILED",
        },
        "exchange_evidence_engine": {
            "mode": "INDEPENDENT_PARALLEL_PROBES",
            "failover_between_exchanges": False,
            "selection_used_for_current_top125": False,
        },
    }


# ---------------------------------------------------------------------------
# U06.5 Unit 5 — Independent order-book acquisition + normalization.
# ---------------------------------------------------------------------------

def _valid_orderbook_payload(payload: Any) -> bool:
    if not isinstance(payload, dict):
        return False
    bids = payload.get("bids")
    asks = payload.get("asks")
    if not isinstance(bids, list) or not isinstance(asks, list):
        return False
    if not bids or not asks:
        return False
    return all(
        isinstance(row, list) and len(row) >= 2
        and safe_float(row[0]) is not None
        and safe_float(row[1]) is not None
        for row in bids + asks
    )


def _normalize_orderbook(
    exchange: str,
    spec: Dict[str, Any],
    result: Any,
) -> Dict[str, Any]:
    """Normalize one exchange's raw order-book payload into the U06.5-A contract.

    Each exchange is probed independently. No failover between exchanges.
    Provider-supplied depth is preserved exactly; no fabricated levels.
    """
    retrieved_at = result.retrieved_at if result is not None else utc_now()

    if result is None or not result.ok or not _valid_orderbook_payload(result.payload):
        return {
            "exchange": exchange,
            "status": "NOT_AVAILABLE",
            "selected_provider": exchange,
            "attempts": [{
                "provider": exchange,
                "provider_mode": spec.get("mode"),
                "endpoint": spec.get("url", "").split("/api")[-1],
                "http_status": getattr(result, "status", None),
                "ok": bool(result and result.ok),
                "valid": False,
                "retrieved_at": retrieved_at,
                "error_class": getattr(result, "error_class", None),
                "error_message": getattr(result, "error_message", None),
            }],
            "bids": [],
            "asks": [],
        }

    payload = result.payload
    bids = [
        {
            "price": safe_float(row[0]),
            "size": safe_float(row[1]),
        }
        for row in payload["bids"]
        if isinstance(row, list) and len(row) >= 2
    ]
    asks = [
        {
            "price": safe_float(row[0]),
            "size": safe_float(row[1]),
        }
        for row in payload["asks"]
        if isinstance(row, list) and len(row) >= 2
    ]

    return {
        "exchange": exchange,
        "status": "VALIDATED",
        "selected_provider": exchange,
        "selected_provider_mode": spec.get("mode"),
        "fallback_used": False,
        "attempts": [{
            "provider": exchange,
            "provider_mode": spec.get("mode"),
            "endpoint": spec.get("url", "").split("/api")[-1],
            "http_status": result.status,
            "ok": result.ok,
            "valid": True,
            "retrieved_at": retrieved_at,
            "error_class": result.error_class,
            "error_message": result.error_message,
        }],
        "bids": bids,
        "asks": asks,
    }


def acquire_multi_exchange_orderbook() -> Dict[str, Any]:
    """Probe all 8 core exchanges for order-book depth independently.

    Each exchange is an independent probe. No failover between exchanges.
    Missing features (depth, spread) are never fabricated.
    """
    specs = ORDERBOOK_SPECS
    per_exchange: Dict[str, Dict[str, Any]] = {}
    for exchange, spec in specs.items():
        result = http_json(spec["url"], params=spec.get("params"))
        per_exchange[exchange] = _normalize_orderbook(
            exchange, spec, result
        )

    validated = [
        x for x in per_exchange.values() if x.get("status") == "VALIDATED"
    ]
    validated_count = len(validated)
    total_count = len(specs)

    return {
        "probe_symbol": MULTI_EXCHANGE_PROBE_SYMBOL,
        "volume_definition": "PROVIDER_SUPPLIED_TRADED_BASE_VOLUME",
        "requested_exchanges": list(specs.keys()),
        "per_exchange": per_exchange,
        "validated_exchange_count": validated_count,
        "target_exchange_count": TARGET_EXCHANGE_COUNT,
        "min_validated_exchange_count": MIN_VALIDATED_EXCHANGE_COUNT,
        "coverage_ratio": (
            validated_count / total_count if total_count else 0.0
        ),
        "gate": {
            "name": "U06_5_UNIT_5_ORDERBOOK_COVERAGE",
            "required": MIN_VALIDATED_EXCHANGE_COUNT,
            "target": TARGET_EXCHANGE_COUNT,
            "actual": validated_count,
            "passed": validated_count >= MIN_VALIDATED_EXCHANGE_COUNT,
            "status": (
                "PASSED" if validated_count >= MIN_VALIDATED_EXCHANGE_COUNT
                else "FAILED"
            ),
        },
        "orderbook_engine": {
            "mode": "INDEPENDENT_PARALLEL_PROBES",
            "failover_between_exchanges": False,
            "fabricated_depth": False,
            "selection_used_for_current_top125": False,
        },
    }