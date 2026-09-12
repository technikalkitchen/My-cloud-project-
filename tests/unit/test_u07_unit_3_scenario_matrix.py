"""Stage 7 (U07) Unit 7.3 — Scenario matrix focused tests."""
from __future__ import annotations

import pytest

from app.analysis.enums import Direction
from app.analysis.matrix import (
    SCENARIO_MATRIX,
    lookup_scenario,
    scenario_matrix_self_tests,
)


def test_self_tests_pass():
    result = scenario_matrix_self_tests()
    assert result["status"] == "PASS"
    assert result["passed"] == result["total"]


def test_matrix_size_and_unique_ids():
    assert len(SCENARIO_MATRIX) == 9
    ids = {m["scenario_id"] for m in SCENARIO_MATRIX.values()}
    assert ids == set(range(1, 10))


def test_all_nine_pairs_resolve():
    pairs = [
        (Direction.INCREASE, Direction.DECREASE, 1, "MIRROR"),
        (Direction.DECREASE, Direction.INCREASE, 2, "MIRROR"),
        (Direction.INCREASE, Direction.INCREASE, 3, "PARALLEL"),
        (Direction.DECREASE, Direction.DECREASE, 4, "PARALLEL"),
        (Direction.INCREASE, Direction.RANGE, 5, "RANGE-COMPATIBLE STATE"),
        (Direction.DECREASE, Direction.RANGE, 6, "RANGE-COMPATIBLE STATE"),
        (Direction.RANGE, Direction.INCREASE, 7, "RANGE-COMPATIBLE STATE"),
        (Direction.RANGE, Direction.DECREASE, 8, "RANGE-COMPATIBLE STATE"),
        (Direction.RANGE, Direction.RANGE, 9, "NEUTRAL / FLAT"),
    ]
    for total, usdt, expected_id, expected_type in pairs:
        result = lookup_scenario(total, usdt)
        assert result["scenario_id"] == expected_id
        assert result["scenario_type"] == expected_type
        assert result["total_direction"] == total.value
        assert result["usdt_direction"] == usdt.value


def test_lookup_returns_immutable_copy():
    result = lookup_scenario(
        Direction.INCREASE, Direction.DECREASE
    )
    result["scenario_id"] = 999
    fresh = lookup_scenario(
        Direction.INCREASE, Direction.DECREASE
    )
    assert fresh["scenario_id"] == 1


def test_invalid_total_type_rejected():
    with pytest.raises(TypeError):
        lookup_scenario("INCREASE", Direction.DECREASE)


def test_invalid_usdt_type_rejected():
    with pytest.raises(TypeError):
        lookup_scenario(Direction.INCREASE, "DECREASE")


def test_matrix_consumes_direction_pair_from_calculations():
    """Unit 7.3 consumes the direction pair produced by Unit 7.2."""
    from app.analysis.range_engine import analyze_range

    total_analysis = analyze_range(
        [100.0, 110.0, 120.0]
    )
    usdt_analysis = analyze_range(
        [5.0, 4.5, 4.0]
    )
    result = lookup_scenario(
        total_analysis.direction, usdt_analysis.direction
    )
    assert result["scenario_id"] == 1
    assert result["scenario_type"] == "MIRROR"


def test_all_direction_combinations_are_mapped():
    """The 3x3 direction space is fully covered by the 9-scenario matrix."""
    for total in Direction:
        for usdt in Direction:
            result = lookup_scenario(total, usdt)
            assert 1 <= result["scenario_id"] <= 9