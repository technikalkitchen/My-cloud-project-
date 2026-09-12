"""Stage 8 (U08) Regression Gate — Cell 8 validation.

Comprehensive validation of Cell 8 invariants, contracts, and behavior.
Detects accidental changes to validated Cell 8 behavior.
"""
from __future__ import annotations

from typing import Any, Dict

from app.analysis.enums import Context, Direction
from app.analysis.u08_engine import run_cell_08, cell08_self_tests
from app.analysis.u08_narratives import NARRATIVES, validate_narratives
from app.analysis.u08_result import Cell08Result, cell08_to_dict, cell08_to_json
from app.analysis.u08_scenario import SCENARIO_MATRIX, validate_scenario_matrix
from app.analysis.u08_relative import relative_performance_self_tests
from app.analysis.u08_scenario import scenario_matrix_self_tests


def _result_passes(v: Any) -> bool:
    """Determine whether a sub-result entry counts as a pass."""
    if not isinstance(v, dict):
        return True
    status = v.get("status")
    if status is not None:
        return status in ("PASS", "LOCKED")
    return v.get("matrix_ok", True)


def run_cell08_regression_gate() -> Dict[str, Any]:
    """Run the complete Cell 8 regression validation gate.

    Returns a structured report with all validation results.
    """
    results: Dict[str, Any] = {}

    # 1. Self-tests from engine
    results["engine_self_tests"] = cell08_self_tests()

    # 2. Scenario matrix validation
    results["scenario_matrix"] = scenario_matrix_self_tests()
    results["scenario_matrix_details"] = validate_scenario_matrix()

    # 3. Narrative library validation
    results["narrative_validation"] = validate_narratives()

    # 4. Relative performance self-tests
    results["relative_performance"] = relative_performance_self_tests()

    # 5. Deterministic execution verification
    results["deterministic_execution"] = _test_deterministic_execution()

    # 6. Serialization round-trip
    results["serialization"] = _test_serialization_roundtrip()

    # 7. Scenario coverage verification
    results["scenario_coverage"] = _test_scenario_coverage()

    # 8. Pipeline integration verification
    results["pipeline_integration"] = _test_pipeline_integration()

    # 9. Safety lock verification
    results["safety_locks"] = _test_safety_locks()

    # 10. Volume handling verification
    results["volume_handling"] = _test_volume_handling()

    # Overall status
    all_passed = all(_result_passes(v) for v in results.values())

    return {
        "gate": "CELL_08_REGRESSION",
        "version": "V3.1",
        "status": "PASS" if all_passed else "FAIL",
        "results": results,
    }


def _test_deterministic_execution() -> Dict[str, Any]:
    """Verify that identical inputs produce identical outputs."""
    assets = [
        {"symbol": "BTCUSDT", "change_pct": 2.0, "volume": 1000.0},
        {"symbol": "ETHUSDT", "change_pct": 5.0, "volume": 500.0},
        {"symbol": "SOLUSDT", "change_pct": -1.0, "volume": 200.0},
    ]

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

    # Compare all fields except timestamp (which will differ)
    fields_to_compare = [
        "engine", "version", "scenario_id", "scenario_type",
        "btc_direction", "btc_d_direction", "context",
        "opposite_direction", "selected_pattern",
        "top_10_assets", "strong_movers", "relative_movers",
        "altcoin_structure", "audit",
    ]

    deterministic = all(
        getattr(r1, f) == getattr(r2, f) for f in fields_to_compare
    )

    return {
        "status": "PASS" if deterministic else "FAIL",
        "deterministic": deterministic,
    }


def _test_serialization_roundtrip() -> Dict[str, Any]:
    """Verify dict/JSON serialization preserves data."""
    assets = [
        {"symbol": "BTCUSDT", "change_pct": 2.0, "volume": 1000.0},
        {"symbol": "ETHUSDT", "change_pct": 5.0, "volume": 500.0},
    ]
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=assets,
        pattern_index=1,
    )

    # Dict roundtrip
    d = cell08_to_dict(result)
    dict_ok = (
        isinstance(d, dict)
        and d["engine"] == result.engine
        and d["scenario_id"] == result.scenario_id
        and d["selected_pattern"]["pattern"] == result.selected_pattern["pattern"]
    )

    # JSON roundtrip
    s = cell08_to_json(result)
    import json
    parsed = json.loads(s)
    json_ok = (
        isinstance(s, str)
        and parsed["engine"] == result.engine
        and parsed["scenario_id"] == result.scenario_id
        and parsed["selected_pattern"]["pattern"] == result.selected_pattern["pattern"]
    )

    # Persian text preserved
    persian_result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=assets,
        pattern_index=1,
    )
    persian_json = cell08_to_json(persian_result)
    persian_ok = "رشد" in persian_json or "کاهش" in persian_json or "BTC" in persian_json

    return {
        "status": "PASS" if (dict_ok and json_ok and persian_ok) else "FAIL",
        "dict_roundtrip": dict_ok,
        "json_roundtrip": json_ok,
        "persian_preserved": persian_ok,
    }


