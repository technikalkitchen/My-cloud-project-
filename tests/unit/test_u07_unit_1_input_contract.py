"""Stage 7 (U07) Unit 7.1 — Input contract focused tests."""
from __future__ import annotations

import pytest

from app.analysis.input_contract import (
    input_contract_self_tests,
    validate_stage7_input,
)
from app.config.quality import FRESHNESS_THRESHOLD_SECONDS


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
        "DEFINITIONS": {
            "KITCHEN_TOTAL_TOP125": "SUM(MARKET_CAP of ranks 1-125)",
            "KITCHEN_USDT_D": "USDT_MARKET_CAP / KITCHEN_TOTAL_TOP125 * 100",
        },
        "PROVENANCE": {"SOURCE": "coinmarketcap"},
        "FRESHNESS": {
            "status": "FRESH",
            "threshold_seconds": FRESHNESS_THRESHOLD_SECONDS,
        },
        "COVERAGE": {"top125": 1.0},
        "NO_DATA_FABRICATION": True,
        "errors": [],
        "warnings": [],
    }


def test_self_tests_pass():
    result = input_contract_self_tests()
    assert result["status"] == "PASS"
    assert result["passed"] == result["total"]


def test_valid_adapter_builds_contract():
    contract = validate_stage7_input(_base_adapter())
    assert contract.source_cell == "U06.5"
    assert contract.total_series == [3_000_000_000.0, 3_100_000_000.0]
    assert contract.usdt_d_series == [5.0, 4.8]
    assert contract.no_data_fabrication is True
    assert contract.freshness["status"] == "FRESH"


def test_wrong_source_cell_rejected():
    adapter = _base_adapter()
    adapter["SOURCE_CELL"] = "U08"
    with pytest.raises(ValueError):
        validate_stage7_input(adapter)


def test_missing_required_field_rejected():
    adapter = _base_adapter()
    adapter.pop("SNAPSHOT_HASH")
    with pytest.raises(ValueError):
        validate_stage7_input(adapter)


def test_stale_freshness_rejected():
    adapter = _base_adapter()
    adapter["FRESHNESS"] = {
        "status": "STALE",
        "threshold_seconds": FRESHNESS_THRESHOLD_SECONDS,
    }
    with pytest.raises(ValueError):
        validate_stage7_input(adapter)


def test_unavailable_freshness_accepted():
    adapter = _base_adapter()
    adapter["FRESHNESS"] = {
        "status": "UNAVAILABLE",
        "threshold_seconds": FRESHNESS_THRESHOLD_SECONDS,
    }
    contract = validate_stage7_input(adapter)
    assert contract.freshness["status"] == "UNAVAILABLE"


def test_short_series_rejected():
    adapter = _base_adapter()
    adapter["TOTAL_SERIES"] = [3_000_000_000.0]
    with pytest.raises(ValueError):
        validate_stage7_input(adapter)


def test_non_finite_value_rejected():
    adapter = _base_adapter()
    adapter["USDT_D_SERIES"] = [5.0, float("nan")]
    with pytest.raises(ValueError):
        validate_stage7_input(adapter)


def test_non_positive_value_rejected():
    adapter = _base_adapter()
    adapter["TOTAL_SERIES"] = [0.0, 100.0]
    with pytest.raises(ValueError):
        validate_stage7_input(adapter)


def test_length_mismatch_rejected():
    adapter = _base_adapter()
    adapter["TOTAL_SERIES"] = [1.0, 2.0, 3.0]
    with pytest.raises(ValueError):
        validate_stage7_input(adapter)


def test_fabrication_flag_rejected():
    adapter = _base_adapter()
    adapter["NO_DATA_FABRICATION"] = False
    with pytest.raises(ValueError):
        validate_stage7_input(adapter)


def test_non_dict_adapter_rejected():
    with pytest.raises(TypeError):
        validate_stage7_input("not a dict")


def test_non_dict_section_rejected():
    adapter = _base_adapter()
    adapter["PROVENANCE"] = None
    with pytest.raises(ValueError):
        validate_stage7_input(adapter)


def test_history_status_partial_accepted():
    adapter = _base_adapter()
    adapter["HISTORY_STATUS"] = "PARTIAL"
    contract = validate_stage7_input(adapter)
    assert contract.history_status == "PARTIAL"


def test_history_status_invalid_rejected():
    adapter = _base_adapter()
    adapter["HISTORY_STATUS"] = "UNKNOWN"
    with pytest.raises(ValueError):
        validate_stage7_input(adapter)


def test_max_freshness_age_seconds_negative_rejected():
    adapter = _base_adapter()
    with pytest.raises(ValueError):
        validate_stage7_input(adapter, max_freshness_age_seconds=-1)


def test_max_freshness_age_seconds_non_numeric_rejected():
    adapter = _base_adapter()
    with pytest.raises(TypeError):
        validate_stage7_input(adapter, max_freshness_age_seconds="x")