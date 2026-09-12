"""Stage 8 (U08) Unit 8.7 — Altcoin/Volume focused tests.

Covers ``build_altcoin_structure_context``, ``volume_record``,
``ensure_volume_fields``, ``build_strong_movers``,
``build_relative_movers``, and ``build_scenario_ranking``
from ``app.analysis.u08_altcoin``.
"""
from __future__ import annotations

import pytest

from app.analysis.enums import Context, Direction
from app.analysis.u08_altcoin import (
    build_altcoin_structure_context,
    build_relative_movers,
    build_scenario_ranking,
    build_strong_movers,
    ensure_volume_fields,
    volume_record,
)
from app.analysis.u08_config import CELL08_CONFIG, Cell08Config


# ---- build_altcoin_structure_context -------------------------------------

def test_altcoin_structure_not_opposite():
    result = build_altcoin_structure_context(
        Direction.INCREASE, Direction.INCREASE,
    )
    assert result["enabled"] is False
    assert result["reason"] == "BTC and BTC.D are not in opposite directions."


def test_altcoin_structure_opposite_increase_decrease():
    result = build_altcoin_structure_context(
        Direction.INCREASE, Direction.DECREASE,
    )
    assert result["enabled"] is True
    assert result["reason"] == "BTC and BTC.D are in opposite directions."


def test_altcoin_structure_opposite_decrease_increase():
    result = build_altcoin_structure_context(
        Direction.DECREASE, Direction.INCREASE,
    )
    assert result["enabled"] is True


def test_altcoin_structure_opposite_includes_optional_fields():
    total2 = {"value": 100.0}
    total3 = {"value": 200.0}
    others_d = {"value": 300.0}
    result = build_altcoin_structure_context(
        Direction.INCREASE,
        Direction.DECREASE,
        total2=total2,
        total3=total3,
        others_d=others_d,
    )
    assert result["enabled"] is True
    assert result["total2"] == total2
    assert result["total3"] == total3
    assert result["others_d"] == others_d


def test_altcoin_structure_not_opposite_keeps_optional_fields():
    total2 = {"value": 100.0}
    result = build_altcoin_structure_context(
        Direction.INCREASE, Direction.INCREASE,
        total2=total2,
    )
    assert result["total2"] == total2


def test_altcoin_structure_no_optional_fields():
    result = build_altcoin_structure_context(
        Direction.INCREASE, Direction.INCREASE,
    )
    assert result["total2"] is None
    assert result["total3"] is None
    assert result["others_d"] is None


# ---- volume_record -------------------------------------------------------

def test_volume_record_extracts_fields():
    asset = {
        "symbol": "ETHUSDT",
        "direction": "INCREASE",
        "price": 3000.0,
        "change_pct": 2.5,
        "volume": 1500.0,
        "relative_btc_performance_pct": 1.0,
    }
    result = volume_record(asset)
    assert result == asset


def test_volume_record_missing_fields():
    asset = {"symbol": "X"}
    result = volume_record(asset)
    assert result["symbol"] == "X"
    assert result["direction"] is None
    assert result["price"] is None
    assert result["change_pct"] is None
    assert result["volume"] is None
    assert result["relative_btc_performance_pct"] is None


# ---- ensure_volume_fields ------------------------------------------------

def test_ensure_volume_fields_available():
    assets = [{"symbol": "A", "volume": 100.0}]
    result = ensure_volume_fields(assets)
    assert result[0]["volume"] == 100.0
    assert result[0]["volume_status"] == "AVAILABLE"


def test_ensure_volume_fields_unavailable():
    assets = [{"symbol": "A", "volume": None}]
    result = ensure_volume_fields(assets)
    assert result[0]["volume"] is None
    assert result[0]["volume_status"] == "UNAVAILABLE"


def test_ensure_volume_fields_zero_volume_available():
    assets = [{"symbol": "A", "volume": 0.0}]
    result = ensure_volume_fields(assets)
    assert result[0]["volume"] == 0.0
    assert result[0]["volume_status"] == "AVAILABLE"


def test_ensure_volume_fields_does_not_mutate_input():
    assets = [{"symbol": "A", "volume": 100.0}]
    original = [dict(a) for a in assets]
    ensure_volume_fields(assets)
    assert assets == original


def test_ensure_volume_fields_volume_required_false():
    custom = Cell08Config(volume_required=False)
    import app.analysis.u08_altcoin as altmod
    orig = altmod.CELL08_CONFIG
    altmod.CELL08_CONFIG = custom
    try:
        assets = [{"symbol": "A", "volume": None}]
        result = ensure_volume_fields(assets)
        assert result[0]["volume_status"] == "AVAILABLE"
    finally:
        altmod.CELL08_CONFIG = orig


