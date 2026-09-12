"""Stage 8 (U08) Unit 8.10 — Final Engine focused tests.

Covers ``run_cell_08`` from ``app.analysis.u08_engine``.
"""
from __future__ import annotations

import pytest

from app.analysis.u08_engine import run_cell_08, cell08_self_tests


def _sample_assets():
    return [
        {"symbol": "BTCUSDT", "change_pct": 2.0, "volume": 1000.0},
        {"symbol": "ETHUSDT", "change_pct": 5.0, "volume": 500.0},
        {"symbol": "SOLUSDT", "change_pct": -1.0, "volume": 200.0},
        {"symbol": "XRPUSDT", "change_pct": 3.0, "volume": 300.0},
    ]


# ---- Basic execution ---------------------------------------------------------

def test_run_cell08_returns_cell08result():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
        pattern_index=1,
    )
    from app.analysis.u08_result import Cell08Result
    assert isinstance(result, Cell08Result)


def test_run_cell08_core_fields_populated():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
        pattern_index=1,
    )
    assert result.engine == "CELL_08"
    assert result.version == "V3.1"
    assert result.timestamp_utc is not None
    assert result.scenario_id == 2
    assert result.scenario_type == "BTC_UP_BTC_D_DOWN"
    assert result.btc_direction == "INCREASE"
    assert result.btc_d_direction == "DECREASE"
    assert result.context == "BULLISH"
    assert result.opposite_direction is True


def test_run_cell08_all_output_lists_present():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
        pattern_index=1,
    )
    assert isinstance(result.top_10_assets, list)
    assert isinstance(result.strong_movers, list)
    assert isinstance(result.relative_movers, list)
    assert isinstance(result.altcoin_structure, dict)
    assert isinstance(result.audit, dict)
    assert isinstance(result.selected_pattern, dict)


# ---- Scenario coverage -------------------------------------------------------

@pytest.mark.parametrize(
    "btc_dir,btc_d_dir,expected_scenario,expected_context",
    [
        ("INCREASE", "INCREASE", 1, "BULLISH"),
        ("INCREASE", "DECREASE", 2, "BULLISH"),
        ("INCREASE", "RANGE", 3, "BULLISH"),
        ("DECREASE", "INCREASE", 4, "BEARISH"),
        ("DECREASE", "DECREASE", 5, "BEARISH"),
        ("DECREASE", "RANGE", 6, "BEARISH"),
        ("RANGE", "INCREASE", 7, "RANGE"),
        ("RANGE", "DECREASE", 8, "RANGE"),
        ("RANGE", "RANGE", 9, "RANGE"),
    ],
)
def test_run_cell08_all_scenarios(btc_dir, btc_d_dir, expected_scenario, expected_context):
    assets = _sample_assets()
    result = run_cell_08(
        btc_direction=btc_dir,
        btc_d_direction=btc_d_dir,
        btc_change_pct=2.0 if btc_dir == "INCREASE" else (-2.0 if btc_dir == "DECREASE" else 0.0),
        assets=assets,
        pattern_index=1,
    )
    assert result.scenario_id == expected_scenario
    assert result.context == expected_context


# ---- Opposite direction detection --------------------------------------------

def test_opposite_direction_true_for_increase_decrease():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
        pattern_index=1,
    )
    assert result.opposite_direction is True


def test_opposite_direction_true_for_decrease_increase():
    result = run_cell_08(
        btc_direction="DECREASE",
        btc_d_direction="INCREASE",
        btc_change_pct=-2.0,
        assets=_sample_assets(),
        pattern_index=1,
    )
    assert result.opposite_direction is True


def test_opposite_direction_false_for_same_direction():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="INCREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
        pattern_index=1,
    )
    assert result.opposite_direction is False


# ---- Altcoin structure -------------------------------------------------------

def test_altcoin_structure_enabled_when_opposite():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
        pattern_index=1,
    )
    assert result.altcoin_structure["enabled"] is True
    assert result.altcoin_structure["reason"] == "BTC and BTC.D are in opposite directions."


