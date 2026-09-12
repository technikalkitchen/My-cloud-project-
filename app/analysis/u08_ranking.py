"""Stage 8 (U08) Cell 8 ranking helpers."""
from __future__ import annotations

from typing import Any, Dict, List

from app.analysis.enums import Context, Direction
from app.analysis.u08_normalize import _safe_float


def rank_strong_movers(
    assets: List[Dict[str, Any]],
    market_context: Context,
    n: int,
) -> List[Dict[str, Any]]:
    """Rank assets by absolute price movement for the market context."""

    valid_assets = [
        asset
        for asset in assets
        if _safe_float(asset.get("change_pct")) is not None
    ]

    if market_context == Context.BULLISH:
        ranked = sorted(
            valid_assets,
            key=lambda asset: _safe_float(asset.get("change_pct")),
            reverse=True,
        )
    elif market_context == Context.BEARISH:
        ranked = sorted(
            valid_assets,
            key=lambda asset: _safe_float(asset.get("change_pct")),
        )
    else:
        ranked = sorted(
            valid_assets,
            key=lambda asset: abs(
                _safe_float(asset.get("change_pct"))
            ),
            reverse=True,
        )

    return ranked[:n]


def rank_relative_movers(
    assets: List[Dict[str, Any]],
    market_context: Context,
    n: int,
) -> List[Dict[str, Any]]:
    """Rank assets by their relative performance versus BTC."""

    valid = [
        asset
        for asset in assets
        if _safe_float(
            asset.get("relative_btc_performance_pct")
        ) is not None
    ]

    if market_context == Context.BEARISH:
        ranked = sorted(
            valid,
            key=lambda asset: _safe_float(
                asset.get("relative_btc_performance_pct")
            ),
        )
    else:
        ranked = sorted(
            valid,
            key=lambda asset: _safe_float(
                asset.get("relative_btc_performance_pct")
            ),
            reverse=True,
        )

    return ranked[:n]


def rank_top_assets(
    assets: List[Dict[str, Any]],
    market_context: Context,
    n: int = 10,
) -> List[Dict[str, Any]]:
    """Rank assets by movement and USDT-pair volume."""

    valid = []

    for asset in assets:
        change = _safe_float(asset.get("change_pct"))
        volume = _safe_float(asset.get("volume"))

        if change is None:
            continue

        if volume is None:
            volume = 0.0

        asset = dict(asset)
        asset["volume"] = volume
        valid.append(asset)

    if market_context == Context.BULLISH:
        valid.sort(
            key=lambda asset: (
                _safe_float(asset.get("change_pct")),
                _safe_float(asset.get("volume")),
            ),
            reverse=True,
        )
    elif market_context == Context.BEARISH:
        valid.sort(
            key=lambda asset: (
                _safe_float(asset.get("change_pct")),
                _safe_float(asset.get("volume")),
            ),
        )
    else:
        valid.sort(
            key=lambda asset: (
                abs(_safe_float(asset.get("change_pct"))),
                _safe_float(asset.get("volume")),
            ),
            reverse=True,
        )

    return valid[:n]


def is_opposite_direction(
    btc_direction: Direction,
    btc_d_direction: Direction,
) -> bool:
    """Return whether BTC and BTC.D move in opposite directions."""

    return (
        (
            btc_direction == Direction.INCREASE
            and btc_d_direction == Direction.DECREASE
        )
        or (
            btc_direction == Direction.DECREASE
            and btc_d_direction == Direction.INCREASE
        )
    )


def add_absolute_direction(
    assets: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Add an absolute movement label to each asset copy."""

    output = []

    for asset in assets:
        asset = dict(asset)
        change = _safe_float(asset.get("change_pct"))

        if change is None:
            asset["direction"] = "UNKNOWN"
        elif change > 0:
            asset["direction"] = "INCREASE"
        elif change < 0:
            asset["direction"] = "DECREASE"
        else:
            asset["direction"] = "RANGE"

        output.append(asset)

    return output
