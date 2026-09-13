"""U09 Unit 3 — Relative Strength / Composition / Participation / Message tests."""
from __future__ import annotations

import math
from datetime import datetime, timezone

import pytest

from app.config.market_universe import CONFIG
from app.market.universe import (
    SEGMENTS,
    build_message,
    composition_compare,
    fmt_pct,
    participation_brain,
    relative_strength,
)


# ---------------------------------------------------------------------------
# Helpers for building segment-like structures
# ---------------------------------------------------------------------------

def _seg(count=0, change=2.0, mc=100.0, rising=None, flat=None, falling=None):
    breadth = {
        "rising_count": rising if rising is not None else 0,
        "flat_count": flat if flat is not None else 0,
        "falling_count": falling if falling is not None else 0,
        "rising_pct": None if rising is None else (rising / count * 100 if count else None),
        "flat_pct": None if flat is None else (flat / count * 100 if count else None),
        "falling_pct": None if falling is None else (falling / count * 100 if count else None),
        "breadth_state": "UNAVAILABLE",
        "price_change_threshold_pct": CONFIG["breadth_threshold_pct"],
    }
    return {
        "constituents": [{"provider_asset_id": f"a{i}", "price_change_24h_pct": change} for i in range(count)],
        "count": count,
        "aggregate_market_cap_usd": mc,
        "market_cap_change_pct": change,
        "dominance_pct": mc,
        "dominance_change_pct": change * 0.1,
        "breadth": breadth,
    }


# ---------------------------------------------------------------------------
# relative_strength
# ---------------------------------------------------------------------------

def test_relative_strength_returns_dict():
    seg = {
        "BTC": _seg(1, mc=1000.0),
        "ETH": _seg(1, mc=500.0),
        "TOP10_ALT": _seg(3, mc=300.0),
        "BROAD_ALT_11_125": _seg(5, mc=200.0),
    }
    rs = relative_strength(seg)
    assert isinstance(rs, dict)
    assert "BTC_MC_OVER_ETH_MC" in rs
    assert "BTC_MC_OVER_TOP10_ALT_MC" in rs
    assert "BTC_MC_OVER_BROAD_ALT_11_125_MC" in rs
    assert "ETH_MC_OVER_TOP10_ALT_MC" in rs
    assert "TOP10_ALT_MC_OVER_BROAD_ALT_11_125_MC" in rs


def test_relative_strength_correct_ratios():
    seg = {
        "BTC": _seg(1, mc=1000.0),
        "ETH": _seg(1, mc=500.0),
        "TOP10_ALT": _seg(1, mc=200.0),
        "BROAD_ALT_11_125": _seg(1, mc=100.0),
    }
    rs = relative_strength(seg)
    assert rs["BTC_MC_OVER_ETH_MC"] == 2.0
    assert rs["BTC_MC_OVER_TOP10_ALT_MC"] == 5.0
    assert rs["BTC_MC_OVER_BROAD_ALT_11_125_MC"] == 10.0
    assert rs["ETH_MC_OVER_TOP10_ALT_MC"] == 2.5
    assert rs["TOP10_ALT_MC_OVER_BROAD_ALT_11_125_MC"] == 2.0


def test_relative_strength_btc_over_each():
    seg = {
        "BTC": _seg(1, mc=100.0),
        "ETH": _seg(1, mc=50.0),
        "TOP10_ALT": _seg(1, mc=25.0),
        "BROAD_ALT_11_125": _seg(1, mc=10.0),
    }
    rs = relative_strength(seg)
    assert rs["ETH_MC_OVER_BTC_MC"] == 0.5
    assert rs["TOP10_ALT_MC_OVER_BTC_MC"] == 0.25
    assert rs["BROAD_ALT_11_125_MC_OVER_BTC_MC"] == 0.1


def test_relative_strength_none_for_zero_mc():
    seg = {
        "BTC": _seg(1, mc=0.0),
        "ETH": _seg(1, mc=50.0),
        "TOP10_ALT": _seg(1, mc=25.0),
        "BROAD_ALT_11_125": _seg(1, mc=10.0),
    }
    rs = relative_strength(seg)
    assert rs["BTC_MC_OVER_ETH_MC"] is None
    assert rs["BTC_MC_OVER_BTC_MC"] is None


