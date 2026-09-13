"""U09 Unit 2 — Universe / Reference Data / Four Segments tests."""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

import pytest

from app.config.market_universe import CONFIG
from app.market.universe import (
    SEGMENTS,
    build_reference_from_24h,
    build_segments,
    dominance,
    dominance_change_pct,
    pct_change,
    reference_timestamp_from_provider_24h,
    segment_for_rank,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_asset(rank, price=100.0, mc=None, sym=None, change=None):
    if mc is None:
        mc = 1_000_000_000.0 / rank
    if sym is None:
        sym = f"A{rank}"
    if change is None:
        change = 2.0
    return {
        "provider_asset_id": f"asset-{rank}",
        "symbol": sym,
        "name": f"Asset {rank}",
        "price_usd": price,
        "market_cap_usd": mc,
        "provider_rank": rank,
        "price_change_24h_pct": change,
        "market_cap_change_24h_pct": change,
        "provider_timestamp": "2026-09-12T12:00:00+00:00",
    }


# ---------------------------------------------------------------------------
# SEGMENTS — four segment boundaries
# ---------------------------------------------------------------------------

def test_segments_is_dict():
    assert isinstance(SEGMENTS, dict)


def test_segments_has_four_keys():
    assert set(SEGMENTS.keys()) == {"BTC", "ETH", "TOP10_ALT", "BROAD_ALT_11_125"}


def test_segment_btc_contains_rank_1():
    assert 1 in SEGMENTS["BTC"]


def test_segment_btc_excludes_rank_2():
    assert 2 not in SEGMENTS["BTC"]


def test_segment_eth_contains_rank_2():
    assert 2 in SEGMENTS["ETH"]


def test_segment_eth_excludes_rank_3():
    assert 3 not in SEGMENTS["ETH"]


def test_segment_top10_range_3_to_10():
    assert list(SEGMENTS["TOP10_ALT"]) == list(range(3, 11))


def test_segment_broad_range_11_to_125():
    assert list(SEGMENTS["BROAD_ALT_11_125"]) == list(range(11, 126))


def test_segment_for_rank_btc():
    assert segment_for_rank(1) == "BTC"


def test_segment_for_rank_eth():
    assert segment_for_rank(2) == "ETH"


def test_segment_for_rank_top10():
    assert segment_for_rank(3) == "TOP10_ALT"
    assert segment_for_rank(10) == "TOP10_ALT"


def test_segment_for_rank_broad():
    assert segment_for_rank(11) == "BROAD_ALT_11_125"
    assert segment_for_rank(125) == "BROAD_ALT_11_125"


def test_segment_for_rank_out_of_universe():
    assert segment_for_rank(0) == "OUT_OF_UNIVERSE"
    assert segment_for_rank(126) == "OUT_OF_UNIVERSE"
    assert segment_for_rank(-1) == "OUT_OF_UNIVERSE"


def test_segment_for_rank_coverage():
    all_ranks = set()
    for rr in SEGMENTS.values():
        for r in rr:
            assert r not in all_ranks, f"rank {r} in multiple segments"
            all_ranks.add(r)
    assert all_ranks == set(range(1, 126))


# ---------------------------------------------------------------------------
# pct_change
# ---------------------------------------------------------------------------

def test_pct_change_basic():
    assert pct_change(110.0, 100.0) == 10.0


def test_pct_change_negative():
    assert pct_change(90.0, 100.0) == -10.0


def test_pct_change_none_current():
    assert pct_change(None, 100.0) is None


def test_pct_change_none_reference():
    assert pct_change(100.0, None) is None


def test_pct_change_both_none():
    assert pct_change(None, None) is None


def test_pct_change_zero_reference():
    assert pct_change(100.0, 0.0) is None


def test_pct_change_zero_current_nonzero_ref():
    assert pct_change(0.0, 100.0) == -100.0


def test_pct_change_nonnegative_current():
    assert pct_change(-1.0, 100.0) is None


def test_pct_change_nonnegative_reference():
    assert pct_change(100.0, -1.0) is None


def test_pct_change_nan_current():
    assert pct_change(float("nan"), 100.0) is None


def test_pct_change_inf_reference():
    assert pct_change(100.0, float("inf")) is None


def test_pct_change_basic_integer():
    assert abs(pct_change(110, 100) - 10.0) < 1e-9


# ---------------------------------------------------------------------------
# dominance
# ---------------------------------------------------------------------------

def test_dominance_basic():
    assert dominance(50.0, 200.0) == 25.0


def test_dominance_full():
    assert dominance(100.0, 100.0) == 100.0


def test_dominance_none_segment():
    assert dominance(None, 100.0) is None


def test_dominance_none_total():
    assert dominance(50.0, None) is None


def test_dominance_both_none():
    assert dominance(None, None) is None


def test_dominance_zero_total():
    assert dominance(50.0, 0.0) is None


def test_dominance_negative_segment():
    assert dominance(-10.0, 100.0) is None


def test_dominance_negative_total():
    assert dominance(50.0, -100.0) is None


def test_dominance_zero_segment():
    assert dominance(0.0, 100.0) == 0.0


# ---------------------------------------------------------------------------
# dominance_change_pct
# ---------------------------------------------------------------------------

def test_dominance_change_pct_basic():
    assert abs(dominance_change_pct(12.6, 12.0) - 5.0) < 1e-12


def test_dominance_change_pct_vs_pp():
    rel = dominance_change_pct(12.6, 12.0)
    pp = 12.6 - 12.0
    assert rel != pp, "relative % should differ from percentage points"


def test_dominance_change_pct_none():
    assert dominance_change_pct(None, 12.0) is None
    assert dominance_change_pct(12.0, None) is None


def test_dominance_change_pct_zero_reference():
    assert dominance_change_pct(12.6, 0.0) is None


# ---------------------------------------------------------------------------
# reference_timestamp_from_provider_24h
# ---------------------------------------------------------------------------

def test_reference_timestamp_exact_24h():
    ts = "2026-09-02T14:43:00+00:00"
    assert reference_timestamp_from_provider_24h(ts) == "2026-09-01T14:43:00+00:00"


def test_reference_timestamp_none():
    assert reference_timestamp_from_provider_24h(None) is None


def test_reference_timestamp_empty_string():
    assert reference_timestamp_from_provider_24h("") is None


def test_reference_timestamp_invalid():
    assert reference_timestamp_from_provider_24h("not-a-timestamp") is None


def test_reference_timestamp_iso_z():
    ts = "2026-09-02T14:43:00Z"
    assert reference_timestamp_from_provider_24h(ts) == "2026-09-01T14:43:00+00:00"


# ---------------------------------------------------------------------------
# build_reference_from_24h
# ---------------------------------------------------------------------------

def test_build_reference_basic():
    assets = [_make_asset(1), _make_asset(2)]
    ref = build_reference_from_24h(assets)
    assert "asset-1" in ref
    assert "asset-2" in ref
    for k, v in ref.items():
        assert v > 0


def test_build_reference_changing():
    mc = 1_000_000_000.0
    assets = [{"provider_asset_id": "a1", "market_cap_usd": mc, "market_cap_change_24h_pct": 10.0}]
    ref = build_reference_from_24h(assets)
    expected = mc / (1.0 + 10.0 / 100.0)
    assert abs(ref["a1"] - expected) < 1e-6


def test_build_reference_negative_change():
    mc = 1_000_000_000.0
    assets = [{"provider_asset_id": "a1", "market_cap_usd": mc, "market_cap_change_24h_pct": -5.0}]
    ref = build_reference_from_24h(assets)
    expected = mc / (1.0 - 5.0 / 100.0)
    assert abs(ref["a1"] - expected) < 1e-6


def test_build_reference_no_change_field():
    asset = {"provider_asset_id": "a1", "market_cap_usd": 1e9}
    ref = build_reference_from_24h([asset])
    assert len(ref) == 0


def test_build_reference_all_none():
    assets = [{"provider_asset_id": "a1", "market_cap_usd": 1e9, "market_cap_change_24h_pct": None}]
    ref = build_reference_from_24h(assets)
    assert len(ref) == 0


def test_build_reference_zero_change():
    mc = 1_000_000_000.0
    assets = [{"provider_asset_id": "a1", "market_cap_usd": mc, "market_cap_change_24h_pct": 0.0}]
    ref = build_reference_from_24h(assets)
    expected = mc
    assert abs(ref["a1"] - expected) < 1e-6


def test_build_reference_negative_100_excluded():
    asset = _make_asset(1, change=-100.0)
    ref = build_reference_from_24h([asset])
    assert len(ref) == 0


def test_build_reference_less_than_neg100_excluded():
    asset = _make_asset(1, change=-150.0)
    ref = build_reference_from_24h([asset])
    assert len(ref) == 0


def test_build_reference_large_portfolio():
    assets = [_make_asset(i) for i in range(1, 126)]
    ref = build_reference_from_24h(assets)
    assert len(ref) == 125


# ---------------------------------------------------------------------------
# build_segments — four-segment composition
# ---------------------------------------------------------------------------

def _make_assets(count=125, change_fn=None):
    assets = []
    for rank in range(1, count + 1):
        ch = 2.0 if change_fn is None else change_fn(rank)
        assets.append(_make_asset(rank, change=ch))
    return assets


def test_build_segments_basic_structure():
    assets = _make_assets(125)
    ref = build_reference_from_24h(assets)
    result = build_segments(assets, ref)
    assert "segments" in result
    assert set(result["segments"].keys()) == {"BTC", "ETH", "TOP10_ALT", "BROAD_ALT_11_125"}
    assert result["total_125_mc"] > 0


def test_build_segments_total_mc_sum():
    assets = _make_assets(125)
    ref = build_reference_from_24h(assets)
    result = build_segments(assets, ref)
    total_mc = sum(s["aggregate_market_cap_usd"] for s in result["segments"].values())
    assert abs(total_mc - result["total_125_mc"]) < 1e-6


def test_build_segments_btc_one_constituent():
    assets = _make_assets(125)
    ref = build_reference_from_24h(assets)
    result = build_segments(assets, ref)
    btc = result["segments"]["BTC"]
    assert btc["count"] == 1
    assert len(btc["constituents"]) == 1
    assert btc["constituents"][0]["provider_rank"] == 1


def test_build_segments_eth_one_constituent():
    assets = _make_assets(125)
    ref = build_reference_from_24h(assets)
    result = build_segments(assets, ref)
    eth = result["segments"]["ETH"]
    assert eth["count"] == 1


def test_build_segments_top10_eight_constituents():
    assets = _make_assets(125)
    ref = build_reference_from_24h(assets)
    result = build_segments(assets, ref)
    top10 = result["segments"]["TOP10_ALT"]
    assert top10["count"] == 8
    ranks = [c["provider_rank"] for c in top10["constituents"]]
    assert ranks == list(range(3, 11))


def test_build_segments_broad_115_constituents():
    assets = _make_assets(125)
    ref = build_reference_from_24h(assets)
    result = build_segments(assets, ref)
    broad = result["segments"]["BROAD_ALT_11_125"]
    assert broad["count"] == 115


def test_build_segments_dominance_partition():
    assets = _make_assets(125)
    ref = build_reference_from_24h(assets)
    result = build_segments(assets, ref)
    partition = sum(s["dominance_pct"] or 0 for s in result["segments"].values())
    assert abs(partition - 100.0) <= CONFIG["dominance_partition_tolerance_pct"]


def test_build_segments_all_have_breadth():
    assets = _make_assets(125)
    ref = build_reference_from_24h(assets)
    result = build_segments(assets, ref)
    for seg_name, seg_data in result["segments"].items():
        assert "breadth" in seg_data
        b = seg_data["breadth"]
        assert "rising_count" in b
        assert "flat_count" in b
        assert "falling_count" in b
        assert "rising_pct" in b
        assert "flat_pct" in b
        assert "falling_pct" in b
        assert "breadth_state" in b
        assert b["breadth_state"] in ("STRONG", "POSITIVE", "WEAK", "NEGATIVE", "MIXED", "UNAVAILABLE")


def test_build_segments_rising_flat_falling_counts():
    assets = _make_assets(20, change_fn=lambda r: 1.0 if r <= 10 else (0.0 if r <= 15 else -1.0))
    ref = build_reference_from_24h(assets)
    result = build_segments(assets, ref)
    for seg_data in result["segments"].values():
        b = seg_data["breadth"]
        total = b["rising_count"] + b["flat_count"] + b["falling_count"]
        assert total == seg_data["count"]


def test_build_segments_breadth_state_strong():
    assets = _make_assets(20, change_fn=lambda r: 10.0 if r <= 14 else -1.0)
    ref = build_reference_from_24h(assets)
    result = build_segments(assets, ref)
    for seg_data in result["segments"].values():
        b = seg_data["breadth"]
        if b["rising_pct"] is not None and b["rising_pct"] >= 70:
            assert b["breadth_state"] == "STRONG"


def test_build_segments_breadth_state_weak():
    assets = _make_assets(20, change_fn=lambda r: -10.0 if r <= 14 else 1.0)
    ref = build_reference_from_24h(assets)
    result = build_segments(assets, ref)
    for seg_data in result["segments"].values():
        b = seg_data["breadth"]
        if b["falling_pct"] is not None and b["falling_pct"] >= 70:
            assert b["breadth_state"] == "WEAK"


def test_build_segments_dominance_change_pct_and_pp():
    assets = _make_assets(125)
    ref = build_reference_from_24h(assets)
    result = build_segments(assets, ref)
    checked = False
    for seg_name, seg_data in result["segments"].items():
        dcc = seg_data["dominance_change_pct"]
        dcp = seg_data["dominance_change_pp"]
        if dcc is not None and dcp is not None and (dcc != 0.0 or dcp != 0.0):
            checked = True
            assert dcc != dcp, f"{seg_name}: dominance_change_pct ({dcc}) should differ from pp ({dcp})"
    assert checked, "No segment had non-zero dominance change values to compare"


def test_build_segments_reference_mc_consistency():
    assets = _make_assets(10)
    ref = build_reference_from_24h(assets)
    result = build_segments(assets, ref)
    for seg_name, seg_data in result["segments"].items():
        if seg_data["count"] == 0:
            continue
        if seg_data["reference_market_cap_usd"] is not None:
            mc = seg_data["aggregate_market_cap_usd"]
            assert seg_data["reference_market_cap_usd"] > 0
            assert mc > 0


def test_build_segments_zero_assets():
    result = build_segments([], {})
    for seg_data in result["segments"].values():
        assert seg_data["count"] == 0
        assert seg_data["breadth"]["breadth_state"] == "UNAVAILABLE"


def test_build_segments_total_mc_is_sum():
    assets = _make_assets(50)
    ref = build_reference_from_24h(assets)
    result = build_segments(assets, ref)
    manual_total = sum(float(a["market_cap_usd"]) for a in assets)
    assert abs(result["total_125_mc"] - manual_total) < 1e-6


def test_build_segments_ranks_in_segment():
    assets = _make_assets(125)
    ref = build_reference_from_24h(assets)
    result = build_segments(assets, ref)
    for seg_name, seg_data in result["segments"].items():
        for constituent in seg_data["constituents"]:
            rank = int(constituent["provider_rank"])
            assert rank in SEGMENTS[seg_name], f"rank {rank} in {seg_name}"


# ---------------------------------------------------------------------------
# Combined: full synthetic universe (mirrors notebook synthetic_validation_suite)
# ---------------------------------------------------------------------------

def test_synthetic_universe_rank_identity():
    assets = _make_assets(125)
    ref = build_reference_from_24h(assets)
    result = build_segments(assets, ref)
    partition = sum(s["dominance_pct"] or 0 for s in result["segments"].values())
    assert abs(partition - 100.0) <= CONFIG["dominance_partition_tolerance_pct"]


def test_breadth_10_5_5():
    assets = _make_assets(20, change_fn=lambda r: 1.0 if r <= 10 else (0.0 if r <= 15 else -1.0))
    ref = build_reference_from_24h(assets)
    result = build_segments(assets, ref)
    for seg_data in result["segments"].values():
        b = seg_data["breadth"]
        total = b["rising_count"] + b["flat_count"] + b["falling_count"]
        assert total == seg_data["count"]


def test_dominance_relative_vs_pp_distinction():
    assert abs(dominance_change_pct(12.6, 12.0) - 5.0) < 1e-12
    assert abs((12.6 - 12.0) - 0.6) < 1e-12


def test_reference_timestamp_24h_semantics():
    ts = "2026-09-02T14:43:00+00:00"
    assert reference_timestamp_from_provider_24h(ts) == "2026-09-01T14:43:00+00:00"


def test_zero_reference_guard_pct():
    assert pct_change(100.0, 0.0) is None


def test_pct_change_100_98():
    result = pct_change(100.0, 98.0)
    assert abs(result - 2.0408163265306123) < 1e-12


def test_build_segments_with_zero_assets_empty_segments():
    result = build_segments([], {})
    assert len(result["segments"]) == 4
    for seg in result["segments"].values():
        assert seg["count"] == 0
        assert seg["aggregate_market_cap_usd"] == 0.0


def test_build_segments_no_reference():
    assets = _make_assets(50)
    result = build_segments(assets, {})
    for seg_data in result["segments"].values():
        assert seg_data["reference_market_cap_usd"] is None
        assert seg_data["reference_dominance_pct"] is None
        assert seg_data["dominance_change_pct"] is None
        assert seg_data["dominance_change_pp"] is None


def test_build_segments_partial_reference():
    assets = _make_assets(50)
    partial_ref = {a["provider_asset_id"]: a["market_cap_usd"] * 0.9 for a in assets[:25]}
    result = build_segments(assets, partial_ref)
    for seg_data in result["segments"].values():
        assert "reference_market_cap_usd" in seg_data


def test_constituents_have_segment_field():
    assets = _make_assets(125)
    ref = build_reference_from_24h(assets)
    result = build_segments(assets, ref)
    for seg_name, seg_data in result["segments"].items():
        for c in seg_data["constituents"]:
            assert c.get("segment") == seg_name
