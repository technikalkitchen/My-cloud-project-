"""U06.5 Unit 8 — Dynamic market-cap ranking + Kitchen index engine.

Deterministic/synthetic tests only. No live network calls.
"""
from __future__ import annotations

import pytest

from app.market.ranking import (
    INDEX_VERSION,
    RANKING_VERSION,
    calculate_indices_from_top125,
    deterministic_sort_key,
    dynamic_rank_assets,
)
from app.config.quality import (
    CORE_ASSETS,
    TOP_N,
    TARGET_CANDIDATE_POOL,
)


def _make_asset(
    symbol="A",
    market_cap=None,
    canonical_asset_id=None,
    provider_rank=None,
    **extra,
):
    asset = {
        "provider_asset_id": canonical_asset_id or f"id_{symbol}",
        "canonical_asset_id": canonical_asset_id or f"id_{symbol}",
        "symbol": symbol,
        "name": symbol,
        "provider": "TEST",
        "provider_mode": "TEST",
        "provider_rank": provider_rank,
        "price": 100.0,
        "market_cap": market_cap,
        "volume_24h": 1_000_000.0,
        "source_timestamp": "2026-09-11T16:29:00+00:00",
        "retrieved_at": "2026-09-11T16:30:00+00:00",
        "identity_status": "VALIDATED",
    }
    asset.update(extra)
    return asset


def _make_full_top125():
    """Generate a valid 125-asset universe: BTC, ETH, USDT, then 122 alts."""
    assets = []
    for i in range(TOP_N):
        if i == 0:
            symbol = "BTC"
        elif i == 1:
            symbol = "ETH"
        elif i == 2:
            symbol = "USDT"
        else:
            symbol = f"A{i}"
        assets.append(
            _make_asset(
                symbol=symbol,
                market_cap=float(1_000_000_000 - i * 1_000_000),
                canonical_asset_id=f"cmc:{1000 + i}",
                provider_rank=i + 1,
            )
        )
    return assets


# ---------------------------------------------------------------------------
# Deterministic sort key
# ---------------------------------------------------------------------------

def test_u06_5_unit_8_deterministic_sort_key():
    a = {"market_cap": 100.0, "canonical_asset_id": "b", "symbol": "X"}
    b = {"market_cap": 200.0, "canonical_asset_id": "a", "symbol": "Y"}
    key_a = deterministic_sort_key(a)
    key_b = deterministic_sort_key(b)
    assert key_b < key_a  # -200.0 < -100.0 → higher market_cap sorts first

    same_mc = [
        {"market_cap": 100.0, "canonical_asset_id": "z", "symbol": "Y"},
        {"market_cap": 100.0, "canonical_asset_id": "a", "symbol": "Y"},
        {"market_cap": 100.0, "canonical_asset_id": "a", "symbol": "X"},
    ]
    same_mc.sort(key=deterministic_sort_key)
    assert same_mc[0]["symbol"] == "X"
    assert same_mc[1]["canonical_asset_id"] == "a"
    assert same_mc[2]["canonical_asset_id"] == "z"

    no_mc = {"symbol": "Z"}
    key = deterministic_sort_key(no_mc)
    assert key[0] == 1.0  # -(mc or -1.0) where mc is None → -(-1.0) = 1.0


# ---------------------------------------------------------------------------
# Dynamic ranking
# ---------------------------------------------------------------------------

def test_u06_5_unit_8_dynamic_rank_basic():
    assets = [
        _make_asset(symbol="BTC", market_cap=1000.0, canonical_asset_id="btc_id"),
        _make_asset(symbol="ETH", market_cap=500.0, canonical_asset_id="eth_id"),
        _make_asset(symbol="SOL", market_cap=750.0, canonical_asset_id="sol_id"),
    ]
    result = dynamic_rank_assets(assets)
    assert result["status"] == "DATA_PARTIAL"
    assert result["candidate_received"] == 3
    assert result["candidate_valid"] == 3
    assert len(result["all_valid_ranked"]) == 3
    ranked = result["all_valid_ranked"]
    assert ranked[0]["calculated_rank"] == 1
    assert ranked[0]["symbol"] == "BTC"
    assert ranked[1]["symbol"] == "SOL"
    assert ranked[2]["symbol"] == "ETH"
    assert ranked[0]["ranking_version"] == RANKING_VERSION


