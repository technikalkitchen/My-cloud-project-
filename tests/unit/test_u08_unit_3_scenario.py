"""Stage 8 (U08) Unit 8.3 — BTC/BTC.D scenario matrix focused tests."""
from __future__ import annotations

import pytest

from app.analysis.enums import Direction
from app.analysis.u08_scenario import (
    SCENARIO_MATRIX,
    lookup_scenario,
    resolve_scenario,
    scenario_matrix_self_tests,
    validate_scenario_matrix,
)


@pytest.mark.parametrize(
    "btc_direction,btc_d_direction,scenario_id,scenario_type",
    [
        (Direction.INCREASE, Direction.INCREASE, 1, "BTC_UP_BTC_D_UP"),
        (Direction.INCREASE, Direction.DECREASE, 2, "BTC_UP_BTC_D_DOWN"),
        (Direction.INCREASE, Direction.RANGE, 3, "BTC_UP_BTC_D_RANGE"),
        (Direction.DECREASE, Direction.INCREASE, 4, "BTC_DOWN_BTC_D_UP"),
        (Direction.DECREASE, Direction.DECREASE, 5, "BTC_DOWN_BTC_D_DOWN"),
        (Direction.DECREASE, Direction.RANGE, 6, "BTC_DOWN_BTC_D_RANGE"),
        (Direction.RANGE, Direction.INCREASE, 7, "BTC_RANGE_BTC_D_UP"),
        (Direction.RANGE, Direction.DECREASE, 8, "BTC_RANGE_BTC_D_DOWN"),
        (Direction.RANGE, Direction.RANGE, 9, "BTC_RANGE_BTC_D_RANGE"),
    ],
)
def test_all_nine_pairs_resolve(
    btc_direction,
    btc_d_direction,
    scenario_id,
    scenario_type,
):
    result = lookup_scenario(btc_direction, btc_d_direction)

    assert result["scenario_id"] == scenario_id
    assert result["scenario_type"] == scenario_type
    assert result["btc_direction"] == btc_direction.value
    assert result["btc_d_direction"] == btc_d_direction.value


def test_matrix_is_locked_to_nine_unique_scenarios():
    assert len(SCENARIO_MATRIX) == 9
    assert {
        mapping["scenario_id"] for mapping in SCENARIO_MATRIX.values()
    } == set(range(1, 10))


def test_resolve_scenario_accepts_direction_aliases():
    result = resolve_scenario("up", "flat")

    assert result["scenario_id"] == 3
    assert result["scenario_type"] == "BTC_UP_BTC_D_RANGE"


def test_lookup_rejects_non_direction_inputs():
    with pytest.raises(TypeError):
        lookup_scenario("INCREASE", Direction.INCREASE)

    with pytest.raises(TypeError):
        lookup_scenario(Direction.INCREASE, "INCREASE")


def test_resolve_rejects_unknown_direction_alias():
    with pytest.raises(ValueError):
        resolve_scenario("unknown", Direction.RANGE)


def test_lookup_returns_a_copy():
    result = lookup_scenario(Direction.INCREASE, Direction.INCREASE)
    result["scenario_id"] = 99

    fresh = lookup_scenario(Direction.INCREASE, Direction.INCREASE)
    assert fresh["scenario_id"] == 1


def test_self_tests_pass():
    result = scenario_matrix_self_tests()

    assert result["status"] == "PASS"
    assert result["passed"] == result["total"]


def test_validate_scenario_matrix_reports_all_pairs():
    result = validate_scenario_matrix()

    assert result["matrix_ok"] is True
    assert result["total_scenarios"] == 9
    assert len(result["details"]) == 9
