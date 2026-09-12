"""Stage 8 (U08) Unit 8.6 — Ranking focused tests.

Covers ``rank_strong_movers``, ``rank_relative_movers``,
``rank_top_assets``, ``is_opposite_direction``, and
``add_absolute_direction`` from ``app.analysis.u08_ranking``.
"""
from __future__ import annotations

import pytest

from app.analysis.enums import Context, Direction
from app.analysis.u08_ranking import (
    add_absolute_direction,
    is_opposite_direction,
    rank_relative_movers,
    rank_strong_movers,
    rank_top_assets,
)


# ---- rank_strong_movers ----------------------------------------------------

@pytest.mark.parametrize(
    "direction,expected",
    [
        (Context.BULLISH, ["C", "A"]),
        (Context.BEARISH, ["B", "A"]),
        (Context.RANGE, ["C", "A"]),
    ],
)
def test_rank_strong_movers_sorts_by_change(direction, expected):
    assets = [
        {"symbol": "A", "change_pct": 5.0},
        {"symbol": "B", "change_pct": -3.0},
        {"symbol": "C", "change_pct": 10.0},
    ]
    result = rank_strong_movers(assets, direction, 2)
    assert [a["symbol"] for a in result] == expected


def test_rank_strong_movers_respects_n_limit():
    assets = [
        {"symbol": "A", "change_pct": 5.0},
        {"symbol": "B", "change_pct": 3.0},
        {"symbol": "C", "change_pct": 1.0},
    ]
    result = rank_strong_movers(assets, Context.BULLISH, 2)
    assert len(result) == 2
    assert [a["symbol"] for a in result] == ["A", "B"]


def test_rank_strong_movers_filters_none_change():
    assets = [
        {"symbol": "A", "change_pct": 5.0},
        {"symbol": "B", "change_pct": None},
        {"symbol": "C", "change_pct": 3.0},
    ]
    result = rank_strong_movers(assets, Context.BULLISH, 5)
    assert [a["symbol"] for a in result] == ["A", "C"]


def test_rank_strong_movers_empty_returns_empty():
    assert rank_strong_movers([], Context.BULLISH, 5) == []


def test_rank_strong_movers_all_none_change():
    assets = [{"symbol": "A", "change_pct": None}]
    assert rank_strong_movers(assets, Context.BULLISH, 5) == []


def test_rank_strong_movers_zero_change_bullish():
    assets = [
        {"symbol": "A", "change_pct": 0.0},
        {"symbol": "B", "change_pct": 1.0},
    ]
    result = rank_strong_movers(assets, Context.BULLISH, 2)
    assert [a["symbol"] for a in result] == ["B", "A"]


def test_rank_strong_movers_zero_change_range():
    assets = [
        {"symbol": "A", "change_pct": 0.0},
        {"symbol": "B", "change_pct": 3.0},
    ]
    result = rank_strong_movers(assets, Context.RANGE, 2)
    assert [a["symbol"] for a in result] == ["B", "A"]


def test_rank_strong_movers_does_not_mutate_input():
    assets = [{"symbol": "A", "change_pct": 5.0}]
    original = [dict(a) for a in assets]
    rank_strong_movers(assets, Context.BULLISH, 1)
    assert assets == original


# ---- rank_relative_movers --------------------------------------------------

@pytest.mark.parametrize(
    "direction,expected",
    [
        (Context.BULLISH, ["C", "A"]),
        (Context.BEARISH, ["B", "A"]),
        (Context.RANGE, ["C", "A"]),
    ],
)
def test_rank_relative_movers_sorts_by_relative(direction, expected):
    assets = [
        {"symbol": "A", "relative_btc_performance_pct": 2.0},
        {"symbol": "B", "relative_btc_performance_pct": -1.0},
        {"symbol": "C", "relative_btc_performance_pct": 5.0},
    ]
    result = rank_relative_movers(assets, direction, 2)
    assert [a["symbol"] for a in result] == expected


def test_rank_relative_movers_filters_none_relative():
    assets = [
        {"symbol": "A", "relative_btc_performance_pct": 2.0},
        {"symbol": "B", "relative_btc_performance_pct": None},
        {"symbol": "C", "relative_btc_performance_pct": -1.0},
    ]
    result = rank_relative_movers(assets, Context.BULLISH, 5)
    assert [a["symbol"] for a in result] == ["A", "C"]


def test_rank_relative_movers_empty_returns_empty():
    assert rank_relative_movers([], Context.BULLISH, 5) == []


