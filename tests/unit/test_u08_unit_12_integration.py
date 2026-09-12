"""Stage 8 (U08) Unit 8.12 — Cell 8 integration test.

Validates the complete Cell 8 pipeline end-to-end:
  - Blocks 1-4 components compose correctly through ``run_cell_08``.
  - The 27 Persian narratives are correctly attached per scenario.
  - Ranking, relative performance, altcoin structure, and volume outputs
    survive the full pipeline.
  - Dict/JSON serialization preserves Persian text.
  - Deterministic outputs match the original Cell 8 notebook contracts.
"""
from __future__ import annotations

import copy
import json

import pytest

from app.analysis.enums import Direction
from app.analysis.u08_narratives import NARRATIVES, get_narrative
from app.analysis.u08_regression import run_cell08_regression_gate
from app.analysis.u08_result import Cell08Result, cell08_to_dict, cell08_to_json
from app.analysis.u08_engine import cell08_self_tests, run_cell_08


def _sample_assets():
    return [
        {"symbol": "BTCUSDT", "change_pct": 2.0, "volume": 1000.0,
         "price": 50000.0},
        {"symbol": "ETHUSDT", "change_pct": 5.0, "volume": 500.0,
         "price": 3000.0},
        {"symbol": "SOLUSDT", "change_pct": -1.0, "volume": 200.0,
         "price": 150.0},
        {"symbol": "XRPUSDT", "change_pct": 3.0, "volume": 300.0,
         "price": 2.5},
        {"symbol": "ADAUSDT", "change_pct": -4.0, "volume": None,
         "price": 0.5},
    ]


SCENARIOS = [
    (Direction.INCREASE, Direction.INCREASE, 1, "BULLISH"),
    (Direction.INCREASE, Direction.DECREASE, 2, "BULLISH"),
    (Direction.INCREASE, Direction.RANGE, 3, "BULLISH"),
    (Direction.DECREASE, Direction.INCREASE, 4, "BEARISH"),
    (Direction.DECREASE, Direction.DECREASE, 5, "BEARISH"),
    (Direction.DECREASE, Direction.RANGE, 6, "BEARISH"),
    (Direction.RANGE, Direction.INCREASE, 7, "RANGE"),
    (Direction.RANGE, Direction.DECREASE, 8, "RANGE"),
    (Direction.RANGE, Direction.RANGE, 9, "RANGE"),
]


# ---- Pipeline produces Cell08Result -------------------------------------------

def test_pipeline_returns_cell08result():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
    )
    assert isinstance(result, Cell08Result)


def test_pipeline_result_has_all_notebook_fields():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
    )
    for field in [
        "engine", "version", "timestamp_utc", "scenario_id",
        "scenario_type", "btc_direction", "btc_d_direction",
        "context", "opposite_direction", "selected_pattern",
        "top_10_assets", "strong_movers", "relative_movers",
        "altcoin_structure", "audit",
    ]:
        assert hasattr(result, field), f"Missing field: {field}"


def test_pipeline_engine_identifies_as_cell_08():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="INCREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
    )
    assert result.engine == "CELL_08"
    assert result.version == "V3.1"
    assert result.audit["engine"] == "CELL_08"
    assert result.audit["engine_version"] == "V3.1"
    assert result.audit["execution"] == "ANALYSIS_ONLY"


# ---- Blocks 1-4 composition ---------------------------------------------------

def test_pipeline_blocks_compose_scenario_resolution():
    """Block 3 (scenario) connects correctly to engine output."""
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
    )
    assert result.scenario_id == 2
    assert result.scenario_type == "BTC_UP_BTC_D_DOWN"
    assert result.btc_direction == "INCREASE"
    assert result.btc_d_direction == "DECREASE"


def test_pipeline_blocks_compose_context_classification():
    """Block 4 (context) connects correctly to engine output."""
    for btc_dir, btc_d_dir, scenario_id, expected_context in SCENARIOS:
        btc_change = 2.0 if btc_dir == Direction.INCREASE else (
            -2.0 if btc_dir == Direction.DECREASE else 0.0
        )
        result = run_cell_08(
            btc_direction=btc_dir,
            btc_d_direction=btc_d_dir,
            btc_change_pct=btc_change,
            assets=_sample_assets(),
        )
        assert result.context == expected_context
        assert result.scenario_id == scenario_id


