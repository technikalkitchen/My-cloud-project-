"""Stage 7 (U07) regression tests.

run_u07_regression_tests — full regression suite.
"""
from __future__ import annotations

from typing import Any, Dict

from app.analysis.config import DEFAULT_RANGE_CONFIG
from app.analysis.enums import Direction
from app.analysis.matrix import SCENARIO_MATRIX
from app.analysis.range_engine import analyze_range
from app.analysis.validation_helpers import (
    validate_scenario_matrix,
    validate_timeframes,
)
from app.config.quality import (
    ORDERS_ENABLED,
    PORTFOLIO_ACTIONS_ENABLED,
    STRATEGY_ENABLED,
    TRADING_ENABLED,
)


def run_u07_regression_tests() -> Dict[str, Any]:

    # --------------------------------------------------------
    # MATRIX TEST
    # --------------------------------------------------------

    matrix = validate_scenario_matrix()

    # --------------------------------------------------------
    # TIMEFRAME TEST
    # --------------------------------------------------------

    timeframe = validate_timeframes()

    # --------------------------------------------------------
    # ZERO MOVEMENT TEST
    # --------------------------------------------------------

    zero_series = [
        100.0,
        102.0,
        98.0,
        101.0,
        100.0,
    ]

    zero_result = analyze_range(
        zero_series,
        config=DEFAULT_RANGE_CONFIG,
    )

    zero_movement_ok = (
        zero_result.direction
        == Direction.RANGE
    )

    # --------------------------------------------------------
    # RANGE INTERNAL-MOVEMENT TEST
    # --------------------------------------------------------

    choppy_series = [
        100,
        104,
        99,
        103,
        98,
        102,
        100,
    ]

    choppy_result = analyze_range(
        choppy_series,
        config=DEFAULT_RANGE_CONFIG,
    )

    internal_structure_checked = (
        choppy_result.switch_count > 0
    )

    # --------------------------------------------------------
    # NINE SCENARIO PAIR TEST
    # --------------------------------------------------------

    scenario_pairs = [

        (
            Direction.INCREASE,
            Direction.DECREASE,
        ),

        (
            Direction.DECREASE,
            Direction.INCREASE,
        ),

        (
            Direction.INCREASE,
            Direction.INCREASE,
        ),

        (
            Direction.DECREASE,
            Direction.DECREASE,
        ),

        (
            Direction.INCREASE,
            Direction.RANGE,
        ),

        (
            Direction.DECREASE,
            Direction.RANGE,
        ),

        (
            Direction.RANGE,
            Direction.INCREASE,
        ),

        (
            Direction.RANGE,
            Direction.DECREASE,
        ),

        (
            Direction.RANGE,
            Direction.RANGE,
        ),
    ]

    nine_scenarios_ok = all(
        pair in SCENARIO_MATRIX
        for pair in scenario_pairs
    )

    # --------------------------------------------------------
    # EXECUTION LOCK TEST
    # --------------------------------------------------------

    locks_ok = (
        TRADING_ENABLED is False
        and ORDERS_ENABLED is False
        and STRATEGY_ENABLED is False
        and PORTFOLIO_ACTIONS_ENABLED is False
    )

    # --------------------------------------------------------
    # OVERALL
    # --------------------------------------------------------

    overall = (

        matrix["matrix_ok"]

        and matrix["narratives_ok"]

        and timeframe["passed"]

        and zero_movement_ok

        and internal_structure_checked

        and nine_scenarios_ok

        and locks_ok
    )

    return {

        "status":
            "PASS"
            if overall
            else "FAIL",

        "matrix":
            matrix,

        "timeframe":
            timeframe,

        "zero_movement_edge_case": {

            "passed":
                zero_movement_ok,

            "classification":
                zero_result.direction.value,
        },

        "internal_structure": {

            "passed":
                internal_structure_checked,

            "switch_count":
                choppy_result.switch_count,
        },

        "nine_scenarios": {

            "passed":
                nine_scenarios_ok,

            "count":
                len(scenario_pairs),
        },

        "execution_locks": {

            "passed":
                locks_ok,
        },
    }
