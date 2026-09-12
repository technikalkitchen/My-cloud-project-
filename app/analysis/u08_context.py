"""Stage 8 (U08) BTC/BTC.D context classification."""
from __future__ import annotations

from typing import Any

from app.analysis.enums import Context, Direction
from app.analysis.u08_normalize import _normalize_direction


def classify_context(
    btc_direction: Any,
    btc_d_direction: Any,
) -> Context:
    """Classify market context from BTC direction only."""

    btc_direction = _normalize_direction(btc_direction)
    _normalize_direction(btc_d_direction)

    if btc_direction == Direction.INCREASE:
        return Context.BULLISH

    if btc_direction == Direction.DECREASE:
        return Context.BEARISH

    return Context.RANGE
