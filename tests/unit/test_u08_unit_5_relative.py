"""Stage 8 (U08) Unit 8.5 — relative BTC performance focused tests."""
from __future__ import annotations

import pytest

from app.analysis.enums import RelativeDirection
from app.analysis.u08_relative import (
    calculate_relative_btc_performance,
    classify_relative_performance,
    enrich_relative_performance,
    relative_performance_self_tests,
)


@pytest.mark.parametrize(
    "asset_change,btc_change,expected",
    [
        (-1.0, -3.0, 2.0),
        (1.0, 3.0, -2.0),
        ("5", "2", 3.0),
        (0.0, 0.0, 0.0),
    ],
)
def test_calculate_relative_performance_subtracts_btc(
    asset_change,
    btc_change,
    expected,
):
    assert calculate_relative_btc_performance(asset_change, btc_change) == expected


@pytest.mark.parametrize(
    "asset_change,btc_change",
    [
        (None, 1.0),
        (1.0, None),
        ("invalid", 1.0),
        (float("inf"), 1.0),
    ],
)
def test_calculate_relative_performance_returns_none_for_invalid_input(
    asset_change,
    btc_change,
):
    assert calculate_relative_btc_performance(asset_change, btc_change) is None


def test_classify_relative_performance_strength():
    assert (
        classify_relative_performance(-1.0, -3.0)
        is RelativeDirection.RELATIVE_STRENGTH
    )


def test_classify_relative_performance_weakness():
    assert (
        classify_relative_performance(1.0, 3.0)
        is RelativeDirection.RELATIVE_WEAKNESS
    )


def test_classify_relative_performance_neutral():
    assert (
        classify_relative_performance(2.0, 2.0)
        is RelativeDirection.RELATIVE_NEUTRAL
    )


def test_classify_relative_performance_epsilon_boundaries():
    assert (
        classify_relative_performance(1.5, 1.0, epsilon_pct=0.5)
        is RelativeDirection.RELATIVE_NEUTRAL
    )
    assert (
        classify_relative_performance(0.5, 1.0, epsilon_pct=0.5)
        is RelativeDirection.RELATIVE_NEUTRAL
    )
    assert (
        classify_relative_performance(1.6, 1.0, epsilon_pct=0.5)
        is RelativeDirection.RELATIVE_STRENGTH
    )
    assert (
        classify_relative_performance(0.4, 1.0, epsilon_pct=0.5)
        is RelativeDirection.RELATIVE_WEAKNESS
    )


def test_classify_relative_performance_missing_input_is_neutral():
    assert (
        classify_relative_performance(None, 1.0)
        is RelativeDirection.RELATIVE_NEUTRAL
    )


def test_enrich_relative_performance_adds_fields_and_preserves_input():
    assets = [
        {
            "asset": "ETH",
            "pct_change": 4.0,
            "volume": 100.0,
            "extra": "kept",
        },
        {
            "symbol": "SOL",
            "change_pct": -2.0,
            "volume": 50.0,
        },
        {"symbol": "INVALID", "change_pct": "invalid"},
    ]
    original = [dict(asset) for asset in assets]

    enriched = enrich_relative_performance(assets, btc_change_pct=2.0)

    assert assets == original
    assert [asset["symbol"] for asset in enriched] == ["ETH", "SOL", "INVALID"]
    assert enriched[0]["extra"] == "kept"
    assert enriched[0]["relative_btc_performance_pct"] == 2.0
    assert enriched[0]["relative_direction"] == RelativeDirection.RELATIVE_STRENGTH.value
    assert enriched[1]["relative_btc_performance_pct"] == -4.0
    assert enriched[1]["relative_direction"] == RelativeDirection.RELATIVE_WEAKNESS.value
    assert enriched[2]["relative_btc_performance_pct"] is None
    assert enriched[2]["relative_direction"] == RelativeDirection.RELATIVE_NEUTRAL.value


def test_self_tests_pass():
    result = relative_performance_self_tests()

    assert result["status"] == "PASS"
    assert result["passed"] == result["total"]
