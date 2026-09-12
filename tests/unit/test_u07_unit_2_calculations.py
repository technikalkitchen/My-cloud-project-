"""Stage 7 (U07) Unit 7.2 — Calculations + validation focused tests."""
from __future__ import annotations

import pytest

from app.analysis.calculations import (
    calculate_stage7,
    calculations_self_tests,
)
from app.analysis.input_contract import (
    Stage7InputContract,
    validate_stage7_input,
)


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
        "TIMEFRAME": "5m",
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


def _contract():
    return validate_stage7_input(_base_adapter())


def test_self_tests_pass():
    result = calculations_self_tests()
    assert result["status"] == "PASS"
    assert result["passed"] == result["total"]


def test_total_pct_movement():
    calc = calculate_stage7(_contract())
    assert abs(calc.total_net_change_pct - 3.3333333333333335) < 1e-9


def test_total_extremes_and_amplitude():
    calc = calculate_stage7(_contract())
    assert calc.total_high == 3_100_000_000.0
    assert calc.total_low == 3_000_000_000.0
    assert abs(calc.total_amplitude_pct - 3.3333333333333335) < 1e-9


def test_usdt_d_pct_and_pp_distinct():
    calc = calculate_stage7(_contract())
    assert abs(calc.usdt_d_net_change_pct - (-4.0)) < 1e-9
    assert abs(calc.usdt_d_net_change_pp - (-0.2)) < 1e-9
    assert calc.usdt_d_net_change_pct != calc.usdt_d_net_change_pp


def test_total2_total3_calculated():
    calc = calculate_stage7(_contract())
    assert abs(calc.total2_net_change_pct - calc.total_net_change_pct) < 1e-9
    assert abs(calc.total3_net_change_pct - calc.total_net_change_pct) < 1e-9


def test_btc_d_pct_and_pp():
    calc = calculate_stage7(_contract())
    assert abs(calc.btc_d_net_change_pct - 2.5) < 1e-9
    assert abs(calc.btc_d_net_change_pp - 1.0) < 1e-9


def test_status_and_freshness_propagated():
    calc = calculate_stage7(_contract())
    assert calc.data_status == "FROZEN"
    assert calc.freshness_status == "FRESH"
    assert calc.point_count == 2


def _contract_with(total, usdt_d, total2=None, total3=None, btc_d=None):
    if total2 is None:
        total2 = total
    if total3 is None:
        total3 = total
    if btc_d is None:
        btc_d = usdt_d
    now = "2026-09-11T16:30:00+00:00"
    return Stage7InputContract(
        source_cell="U06.5",
        schema_version="U06_5_SCHEMA_V6_0",
        run_id="RUN",
        snapshot_id="SNAP",
        snapshot_hash="abc",
        data_status="FROZEN",
        timeframe="5m",
        dataset_mode="SNAPSHOT",
        analysis_range={"start": "2026-09-10", "end": "2026-09-11"},
        available_range={"start": now, "end": now},
        history_status="VALIDATED",
        history_source="KITCHEN_RECORDED",
        history_coverage=1.0,
        history_points=[],
        total_series=[float(v) for v in total],
        total2_series=[float(v) for v in total2],
        total3_series=[float(v) for v in total3],
        btc_d_series=[float(v) for v in btc_d],
        usdt_d_series=[float(v) for v in usdt_d],
        current_values={},
        provider_metadata={},
        definitions={},
        provenance={},
        freshness={"status": "FRESH", "threshold_seconds": 900},
        coverage={},
        no_data_fabrication=True,
        validation={},
        errors=[],
        warnings=[],
    )


def test_non_finite_rejected():
    contract = _contract_with([3_000_000_000.0, float("inf")], [5.0, 4.8])
    with pytest.raises(ValueError):
        calculate_stage7(contract)


def test_non_positive_rejected():
    contract = _contract_with([0.0, 100.0], [5.0, 4.8])
    with pytest.raises(ValueError):
        calculate_stage7(contract)


def test_length_mismatch_rejected():
    contract = _contract_with([1.0, 2.0, 3.0], [5.0, 4.8])
    with pytest.raises(ValueError):
        calculate_stage7(contract)


def test_contract_type_required():
    with pytest.raises(TypeError):
        calculate_stage7("not a contract")


def test_zero_start_rejected():
    contract = _contract_with(
        [0.0, 100.0],
        [5.0, 4.8],
        total2=[0.0, 100.0],
        total3=[0.0, 100.0],
        btc_d=[40.0, 41.0],
    )
    with pytest.raises(ValueError):
        calculate_stage7(contract)