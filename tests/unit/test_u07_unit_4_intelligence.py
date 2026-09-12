"""Stage 7 (U07) Unit 7.4 — Intelligence + Persian narratives focused tests."""
from __future__ import annotations

import pytest

from app.analysis.narratives import (
    NARRATIVES,
    narratives_self_tests,
    select_narrative,
)


def test_self_tests_pass():
    result = narratives_self_tests()
    assert result["status"] == "PASS"
    assert result["passed"] == result["total"]


def test_narrative_library_structure():
    assert len(NARRATIVES) == 9
    assert all(len(v) == 3 for v in NARRATIVES.values())
    assert sum(len(v) for v in NARRATIVES.values()) == 27


def test_all_narratives_non_empty_strings():
    for scenario_id, patterns in NARRATIVES.items():
        assert 1 <= scenario_id <= 9
        for pattern in patterns:
            assert isinstance(pattern, str)
            assert len(pattern) > 0


def test_each_scenario_has_three_distinct_patterns():
    for patterns in NARRATIVES.values():
        assert len(set(patterns)) == 3


def test_select_narrative_returns_locked_text():
    text = select_narrative(1, 1)
    assert text == NARRATIVES[1][0]
    assert text.startswith("رشد ارزش کل بازار")


def test_pattern_index_validation():
    for scenario_id in range(1, 10):
        for pattern_index in (1, 2, 3):
            text = select_narrative(scenario_id, pattern_index)
            assert text == NARRATIVES[scenario_id][pattern_index - 1]


def test_invalid_scenario_id_rejected():
    with pytest.raises(ValueError):
        select_narrative(0, 1)
    with pytest.raises(ValueError):
        select_narrative(10, 1)


def test_invalid_pattern_index_rejected():
    with pytest.raises(ValueError):
        select_narrative(1, 0)
    with pytest.raises(ValueError):
        select_narrative(1, 4)


def test_invalid_scenario_type_rejected():
    with pytest.raises(TypeError):
        select_narrative("1", 1)


def test_invalid_pattern_type_rejected():
    with pytest.raises(TypeError):
        select_narrative(1, "1")


def test_narrative_text_is_immutable():
    text = select_narrative(9, 3)
    assert text == NARRATIVES[9][2]


def test_consumes_scenario_id_from_matrix():
    from app.analysis.enums import Direction
    from app.analysis.matrix import lookup_scenario

    scenario = lookup_scenario(
        Direction.INCREASE, Direction.DECREASE
    )
    text = select_narrative(scenario["scenario_id"], 1)
    assert text == NARRATIVES[1][0]


def test_no_creative_rewriting():
    for scenario_id in range(1, 10):
        for pattern_index in (1, 2, 3):
            assert (
                select_narrative(scenario_id, pattern_index)
                == NARRATIVES[scenario_id][pattern_index - 1]
            )