def test_relative_strength_none_for_negative():
    seg = {
        "BTC": _seg(1, mc=-100.0),
        "ETH": _seg(1, mc=50.0),
        "TOP10_ALT": _seg(1, mc=25.0),
        "BROAD_ALT_11_125": _seg(1, mc=10.0),
    }
    rs = relative_strength(seg)
    assert rs["BTC_MC_OVER_ETH_MC"] is None


def test_relative_strength_all_pairs_present():
    seg = {
        "BTC": _seg(1, mc=100.0),
        "ETH": _seg(1, mc=50.0),
        "TOP10_ALT": _seg(1, mc=25.0),
        "BROAD_ALT_11_125": _seg(1, mc=10.0),
    }
    rs = relative_strength(seg)
    expected_keys = [
        "BTC_MC_OVER_ETH_MC", "BTC_MC_OVER_TOP10_ALT_MC", "BTC_MC_OVER_BROAD_ALT_11_125_MC",
        "ETH_MC_OVER_TOP10_ALT_MC", "TOP10_ALT_MC_OVER_BROAD_ALT_11_125_MC",
        "BTC_MC_OVER_BTC_MC",
        "ETH_MC_OVER_BTC_MC", "TOP10_ALT_MC_OVER_BTC_MC", "BROAD_ALT_11_125_MC_OVER_BTC_MC",
    ]
    assert set(rs.keys()) == set(expected_keys)


# ---------------------------------------------------------------------------
# composition_compare — no snapshots
# ---------------------------------------------------------------------------

def test_composition_no_snapshots_returns_stable():
    result = composition_compare([])
    assert result["composition_changed"] is False
    assert result["composition_quality"] == "STABLE"
    assert result["previous_snapshot"] is None
    assert result["changes"] == []
    assert result["entered"] == []
    assert result["exited"] == []


def test_comparison_with_no_assets():
    result = composition_compare([])
    assert result["composition_changed"] is False
    assert result["composition_quality"] == "STABLE"


# ---------------------------------------------------------------------------
# participation_brain
# ---------------------------------------------------------------------------

def test_participation_brain_broadening():
    seg = {
        "BTC": _seg(1, change=3.0, mc=1000.0),
        "ETH": _seg(1, change=2.0, mc=500.0),
        "TOP10_ALT": _seg(14, change=3.0, mc=800.0, rising=12),
        "BROAD_ALT_11_125": _seg(10, change=2.5, mc=600.0, rising=8),
    }
    rs = relative_strength(seg)
    comp = {"composition_quality": "STABLE"}
    state, explanation = participation_brain(seg, rs, comp)
    assert state == "BROADENING"
    assert "TOP10" in explanation
    assert "BROAD" in explanation


def test_participation_brain_concentrated():
    seg = {
        "BTC": _seg(1, change=2.0, mc=1000.0),
        "ETH": _seg(1, change=1.5, mc=500.0),
        "TOP10_ALT": _seg(1, change=-1.0, mc=100.0, rising=0),
        "BROAD_ALT_11_125": _seg(1, change=-2.0, mc=50.0, rising=0),
    }
    rs = relative_strength(seg)
    comp = {"composition_quality": "STABLE"}
    state, explanation = participation_brain(seg, rs, comp)
    assert state == "CONCENTRATED"
    assert "concentrated" in explanation.lower() or "core" in explanation.lower()


def test_participation_brain_weakening():
    seg = {
        "BTC": _seg(1, change=-1.0, mc=1000.0),
        "ETH": _seg(1, change=-0.5, mc=500.0),
        "TOP10_ALT": _seg(1, change=-3.0, mc=100.0, rising=0),
        "BROAD_ALT_11_125": _seg(1, change=-3.0, mc=50.0, rising=0),
    }
    rs = relative_strength(seg)
    comp = {"composition_quality": "STABLE"}
    state, explanation = participation_brain(seg, rs, comp)
    assert state == "WEAKENING"
    assert "deteriorating" in explanation.lower() or "weak" in explanation.lower()


def test_participation_brain_mixed():
    seg = {
        "BTC": _seg(1, change=2.0, mc=1000.0),
        "ETH": _seg(1, change=-1.0, mc=500.0),
        "TOP10_ALT": _seg(1, change=1.0, mc=100.0, rising=5),
        "BROAD_ALT_11_125": _seg(1, change=-0.5, mc=50.0, rising=3),
    }
    rs = relative_strength(seg)
    comp = {"composition_quality": "STABLE"}
    state, explanation = participation_brain(seg, rs, comp)
    assert state == "MIXED"
    assert "not directionally uniform" in explanation


