"""Stage 7 (U07) validation helpers.

validate_scenario_matrix — matrix integrity check.
validate_timeframes — timeframe regression test.
"""
from __future__ import annotations

from typing import Any, Dict

from app.analysis.enums import Direction
from app.analysis.matrix import SCENARIO_MATRIX
from app.analysis.narratives import NARRATIVES
from app.analysis.timeframe import parse_timeframe


def validate_scenario_matrix() -> Dict[str, Any]:

    expected = {
        1: (Direction.INCREASE, Direction.DECREASE),
        2: (Direction.DECREASE, Direction.INCREASE),
        3: (Direction.INCREASE, Direction.INCREASE),
        4: (Direction.DECREASE, Direction.DECREASE),
        5: (Direction.INCREASE, Direction.RANGE),
        6: (Direction.DECREASE, Direction.RANGE),
        7: (Direction.RANGE, Direction.INCREASE),
        8: (Direction.RANGE, Direction.DECREASE),
        9: (Direction.RANGE, Direction.RANGE),
    }

    checks = []

    for scenario_id, pair in expected.items():

        actual = SCENARIO_MATRIX.get(pair)

        checks.append({
            "scenario_id": scenario_id,
            "pair": [
                pair[0].value,
                pair[1].value,
            ],
            "exists": actual is not None,
            "correct_id": (
                actual is not None
                and actual["scenario_id"] == scenario_id
            ),
        })

    narrative_checks = {
        scenario_id: len(
            NARRATIVES.get(scenario_id, [])
        ) == 3
        for scenario_id in expected
    }

    all_matrix_ok = all(
        x["exists"] and x["correct_id"]
        for x in checks
    )

    all_narratives_ok = all(
        narrative_checks.values()
    )

    return {
        "matrix_ok": all_matrix_ok,
        "narratives_ok": all_narratives_ok,
        "total_scenarios": len(SCENARIO_MATRIX),
        "total_narrative_patterns": sum(
            len(v)
            for v in NARRATIVES.values()
        ),
        "details": checks,
        "narrative_details": narrative_checks,
    }


# ============================================================
# 12. TIMEFRAME REGRESSION VALIDATION
# ============================================================

def validate_timeframes() -> Dict[str, Any]:

    tests = [
        "1m",
        "3m",
        "5m",
        "15m",
        "30m",
        "1h",
        "2h",
        "4h",
        "6h",
        "8h",
        "12h",
        "1D",
        "1W",
        "1M",
    ]

    results = []

    for tf in tests:

        result = parse_timeframe(tf)

        # ----------------------------------------------------
        # Only minute/hour timeframes below 1D get warning.
        # Day/week/month do not.
        # ----------------------------------------------------

        raw_unit = tf.strip()[-1]

        if raw_unit in ("m", "h", "H"):

            expected_warning = (
                "SUB_DAILY_WARNING"
            )

        else:

            expected_warning = None

        results.append({
            "timeframe": tf,
            "valid": result["valid"],
            "warning": result["warning"],
            "expected_warning": expected_warning,
            "passed": (
                result["valid"] is True
                and result["warning"]
                == expected_warning
            ),
        })

    return {
        "passed": all(
            x["passed"]
            for x in results
        ),
        "details": results,
    }
