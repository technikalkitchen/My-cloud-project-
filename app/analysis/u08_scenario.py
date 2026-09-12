"""Stage 8 (U08) BTC/BTC.D 9-scenario matrix."""
from __future__ import annotations

from typing import Any, Dict, Tuple

from app.analysis.enums import Direction
from app.analysis.u08_normalize import _normalize_direction


SCENARIO_MATRIX: Dict[
    Tuple[Direction, Direction],
    Dict[str, Any],
] = {
    (Direction.INCREASE, Direction.INCREASE): {
        "scenario_id": 1,
        "scenario_type": "BTC_UP_BTC_D_UP",
    },
    (Direction.INCREASE, Direction.DECREASE): {
        "scenario_id": 2,
        "scenario_type": "BTC_UP_BTC_D_DOWN",
    },
    (Direction.INCREASE, Direction.RANGE): {
        "scenario_id": 3,
        "scenario_type": "BTC_UP_BTC_D_RANGE",
    },
    (Direction.DECREASE, Direction.INCREASE): {
        "scenario_id": 4,
        "scenario_type": "BTC_DOWN_BTC_D_UP",
    },
    (Direction.DECREASE, Direction.DECREASE): {
        "scenario_id": 5,
        "scenario_type": "BTC_DOWN_BTC_D_DOWN",
    },
    (Direction.DECREASE, Direction.RANGE): {
        "scenario_id": 6,
        "scenario_type": "BTC_DOWN_BTC_D_RANGE",
    },
    (Direction.RANGE, Direction.INCREASE): {
        "scenario_id": 7,
        "scenario_type": "BTC_RANGE_BTC_D_UP",
    },
    (Direction.RANGE, Direction.DECREASE): {
        "scenario_id": 8,
        "scenario_type": "BTC_RANGE_BTC_D_DOWN",
    },
    (Direction.RANGE, Direction.RANGE): {
        "scenario_id": 9,
        "scenario_type": "BTC_RANGE_BTC_D_RANGE",
    },
}

assert len(SCENARIO_MATRIX) == 9


def lookup_scenario(
    btc_direction: Direction,
    btc_d_direction: Direction,
) -> Dict[str, Any]:
    """Return the canonical Cell 8 scenario for a direction pair."""

    if not isinstance(btc_direction, Direction):
        raise TypeError("btc_direction must be a Direction.")
    if not isinstance(btc_d_direction, Direction):
        raise TypeError("btc_d_direction must be a Direction.")

    pair = (btc_direction, btc_d_direction)
    mapping = SCENARIO_MATRIX.get(pair)
    if mapping is None:
        raise RuntimeError(
            "CELL08_ERROR: "
            "No canonical scenario exists."
        )

    return {
        "scenario_id": int(mapping["scenario_id"]),
        "scenario_type": str(mapping["scenario_type"]),
        "btc_direction": btc_direction.value,
        "btc_d_direction": btc_d_direction.value,
    }


def resolve_scenario(
    btc_direction: Any,
    btc_d_direction: Any,
) -> Dict[str, Any]:
    """Normalize aliases and resolve the Cell 8 scenario."""

    btc_direction = _normalize_direction(btc_direction)
    btc_d_direction = _normalize_direction(btc_d_direction)

    return lookup_scenario(
        btc_direction,
        btc_d_direction,
    )


def scenario_matrix_self_tests() -> Dict[str, Any]:
    """Run deterministic integrity checks for the Cell 8 matrix."""

    expected = {
        (Direction.INCREASE, Direction.INCREASE): 1,
        (Direction.INCREASE, Direction.DECREASE): 2,
        (Direction.INCREASE, Direction.RANGE): 3,
        (Direction.DECREASE, Direction.INCREASE): 4,
        (Direction.DECREASE, Direction.DECREASE): 5,
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
            and result["btc_direction"] == pair[0].value
            and result["btc_d_direction"] == pair[1].value
        )

    tests["matrix_size"] = len(SCENARIO_MATRIX) == 9
    tests["scenario_ids_unique"] = (
        len({mapping["scenario_id"] for mapping in SCENARIO_MATRIX.values()})
        == 9
    )

    try:
        lookup_scenario("INCREASE", Direction.INCREASE)
        tests["invalid_btc_type_rejected"] = False
    except TypeError:
        tests["invalid_btc_type_rejected"] = True

    try:
        lookup_scenario(Direction.INCREASE, "INCREASE")
        tests["invalid_btc_d_type_rejected"] = False
    except TypeError:
        tests["invalid_btc_d_type_rejected"] = True

    return {
        "status": "PASS" if all(tests.values()) else "FAIL",
        "passed": sum(tests.values()),
        "total": len(tests),
        "tests": tests,
    }


def validate_scenario_matrix() -> Dict[str, Any]:
    """Return matrix integrity details for regression reporting."""

    checks = []
    for pair, mapping in SCENARIO_MATRIX.items():
        checks.append({
            "scenario_id": mapping["scenario_id"],
            "pair": [pair[0].value, pair[1].value],
            "scenario_type": mapping["scenario_type"],
        })

    return {
        "matrix_ok": len(SCENARIO_MATRIX) == 9,
        "total_scenarios": len(SCENARIO_MATRIX),
        "details": checks,
    }