def test_pipeline_blocks_compose_relative_performance():
    """Block 5 (relative) connects: relative_movers carry relative fields."""
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="INCREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
    )
    for asset in result.relative_movers:
        assert "relative_btc_performance_pct" in asset
        assert "relative_direction" in asset
        assert asset["relative_direction"] in (
            "RELATIVE_STRENGTH", "RELATIVE_WEAKNESS", "RELATIVE_NEUTRAL",
        )


def test_pipeline_blocks_compose_ranking_output():
    """Block 6/7 (ranking/altcoin) connect: strong_movers sorted by context."""
    bullish_assets = [
        {"symbol": "A", "change_pct": 5.0, "volume": 100.0},
        {"symbol": "B", "change_pct": 3.0, "volume": 200.0},
        {"symbol": "C", "change_pct": 10.0, "volume": 50.0},
    ]
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="INCREASE",
        btc_change_pct=2.0,
        assets=bullish_assets,
    )
    # BULLISH: strong movers sorted by change_pct desc
    changes = [a["change_pct"] for a in result.strong_movers]
    assert changes == sorted(changes, reverse=True)


def test_pipeline_blocks_compose_narratives():
    """Block 8 (narratives) connects: pattern is attached and matches scenario."""
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
        pattern_index=1,
    )
    expected = get_narrative(result.scenario_id, 1)
    assert result.selected_pattern["pattern"] == expected["pattern"]
    assert result.selected_pattern["title"] == expected["title"]
    assert result.selected_pattern["text"] == expected["text"]


# ---- 27 Persian narratives correctness ----------------------------------------

def test_all_9_scenarios_have_3_patterns():
    for scenario_id in range(1, 10):
        assert len(NARRATIVES[scenario_id]) == 3


def test_total_narratives_is_27():
    total = sum(len(NARRATIVES[sid]) for sid in range(1, 10))
    assert total == 27


@pytest.mark.parametrize("scenario_id", list(range(1, 10)))
def test_scenario_narratives_attached_to_result(scenario_id):
    """Each scenario's patterns are reachable through the engine."""
    dirs = list(Direction)
    btc_dir, btc_d_dir = dirs[(scenario_id - 1) % 3], dirs[(scenario_id - 1) // 3]
    result = run_cell_08(
        btc_direction=btc_dir,
        btc_d_direction=btc_d_dir,
        btc_change_pct=2.0,
        assets=_sample_assets(),
        pattern_index=1,
    )
    expected = NARRATIVES[result.scenario_id][0]
    assert result.selected_pattern["pattern"] == expected["pattern"]
    assert result.selected_pattern["title"] == expected["title"]


def test_persian_narrative_text_preserved_in_result():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
        pattern_index=1,
    )
    text = result.selected_pattern["text"]
    assert "رشد" in text
    assert "کاهش" in text or "BTC.D" in text


# ---- Altcoin structure -------------------------------------------------------

@pytest.mark.parametrize(
    "btc_dir,btc_d_dir,expected_enabled",
    [
        (Direction.INCREASE, Direction.DECREASE, True),
        (Direction.DECREASE, Direction.INCREASE, True),
        (Direction.INCREASE, Direction.INCREASE, False),
        (Direction.DECREASE, Direction.DECREASE, False),
        (Direction.RANGE, Direction.RANGE, False),
    ],
)
def test_altcoin_structure_lifecycle(btc_dir, btc_d_dir, expected_enabled):
    result = run_cell_08(
        btc_direction=btc_dir,
        btc_d_direction=btc_d_dir,
        btc_change_pct=2.0,
        assets=_sample_assets(),
    )
    assert result.altcoin_structure["enabled"] is expected_enabled
    assert "reason" in result.altcoin_structure
    assert "total2" in result.altcoin_structure
    assert "total3" in result.altcoin_structure
    assert "others_d" in result.altcoin_structure


def test_altcoin_structure_preserves_optional_data():
    total2 = {"value": 100.0, "name": "TOTAL2"}
    total3 = {"value": 200.0, "name": "TOTAL3"}
    others_d = {"value": 50.0, "name": "OTHERS.D"}
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
        total2=total2,
        total3=total3,
        others_d=others_d,
    )
    assert result.altcoin_structure["total2"] == total2
    assert result.altcoin_structure["total3"] == total3
    assert result.altcoin_structure["others_d"] == others_d


