"""U06.5 Unit 7 — Reliability-weighted multi-exchange reference price engine.

Deterministic/synthetic tests only. No live network calls.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone, timedelta

import pytest

from app.market.reference import (
    OUTLIER_ENGINE_VERSION,
    PRICE_AGGREGATOR_VERSION,
    REFERENCE_ENGINE_VERSION,
    _bounded01,
    _freshness_score,
    _impact_score,
    _relative_log_score,
    _spread_score,
    _build_reliability_scores,
    build_live_reference_price_from_multi_exchange,
    make_market_observation,
    median_abs_deviation,
    normalize_quote_to_usd,
    orderbook_quality_metrics,
    outlier_filter_v1,
    price_aggregate_v1,
    validate_market_observation,
    validate_reliability_weights,
)
from app.config.quality import (
    QUALITY_CONFIG,
    TARGET_EXCHANGE_COUNT,
    FRESHNESS_THRESHOLD_SECONDS,
)

RETRIEVED_AT = "2026-09-11T16:30:00+00:00"


# ---------------------------------------------------------------------------
# Weight validation
# ---------------------------------------------------------------------------

def test_u06_5_unit_7_validate_reliability_weights():
    result = validate_reliability_weights()
    assert result["valid"] is True
    assert result["failures"] == []
    assert result["weight_sum"] == pytest.approx(1.0, abs=1e-6)
    assert "data_integrity" in result["weights"]
    assert "cross_exchange_consistency" in result["weights"]


def test_u06_5_unit_7_weights_are_non_negative():
    result = validate_reliability_weights()
    for name, weight in result["weights"].items():
        assert weight >= 0, f"{name} weight is negative"


# ---------------------------------------------------------------------------
# MAD / outlier filtering
# ---------------------------------------------------------------------------

def test_u06_5_unit_7_median_abs_deviation():
    assert median_abs_deviation([]) == 0.0
    assert median_abs_deviation([5.0]) == 0.0
    assert median_abs_deviation([1.0, 1.0, 1.0]) == 0.0
    assert median_abs_deviation([1.0, 2.0, 3.0]) == 1.0
    assert median_abs_deviation([1.0, 2.0, 3.0, 4.0, 5.0]) == 1.0


def test_u06_5_unit_7_bounded01():
    assert _bounded01(0.5) == 0.5
    assert _bounded01(-0.1) == 0.0
    assert _bounded01(1.5) == 1.0
    assert _bounded01(None) is None
    assert _bounded01(float("nan")) is None
    assert _bounded01(float("inf")) is None


def test_u06_5_unit_7_outlier_filter_no_outliers():
    observations = [
        {"normalized_usd_price": 100.0, "exchange": "EX1"},
        {"normalized_usd_price": 101.0, "exchange": "EX2"},
        {"normalized_usd_price": 102.0, "exchange": "EX3"},
    ]
    result = outlier_filter_v1(observations)
    assert result["status"] == "VALIDATED"
    assert len(result["accepted"]) == 3
    assert len(result["rejected"]) == 0
    assert result["version"] == OUTLIER_ENGINE_VERSION
    assert result["median"] == 101.0
    assert result["mad"] == 1.0
    for item in result["accepted"]:
        assert "outlier_percentage_deviation" in item
        assert "outlier_robust_z" in item


def test_u06_5_unit_7_outlier_filter_rejects_extreme():
    observations = [
        {"normalized_usd_price": 100.0, "exchange": "EX1"},
        {"normalized_usd_price": 101.0, "exchange": "EX2"},
        {"normalized_usd_price": 5000.0, "exchange": "EX3"},
    ]
    result = outlier_filter_v1(observations)
    assert result["status"] == "VALIDATED"
    assert len(result["accepted"]) == 2
    assert len(result["rejected"]) == 1
    assert result["rejected"][0]["reason"] == "ROBUST_OUTLIER"
    assert "percentage_deviation" in result["rejected"][0]
    assert "robust_z" in result["rejected"][0]


def test_u06_5_unit_7_outlier_filter_rejects_invalid_price():
    observations = [
        {"normalized_usd_price": None, "exchange": "EX1"},
        {"normalized_usd_price": 100.0, "exchange": "EX2"},
    ]
    result = outlier_filter_v1(observations)
    assert len(result["accepted"]) == 1
    assert len(result["rejected"]) == 1
    assert result["rejected"][0]["reason"] == "PRICE_INVALID"


def test_u06_5_unit_7_outlier_filter_all_rejected():
    observations = [
        {"normalized_usd_price": None, "exchange": "EX1"},
    ]
    result = outlier_filter_v1(observations)
    assert result["status"] == "DATA_UNAVAILABLE"
    assert len(result["accepted"]) == 0
    assert len(result["rejected"]) == 0


def test_u06_5_unit_7_outlier_filter_empty():
    result = outlier_filter_v1([])
    assert result["status"] == "DATA_UNAVAILABLE"
    assert result["median"] is None
    assert result["mad"] is None


# ---------------------------------------------------------------------------
# Market observation model
# ---------------------------------------------------------------------------

def _make_obs(
    exchange="EX1",
    price=100.0,
    volume_usd_24h=None,
    timestamp=None,
    quote_asset="USDT",
    asset="TEST",
    market_type="SPOT",
    retrieved_at=RETRIEVED_AT,
):
    return make_market_observation(
        exchange=exchange,
        exchange_id=exchange,
        asset=asset,
        base_asset=asset,
        quote_asset=quote_asset,
        market_id=f"{asset}{quote_asset}",
        market_type=market_type,
        price=price,
        volume_usd_24h=volume_usd_24h,
        timestamp=timestamp or retrieved_at,
        retrieved_at=retrieved_at,
        provider=exchange,
    )


def test_u06_5_unit_7_make_market_observation():
    obs = _make_obs(price=100.0, timestamp="2026-09-11T16:29:00+00:00")
    assert obs["exchange"] == "EX1"
    assert obs["asset"] == "TEST"
    assert obs["price"] == 100.0
    assert obs["quote_asset"] == "USDT"
    assert obs["market_type"] == "SPOT"
    assert obs["quality_status"] == "UNVALIDATED"
    assert obs["rejection_reason"] is None
    assert obs["age_seconds"] == 60.0


def test_u06_5_unit_7_normalize_quote_to_usd():
    obs = _make_obs(price=100.0, quote_asset="USDT")
    price, meta = normalize_quote_to_usd(obs)
    assert price == 100.0
    assert meta["status"] == "VALIDATED"
    assert meta["chain"] == ["USDT", "USD"]

    obs_usd = _make_obs(price=101.0, quote_asset="USD")
    price2, meta2 = normalize_quote_to_usd(obs_usd)
    assert price2 == 101.0
    assert meta2["chain"] == ["USD", "USD"]

    obs_usdc = _make_obs(price=99.0, quote_asset="USDC")
    price3, _ = normalize_quote_to_usd(obs_usdc)
    assert price3 == 99.0

    obs_btc = _make_obs(price=0.01, quote_asset="BTC")
    price_btc, meta_btc = normalize_quote_to_usd(obs_btc, {"BTC": 100_000.0})
    assert price_btc == 1000.0
    assert meta_btc["chain"] == ["BTC", "USD"]
    assert meta_btc["conversion_rate"] == 100_000.0

    obs_eth = _make_obs(price=1.0, quote_asset="ETH")
    price_eth, meta_eth = normalize_quote_to_usd(obs_eth, {"ETH": 2_500.0})
    assert price_eth == 2_500.0
    assert meta_eth["chain"] == ["ETH", "USD"]

    obs_bad = _make_obs(price=0.0, quote_asset="USDT")
    price_bad, meta_bad = normalize_quote_to_usd(obs_bad)
    assert price_bad is None
    assert meta_bad["status"] == "INVALID_PRICE"

    obs_no_conversion = _make_obs(price=50.0, quote_asset="JPY")
    price_jpy, meta_jpy = normalize_quote_to_usd(obs_no_conversion)
    assert price_jpy is None
    assert meta_jpy["status"] == "UNAVAILABLE"


def test_u06_5_unit_7_validate_market_observation():
    fresh = "2026-09-11T16:29:00+00:00"
    obs = _make_obs(price=100.0, timestamp=fresh, volume_usd_24h=1_000_000)
    ok, reason = validate_market_observation(obs)
    assert ok is True
    assert reason == "VALID"

    stale = "2026-09-11T14:00:00+00:00"
    obs_stale = _make_obs(price=100.0, timestamp=stale, volume_usd_24h=1_000_000)
    ok_stale, reason_stale = validate_market_observation(obs_stale)
    assert ok_stale is False
    assert reason_stale == "STALE_DATA"

    obs_bad_price = _make_obs(price=-1.0)
    ok_bad, reason_bad = validate_market_observation(obs_bad_price)
    assert ok_bad is False
    assert reason_bad == "PRICE_INVALID"

    obs_future = _make_obs(price=100.0, market_type="FUTURES")
    ok_fut, reason_fut = validate_market_observation(obs_future)
    assert ok_fut is False
    assert reason_fut == "WRONG_MARKET_TYPE"

    obs_no_asset = _make_obs(price=100.0, asset="")
    obs_no_asset["asset"] = ""
    ok_no_asset, reason_no_asset = validate_market_observation(obs_no_asset)
    assert ok_no_asset is False
    assert reason_no_asset == "ASSET_IDENTITY_MISSING"


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def test_u06_5_unit_7_freshness_score():
    assert _freshness_score(None) is None
    assert _freshness_score(-1.0) is None
    assert _freshness_score(0.0) == 1.0
    score = _freshness_score(float(FRESHNESS_THRESHOLD_SECONDS))
    assert 0.0 < score < 1.0


def test_u06_5_unit_7_spread_score():
    assert _spread_score(None) is None
    assert _spread_score(-1.0) is None
    assert _spread_score(0.0) == 1.0
    score = _spread_score(
        float(QUALITY_CONFIG["spread_soft_limit_bps"])
    )
    assert 0.0 < score < 1.0


def test_u06_5_unit_7_impact_score():
    assert _impact_score(None) is None
    assert _impact_score(-1.0) is None
    assert _impact_score(0.0) == 1.0
    assert _impact_score(10.0) < 1.0
    assert _impact_score(10.0) > _impact_score(100.0)


def test_u06_5_unit_7_relative_log_score():
    peers = [100.0, 200.0, 300.0]
    assert _relative_log_score(None, peers) is None
    assert _relative_log_score(0.0, peers) is None
    assert _relative_log_score(-5.0, peers) is None
    assert _relative_log_score(300.0, peers) == 1.0
    assert _relative_log_score(100.0, peers) == 0.0
    assert 0.0 < _relative_log_score(200.0, peers) < 1.0

    assert _relative_log_score(200.0, []) is None
    assert _relative_log_score(200.0, None) is None


# ---------------------------------------------------------------------------
# Reliability scoring
# ---------------------------------------------------------------------------

def _make_validated_obs(exchange, price, market_quality=None):
    obs = _make_obs(exchange=exchange, price=price)
    obs["quality_status"] = "VALIDATED"
    obs["volume_usd_24h"] = 1_000_000.0
    obs["normalized_usd_price"] = price
    if market_quality is not None:
        obs["market_quality"] = market_quality
    return obs


def test_u06_5_unit_7_reliability_score_no_orderbook_quality():
    obs1 = _make_validated_obs("EX1", 100.0)
    obs2 = _make_validated_obs("EX2", 101.0)
    obs1["market_quality"] = {"status": "NOT_AVAILABLE"}
    obs2["market_quality"] = {"status": "NOT_AVAILABLE"}
    scored = _build_reliability_scores([obs1, obs2])
    assert len(scored) == 2
    for item in scored:
        components = item["reliability"]["components"]
        assert components["data_integrity"]["status"] == "AVAILABLE"
        assert components["near_depth"]["status"] == "NOT_AVAILABLE"
        assert components["near_depth"]["weight_excluded"] is True
        assert components["far_depth"]["status"] == "NOT_AVAILABLE"
        assert components["spread"]["status"] == "NOT_AVAILABLE"
        assert components["price_impact"]["status"] == "NOT_AVAILABLE"
        assert components["freshness"]["status"] == "AVAILABLE"
        assert components["volume"]["status"] == "AVAILABLE"
        assert components["cross_exchange_consistency"]["status"] == "AVAILABLE"
        assert 0.0 <= item["reliability"]["score"] <= 1.0
        assert item["reliability"]["fixed_exchange_rank"] is False


def _make_deep_book():
    """A validated order book with enough depth for $10k/$100k impact tests."""
    bids = [[99.95 - i * 0.05, 500.0] for i in range(20)]
    asks = [[100.05 + i * 0.05, 500.0] for i in range(20)]
    return {
        "status": "VALIDATED",
        "mid_price": 100.0,
        "spread_pct": 0.1,
        "bids": bids,
        "asks": asks,
        "source_timestamp": "2026-09-11T16:29:30+00:00",
        "retrieved_at": RETRIEVED_AT,
        "level_count_bid": 20,
        "level_count_ask": 20,
    }


def test_u06_5_unit_7_reliability_score_with_orderbook_quality():
    quality = orderbook_quality_metrics(_make_deep_book())
    obs1 = _make_validated_obs("EX1", 100.0, market_quality=quality)
    obs2 = _make_validated_obs("EX2", 101.0, market_quality=quality)
    scored = _build_reliability_scores([obs1, obs2])
    for item in scored:
        components = item["reliability"]["components"]
        assert components["near_depth"]["status"] == "AVAILABLE"
        assert components["far_depth"]["status"] == "AVAILABLE"
        assert components["spread"]["status"] == "AVAILABLE"
        assert components["price_impact"]["status"] == "AVAILABLE"
        assert 0.0 <= item["reliability"]["score"] <= 1.0


def test_u06_5_unit_7_reliability_score_denominator_renormalized():
    obs1 = _make_validated_obs("EX1", 100.0)
    obs2 = _make_validated_obs("EX2", 101.0)
    obs1["market_quality"] = {"status": "NOT_AVAILABLE"}
    obs2["market_quality"] = {"status": "NOT_AVAILABLE"}
    scored = _build_reliability_scores([obs1, obs2])
    item = scored[0]
    weights = QUALITY_CONFIG["reliability_component_weights"]
    present_weight_sum = sum(
        weights[name] for name, v in item["reliability"]["components"].items()
        if v["status"] == "AVAILABLE"
    )
    excluded_weight_sum = sum(
        weights[name] for name, v in item["reliability"]["components"].items()
        if v["status"] == "NOT_AVAILABLE"
    )
    total_weight = present_weight_sum + excluded_weight_sum
    assert total_weight == pytest.approx(1.0, abs=1e-6)
    assert present_weight_sum < 1.0
    assert excluded_weight_sum > 0


# ---------------------------------------------------------------------------
# Price aggregation
# ---------------------------------------------------------------------------

def test_u06_5_unit_7_price_aggregate_valid():
    obs1 = _make_validated_obs("EX1", 100.0)
    obs2 = _make_validated_obs("EX2", 101.0)
    result = price_aggregate_v1([obs1, obs2])
    assert result["status"] == "CALCULATED"
    assert result["reference_price"] is not None
    assert 100.0 <= result["reference_price"] <= 101.0
    assert "confidence" in result
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["aggregate_version"] == PRICE_AGGREGATOR_VERSION
    assert "outlier" in result
    assert result["methodology"]["missing_features_are_not_fabricated"] is True


def test_u06_5_unit_7_price_aggregate_outlier_rejected():
    obs1 = _make_validated_obs("EX1", 100.0)
    obs2 = _make_validated_obs("EX2", 101.0)
    obs3 = _make_validated_obs("EX3", 5000.0)
    result = price_aggregate_v1([obs1, obs2, obs3])
    assert len(result["rejected_markets"]) >= 1
    assert any(
        r.get("reason") == "ROBUST_OUTLIER"
        for r in result["rejected_markets"]
    )
    assert result["reference_price"] is not None


def test_u06_5_unit_7_price_aggregate_all_rejected_by_quality():
    stale = "2026-09-11T14:00:00+00:00"
    obs = _make_obs(exchange="EX1", price=100.0, timestamp=stale)
    obs["normalized_usd_price"] = 100.0
    obs["volume_usd_24h"] = 1_000_000.0
    result = price_aggregate_v1([obs])
    assert result["status"] == "DATA_UNAVAILABLE"
    assert len(result["rejected_markets"]) >= 1
    assert result["reference_price"] is None


def test_u06_5_unit_7_price_aggregate_cross_exchange_confirmed():
    obs1 = _make_validated_obs("EX1", 100.0)
    obs2 = _make_validated_obs("EX2", 101.0)
    result = price_aggregate_v1([obs1, obs2])
    assert result["status"] == "CALCULATED"
    assert result["reference_price"] is not None
    assert result["methodology"]["single_exchange_is_not_cross_exchange_confirmed"] is False


def test_u06_5_unit_7_price_aggregate_confidence_components():
    obs1 = _make_validated_obs("EX1", 100.0)
    obs2 = _make_validated_obs("EX2", 101.0)
    result = price_aggregate_v1([obs1, obs2])
    cc = result["confidence_components"]
    assert "mean_reliability" in cc
    assert "cross_exchange_agreement" in cc
    assert "exchange_coverage" in cc


def test_u06_5_unit_7_price_aggregate_weights_normalized():
    obs1 = _make_validated_obs("EX1", 100.0)
    obs2 = _make_validated_obs("EX2", 101.0)
    result = price_aggregate_v1([obs1, obs2])
    nw = result["normalized_weights"]
    total = sum(nw.values())
    assert total == pytest.approx(1.0, abs=1e-9)


def test_u06_5_unit_7_price_aggregate_rejects_non_spot():
    obs = _make_obs(exchange="EX1", price=100.0, market_type="FUTURES")
    obs["normalized_usd_price"] = 100.0
    result = price_aggregate_v1([obs])
    assert result["status"] == "DATA_UNAVAILABLE"
    assert len(result["rejected_markets"]) >= 1


# ---------------------------------------------------------------------------
# Build live reference price from multi-exchange evidence
# ---------------------------------------------------------------------------

def _make_multi_exchange_evidence():
    book = {
        "status": "VALIDATED",
        "mid_price": 100.0,
        "spread_pct": 0.1,
        "bids": [[99.95, 5.0], [99.90, 10.0]],
        "asks": [[100.05, 5.0], [100.10, 10.0]],
        "source_timestamp": "2026-09-11T16:29:30+00:00",
        "retrieved_at": RETRIEVED_AT,
        "level_count_bid": 2,
        "level_count_ask": 2,
    }
    per_exchange = {
        "binance": {
            "ohlcv": [{
                "timestamp": "2026-09-11T16:25:00+00:00",
                "close": 100.0,
                "quote_volume": 500_000.0,
                "volume": 5000.0,
                "market_id": "BTCUSDT",
                "volume_source": "PROVIDER_SUPPLIED_TRADED_BASE_VOLUME",
                "timeframe": "5m",
            }],
            "retrieved_at": RETRIEVED_AT,
            "orderbook_quality": orderbook_quality_metrics(book),
        },
        "okx": {
            "ohlcv": [{
                "timestamp": "2026-09-11T16:25:00+00:00",
                "close": 101.0,
                "quote_volume": 600_000.0,
                "volume": 6000.0,
                "market_id": "BTC-USDT",
                "volume_source": "PROVIDER_SUPPLIED_TRADED_BASE_VOLUME",
                "timeframe": "5m",
            }],
            "retrieved_at": RETRIEVED_AT,
            "orderbook_quality": orderbook_quality_metrics(book),
        },
    }
    return {"per_exchange": per_exchange}


def test_u06_5_unit_7_build_live_reference_price():
    evidence = _make_multi_exchange_evidence()
    result = build_live_reference_price_from_multi_exchange(evidence)
    assert result["status"] in ("CALCULATED", "INSUFFICIENT_CROSS_EXCHANGE_CONFIRMATION")
    assert result["symbol"] == "BTC"
    assert result["engine_version"] == REFERENCE_ENGINE_VERSION
    assert result["source_policy"] == "DYNAMIC_RELIABILITY_WEIGHTED_MULTI_EXCHANGE"
    assert result["not_global_market_cap"] is True


def test_u06_5_unit_7_build_live_reference_price_no_observations():
    result = build_live_reference_price_from_multi_exchange({"per_exchange": {}})
    assert result["status"] == "NOT_AVAILABLE"
    assert result["reason"] == "NO_VALID_EXCHANGE_PRICE_OBSERVATIONS"


# ---------------------------------------------------------------------------
# Orderbook quality metrics
# ---------------------------------------------------------------------------

def test_u06_5_unit_7_orderbook_quality_validated():
    book = _make_deep_book()
    quality = orderbook_quality_metrics(book)
    assert quality["status"] == "VALIDATED"
    assert quality["mid_price"] == 100.0
    assert quality["spread_bps"] == 10.0
    assert "0.05%" in quality["depth_bands"]
    assert "1.00%" in quality["depth_bands"]
    assert "10000" in quality["price_impact"]
    assert "100000" in quality["price_impact"]
    assert quality["age_seconds"] == 30.0


def test_u06_5_unit_7_orderbook_quality_not_available():
    assert orderbook_quality_metrics({"status": "NOT_AVAILABLE"}) == {"status": "NOT_AVAILABLE"}
    assert orderbook_quality_metrics({"status": "VALIDATED"}) == {"status": "NOT_AVAILABLE"}
    assert orderbook_quality_metrics({}) == {"status": "NOT_AVAILABLE"}


# ---------------------------------------------------------------------------
# Self-test parity with notebook market_engine_self_tests
# ---------------------------------------------------------------------------

def test_u06_5_unit_7_market_engine_self_test_parity():
    """Mirror the notebook's market_engine_self_tests for Unit 7 functions."""
    now = RETRIEVED_AT

    base = [
        make_market_observation(
            exchange="EX1", exchange_id="EX1",
            asset="TEST", base_asset="TEST", quote_asset="USDT",
            market_id="TESTUSDT", market_type="SPOT",
            price=100.0, volume_usd_24h=1_000_000,
            timestamp=now, retrieved_at=now, provider="TEST",
        ),
        make_market_observation(
            exchange="EX2", exchange_id="EX2",
            asset="TEST", base_asset="TEST", quote_asset="USD",
            market_id="TESTUSD", market_type="SPOT",
            price=101.0, volume_usd_24h=2_000_000,
            timestamp=now, retrieved_at=now, provider="TEST",
        ),
        make_market_observation(
            exchange="EX3", exchange_id="EX3",
            asset="TEST", base_asset="TEST", quote_asset="USD",
            market_id="TESTUSD3", market_type="SPOT",
            price=5000.0, volume_usd_24h=1_000_000,
            timestamp=now, retrieved_at=now, provider="TEST",
        ),
    ]

    conversion_prices = {"BTC": 100_000.0, "ETH": 2_500.0}
    for item in base:
        normalized, meta = normalize_quote_to_usd(item, conversion_prices)
        item["normalized_usd_price"] = normalized
        item["usd_normalization"] = meta

    assert base[0]["normalized_usd_price"] == 100.0
    assert base[1]["normalized_usd_price"] == 101.0
    assert base[2]["normalized_usd_price"] == 5000.0

    agg = price_aggregate_v1(base)

    assert len(agg["rejected_markets"]) >= 1
    assert agg["reference_price"] is not None
    assert agg["aggregate_version"] == PRICE_AGGREGATOR_VERSION