def test_u06_5_unit_8_dynamic_rank_excludes_invalid():
    assets = [
        _make_asset(symbol="BTC", market_cap=1000.0, canonical_asset_id="btc_id"),
        _make_asset(symbol="ETH", market_cap=None, canonical_asset_id="eth_id"),
        _make_asset(symbol="SOL", market_cap=-50.0, canonical_asset_id="sol_id"),
    ]
    result = dynamic_rank_assets(assets)
    assert result["candidate_received"] == 3
    assert result["candidate_valid"] == 1
    assert result["candidate_invalid"] == 2
    assert len(result["all_valid_ranked"]) == 1
    assert result["all_valid_ranked"][0]["symbol"] == "BTC"


def test_u06_5_unit_8_dynamic_rank_full_top125():
    assets = _make_full_top125()
    result = dynamic_rank_assets(assets)
    assert result["status"] == "VALIDATED"
    assert len(result["top125"]) == TOP_N
    assert result["top125"][0]["calculated_rank"] == 1
    assert result["top125"][0]["symbol"] == "BTC"
    assert result["top125"][0]["segment"] == "BTC"
    assert result["top125"][1]["symbol"] == "ETH"
    assert result["top125"][1]["segment"] == "ETH"
    assert result["top125"][2]["symbol"] == "USDT"
    assert result["top125"][2]["segment"] == "TOP10_ALT"
    assert result["top125"][9]["segment"] == "TOP10_ALT"
    assert result["top125"][10]["segment"] == "BROAD_ALT_11_125"


def test_u06_5_unit_8_dynamic_rank_segments():
    assets = _make_full_top125()
    result = dynamic_rank_assets(assets)
    top125 = result["top125"]
    assert top125[0]["segment"] == "BTC"
    assert top125[1]["segment"] == "ETH"
    for i in range(2, 10):
        assert top125[i]["segment"] == "TOP10_ALT"
    for i in range(10, 125):
        assert top125[i]["segment"] == "BROAD_ALT_11_125"


def test_u06_5_unit_8_dynamic_rank_consistency():
    assets = _make_full_top125()
    result = dynamic_rank_assets(assets)
    top125 = result["top125"]
    for i, item in enumerate(top125):
        assert item["rank_consistency"] == "MATCH"  # provider_rank == calculated_rank

    assets_mismatch = _make_full_top125()
    assets_mismatch[0]["provider_rank"] = 5
    result_mismatch = dynamic_rank_assets(assets_mismatch)
    assert result_mismatch["top125"][0]["rank_consistency"] == "WARNING"

    assets_minor = _make_full_top125()
    assets_minor[0]["provider_rank"] = 3
    result_minor = dynamic_rank_assets(assets_minor)
    assert result_minor["top125"][0]["rank_consistency"] == "MINOR_DIFFERENCE"

    assets_none = _make_full_top125()
    assets_none[0]["provider_rank"] = None
    result_none = dynamic_rank_assets(assets_none)
    assert result_none["top125"][0]["rank_consistency"] == "UNAVAILABLE"


def test_u06_5_unit_8_dynamic_rank_tie_break():
    assets = [
        _make_asset(symbol="AAA", market_cap=100.0, canonical_asset_id="z_id"),
        _make_asset(symbol="BBB", market_cap=100.0, canonical_asset_id="a_id"),
    ]
    result = dynamic_rank_assets(assets)
    ranked = result["all_valid_ranked"]
    assert ranked[0]["canonical_asset_id"] == "a_id"
    assert ranked[1]["canonical_asset_id"] == "z_id"


def test_u06_5_unit_8_dynamic_rank_coverage_ratio():
    assets = [
        _make_asset(symbol="BTC", market_cap=1000.0, canonical_asset_id="id_1"),
    ]
    result = dynamic_rank_assets(assets)
    assert result["candidate_requested"] == TARGET_CANDIDATE_POOL
    assert result["candidate_coverage_ratio"] == pytest.approx(
        1.0 / TARGET_CANDIDATE_POOL
    )
    assert result["tie_break_rule"] == (
        "market_cap_desc, canonical_asset_id_asc, symbol_asc"
    )


# ---------------------------------------------------------------------------
# Kitchen indices
# ---------------------------------------------------------------------------