def test_altcoin_structure_none_when_not_opposite():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="INCREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
    )
    assert result.altcoin_structure["total2"] is None
    assert result.altcoin_structure["total3"] is None
    assert result.altcoin_structure["others_d"] is None


# ---- Volume handling ---------------------------------------------------------

def test_volume_status_on_all_output_assets():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
    )
    all_assets = result.top_10_assets + result.strong_movers + result.relative_movers
    assert all("volume_status" in a for a in all_assets)
    assert all("volume" in a for a in all_assets)


def test_volume_none_marked_unavailable():
    assets = [
        {"symbol": "ETHUSDT", "change_pct": 5.0, "volume": None},
    ]
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="INCREASE",
        btc_change_pct=2.0,
        assets=assets,
    )
    all_assets = result.top_10_assets + result.strong_movers + result.relative_movers
    unavailable = [a for a in all_assets if a["volume"] is None]
    assert all(a["volume_status"] == "UNAVAILABLE" for a in unavailable)


def test_volume_zero_marked_available():
    assets = [
        {"symbol": "ETHUSDT", "change_pct": 5.0, "volume": 0.0},
    ]
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="INCREASE",
        btc_change_pct=2.0,
        assets=assets,
    )
    all_assets = result.top_10_assets + result.strong_movers + result.relative_movers
    for a in all_assets:
        if a["volume"] == 0.0:
            assert a["volume_status"] == "AVAILABLE"


def test_btc_pair_volume_stripped_from_output():
    assets = [
        {"symbol": "ETHUSDT", "change_pct": 5.0, "volume": 100.0,
         "btc_pair_volume": 50.0, "btc_pair_change_pct": 2.0},
    ]
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=assets,
    )
    all_assets = result.top_10_assets + result.strong_movers + result.relative_movers
    assert all("btc_pair_volume" not in a for a in all_assets)
    assert all("btc_pair_change_pct" not in a for a in all_assets)


# ---- Serialization with Persian text ------------------------------------------

def test_complete_pipeline_dict_serialization():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
    )
    d = cell08_to_dict(result)
    assert isinstance(d, dict)
    assert d["engine"] == "CELL_08"
    assert d["version"] == "V3.1"
    assert d["scenario_id"] == 2
    assert d["selected_pattern"]["pattern"] == "Pattern 1"
    assert d["selected_pattern"]["title"] == "\U0001f7e2 Altcoin Strength"


def test_complete_pipeline_json_serialization_persian():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
    )
    s = cell08_to_json(result)
    parsed = json.loads(s)
    assert parsed["engine"] == "CELL_08"
    # Persian text preserved (not escaped)
    assert "رشد" in s
    assert parsed["selected_pattern"]["text"] == result.selected_pattern["text"]


def test_complete_pipeline_json_parsable_with_unicode():
    """JSON must round-trip Persian text without corruption."""
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
        pattern_index=2,
    )
    s = cell08_to_json(result)
    parsed = json.loads(s)
    assert parsed["selected_pattern"]["text"] == result.selected_pattern["text"]
    assert "الگو" in parsed["selected_pattern"]["text"].lower() or \
        any(c in parsed["selected_pattern"]["text"] for c in "اآبپتث")


def test_json_uses_ensure_ascii_false():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
    )
    s = cell08_to_json(result)
    # If ensure_ascii=True, Persian would be escaped as \uXXXX
    assert "\\u" not in s


# ---- Deterministic notebook parity --------------------------------------------

def test_pipeline_deterministic_across_runs():
    assets = _sample_assets()
    r1 = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=copy.deepcopy(assets),
        pattern_index=1,
    )
    r2 = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=copy.deepcopy(assets),
        pattern_index=1,
    )
    for field in [
        "engine", "version", "scenario_id", "scenario_type",
        "btc_direction", "btc_d_direction", "context",
        "opposite_direction", "selected_pattern",
        "top_10_assets", "strong_movers", "relative_movers",
        "altcoin_structure", "audit",
    ]:
        assert getattr(r1, field) == getattr(r2, field), f"Non-deterministic: {field}"


def test_pipeline_input_not_mutated():
    assets = _sample_assets()
    original = [dict(a) for a in assets]
    run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=assets,
    )
    assert assets == original


