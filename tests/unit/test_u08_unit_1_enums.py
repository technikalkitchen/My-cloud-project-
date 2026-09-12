"""Stage 8 (U08) Unit 1 — Cell 8 enums.

Cell 8 uses its own Context and RelativeDirection enums. Direction is
shared (reused from the Stage 7 enum module) since both stages use the
identical INCREASE / DECREASE / RANGE triad.
"""
from __future__ import annotations

import pytest

from app.analysis.enums import (
    Context,
    Direction,
    RelativeDirection,
)


def test_direction_values():
    assert Direction.INCREASE.value == "INCREASE"
    assert Direction.DECREASE.value == "DECREASE"
    assert Direction.RANGE.value == "RANGE"


def test_direction_is_str_enum():
    assert Direction.INCREASE.value == "INCREASE"
    assert str(Direction.INCREASE) == "Direction.INCREASE"


def test_context_values():
    assert {c.value for c in Context} == {"BULLISH", "BEARISH", "RANGE"}
    assert Context.BULLISH == "BULLISH"
    assert Context.BEARISH == "BEARISH"
    assert Context.RANGE == "RANGE"


def test_relative_direction_values():
    assert {d.value for d in RelativeDirection} == {
        "RELATIVE_STRENGTH",
        "RELATIVE_WEAKNESS",
        "RELATIVE_NEUTRAL",
    }
    assert RelativeDirection.RELATIVE_STRENGTH.value == "RELATIVE_STRENGTH"
    assert (
        RelativeDirection.RELATIVE_NEUTRAL.value == "RELATIVE_NEUTRAL"
    )


def test_enums_are_str_subclasses():
    assert issubclass(Context, str)
    assert issubclass(RelativeDirection, str)


def test_no_duplicate_enum_members():
    for enum_cls in (Direction, Context, RelativeDirection):
        values = [m.value for m in enum_cls]
        assert len(values) == len(set(values)), f"Duplicate values in {enum_cls}"
