"""Stage 8 (U08) Unit 8.11 — Regression Gate focused tests.

Covers ``run_cell08_regression_gate`` from ``app.analysis.u08_regression``.
"""
from __future__ import annotations

import pytest

from app.analysis.u08_regression import run_cell08_regression_gate


def test_regression_gate_returns_structured_report():
    report = run_cell08_regression_gate()
    assert isinstance(report, dict)
    assert report["gate"] == "CELL_08_REGRESSION"
    assert report["version"] == "V3.1"
    assert "status" in report
    assert "results" in report


def test_regression_gate_overall_pass():
    report = run_cell08_regression_gate()
    assert report["status"] == "PASS"


def test_regression_gate_contains_all_checks():
    report = run_cell08_regression_gate()
    results = report["results"]
    expected_checks = [
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
    ]
    for check in expected_checks:
        assert check in results, f"Missing check: {check}"


def test_engine_self_tests_in_gate():
    report = run_cell08_regression_gate()
    engine_tests = report["results"]["engine_self_tests"]
    assert engine_tests["status"] == "PASS"
    assert engine_tests["passed"] == engine_tests["total"]


def test_scenario_matrix_in_gate():
    report = run_cell08_regression_gate()
    matrix = report["results"]["scenario_matrix"]
    assert matrix["status"] == "PASS"
    assert matrix["passed"] == matrix["total"]


def test_narrative_validation_in_gate():
    report = run_cell08_regression_gate()
    narrative = report["results"]["narrative_validation"]
    assert narrative["scenarios"] == 9
    assert narrative["patterns"] == 27
    assert narrative["status"] == "LOCKED"


def test_relative_performance_in_gate():
    report = run_cell08_regression_gate()
    rel = report["results"]["relative_performance"]
    assert rel["status"] == "PASS"
    assert rel["passed"] == rel["total"]


def test_deterministic_execution_in_gate():
    report = run_cell08_regression_gate()
    det = report["results"]["deterministic_execution"]
    assert det["status"] == "PASS"
    assert det["deterministic"] is True


def test_serialization_in_gate():
    report = run_cell08_regression_gate()
    ser = report["results"]["serialization"]
    assert ser["status"] == "PASS"
    assert ser["dict_roundtrip"] is True
    assert ser["json_roundtrip"] is True
    assert ser["persian_preserved"] is True


def test_scenario_coverage_in_gate():
    report = run_cell08_regression_gate()
    cov = report["results"]["scenario_coverage"]
    assert cov["status"] == "PASS"
    assert cov["all_scenarios_covered"] is True
    # All 9 scenarios should be tested
    assert len(cov["details"]) == 9
    for i in range(1, 10):
        assert cov["details"][f"scenario_{i}"] is True


def test_pipeline_integration_in_gate():
    report = run_cell08_regression_gate()
    pipe = report["results"]["pipeline_integration"]
    assert pipe["status"] == "PASS"
    checks = pipe["checks"]
    assert checks["scenario_resolution"] is True
    assert checks["context_classification"] is True
    assert checks["ranking_executed"] is True
    assert checks["strong_movers_generated"] is True
    assert checks["relative_movers_generated"] is True
    assert checks["altcoin_structure_enabled"] is True
    assert checks["altcoin_structure_has_optional"] is True
    assert checks["narrative_attached"] is True
    assert checks["audit_contains_locks"] is True
    assert checks["opposite_direction_flag"] is True
    assert checks["btc_is_benchmark"] is True
    assert checks["absolute_direction_preserved"] is True
    assert checks["relative_performance_complementary"] is True


def test_safety_locks_in_gate():
    report = run_cell08_regression_gate()
    locks = report["results"]["safety_locks"]
    assert locks["status"] == "PASS"
    assert locks["locks"]["trading_enabled"] is False
    assert locks["locks"]["orders_enabled"] is False
    assert locks["locks"]["strategy_enabled"] is False
    assert locks["locks"]["portfolio_actions_enabled"] is False
    assert locks["locks"]["scenarios_locked"] is True
    assert locks["locks"]["narratives_locked"] is True


def test_volume_handling_in_gate():
    report = run_cell08_regression_gate()
    vol = report["results"]["volume_handling"]
    assert vol["status"] == "PASS"
    checks = vol["checks"]
    assert checks["volume_field_present"] is True
    assert checks["volume_status_present"] is True
    assert checks["none_volume_marked_unavailable"] is True
    assert checks["zero_volume_marked_available"] is True
    assert checks["btc_pair_volume_not_in_output"] is True