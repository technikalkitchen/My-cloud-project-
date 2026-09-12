"""Stage 7 (U07) Unit 7.5 — Final integration + verification tests."""
from __future__ import annotations

import copy

import pytest

from app.analysis.engine import ScenarioResult, run_stage7
from app.analysis.input_contract import validate_stage7_input


def _base_adapter():
    now = "2026-09-11T16:30:00+00:00"
    points = [
        {
            "timestamp": now,
            "KITCHEN_TOTAL_TOP125": 3_000_000_000.0,
            "KITCHEN_USDT_D": 5.0,
            "KITCHEN_BTC_D": 40.0,
        },
        {
            "timestamp": now,
            "KITCHEN_TOTAL_TOP125": 3_100_000_000.0,
            "KITCHEN_USDT_D": 4.8,
            "KITCHEN_BTC_D": 41.0,
        },
    ]
    return {
        "SOURCE_CELL": "U06.5",
        "SCHEMA_VERSION": "U06_5_SCHEMA_V6_0",
        "RUN_ID": "RUN",
        "SNAPSHOT_ID": "SNAP",
        "SNAPSHOT_HASH": "abc",
        "DATA_STATUS": "FROZEN",
        "TIMEFRAME": "1h",
        "DATASET_MODE": "SNAPSHOT",
        "ANALYSIS_RANGE": {"start": "2026-09-10", "end": "2026-09-11"},
        "AVAILABLE_RANGE": {"start": now, "end": now},
        "HISTORY_STATUS": "VALIDATED",
        "HISTORY_SOURCE": "KITCHEN_RECORDED",
        "HISTORY_COVERAGE": 1.0,
        "HISTORY_POINTS": points,
        "TOTAL_SERIES": [p["KITCHEN_TOTAL_TOP125"] for p in points],
        "TOTAL2_SERIES": [p["KITCHEN_TOTAL_TOP125"] for p in points],
        "TOTAL3_SERIES": [p["KITCHEN_TOTAL_TOP125"] for p in points],
        "BTC_D_SERIES": [p["KITCHEN_BTC_D"] for p in points],
        "USDT_D_SERIES": [p["KITCHEN_USDT_D"] for p in points],
        "CURRENT_VALUES": {
            "KITCHEN_TOTAL_TOP125": 3_100_000_000.0,
            "KITCHEN_USDT_D": 4.8,
        },
        "PROVIDER_METADATA": {"provider": "coinmarketcap"},
        "DEFINITIONS": {},
        "PROVENANCE": {"SOURCE": "coinmarketcap"},
        "FRESHNESS": {"status": "FRESH", "threshold_seconds": 900},
        "COVERAGE": {"top125": 1.0},
        "NO_DATA_FABRICATION": True,
        "errors": [],
        "warnings": [],
    }


def test_pipeline_returns_scenario_result():
    result = run_stage7(_base_adapter(), pattern_index=1)
    assert isinstance(result, ScenarioResult)
    assert 1 <= result.scenario_id <= 9
    assert result.scenario_type
    assert result.total_classification in {
        "INCREASE", "DECREASE", "RANGE"
    }
    assert result.usdt_d_classification in {
        "INCREASE", "DECREASE", "RANGE"
    }
    assert 1 <= result.pattern_index <= 3
    assert result.selected_pattern
    assert result.timeframe == "1h"
    assert result.timeframe_valid is True


def test_pipeline_consumes_all_units():
    result = run_stage7(_base_adapter(), pattern_index=1)
    audit = result.audit
    assert audit["pipeline"] == "U07.1->U07.2->U07.3->U07.4"
    assert "input_contract" in audit
    assert "calculations" in audit
    assert "scenario" in audit
    assert "approved_narrative" in audit
    assert audit["scenario"]["scenario_id"] == result.scenario_id
    assert audit["scenario"]["scenario_type"] == result.scenario_type


def test_pipeline_execution_locks_disabled():
    result = run_stage7(_base_adapter(), pattern_index=1)
    locks = result.audit["execution_locks"]
    assert locks["trading"] is False
    assert locks["orders"] is False
    assert locks["strategy"] is False
    assert locks["portfolio_actions"] is False


def test_pipeline_no_trading_signals():
    result = run_stage7(_base_adapter(), pattern_index=1)
    for field in (
        "entry", "exit", "long", "short", "trigger", "trade",
        "signal", "order", "position",
    ):
        assert field not in result.audit
        assert field not in result.audit.get("scenario", {})


def test_pipeline_deterministic():
    adapter = _base_adapter()
    r1 = run_stage7(adapter, pattern_index=1)
    r2 = run_stage7(copy.deepcopy(adapter), pattern_index=1)
    assert r1.scenario_id == r2.scenario_id
    assert r1.scenario_type == r2.scenario_type
    assert r1.total_classification == r2.total_classification
    assert r1.usdt_d_classification == r2.usdt_d_classification
    assert r1.selected_pattern == r2.selected_pattern


def test_pipeline_pattern_index_variants():
    adapter = _base_adapter()
    r1 = run_stage7(adapter, pattern_index=1)
    r2 = run_stage7(adapter, pattern_index=2)
    r3 = run_stage7(adapter, pattern_index=3)
    assert r1.pattern_index == 1
    assert r2.pattern_index == 2
    assert r3.pattern_index == 3
    assert r1.selected_pattern != r2.selected_pattern
    assert r2.selected_pattern != r3.selected_pattern


def test_pipeline_invalid_pattern_index_rejected():
    with pytest.raises(ValueError):
        run_stage7(_base_adapter(), pattern_index=4)


def test_pipeline_rejects_unavailable_freshness():
    adapter = _base_adapter()
    adapter["FRESHNESS"] = {
        "status": "STALE", "threshold_seconds": 900
    }
    with pytest.raises(ValueError):
        run_stage7(adapter)


def test_pipeline_rejects_missing_history():
    adapter = _base_adapter()
    adapter["TOTAL_SERIES"] = [3_000_000_000.0]
    with pytest.raises(ValueError):
        run_stage7(adapter)


def test_pipeline_source_must_be_u065():
    adapter = _base_adapter()
    adapter["SOURCE_CELL"] = "U08"
    with pytest.raises(ValueError):
        run_stage7(adapter)


def test_pipeline_consumes_u065_adapter():
    """Unit 7.5 connects the actual U06.5 adapter from the frozen foundation."""
    from app.market.finalization import run_u06_5

    result = run_u06_5(skip_self_tests=True)
    adapter = result["adapters"]["u07"]

    assert adapter["SOURCE_CELL"] == "U06.5"
    assert adapter["SCHEMA_VERSION"] == "U06_5_SCHEMA_V6_0"
    assert adapter["NO_DATA_FABRICATION"] is True
    assert adapter["SNAPSHOT_HASH"] == result["data_foundation"]["snapshot_hash"]


def test_pipeline_rejects_real_u065_adapter_without_history():
    """A real adapter with no recorded history is NOT silently accepted."""
    from app.market.finalization import run_u06_5

    result = run_u06_5(skip_self_tests=True)
    adapter = result["adapters"]["u07"]
    with pytest.raises(ValueError):
        run_stage7(adapter)
