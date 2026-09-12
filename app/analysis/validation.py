"""Stage 7 (U07) input validation.

validate_series, validate_ohlc_structure, validate_user_range.
USER RANGE IS AUTHORITATIVE — the engine never changes it and never
silently replaces it.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List

from app.analysis.metrics import _is_finite_number


def validate_series(series: List[float], name: str) -> None:
    if not isinstance(series, list):
        raise TypeError(f"{name} must be a list.")
    if len(series) < 2:
        raise ValueError(f"{name} requires at least 2 observations.")
    for value in series:
        if not _is_finite_number(value):
            raise ValueError(f"{name} contains a non-finite value.")
    if any(float(v) <= 0 for v in series):
        raise ValueError(f"{name} must contain positive values.")


def validate_ohlc_structure(
    highs: List[float],
    lows: List[float],
    closes: List[float],
    name: str,
) -> None:
    """Validate basic OHLC structural consistency.

    Rules:
        high >= low
        low <= close <= high
    """
    if not (len(highs) == len(lows) == len(closes)):
        raise ValueError(
            f"{name}: highs, lows and closes must have equal lengths."
        )
    for i, (high, low, close) in enumerate(zip(highs, lows, closes)):
        high = float(high)
        low = float(low)
        close = float(close)
        if high < low:
            raise ValueError(f"{name}: high < low at index {i}.")
        if close < low or close > high:
            raise ValueError(
                f"{name}: close outside high/low range at index {i}."
            )


def validate_user_range(analysis_range: Any) -> Dict[str, Any]:
    """USER RANGE IS AUTHORITATIVE.

    The engine never changes it and never silently replaces it.
    """
    if analysis_range is None:
        raise ValueError("analysis_range is required.")

    if isinstance(analysis_range, dict):
        if "start" not in analysis_range or "end" not in analysis_range:
            raise ValueError(
                "analysis_range dict must contain start and end."
            )
        start = analysis_range["start"]
        end = analysis_range["end"]
        if start is None or end is None:
            raise ValueError("analysis_range start/end cannot be None.")
        return {
            "start": start,
            "end": end,
            "custom": bool(analysis_range.get("custom", True)),
            "label": analysis_range.get("label"),
        }

    if isinstance(analysis_range, (tuple, list)):
        if len(analysis_range) != 2:
            raise ValueError(
                "analysis_range sequence must contain exactly 2 values."
            )
        return {
            "start": analysis_range[0],
            "end": analysis_range[1],
            "custom": True,
            "label": None,
        }

    raise TypeError("analysis_range must be a dict, tuple, or list.")