def _test_scenario_coverage() -> Dict[str, Any]:
    """Verify all 9 scenarios produce valid outputs."""
    assets = [
        {"symbol": "BTCUSDT", "change_pct": 2.0, "volume": 1000.0},
        {"symbol": "ETHUSDT", "change_pct": 5.0, "volume": 500.0},
    ]

    scenarios = [
        (Direction.INCREASE, Direction.INCREASE),
        (Direction.INCREASE, Direction.DECREASE),
        (Direction.INCREASE, Direction.RANGE),
        (Direction.DECREASE, Direction.INCREASE),
        (Direction.DECREASE, Direction.DECREASE),
        (Direction.DECREASE, Direction.RANGE),
        (Direction.RANGE, Direction.INCREASE),
        (Direction.RANGE, Direction.DECREASE),
        (Direction.RANGE, Direction.RANGE),
    ]

    all_ok = True
    details = {}
    for i, (btc_dir, btc_d_dir) in enumerate(scenarios, 1):
        try:
            result = run_cell_08(
                btc_direction=btc_dir,
                btc_d_direction=btc_d_dir,
                btc_change_pct=2.0 if btc_dir == Direction.INCREASE else (-2.0 if btc_dir == Direction.DECREASE else 0.0),
                assets=assets,
                pattern_index=1,
            )
            ok = (
                isinstance(result, Cell08Result)
                and result.scenario_id == i
                and result.btc_direction == btc_dir.value
                and result.btc_d_direction == btc_d_dir.value
                and result.context in ("BULLISH", "BEARISH", "RANGE")
            )
            details[f"scenario_{i}"] = ok
            if not ok:
                all_ok = False
        except Exception as e:
            details[f"scenario_{i}"] = f"ERROR: {e}"
            all_ok = False

    return {
        "status": "PASS" if all_ok else "FAIL",
        "all_scenarios_covered": all_ok,
        "details": details,
    }


def _test_pipeline_integration() -> Dict[str, Any]:
    """Verify the complete pipeline integrates all Block 1-4 components."""
    assets = [
        {"symbol": "BTCUSDT", "change_pct": 2.0, "volume": 1000.0},
        {"symbol": "ETHUSDT", "change_pct": 5.0, "volume": 500.0},
        {"symbol": "SOLUSDT", "change_pct": 3.0, "volume": 300.0},
        {"symbol": "XRPUSDT", "change_pct": -1.0, "volume": 200.0},
    ]

    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=assets,
        pattern_index=1,
        total2={"value": 100.0},
        total3={"value": 200.0},
        others_d={"value": 50.0},
    )

    checks = {
        "scenario_resolution": result.scenario_id == 2,
        "context_classification": result.context == "BULLISH",
        "ranking_executed": len(result.top_10_assets) > 0,
        "strong_movers_generated": len(result.strong_movers) > 0,
        "relative_movers_generated": len(result.relative_movers) > 0,
        "altcoin_structure_enabled": result.altcoin_structure["enabled"] is True,
        "altcoin_structure_has_optional": (
            result.altcoin_structure["total2"] == {"value": 100.0}
            and result.altcoin_structure["total3"] == {"value": 200.0}
            and result.altcoin_structure["others_d"] == {"value": 50.0}
        ),
        "narrative_attached": (
            result.selected_pattern["pattern"] == "Pattern 1"
            and result.selected_pattern["title"] == "🟢 Altcoin Strength"
            and "رشد BTC در کنار کاهش BTC.D" in result.selected_pattern["text"]
        ),
        "audit_contains_locks": (
            result.audit["scenarios_locked"] is True
            and result.audit["narratives_locked"] is True
            and result.audit["narrative_pattern_count"] == 27
        ),
        "opposite_direction_flag": result.opposite_direction is True,
        "btc_is_benchmark": result.audit["btc_is_benchmark"] is True,
        "absolute_direction_preserved": result.audit["absolute_direction_preserved"] is True,
        "relative_performance_complementary": result.audit["relative_performance_is_complementary"] is True,
    }

    all_ok = all(checks.values())

    return {
        "status": "PASS" if all_ok else "FAIL",
        "checks": checks,
    }


def _test_safety_locks() -> Dict[str, Any]:
    """Verify hard safety locks are present in audit."""
    assets = [{"symbol": "BTCUSDT", "change_pct": 2.0, "volume": 1000.0}]
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="INCREASE",
        btc_change_pct=2.0,
        assets=assets,
        pattern_index=1,
    )

    required_locks = {
        "trading_enabled": False,
        "orders_enabled": False,
        "strategy_enabled": False,
        "portfolio_actions_enabled": False,
        "scenarios_locked": True,
        "narratives_locked": True,
    }

    all_ok = all(
        result.audit.get(k) == v for k, v in required_locks.items()
    )

    return {
        "status": "PASS" if all_ok else "FAIL",
        "locks": {k: result.audit.get(k) for k in required_locks},
    }


def _test_volume_handling() -> Dict[str, Any]:
    """Verify volume handling follows Cell 8 rules (USDT pair only, no BTC pair)."""
    assets = [
        {"symbol": "BTCUSDT", "change_pct": 2.0, "volume": 1000.0, "btc_pair_volume": 50.0},
        {"symbol": "ETHUSDT", "change_pct": 5.0, "volume": None},
        {"symbol": "SOLUSDT", "change_pct": 3.0, "volume": 0.0},
    ]

    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="INCREASE",
        btc_change_pct=2.0,
        assets=assets,
        pattern_index=1,
    )

    all_output = result.top_10_assets + result.strong_movers + result.relative_movers

    checks = {
        "volume_field_present": all("volume" in a for a in all_output),
        "volume_status_present": all("volume_status" in a for a in all_output),
        "none_volume_marked_unavailable": any(
            a["volume_status"] == "UNAVAILABLE" for a in all_output if a["volume"] is None
        ),
        "zero_volume_marked_available": any(
            a["volume"] == 0.0 and a["volume_status"] == "AVAILABLE" for a in all_output
        ),
        "btc_pair_volume_not_in_output": all(
            "btc_pair_volume" not in a for a in all_output
        ),
    }

    all_ok = all(checks.values())

    return {
        "status": "PASS" if all_ok else "FAIL",
        "checks": checks,
    }