def test_pipeline_pattern_index_variants():
    assets = _sample_assets()
    results = []
    for pi in (1, 2, 3):
        r = run_cell_08(
            btc_direction="INCREASE",
            btc_d_direction="DECREASE",
            btc_change_pct=2.0,
            assets=copy.deepcopy(assets),
            pattern_index=pi,
        )
        results.append(r)
        assert r.selected_pattern["pattern"] == f"Pattern {pi}"
    assert results[0].selected_pattern["title"] != results[1].selected_pattern["title"]
    assert results[1].selected_pattern["title"] != results[2].selected_pattern["title"]


# ---- Safety locks -------------------------------------------------------------

def test_pipeline_no_trading_signals():
    """No trading/order/strategy signal fields in result or audit."""
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
    )
    for field in ("entry", "exit", "long", "short", "trigger", "trade",
                  "signal", "order", "position"):
        assert field not in result.audit
        assert field not in result.__dict__


def test_pipeline_safety_locks_disabled():
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="INCREASE",
        btc_change_pct=2.0,
        assets=_sample_assets(),
    )
    assert result.audit["trading_enabled"] is False
    assert result.audit["orders_enabled"] is False
    assert result.audit["strategy_enabled"] is False
    assert result.audit["portfolio_actions_enabled"] is False
    assert result.audit["scenarios_locked"] is True
    assert result.audit["narratives_locked"] is True
    assert result.audit["narrative_pattern_count"] == 27
    assert result.audit["btc_is_benchmark"] is True
    assert result.audit["absolute_direction_preserved"] is True
    assert result.audit["relative_performance_is_complementary"] is True
    assert result.audit["btc_pair_analysis_enabled"] is True
    assert result.audit["altcoin_structure_used_only_when_required"] is True


# ---- Regression gate integration ----------------------------------------------

def test_regression_gate_runs_end_to_end():
    report = run_cell08_regression_gate()
    assert report["gate"] == "CELL_08_REGRESSION"
    assert report["version"] == "V3.1"
    assert report["status"] == "PASS"


def test_regression_gate_all_subchecks_pass():
    report = run_cell08_regression_gate()
    results = report["results"]
    for check_name in [
        "engine_self_tests",
        "scenario_matrix",
        "scenario_matrix_details",
        "narrative_validation",
        "relative_performance",
        "deterministic_execution",
        "serialization",
        "scenario_coverage",
        "pipeline_integration",
        "safety_locks",
        "volume_handling",
    ]:
        assert check_name in results, f"Missing gate check: {check_name}"


def test_self_tests_pass():
    report = cell08_self_tests()
    assert report["status"] == "PASS"
    assert report["passed"] == report["total"]


# ---- Notebook contract parity -------------------------------------------------

def test_notebook_contract_opposite_direction_logic():
    """Notebook: opposite only when BTC up/BTC.D down or vice-versa."""
    assert run_cell_08(
        btc_direction="INCREASE", btc_d_direction="DECREASE",
        btc_change_pct=2.0, assets=_sample_assets(),
    ).opposite_direction is True
    assert run_cell_08(
        btc_direction="DECREASE", btc_d_direction="INCREASE",
        btc_change_pct=-2.0, assets=_sample_assets(),
    ).opposite_direction is True
    assert run_cell_08(
        btc_direction="INCREASE", btc_d_direction="INCREASE",
        btc_change_pct=2.0, assets=_sample_assets(),
    ).opposite_direction is False
    assert run_cell_08(
        btc_direction="RANGE", btc_d_direction="RANGE",
        btc_change_pct=0.0, assets=_sample_assets(),
    ).opposite_direction is False


def test_notebook_contract_relative_performance_calculation():
    """Notebook: relative = asset_change - btc_change."""
    from app.analysis.u08_relative import calculate_relative_btc_performance
    assert calculate_relative_btc_performance(-1.0, -3.0) == 2.0
    assert calculate_relative_btc_performance(5.0, 2.0) == 3.0
    assert calculate_relative_btc_performance(None, 1.0) is None


def test_notebook_contract_bearish_ranking():
    """Notebook: BEARISH context sorts strong movers most-negative first."""
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
    )
    changes = [a["change_pct"] for a in result.strong_movers]
    assert changes == sorted(changes)  # ascending = most negative first


def test_notebook_contract_range_ranking_by_abs_change():
    """Notebook: RANGE context sorts by absolute change descending."""
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
    )
    abs_changes = [abs(a["change_pct"]) for a in result.strong_movers]
    assert abs_changes == sorted(abs_changes, reverse=True)