def test_participation_brain_unavailable_composition():
    seg = {
        "BTC": _seg(1, mc=1000.0),
        "ETH": _seg(1, mc=500.0),
        "TOP10_ALT": _seg(1, mc=100.0),
        "BROAD_ALT_11_125": _seg(1, mc=50.0),
    }
    rs = relative_strength(seg)
    comp = {"composition_quality": "UNRELIABLE"}
    state, explanation = participation_brain(seg, rs, comp)
    assert state == "UNAVAILABLE"
    assert "unreliable" in explanation.lower()


def test_participation_brain_unavailable_no_data():
    seg = {
        "BTC": _seg(0),
        "ETH": _seg(1),
        "TOP10_ALT": _seg(1),
        "BROAD_ALT_11_125": _seg(1),
    }
    rs = relative_strength(seg)
    comp = {"composition_quality": "STABLE"}
    state, explanation = participation_brain(seg, rs, comp)
    assert state == "UNAVAILABLE"


# ---------------------------------------------------------------------------
# fmt_pct
# ---------------------------------------------------------------------------

def test_fmt_pct_none():
    assert fmt_pct(None) == "N/A"


def test_fmt_pct_basic():
    assert fmt_pct(3.0) == "+3.0%"
    assert fmt_pct(-2.5) == "-2.5%"


def test_fmt_pct_zero():
    assert fmt_pct(0.0) == "+0.0%"


def test_fmt_pct_small_positive():
    result = fmt_pct(0.00001, min_decimals=2, max_decimals=6)
    assert "0.00001" in result
    assert result.startswith("+")


def test_fmt_pct_small_negative():
    result = fmt_pct(-0.00001, min_decimals=2, max_decimals=6)
    assert "0.00001" in result
    assert "-0.0%" not in result


def test_fmt_pct_no_signed_zero():
    assert "-0.0%" not in fmt_pct(-0.00001, min_decimals=2, max_decimals=6)


def test_fmt_pct_nan():
    assert fmt_pct(float("nan")) == "N/A"


def test_fmt_pct_inf():
    assert fmt_pct(float("inf")) == "N/A"
    assert fmt_pct(float("-inf")) == "N/A"


def test_fmt_pct_string():
    assert fmt_pct("3.5") == "+3.5%"


def test_fmt_pct_string_invalid():
    assert fmt_pct("abc") == "N/A"


def test_fmt_pct_default_min_decimals():
    result = fmt_pct(0.001)
    assert "0.001" in result


def test_fmt_pct_custom_decimals():
    assert fmt_pct(1.5, min_decimals=4, max_decimals=6) == "+1.5000%"


def test_fmt_pct_large_value():
    assert fmt_pct(123.456) == "+123.5%"


def test_fmt_pct_negative_zero():
    result = fmt_pct(-0.0, min_decimals=2, max_decimals=4)
    assert "-0.0%" not in result
    assert "+" in result or result == "0.00%"


# ---------------------------------------------------------------------------
# build_message
# ---------------------------------------------------------------------------

def test_build_message_data_unavailable():
    result = {"validation_status": "DATA_UNAVAILABLE"}
    msg = build_message(result)
    assert "DATA_UNAVAILABLE" in msg


def test_build_message_five_lines():
    seg = {
        "BTC": {
            "constituents": [{"price_change_24h_pct": 3.0}],
            "dominance_change_pct": 0.5,
            "market_cap_change_pct": 2.0,
        },
        "ETH": {
            "constituents": [{"price_change_24h_pct": 2.0}],
            "dominance_change_pct": 0.4,
            "market_cap_change_pct": 1.5,
        },
        "TOP10_ALT": {
            "constituents": [],
            "dominance_change_pct": 0.3,
            "market_cap_change_pct": 1.0,
        },
        "BROAD_ALT_11_125": {
            "constituents": [],
            "dominance_change_pct": 0.2,
            "market_cap_change_pct": 0.5,
        },
    }
    result = {"validation_status": "PASS", "segments": seg}
    msg = build_message(result)
    assert len(msg.splitlines()) == 5


def test_build_message_has_market_participation():
    seg = {
        "BTC": {"constituents": [{"price_change_24h_pct": 3.0}], "dominance_change_pct": 0.5, "market_cap_change_pct": 2.0},
        "ETH": {"constituents": [{"price_change_24h_pct": 2.0}], "dominance_change_pct": 0.4, "market_cap_change_pct": 1.5},
        "TOP10_ALT": {"constituents": [], "dominance_change_pct": 0.3, "market_cap_change_pct": 1.0},
        "BROAD_ALT_11_125": {"constituents": [], "dominance_change_pct": 0.2, "market_cap_change_pct": 0.5},
    }
    result = {"validation_status": "PASS", "segments": seg}
    msg = build_message(result)
    assert "MARKET PARTICIPATION" in msg


