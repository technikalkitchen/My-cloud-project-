"""Stage 8 (U08) normalization helpers — Cell 8.

Safe numeric coercion + alias-aware direction normalization, mirroring
Notebook Cell 8 (``_safe_float``, ``_safe_pct_change``, ``_normalize_direction``,
``normalize_asset``).

These helpers are Cell-8-specific and intentionally local to Stage 8:
``_safe_float`` returns ``Optional[float]`` (Cell 8 semantics), which differs
from Stage 7's ``metrics._is_finite_number`` (returns ``bool``).
"""
from __future__ import annotations

import math
from typing import Any, Dict, Optional

from app.analysis.enums import Direction


def _finite(value: Any) -> bool:
    """Return True iff ``value`` coerces to a finite float."""

    try:
        value = float(value)
    except (TypeError, ValueError):
        return False

    return math.isfinite(value)


def _safe_float(value: Any) -> Optional[float]:
    """Coerce to float; return None for None, non-numeric, inf/nan."""

    if value is None:
        return None

    try:
        value = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(value):
        return None

    return value


def _safe_pct_change(start: Any, end: Any) -> Optional[float]:
    """Percentage change from start to end, or None if not computable."""

    start = _safe_float(start)
    end = _safe_float(end)

    if start is None or end is None:
        return None

    if start == 0:
        return None

    return ((end - start) / start) * 100.0


_DIRECTION_ALIASES = {
    "INCREASE": Direction.INCREASE,
    "UP": Direction.INCREASE,
    "BULLISH": Direction.INCREASE,
    "RISING": Direction.INCREASE,

    "DECREASE": Direction.DECREASE,
    "DOWN": Direction.DECREASE,
    "BEARISH": Direction.DECREASE,
    "FALLING": Direction.DECREASE,

    "RANGE": Direction.RANGE,
    "FLAT": Direction.RANGE,
    "SIDEWAYS": Direction.RANGE,
}


def _normalize_direction(direction: Any) -> Direction:
    """Convert a colloquial direction token into a Direction enum.

    Accepts Direction enums (passthrough) or strings such as ``"up"``,
    ``"bearish"``, ``"flat"`` (case-insensitive, whitespace-trimmed).
    Raises ValueError for unrecognized tokens.
    """

    if isinstance(direction, Direction):
        return direction

    value = str(direction).upper().strip()

    if value not in _DIRECTION_ALIASES:
        raise ValueError(f"Unsupported direction: {direction}")

    return _DIRECTION_ALIASES[value]


_CHANGE_PCT_ALIASES = ("change_pct", "pct_change", "percent_change")
_BTC_PAIR_CHANGE_PCT_ALIASES = ("btc_pair_change_pct", "btc_pair_pct_change")


def normalize_asset(asset: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Return a normalized copy of an asset dict.

    - ``symbol`` from ``symbol`` or ``asset``
    - ``price``, ``change_pct``, ``volume``, ``btc_pair_change_pct`` via
      ``_safe_float`` with alias fallbacks
    - Returns ``None`` for non-dict input, missing symbol, or empty symbol.
    - Does NOT mutate the input (returns ``dict(asset)`` copy).
    """

    if not isinstance(asset, dict):
        return None

    symbol = asset.get("symbol", asset.get("asset"))
    if symbol is None:
        return None

    symbol = str(symbol).strip()
    if not symbol:
        return None

    price = _safe_float(asset.get("price"))

    change_pct = _safe_float(_first_alias(asset, _CHANGE_PCT_ALIASES))

    volume = _safe_float(asset.get("volume"))

    btc_pair_change_pct = _safe_float(
        _first_alias(asset, _BTC_PAIR_CHANGE_PCT_ALIASES)
    )

    result = dict(asset)
    result["symbol"] = symbol
    result["price"] = price
    result["change_pct"] = change_pct
    result["volume"] = volume
    result["btc_pair_change_pct"] = btc_pair_change_pct

    return result


def _first_alias(asset: Dict[str, Any], aliases: tuple) -> Any:
    """Return the first present value among an ordered alias list."""

    for key in aliases:
        if key in asset:
            return asset[key]
    return None