def test_u06_5_unit_8_calculate_indices_formulas():
    assets = _make_full_top125()
    ranking = dynamic_rank_assets(assets)
    indices = calculate_indices_from_top125(ranking["top125"])
    assert indices["status"] == "CALCULATED"
    assert indices["formula_version"] == INDEX_VERSION
    assert indices["calculated_by"] == "KITCHEN"
    assert indices["tradingview_value_used"] is False

    values = indices["values"]
    total = sum(a["market_cap"] for a in assets)
    btc_mc = assets[0]["market_cap"]
    eth_mc = assets[1]["market_cap"]
    usdt_mc = assets[2]["market_cap"]
    others_mc = sum(a["market_cap"] for a in assets[10:])

    assert values["KITCHEN_TOTAL_TOP125"] == pytest.approx(total)
    assert values["KITCHEN_TOTAL2"] == pytest.approx(total - btc_mc)
    assert values["KITCHEN_TOTAL3"] == pytest.approx(total - btc_mc - eth_mc)
    assert values["KITCHEN_OTHERS"] == pytest.approx(others_mc)
    assert values["KITCHEN_BTC_D"] == pytest.approx(btc_mc / total * 100.0)
    assert values["KITCHEN_ETH_D"] == pytest.approx(eth_mc / total * 100.0)
    assert values["KITCHEN_USDT_D"] == pytest.approx(usdt_mc / total * 100.0)
    assert values["KITCHEN_OTHERS_D"] == pytest.approx(others_mc / total * 100.0)


def test_u06_5_unit_8_calculate_indices_total2_formula():
    """Mirror notebook self-test: TOTAL2 == TOTAL_TOP125 - BTC."""
    assets = _make_full_top125()
    ranking = dynamic_rank_assets(assets)
    indices = calculate_indices_from_top125(ranking["top125"])
    btc_mc = ranking["top125"][0]["market_cap"]
    assert indices["values"]["KITCHEN_TOTAL2"] == pytest.approx(
        indices["values"]["KITCHEN_TOTAL_TOP125"] - btc_mc
    )


def test_u06_5_unit_8_calculate_indices_manifests():
    assets = _make_full_top125()
    ranking = dynamic_rank_assets(assets)
    indices = calculate_indices_from_top125(ranking["top125"])
    manifests = indices["manifests"]
    assert "KITCHEN_TOTAL_TOP125" in manifests
    assert "KITCHEN_BTC_D" in manifests
    assert manifests["KITCHEN_TOTAL2"]["formula"] == (
        "KITCHEN_TOTAL_TOP125 - BTC_MARKET_CAP"
    )
    assert manifests["KITCHEN_BTC_D"]["output"] is not None
    assert manifests["KITCHEN_BTC_D"]["validation_status"] == "VALID"
    assert manifests["KITCHEN_TOTAL_TOP125"]["processor"] == "KITCHEN_U06_5"
    assert len(manifests["KITCHEN_TOTAL_TOP125"]["inputs"]["top125_members"]) == TOP_N


def test_u06_5_unit_8_indices_incomplete_top125():
    assets = _make_full_top125()[:50]
    result = dynamic_rank_assets(assets)
    indices = calculate_indices_from_top125(result["top125"])
    assert indices["status"] == "DATA_PARTIAL"
    assert indices["reason"] == "TOP125_NOT_COMPLETE"
    assert indices["values"] == {}


def test_u06_5_unit_8_indices_core_asset_missing():
    assets = _make_full_top125()
    assets[0]["symbol"] = "BONK"
    assets[0]["canonical_asset_id"] = "bonk_id"
    result = dynamic_rank_assets(assets)
    indices = calculate_indices_from_top125(result["top125"])
    assert indices["status"] == "DATA_UNAVAILABLE"
    assert indices["reason"] == "CORE_ASSET_MISSING"
    assert indices["values"] == {}


def test_u06_5_unit_8_indices_invalid_market_cap():
    assets = _make_full_top125()
    assets[0]["market_cap"] = None
    result = dynamic_rank_assets(assets)
    top125 = result["top125"]
    assert len(top125) == TOP_N - 1  # invalid asset excluded from ranking
    indices = calculate_indices_from_top125(top125)
    assert indices["status"] == "DATA_PARTIAL"
    assert indices["reason"] == "TOP125_NOT_COMPLETE"

    # Directly test the MARKET_CAP_INVALID guard when called with bad data
    bad_top125 = _make_full_top125()[:TOP_N]
    bad_top125[0]["market_cap"] = None
    indices_bad = calculate_indices_from_top125(bad_top125)
    assert indices_bad["status"] == "DATA_PARTIAL"
    assert indices_bad["reason"] == "MARKET_CAP_INVALID"


def test_u06_5_unit_8_indices_zero_total():
    assets = _make_full_top125()
    for a in assets:
        a["market_cap"] = 0.0
    result = dynamic_rank_assets(assets)
    indices = calculate_indices_from_top125(result["top125"])
    values = indices["values"]
    assert values["KITCHEN_TOTAL_TOP125"] == 0.0
    assert values["KITCHEN_BTC_D"] is None
    assert values["KITCHEN_OTHERS_D"] is None