def test_build_message_has_24h():
    seg = {
        "BTC": {"constituents": [{"price_change_24h_pct": 3.0}], "dominance_change_pct": 0.5, "market_cap_change_pct": 2.0},
        "ETH": {"constituents": [{"price_change_24h_pct": 2.0}], "dominance_change_pct": 0.4, "market_cap_change_pct": 1.5},
        "TOP10_ALT": {"constituents": [], "dominance_change_pct": 0.3, "market_cap_change_pct": 1.0},
        "BROAD_ALT_11_125": {"constituents": [], "dominance_change_pct": 0.2, "market_cap_change_pct": 0.5},
    }
    result = {"validation_status": "PASS", "segments": seg}
    msg = build_message(result)
    assert "24H" in msg


def test_build_message_no_pp():
    seg = {
        "BTC": {"constituents": [{"price_change_24h_pct": 3.0}], "dominance_change_pct": 0.5, "market_cap_change_pct": 2.0},
        "ETH": {"constituents": [{"price_change_24h_pct": 2.0}], "dominance_change_pct": 0.4, "market_cap_change_pct": 1.5},
        "TOP10_ALT": {"constituents": [], "dominance_change_pct": 0.3, "market_cap_change_pct": 1.0},
        "BROAD_ALT_11_125": {"constituents": [], "dominance_change_pct": 0.2, "market_cap_change_pct": 0.5},
    }
    result = {"validation_status": "PASS", "segments": seg}
    msg = build_message(result)
    assert " pp" not in msg


def test_build_message_no_participation_state():
    seg = {
        "BTC": {"constituents": [{"price_change_24h_pct": 3.0}], "dominance_change_pct": 0.5, "market_cap_change_pct": 2.0},
        "ETH": {"constituents": [{"price_change_24h_pct": 2.0}], "dominance_change_pct": 0.4, "market_cap_change_pct": 1.5},
        "TOP10_ALT": {"constituents": [], "dominance_change_pct": 0.3, "market_cap_change_pct": 1.0},
        "BROAD_ALT_11_125": {"constituents": [], "dominance_change_pct": 0.2, "market_cap_change_pct": 0.5},
    }
    result = {"validation_status": "PASS", "segments": seg}
    msg = build_message(result)
    assert "Participation:" not in msg


def test_build_message_na_for_empty_segments():
    seg = {
        "BTC": {"constituents": [], "dominance_change_pct": None, "market_cap_change_pct": None},
        "ETH": {"constituents": [], "dominance_change_pct": None, "market_cap_change_pct": None},
        "TOP10_ALT": {"constituents": [], "dominance_change_pct": None, "market_cap_change_pct": None},
        "BROAD_ALT_11_125": {"constituents": [], "dominance_change_pct": None, "market_cap_change_pct": None},
    }
    result = {"validation_status": "PASS", "segments": seg}
    msg = build_message(result)
    assert len(msg.splitlines()) == 5
    assert sum("N/A" in line for line in msg.splitlines()) >= 4


def test_build_message_btc_section():
    seg = {
        "BTC": {"constituents": [{"price_change_24h_pct": 3.0}], "dominance_change_pct": 0.5, "market_cap_change_pct": 2.0},
        "ETH": {"constituents": [{"price_change_24h_pct": 2.0}], "dominance_change_pct": 0.4, "market_cap_change_pct": 1.5},
        "TOP10_ALT": {"constituents": [], "dominance_change_pct": 0.3, "market_cap_change_pct": 1.0},
        "BROAD_ALT_11_125": {"constituents": [], "dominance_change_pct": 0.2, "market_cap_change_pct": 0.5},
    }
    result = {"validation_status": "PASS", "segments": seg}
    msg = build_message(result)
    lines = msg.splitlines()
    assert "BTC" in lines[1]
    assert "BTC.D" in lines[1]
    assert "ETH" in lines[2]
    assert "ETH.D" in lines[2]
    assert "TOP10 ALT MC" in lines[3]
    assert "TOP10.D" in lines[3]
    assert "BROAD 11" in lines[4] or "BROAD" in lines[4]
    assert "BROAD.D" in lines[4]