def test_ensure_volume_fields_empty():
    assert ensure_volume_fields([]) == []


# ---- build_strong_movers -------------------------------------------------

def test_build_strong_movers_ranks_and_marks_volume():
    assets = [
        {"symbol": "A", "change_pct": 5.0, "volume": 100.0},
        {"symbol": "B", "change_pct": -3.0, "volume": None},
    ]
    result = build_strong_movers(assets, Context.BULLISH)
    assert len(result) == 2
    assert result[0]["symbol"] == "A"
    assert result[0]["volume_status"] == "AVAILABLE"
    assert result[1]["symbol"] == "B"
    assert result[1]["volume_status"] == "UNAVAILABLE"


def test_build_strong_movers_uses_config_n():
    custom = Cell08Config(strong_movers_n=1)
    import app.analysis.u08_altcoin as altmod
    orig = altmod.CELL08_CONFIG
    altmod.CELL08_CONFIG = custom
    try:
        assets = [
            {"symbol": "A", "change_pct": 5.0, "volume": 100.0},
            {"symbol": "B", "change_pct": 3.0, "volume": 50.0},
        ]
        result = build_strong_movers(assets, Context.BULLISH)
        assert len(result) == 1
        assert result[0]["symbol"] == "A"
    finally:
        altmod.CELL08_CONFIG = orig


# ---- build_relative_movers -----------------------------------------------

def test_build_relative_movers_ranks_and_marks_volume():
    assets = [
        {
            "symbol": "A",
            "change_pct": 5.0,
            "relative_btc_performance_pct": 2.0,
            "volume": 100.0,
        },
        {
            "symbol": "B",
            "change_pct": 3.0,
            "relative_btc_performance_pct": None,
            "volume": None,
        },
    ]
    result = build_relative_movers(assets, Context.BULLISH)
    assert len(result) == 1
    assert result[0]["symbol"] == "A"
    assert result[0]["volume_status"] == "AVAILABLE"


# ---- build_scenario_ranking ----------------------------------------------

def test_build_scenario_ranking_bullish_case():
    assets = [
        {"symbol": "A", "change_pct": 5.0, "volume": 100.0},
        {"symbol": "B", "change_pct": -3.0, "volume": 200.0},
    ]
    result = build_scenario_ranking(
        assets, Direction.INCREASE, Direction.DECREASE,
    )
    assert result["context"] == "BULLISH"
    assert "strong_movers" in result
    assert "relative_movers" in result
    assert "top_10_assets" in result
    assert isinstance(result["strong_movers"], list)
    assert isinstance(result["relative_movers"], list)
    assert isinstance(result["top_10_assets"], list)


def test_build_scenario_ranking_bearish_case():
    assets = [
        {"symbol": "A", "change_pct": 5.0, "volume": 100.0},
        {"symbol": "B", "change_pct": -3.0, "volume": 200.0},
    ]
    result = build_scenario_ranking(
        assets, Direction.DECREASE, Direction.RANGE,
    )
    assert result["context"] == "BEARISH"


def test_build_scenario_ranking_range_case():
    assets = [
        {"symbol": "A", "change_pct": 5.0, "volume": 100.0},
        {"symbol": "B", "change_pct": -3.0, "volume": 200.0},
    ]
    result = build_scenario_ranking(
        assets, Direction.RANGE, Direction.RANGE,
    )
    assert result["context"] == "RANGE"


def test_build_scenario_ranking_with_relative_performance():
    assets = [
        {
            "symbol": "A",
            "change_pct": 5.0,
            "volume": 100.0,
            "relative_btc_performance_pct": 2.0,
        },
    ]
    result = build_scenario_ranking(
        assets, Direction.INCREASE, Direction.DECREASE,
    )
    # relative_movers should contain asset A with relative fields
    assert len(result["relative_movers"]) >= 1
    found = False
    for mover in result["relative_movers"]:
        if mover["symbol"] == "A":
            assert "relative_btc_performance_pct" in mover
            found = True
    assert found


def test_build_scenario_ranking_empty_assets():
    result = build_scenario_ranking(
        [], Direction.INCREASE, Direction.INCREASE,
    )
    assert result["context"] == "BULLISH"
    assert result["strong_movers"] == []
    assert result["relative_movers"] == []
    assert result["top_10_assets"] == []