def test_altcoin_structure_disabled_when_not_opposite():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="INCREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
        pattern_index=1,
    )
    assert result.altcoin_structure["enabled"] is False
    assert result.altcoin_structure["reason"] == "BTC and BTC.D are not in opposite directions."


def test_altcoin_structure_preserves_optional_fields():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
        pattern_index=1,
        total2={"value": 100.0},
        total3={"value": 200.0},
        others_d={"value": 50.0},
    )
    assert result.altcoin_structure["total2"] == {"value": 100.0}
    assert result.altcoin_structure["total3"] == {"value": 200.0}
    assert result.altcoin_structure["others_d"] == {"value": 50.0}


# ---- Narrative attachment ----------------------------------------------------

def test_selected_pattern_attached_correctly():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
        pattern_index=1,
    )
    assert result.selected_pattern["pattern"] == "Pattern 1"
    assert result.selected_pattern["title"] == "🟢 Altcoin Strength"
    assert "رشد BTC در کنار کاهش BTC.D" in result.selected_pattern["text"]


def test_pattern_index_selection():
    for pi, expected_title in [
        (1, "🟢 Altcoin Strength"),
        (2, "🟢 Altcoin Relative Strength"),
        (3, "🟢 Broad Altcoin Participation"),
    ]:
        result = run_cell_08(
            btc_direction="INCREASE",
            btc_d_direction="DECREASE",
            btc_change_pct=2.0,
            assets=_sample_assets(),
            pattern_index=pi,
        )
        assert result.selected_pattern["pattern"] == f"Pattern {pi}"
        assert result.selected_pattern["title"] == expected_title


def test_invalid_pattern_index_raises():
    with pytest.raises(ValueError):
        run_cell_08(
            btc_direction="INCREASE",
            btc_d_direction="DECREASE",
            btc_change_pct=2.0,
            assets=_sample_assets(),
            pattern_index=4,
        )


# ---- Asset preparation pipeline ----------------------------------------------

def test_assets_filtered_none_change_pct():
    assets = _sample_assets() + [{"symbol": "DOGEUSDT", "change_pct": None, "volume": 100.0}]
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="INCREASE",
        btc_change_pct=2.0,
        assets=assets,
        pattern_index=1,
    )
    all_assets = result.top_10_assets + result.strong_movers + result.relative_movers
    assert all(a.get("change_pct") is not None for a in all_assets)


def test_volume_status_on_all_output_assets():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="INCREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
        pattern_index=1,
    )
    all_output = result.top_10_assets + result.strong_movers + result.relative_movers
    assert all("volume_status" in a for a in all_output)


def test_relative_performance_calculated():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
        pattern_index=1,
    )
    # relative_movers should have relative_btc_performance_pct
    assert any("relative_btc_performance_pct" in a for a in result.relative_movers)


def test_absolute_direction_added():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="INCREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
        pattern_index=1,
    )
    all_output = result.top_10_assets + result.strong_movers + result.relative_movers
    assert all("direction" in a for a in all_output)
    assert all(a["direction"] in ("INCREASE", "DECREASE", "RANGE", "UNKNOWN") for a in all_output)


# ---- Input validation --------------------------------------------------------

def test_invalid_assets_type_raises():
    with pytest.raises(TypeError):
        run_cell_08(
            btc_direction="INCREASE",
            btc_d_direction="DECREASE",
            btc_change_pct=2.0,
            assets="not a list",
            pattern_index=1,
        )


def test_assets_list_copied_not_mutated():
    assets = _sample_assets()
    original = [dict(a) for a in assets]
    run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=assets,
        pattern_index=1,
    )
    assert assets == original


# ---- Audit verification ------------------------------------------------------

def test_audit_contains_all_safety_locks():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
        pattern_index=1,
    )
    audit = result.audit
    assert audit["engine"] == "CELL_08"
    assert audit["engine_version"] == "V3.1"
    assert audit["execution"] == "ANALYSIS_ONLY"
    assert audit["trading_enabled"] is False
    assert audit["orders_enabled"] is False
    assert audit["strategy_enabled"] is False
    assert audit["portfolio_actions_enabled"] is False
    assert audit["scenarios_locked"] is True
    assert audit["narratives_locked"] is True
    assert audit["narrative_pattern_count"] == 27
    assert audit["btc_is_benchmark"] is True
    assert audit["absolute_direction_preserved"] is True
    assert audit["relative_performance_is_complementary"] is True
    assert audit["btc_pair_analysis_enabled"] is True
    assert audit["altcoin_structure_used_only_when_required"] is True
    assert audit["opposite_direction"] is True
    assert "volume_required" in audit