def test_rank_relative_movers_does_not_mutate_input():
    assets = [{"symbol": "A", "relative_btc_performance_pct": 2.0}]
    original = [dict(a) for a in assets]
    rank_relative_movers(assets, Context.BULLISH, 1)
    assert assets == original


# ---- rank_top_assets -------------------------------------------------------

@pytest.mark.parametrize(
    "direction,expected",
    [
        (Context.BULLISH, ["B", "A"]),
        (Context.BEARISH, ["C", "A"]),
        (Context.RANGE, ["B", "A"]),
    ],
)
def test_rank_top_assets_sorts_by_change_then_volume(direction, expected):
    assets = [
        {"symbol": "A", "change_pct": 5.0, "volume": 100.0},
        {"symbol": "B", "change_pct": 5.0, "volume": 200.0},
        {"symbol": "C", "change_pct": 3.0, "volume": 500.0},
    ]
    result = rank_top_assets(assets, direction, 2)
    assert [a["symbol"] for a in result] == expected


def test_rank_top_assets_defaults_none_volume_to_zero():
    assets = [
        {"symbol": "A", "change_pct": 5.0, "volume": None},
        {"symbol": "B", "change_pct": 3.0, "volume": 100.0},
    ]
    result = rank_top_assets(assets, Context.BULLISH, 2)
    assert result[0]["volume"] == 0.0
    assert result[1]["volume"] == 100.0


def test_rank_top_assets_filters_none_change():
    assets = [
        {"symbol": "A", "change_pct": None, "volume": 100.0},
        {"symbol": "B", "change_pct": 3.0, "volume": 50.0},
    ]
    result = rank_top_assets(assets, Context.BULLISH, 2)
    assert [a["symbol"] for a in result] == ["B"]


def test_rank_top_assets_respects_n_limit():
    assets = [
        {"symbol": "A", "change_pct": 5.0, "volume": 100.0},
        {"symbol": "B", "change_pct": 3.0, "volume": 50.0},
    ]
    result = rank_top_assets(assets, Context.BULLISH, 1)
    assert len(result) == 1
    assert result[0]["symbol"] == "A"


def test_rank_top_assets_empty_returns_empty():
    assert rank_top_assets([], Context.BULLISH, 5) == []


def test_rank_top_assets_zero_change_bullish():
    assets = [
        {"symbol": "A", "change_pct": 0.0, "volume": 100.0},
        {"symbol": "B", "change_pct": 1.0, "volume": 50.0},
    ]
    result = rank_top_assets(assets, Context.BULLISH, 2)
    assert [a["symbol"] for a in result] == ["B", "A"]


def test_rank_top_assets_does_not_mutate_input():
    assets = [{"symbol": "A", "change_pct": 5.0, "volume": 100.0}]
    original = [dict(a) for a in assets]
    rank_top_assets(assets, Context.BULLISH, 1)
    assert assets == original


# ---- is_opposite_direction -------------------------------------------------

@pytest.mark.parametrize(
    "d1,d2,expected",
    [
        (Direction.INCREASE, Direction.DECREASE, True),
        (Direction.DECREASE, Direction.INCREASE, True),
        (Direction.INCREASE, Direction.INCREASE, False),
        (Direction.DECREASE, Direction.DECREASE, False),
        (Direction.RANGE, Direction.RANGE, False),
        (Direction.INCREASE, Direction.RANGE, False),
        (Direction.RANGE, Direction.DECREASE, False),
    ],
)
def test_is_opposite_direction(d1, d2, expected):
    assert is_opposite_direction(d1, d2) is expected


# ---- add_absolute_direction ------------------------------------------------

@pytest.mark.parametrize(
    "change,expected",
    [
        (5.0, "INCREASE"),
        (-3.0, "DECREASE"),
        (0.0, "RANGE"),
        (None, "UNKNOWN"),
    ],
)
def test_add_absolute_direction_labels(change, expected):
    assets = [{"symbol": "A", "change_pct": change}]
    result = add_absolute_direction(assets)
    assert result[0]["direction"] == expected


def test_add_absolute_direction_preserves_other_fields():
    assets = [{"symbol": "A", "change_pct": 5.0, "price": 100.0, "extra": "x"}]
    result = add_absolute_direction(assets)
    assert result[0]["price"] == 100.0
    assert result[0]["extra"] == "x"


def test_add_absolute_direction_does_not_mutate_input():
    assets = [{"symbol": "A", "change_pct": 5.0}]
    original = [dict(a) for a in assets]
    add_absolute_direction(assets)
    assert assets == original


def test_add_absolute_direction_empty_returns_empty():
    assert add_absolute_direction([]) == []
