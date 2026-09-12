"""Stage 8 (U08) Unit 2 — Normalization + alias-aware direction.

Covers `_safe_float`, `_safe_pct_change`, `_normalize_direction`,
`normalize_asset`.
"""
from __future__ import annotations

import math

import pytest

from app.analysis.enums import Direction
from app.analysis.u08_normalize import (
    _normalize_direction,
    _safe_float,
    _safe_pct_change,
    normalize_asset,
)


# ---- _safe_float -----------------------------------------------------------

def test_safe_float_none():
    assert _safe_float(None) is None


def test_safe_float_non_numeric():
    assert _safe_float("abc") is None
    assert _safe_float(object()) is None


def test_safe_float_numeric():
    assert _safe_float("1.5") == 1.5
    assert _safe_float(1e2) == 100.0


def test_safe_float_non_finite():
    assert _safe_float(float("inf")) is None
    assert _safe_float(float("-inf")) is None
    assert _safe_float(float("nan")) is None


# ---- _safe_pct_change ------------------------------------------------------

def test_safe_pct_change_basic():
    assert _safe_pct_change(100.0, 110.0) == 10.0
    assert _safe_pct_change(100.0, 90.0) == -10.0


def test_safe_pct_change_handles_strings():
    assert _safe_pct_change("100", "110") == 10.0


def test_safe_pct_change_none_or_zero_start():
    assert _safe_pct_change(None, 110.0) is None
    assert _safe_pct_change(100.0, None) is None
    assert _safe_pct_change(0, 110.0) is None


# ---- _normalize_direction --------------------------------------------------

def test_normalize_direction_passthrough():
    assert _normalize_direction(Direction.INCREASE) is Direction.INCREASE
    assert _normalize_direction(Direction.DECREASE) is Direction.DECREASE
    assert _normalize_direction(Direction.RANGE) is Direction.RANGE


@pytest.mark.parametrize(
    "token,expected",
    [
        ("up", Direction.INCREASE),
        ("UP", Direction.INCREASE),
        ("Bullish", Direction.INCREASE),
        ("rising", Direction.INCREASE),
        ("increase", Direction.INCREASE),
        ("down", Direction.DECREASE),
        ("Bearish", Direction.DECREASE),
        ("falling", Direction.DECREASE),
        ("decrease", Direction.DECREASE),
        ("range", Direction.RANGE),
        ("flat", Direction.RANGE),
        ("sideways", Direction.RANGE),
        ("  Up  ", Direction.INCREASE),
    ],
)
def test_normalize_direction_aliases(token, expected):
    assert _normalize_direction(token) is expected


def test_normalize_direction_unsupported_raises():
    with pytest.raises(ValueError):
        _normalize_direction("nonsense")
    with pytest.raises(ValueError):
        _normalize_direction(None)  # None is not a Direction, str(None).upper()="NONE"
    with pytest.raises(ValueError):
        _normalize_direction(42)


# ---- normalize_asset -------------------------------------------------------

def _sample_asset():
    return {
        "symbol": "AAAUSDT",
        "price": 100.0,
        "change_pct": 5.0,
        "volume": 1000.0,
        "btc_pair_change_pct": 2.0,
    }


def test_normalize_asset_extracts_core_fields():
    out = normalize_asset(_sample_asset())
    assert out["symbol"] == "AAAUSDT"
    assert out["price"] == 100.0
    assert out["change_pct"] == 5.0
    assert out["volume"] == 1000.0
    assert out["btc_pair_change_pct"] == 2.0


def test_normalize_asset_change_pct_aliases():
    asset = {"symbol": "BTC", "price": 10, "pct_change": 3.0}
    out = normalize_asset(asset)
    assert out["change_pct"] == 3.0


def test_normalize_asset_change_pct_percent_change_alias():
    asset = {"symbol": "BTC", "price": 10, "percent_change": -2.0}
    out = normalize_asset(asset)
    assert out["change_pct"] == -2.0


def test_normalize_asset_btc_pair_alias():
    asset = {"symbol": "ETH", "price": 20, "btc_pair_pct_change": 1.5}
    out = normalize_asset(asset)
    assert out["btc_pair_change_pct"] == 1.5


def test_normalize_asset_symbol_alias():
    asset = {"asset": "LINK", "price": 5, "change_pct": 1.0}
    out = normalize_asset(asset)
    assert out["symbol"] == "LINK"


def test_normalize_asset_non_dict_returns_none():
    assert normalize_asset(None) is None
    assert normalize_asset("not a dict") is None
    assert normalize_asset(123) is None


def test_normalize_asset_missing_symbol_returns_none():
    assert normalize_asset({"price": 10, "change_pct": 1.0}) is None
    assert normalize_asset({"symbol": None, "price": 10}) is None
    assert normalize_asset({"symbol": "   ", "price": 10}) is None


def test_normalize_asset_coerces_non_numeric_to_none():
    asset = {"symbol": "X", "price": "abc", "change_pct": "n/a"}
    out = normalize_asset(asset)
    assert out["price"] is None
    assert out["change_pct"] is None


def test_normalize_asset_does_not_mutate_input():
    asset = {"symbol": "AAA", "price": 1, "change_pct": 1, "extra": "keep"}
    original = dict(asset)
    out = normalize_asset(asset)
    assert asset == original
    assert out is not asset
    assert out["extra"] == "keep"
    assert out["symbol"] == "AAA"


def test_normalize_asset_missing_optional_fields_default_none():
    asset = {"symbol": "AAA"}
    out = normalize_asset(asset)
    assert out["price"] is None
    assert out["change_pct"] is None
    assert out["volume"] is None
    assert out["btc_pair_change_pct"] is None