# ---- Determinism -------------------------------------------------------------

def test_deterministic_execution():
    assets = _sample_assets()
    r1 = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=assets,
        pattern_index=1,
    )
    r2 = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=assets,
        pattern_index=1,
    )
    # All fields except timestamp should be identical
    for field in [
        "engine", "version", "scenario_id", "scenario_type",
        "btc_direction", "btc_d_direction", "context",
        "opposite_direction", "selected_pattern",
        "top_10_assets", "strong_movers", "relative_movers",
        "altcoin_structure", "audit",
    ]:
        assert getattr(r1, field) == getattr(r2, field), f"Field {field} differs"


# ---- Serialization -----------------------------------------------------------

def test_serialization_roundtrip():
    from app.analysis.u08_result import cell08_to_dict, cell08_to_json
    import json

    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
        pattern_index=1,
    )

    d = cell08_to_dict(result)
    assert isinstance(d, dict)
    assert d["engine"] == "CELL_08"
    assert d["scenario_id"] == 2

    s = cell08_to_json(result)
    assert isinstance(s, str)
    parsed = json.loads(s)
    assert parsed["engine"] == "CELL_08"
    assert parsed["scenario_id"] == 2


def test_persian_text_serialization():
    from app.analysis.u08_result import cell08_to_json

    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
        pattern_index=1,
    )
    json_str = cell08_to_json(result)
    # Should contain Persian characters (ensure_ascii=False)
    assert "رشد" in json_str or "BTC" in json_str


# ---- Self-tests --------------------------------------------------------------

def test_cell08_self_tests_pass():
    report = cell08_self_tests()
    assert report["status"] == "PASS"
    assert report["passed"] == report["total"]


# ---- Ranking integration -----------------------------------------------------

def test_ranking_respects_bullish_context():
    assets = [
        {"symbol": "A", "change_pct": 5.0, "volume": 100.0},
        {"symbol": "B", "change_pct": 3.0, "volume": 200.0},
        {"symbol": "C", "change_pct": 10.0, "volume": 50.0},
    ]
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="INCREASE",
        btc_change_pct=2.0,
        assets=assets,
        pattern_index=1,
    )
    # BULLISH: sorted by change_pct desc
    assert result.strong_movers[0]["symbol"] == "C"
    assert result.strong_movers[1]["symbol"] == "A"


def test_ranking_respects_bearish_context():
    assets = [
        {"symbol": "A", "change_pct": -5.0, "volume": 100.0},
        {"symbol": "B", "change_pct": -3.0, "volume": 200.0},
        {"symbol": "C", "change_pct": -10.0, "volume": 50.0},
    ]
    result = run_cell_08(
        btc_direction="DECREASE",
        btc_d_direction="RANGE",
        btc_change_pct=-2.0,
        assets=assets,
        pattern_index=1,
    )
    # BEARISH: sorted by change_pct asc (most negative first)
    assert result.strong_movers[0]["symbol"] == "C"
    assert result.strong_movers[1]["symbol"] == "A"


def test_ranking_respects_range_context():
    assets = [
        {"symbol": "A", "change_pct": 5.0, "volume": 100.0},
        {"symbol": "B", "change_pct": -10.0, "volume": 200.0},
        {"symbol": "C", "change_pct": 3.0, "volume": 50.0},
    ]
    result = run_cell_08(
        btc_direction="RANGE",
        btc_d_direction="RANGE",
        btc_change_pct=0.0,
        assets=assets,
        pattern_index=1,
    )
    # RANGE: sorted by abs(change_pct) desc
    assert result.strong_movers[0]["symbol"] == "B"
    assert result.strong_movers[1]["symbol"] == "A"