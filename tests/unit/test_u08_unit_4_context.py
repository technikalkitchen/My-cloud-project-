"""Stage 8 (U08) Unit 8.4 — BTC/BTC.D context focused tests."""
from __future__ import annotations

import pytest

from app.analysis.enums import Context, Direction
from app.analysis.u08_context import classify_context


@pytest.mark.parametrize(
    "btc_d_direction",
    [Direction.INCREASE, Direction.DECREASE, Direction.RANGE],
)
def test_btc_increase_is_bullish_regardless_of_btc_d(btc_d_direction):
    assert classify_context(Direction.INCREASE, btc_d_direction) is Context.BULLISH


@pytest.mark.parametrize(
    "btc_d_direction",
    [Direction.INCREASE, Direction.DECREASE, Direction.RANGE],
)
def test_btc_decrease_is_bearish_regardless_of_btc_d(btc_d_direction):
    assert classify_context(Direction.DECREASE, btc_d_direction) is Context.BEARISH


@pytest.mark.parametrize(
    "btc_d_direction",
    [Direction.INCREASE, Direction.DECREASE, Direction.RANGE],
)
def test_btc_range_is_range_regardless_of_btc_d(btc_d_direction):
    assert classify_context(Direction.RANGE, btc_d_direction) is Context.RANGE


@pytest.mark.parametrize(
    "btc_direction,btc_d_direction,expected",
    [
        ("up", "down", Context.BULLISH),
        ("bearish", "rising", Context.BEARISH),
        ("flat", "sideways", Context.RANGE),
    ],
)
def test_context_accepts_direction_aliases(
    btc_direction,
    btc_d_direction,
    expected,
):
    assert classify_context(btc_direction, btc_d_direction) is expected


def test_context_rejects_invalid_btc_direction():
    with pytest.raises(ValueError):
        classify_context("unknown", Direction.RANGE)


def test_context_rejects_invalid_btc_d_direction():
    with pytest.raises(ValueError):
        classify_context(Direction.INCREASE, "unknown")
