"""Stage 7 (U07) Unit 7.2 — Calculations + validation.

Implements the Stage 7 numerical calculations:
  - Total-market (KITCHEN_TOTAL_TOP125) values and movements.
  - USDT.D values and movements.
  - Percentage movement vs dominance percentage-point movement distinction.
  - Deterministic handling of missing/invalid/stale/edge-case data.

Consumes the Stage7InputContract produced by Unit 7.1. Does NOT duplicate
Unit 7.1 logic.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.analysis.input_contract import Stage7InputContract
from app.analysis.metrics import _is_finite_number, pct_change


@dataclass
class Stage7Calculations:
    total_start: float
    total_end: float
    total_net_change_pct: float
    total_high: float
    total_low: float
    total_amplitude_pct: float

    usdt_d_start: float
    usdt_d_end: float
    usdt_d_net_change_pct: float
    usdt_d_net_change_pp: float
    usdt_d_high: float
    usdt_d_low: float
    usdt_d_amplitude_pct: float

    total2_start: float
    total2_end: float
    total2_net_change_pct: float

    total3_start: float
    total3_end: float
    total3_net_change_pct: float

    btc_d_start: float
    btc_d_end: float
    btc_d_net_change_pct: float
    btc_d_net_change_pp: float

    data_status: str
    freshness_status: str
    point_count: int
    available_range: Dict[str, Any]

    validation: Dict[str, Any]
    errors: List[str]
    warnings: List[str]


def _pct(start: float, end: float) -> float:
    if start == 0:
        raise ValueError("Cannot calculate percentage change from zero.")
    return ((end - start) / start) * 100.0


def _pp(start: float, end: float) -> float:
    """Percentage-point movement (dominance)."""
    return end - start


def _extremes(series: List[float]) -> tuple[float, float]:
    return max(series), min(series)


def _amplitude(series: List[float]) -> float:
    start = float(series[0])
    if start == 0:
        return 0.0
    highest, lowest = _extremes(series)
    return ((highest - lowest) / start) * 100.0


def calculate_stage7(contract: Stage7InputContract) -> Stage7Calculations:
    """Compute Stage 7 calculations from the validated Unit 7.1 contract."""
    if not isinstance(contract, Stage7InputContract):
        raise TypeError("contract must be a Stage7InputContract.")

    total = contract.total_series
    usdt_d = contract.usdt_d_series
    total2 = contract.total2_series
    total3 = contract.total3_series
    btc_d = contract.btc_d_series

    total_start = float(total[0])
    total_end = float(total[-1])
    usdt_d_start = float(usdt_d[0])
    usdt_d_end = float(usdt_d[-1])
    total2_start = float(total2[0])
    total2_end = float(total2[-1])
    total3_start = float(total3[0])
    total3_end = float(total3[-1])
    btc_d_start = float(btc_d[0])
    btc_d_end = float(btc_d[-1])

    total_high, total_low = _extremes(total)
    usdt_d_high, usdt_d_low = _extremes(usdt_d)

    validation: Dict[str, Any] = {
        "total_positive": all(v > 0 for v in total),
        "usdt_d_positive": all(v > 0 for v in usdt_d),
        "total_finite": all(_is_finite_number(v) for v in total),
        "usdt_d_finite": all(_is_finite_number(v) for v in usdt_d),
        "series_lengths_equal": (
            len(total) == len(usdt_d) == len(total2) == len(total3) == len(btc_d)
        ),
        "point_count": len(total),
        "min_points": 2,
        "sufficient_points": len(total) >= 2,
    }

    errors: List[str] = []
    warnings: List[str] = []

    if not validation["sufficient_points"]:
        errors.append(
            "INSUFFICIENT_POINTS: at least 2 history points are required."
        )

    if not validation["total_positive"]:
        errors.append("TOTAL_SERIES contains non-positive values.")

    if not validation["usdt_d_positive"]:
        errors.append("USDT_D_SERIES contains non-positive values.")

    if not validation["total_finite"]:
        errors.append("TOTAL_SERIES contains non-finite values.")

    if not validation["usdt_d_finite"]:
        errors.append("USDT_D_SERIES contains non-finite values.")

    if not validation["series_lengths_equal"]:
        errors.append("Series length mismatch detected.")

    if errors:
        raise ValueError(
            "CALCULATION_VALIDATION_FAILED: " + "; ".join(errors)
        )

    return Stage7Calculations(
        total_start=total_start,
        total_end=total_end,
        total_net_change_pct=_pct(total_start, total_end),
        total_high=total_high,
        total_low=total_low,
        total_amplitude_pct=_amplitude(total),

        usdt_d_start=usdt_d_start,
        usdt_d_end=usdt_d_end,
        usdt_d_net_change_pct=_pct(usdt_d_start, usdt_d_end),
        usdt_d_net_change_pp=_pp(usdt_d_start, usdt_d_end),
        usdt_d_high=usdt_d_high,
        usdt_d_low=usdt_d_low,
        usdt_d_amplitude_pct=_amplitude(usdt_d),

        total2_start=total2_start,
        total2_end=total2_end,
        total2_net_change_pct=_pct(total2_start, total2_end),

        total3_start=total3_start,
        total3_end=total3_end,
        total3_net_change_pct=_pct(total3_start, total3_end),

        btc_d_start=btc_d_start,
        btc_d_end=btc_d_end,
        btc_d_net_change_pct=_pct(btc_d_start, btc_d_end),
        btc_d_net_change_pp=_pp(btc_d_start, btc_d_end),

        data_status=contract.data_status,
        freshness_status=contract.freshness.get("status", "UNAVAILABLE"),
        point_count=len(total),
        available_range=contract.available_range,
        validation=validation,
        errors=list(contract.errors),
        warnings=list(contract.warnings),
    )


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _make_contract():
    from app.analysis.input_contract import validate_stage7_input

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
    adapter = {
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
    return validate_stage7_input(adapter)


def calculations_self_tests() -> Dict[str, Any]:
    """Deterministic self-test for the Stage 7 calculations unit."""
    contract = _make_contract()
    calc = calculate_stage7(contract)

    tests: Dict[str, Any] = {}

    tests["total_pct_movement"] = (
        abs(calc.total_net_change_pct - 3.3333333333333335) < 1e-9
    )
    tests["total_extremes"] = (
        calc.total_high == 3_100_000_000.0
        and calc.total_low == 3_000_000_000.0
    )
    tests["total_amplitude"] = (
        abs(calc.total_amplitude_pct - 3.3333333333333335) < 1e-9
    )

    tests["usdt_d_pct_movement"] = (
        abs(calc.usdt_d_net_change_pct - (-4.0)) < 1e-9
    )
    tests["usdt_d_pp_movement"] = (
        abs(calc.usdt_d_net_change_pp - (-0.2)) < 1e-9
    )
    tests["usdt_d_distinct_from_pct"] = (
        calc.usdt_d_net_change_pct != calc.usdt_d_net_change_pp
    )

    tests["total2_total3_calculated"] = (
        abs(calc.total2_net_change_pct - calc.total_net_change_pct) < 1e-9
        and abs(calc.total3_net_change_pct - calc.total_net_change_pct) < 1e-9
    )

    tests["btc_d_pct_and_pp"] = (
        abs(calc.btc_d_net_change_pct - 2.5) < 1e-9
        and abs(calc.btc_d_net_change_pp - 1.0) < 1e-9
    )

    tests["data_status_propagated"] = calc.data_status == "FROZEN"
    tests["freshness_propagated"] = calc.freshness_status == "FRESH"
    tests["point_count"] = calc.point_count == 2
    tests["available_range_present"] = isinstance(
        calc.available_range, dict
    )

    return {
        "status": "PASS" if all(tests.values()) else "FAIL",
        "passed": sum(tests.values()),
        "total": len(tests),
        "tests": tests,
    }
