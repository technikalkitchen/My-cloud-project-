"""U06.5 Unit 6 — Global asset normalization + validation.

Deterministic/synthetic tests only. No live network calls.
"""
from __future__ import annotations

import pytest

from app.market.global_providers import (
    normalize_cmc_asset,
    normalize_coingecko_asset,
    validate_core_assets,
    validate_identity,
    validate_numeric_market_fields,
    validate_ranked_universe,
    validate_record,
    validate_timestamp_fields,
    freshness_status,
)
from app.config.quality import FRESHNESS_THRESHOLD_SECONDS


RETRIEVED_AT = "2026-09-11T16:30:00+00:00"


def _fresh_timestamp():
    return "2026-09-11T16:29:00+00:00"


def _stale_timestamp():
    return "2026-09-11T14:00:00+00:00"


def test_u06_5_unit_6_normalize_cmc_asset():
    asset = {
        "id": 1,
        "slug": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "rank": 1,
        "last_updated": _fresh_timestamp(),
        "quote": {
            "USD": {
                "price": 100.0,
                "market_cap": 1e12,
                "volume_24h": 1e9,
                "percent_change_1h": 0.5,
                "percent_change_24h": 2.0,
                "rank": 1,
            },
        },
    }
    record = normalize_cmc_asset(asset)
    assert record["provider"] == "coinmarketcap"
    assert record["symbol"] == "BTC"
    assert record["name"] == "Bitcoin"
    assert record["price"] == 100.0
    assert record["market_cap"] == 1e12
    assert record["rank"] == 1
    assert record["last_updated"] == _fresh_timestamp()


def test_u06_5_unit_6_normalize_coingecko_asset():
    asset = {
        "id": "ethereum",
        "symbol": "eth",
        "name": "Ethereum",
        "market_cap_rank": 2,
        "current_price": 2500.0,
        "market_cap": 5e11,
        "total_volume": 5e8,
        "price_change_percentage_1h_in_currency": -1.0,
        "price_change_percentage_24h_in_currency": 3.0,
        "last_updated": _fresh_timestamp(),
    }
    record = normalize_coingecko_asset(asset)
    assert record["provider"] == "coingecko"
    assert record["symbol"] == "ETH"
    assert record["price"] == 2500.0
    assert record["market_cap"] == 5e11
    assert record["rank"] == 2


def test_u06_5_unit_6_validate_identity():
    valid = {
        "provider": "coinmarketcap",
        "symbol": "BTC",
        "canonical_asset_id": 1,
    }
    assert validate_identity(valid) == []
    bad = {"provider": "", "symbol": "", "canonical_asset_id": None}
    failures = validate_identity(bad)
    assert len(failures) == 3


def test_u06_5_unit_6_validate_numeric_market_fields():
    valid = {
        "price": 1.0,
        "market_cap": 2.0,
        "volume_24h": 3.0,
        "percent_change_1h": 0.0,
        "percent_change_24h": 0.0,
    }
    assert validate_numeric_market_fields(valid) == []
    bad = {}
    failures = validate_numeric_market_fields(bad)
    assert len(failures) == 5


def test_u06_5_unit_6_validate_timestamp_fields():
    fresh = {"last_updated": _fresh_timestamp()}
    assert validate_timestamp_fields(fresh, RETRIEVED_AT) == []
    stale = {"last_updated": _stale_timestamp()}
    failures = validate_timestamp_fields(stale, RETRIEVED_AT)
    assert len(failures) == 1
    assert "stale" in failures[0]
    missing = {}
    failures = validate_timestamp_fields(missing, RETRIEVED_AT)
    assert failures == ["missing last_updated"]


def test_u06_5_unit_6_freshness_status():
    assert freshness_status(_fresh_timestamp(), RETRIEVED_AT) == "FRESH"
    assert freshness_status(_stale_timestamp(), RETRIEVED_AT) == "STALE"
    assert freshness_status("not-a-date", RETRIEVED_AT) == "UNAVAILABLE"


def test_u06_5_unit_6_validate_ranked_universe():
    records = [
        {"symbol": f"A{i}", "rank": i}
        for i in range(1, 126)
    ]
    assert validate_ranked_universe(records, 125) == []
    short = records[:10]
    failures = validate_ranked_universe(short, 125)
    assert any("record count" in f for f in failures)
    dup = [
        {"symbol": "A", "rank": 1},
        {"symbol": "B", "rank": 1},
    ]
    failures = validate_ranked_universe(dup, 125)
    assert any("duplicate rank" in f for f in failures)


def test_u06_5_unit_6_validate_core_assets():
    records = [
        {"symbol": "BTC"},
        {"symbol": "ETH"},
        {"symbol": "USDT"},
        {"symbol": "SOL"},
    ]
    assert validate_core_assets(records) == []
    missing = [{"symbol": "ETH"}, {"symbol": "USDT"}]
    failures = validate_core_assets(missing)
    assert failures == ["missing core asset BTC"]


def test_u06_5_unit_6_validate_record_full():
    record = {
        "provider": "coinmarketcap",
        "symbol": "BTC",
        "canonical_asset_id": 1,
        "price": 100.0,
        "market_cap": 1e12,
        "volume_24h": 1e9,
        "percent_change_1h": 0.0,
        "percent_change_24h": 0.0,
        "rank": 1,
        "last_updated": _fresh_timestamp(),
    }
    result = validate_record(record, RETRIEVED_AT)
    assert result["valid"] is True
    assert result["failures"] == []
    assert result["freshness"] == "FRESH"
    bad = dict(record)
    bad["market_cap"] = None
    result = validate_record(bad, RETRIEVED_AT)
    assert result["valid"] is False
    assert any("market_cap" in f for f in result["failures"])