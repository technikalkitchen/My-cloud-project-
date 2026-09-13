"""U09 Unit 1 — Provider validation tests."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta

from app.market.validation import (
    validate_provider_assets,
    freshness_status,
)
from app.config.market_universe import CONFIG


def _make_asset(rank, price=100.0, mc=None, sym=None):
    if mc is None:
        mc = 10_000_000_000.0 / rank
    if sym is None:
        sym = f"A{rank}"
    return {
        "provider_asset_id": f"asset-{rank}",
        "symbol": sym,
        "name": f"Asset {rank}",
        "price_usd": price,
        "market_cap_usd": mc,
        "provider_rank": rank,
        "price_change_24h_pct": 1.0,
        "provider_timestamp": "2026-09-12T12:00:00+00:00",
    }


# ---------------------------------------------------------------------------
# validate_provider_assets
# ---------------------------------------------------------------------------

def test_validate_assets_pass():
    assets = [_make_asset(i) for i in range(1, 126)]
    result = validate_provider_assets(assets, 125)
    assert result["status"] == "PASS"
    assert len(result["valid_assets"]) == 125
    assert result["coverage_ratio"] == 1.0
    assert result["errors"] == []


def test_validate_assets_missing_id():
    assets = [_make_asset(1)]
    assets[0].pop("provider_asset_id")
    result = validate_provider_assets(assets, 125)
    assert result["status"] == "FAIL"
    assert any("missing_id" in e for e in result["errors"])


def test_validate_assets_duplicate_id():
    assets = [_make_asset(1), _make_asset(2)]
    assets[1]["provider_asset_id"] = assets[0]["provider_asset_id"]
    result = validate_provider_assets(assets, 125)
    assert result["status"] == "FAIL"
    assert any("duplicate_id" in e for e in result["errors"])


def test_validate_assets_invalid_rank_type():
    assets = [_make_asset(1)]
    assets[0]["provider_rank"] = "not_a_number"
    result = validate_provider_assets(assets, 125)
    assert result["status"] == "FAIL"
    assert any("invalid_rank" in e for e in result["errors"])


def test_validate_assets_rank_out_of_range():
    assets = [_make_asset(1)]
    assets[0]["provider_rank"] = 126
    result = validate_provider_assets(assets, 125)
    assert result["status"] == "FAIL"
    assert any("rank_out_of_range" in e for e in result["errors"])


def test_validate_assets_rank_zero():
    assets = [_make_asset(1)]
    assets[0]["provider_rank"] = 0
    result = validate_provider_assets(assets, 125)
    assert result["status"] == "FAIL"
    assert any("rank_out_of_range" in e for e in result["errors"])


def test_validate_assets_invalid_price():
    assets = [_make_asset(1)]
    assets[0]["price_usd"] = float("nan")
    result = validate_provider_assets(assets, 125)
    assert result["status"] == "FAIL"
    assert any("invalid_price" in e for e in result["errors"])


def test_validate_assets_negative_price():
    assets = [_make_asset(1)]
    assets[0]["price_usd"] = -1.0
    result = validate_provider_assets(assets, 125)
    assert result["status"] == "FAIL"
    assert any("invalid_price" in e for e in result["errors"])


def test_validate_assets_invalid_market_cap():
    assets = [_make_asset(1)]
    assets[0]["market_cap_usd"] = None
    result = validate_provider_assets(assets, 125)
    assert result["status"] == "FAIL"
    assert any("invalid_market_cap" in e for e in result["errors"])


def test_validate_assets_duplicate_rank():
    assets = [_make_asset(1), _make_asset(2)]
    assets[1]["provider_rank"] = 1
    result = validate_provider_assets(assets, 125)
    assert result["status"] == "FAIL"
    assert any("duplicate_rank" in e for e in result["errors"])


def test_validate_assets_rank_gap():
    assets = [_make_asset(i) for i in range(1, 124)]
    result = validate_provider_assets(assets, 125)
    assert result["status"] == "FAIL"
    assert any("rank_gaps" in e for e in result["errors"])


def test_validate_assets_coverage_short():
    assets = [_make_asset(i) for i in range(1, 10)]
    result = validate_provider_assets(assets, 125)
    assert result["status"] == "FAIL"
    assert any("coverage_count" in e for e in result["errors"])


def test_validate_assets_valid_assets_sorted_by_rank():
    assets = [_make_asset(i) for i in range(1, 6)]
    result = validate_provider_assets(assets, 5)
    assert result["status"] == "PASS"
    assert result["errors"] == []
    for a in result["valid_assets"]:
        assert a["rank_consistency_status"] == "MATCH"
    for i, a in enumerate(result["valid_assets"]):
        assert a["provider_rank"] == i + 1


def test_validate_assets_has_calculated_rank():
    assets = [_make_asset(i) for i in range(1, 6)]
    result = validate_provider_assets(assets, 125)
    for a in result["valid_assets"]:
        assert "calculated_rank" in a
        assert a["calculated_rank"] == a["provider_rank"]


def test_validate_assets_coverage_ratio():
    assets = [_make_asset(i) for i in range(1, 126)]
    result = validate_provider_assets(assets, 125)
    assert result["coverage_ratio"] == 1.0


def test_validate_assets_empty():
    result = validate_provider_assets([], 125)
    assert result["status"] == "FAIL"
    assert any("coverage" in e for e in result["errors"])
    assert any("rank_gap" in e for e in result["errors"])


def test_validate_assets_limited():
    assets = [_make_asset(i, sym=f"A{i}") for i in range(1, 201)]
    result = validate_provider_assets(assets, 200)
    assert result["status"] == "PASS"
    assert len(result["valid_assets"]) == 200


def test_validate_assets_rank_consistency_fields():
    assets = [_make_asset(i) for i in range(1, 6)]
    result = validate_provider_assets(assets, 125)
    for a in result["valid_assets"]:
        assert "rank_difference" in a
        assert "rank_consistency_status" in a
        assert a["rank_consistency_status"] in ("MATCH", "MINOR_DIFFERENCE", "WARNING", "FAIL")


# ---------------------------------------------------------------------------
# freshness_status
# ---------------------------------------------------------------------------

def test_freshness_fresh():
    now = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    ts = now - timedelta(seconds=100)
    state, age = freshness_status(ts, now)
    assert state == "FRESH"
    assert abs(age - 100.0) < 0.01


def test_freshness_stale():
    now = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    ts = now - timedelta(seconds=CONFIG["max_current_age_seconds"] + 1)
    state, age = freshness_status(ts, now)
    assert state == "STALE"
    assert age > CONFIG["max_current_age_seconds"]


def test_freshness_boundary():
    now = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    ts = now - timedelta(seconds=CONFIG["max_current_age_seconds"])
    state, age = freshness_status(ts, now)
    assert state == "FRESH"


def test_freshness_none():
    now = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    state, age = freshness_status(None, now)
    assert state == "UNAVAILABLE"
    assert age is None


def test_freshness_age_zero():
    now = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    state, age = freshness_status(now, now)
    assert state == "FRESH"
    assert age == 0.0
