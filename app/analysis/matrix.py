"""Stage 7 (U07) canonical 9-scenario matrix.

Scenario mapping: exact 9x9 matrix; unmapped pairs raise RuntimeError.
"""
from __future__ import annotations

from typing import Any, Dict, Tuple

from app.analysis.enums import Direction, ScenarioType


SCENARIO_MATRIX: Dict[Tuple[Direction, Direction], Dict[str, object]] = {
    (Direction.INCREASE, Direction.DECREASE): {
        "scenario_id": 1,
        "scenario_type": ScenarioType.MIRROR,
    },

    (Direction.DECREASE, Direction.INCREASE): {
        "scenario_id": 2,
        "scenario_type": ScenarioType.MIRROR,
    },

    (Direction.INCREASE, Direction.INCREASE): {
        "scenario_id": 3,
        "scenario_type": ScenarioType.PARALLEL,
    },

    (Direction.DECREASE, Direction.DECREASE): {
        "scenario_id": 4,
        "scenario_type": ScenarioType.PARALLEL,
    },

    (Direction.INCREASE, Direction.RANGE): {
        "scenario_id": 5,
        "scenario_type": ScenarioType.RANGE_COMPATIBLE_STATE,
    },

    (Direction.DECREASE, Direction.RANGE): {
        "scenario_id": 6,
        "scenario_type": ScenarioType.RANGE_COMPATIBLE_STATE,
    },

    (Direction.RANGE, Direction.INCREASE): {
        "scenario_id": 7,
        "scenario_type": ScenarioType.RANGE_COMPATIBLE_STATE,
    },

    (Direction.RANGE, Direction.DECREASE): {
        "scenario_id": 8,
        "scenario_type": ScenarioType.RANGE_COMPATIBLE_STATE,
    },

    (Direction.RANGE, Direction.RANGE): {
        "scenario_id": 9,
        "scenario_type": ScenarioType.NEUTRAL_FLAT,
    },
}


# ---------------------------------------------------------------------------
# Consumable lookup
# ---------------------------------------------------------------------------

def lookup_scenario(
    total_direction: Direction,
    usdt_direction: Direction,
) -> Dict[str, object]:
    """Return the canonical scenario mapping for a direction pair.

    Consumes the direction pair produced by Unit 7.2 range analysis.
    Raises RuntimeError for any unmapped pair.
    """
    if not isinstance(total_direction, Direction):
        raise TypeError("total_direction must be a Direction.")
    if not isinstance(usdt_direction, Direction):
        raise TypeError("usdt_direction must be a Direction.")

    pair = (total_direction, usdt_direction)
    if pair not in SCENARIO_MATRIX:
        raise RuntimeError(
            "No canonical U07 scenario mapping exists for this pair."
        )

    mapping = SCENARIO_MATRIX[pair]
    return {
        "scenario_id": int(mapping["scenario_id"]),
        "scenario_type": str(mapping["scenario_type"].value),
        "total_direction": total_direction.value,
        "usdt_direction": usdt_direction.value,
    }


def scenario_matrix_self_tests() -> Dict[str, Any]:
    """Deterministic self-test for the canonical scenario matrix."""
    from app.analysis.enums import Direction

    expected = {
        (Direction.INCREASE, Direction.DECREASE): 1,
        (Direction.DECREASE, Direction.INCREASE): 2,
        (Direction.INCREASE, Direction.INCREASE): 3,
        (Direction.DECREASE, Direction.DECREASE): 4,
        (Direction.INCREASE, Direction.RANGE): 5,
        (Direction.DECREASE, Direction.RANGE): 6,
        (Direction.RANGE, Direction.INCREASE): 7,
        (Direction.RANGE, Direction.DECREASE): 8,
        (Direction.RANGE, Direction.RANGE): 9,
    }

    tests: Dict[str, Any] = {}

    for pair, scenario_id in expected.items():
        result = lookup_scenario(*pair)
        tests[f"scenario_{scenario_id}"] = (
            result["scenario_id"] == scenario_id
            and result["total_direction"] == pair[0].value
            and result["usdt_direction"] == pair[1].value
        )

    tests["matrix_size"] = len(SCENARIO_MATRIX) == 9
    tests["scenario_ids_unique"] = len(
        {m["scenario_id"] for m in SCENARIO_MATRIX.values()}
    ) == 9

    try:
        lookup_scenario("NOT_A_DIRECTION", Direction.RANGE)
        tests["invalid_type_rejected"] = False
    except TypeError:
        tests["invalid_type_rejected"] = True

    try:
        lookup_scenario(Direction.INCREASE, "BAD")
        tests["invalid_usdt_type_rejected"] = False
    except TypeError:
        tests["invalid_usdt_type_rejected"] = True

    return {
        "status": "PASS" if all(tests.values()) else "FAIL",
        "passed": sum(tests.values()),
        "total": len(tests),
        "tests": tests,
    }