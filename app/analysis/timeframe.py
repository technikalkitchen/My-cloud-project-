"""Stage 7 (U07) timeframe engine.

Critical rules:
    minute  -> lowercase m
    hour    -> h / H
    day     -> d / D
    week    -> w / W
    month   -> uppercase M

ANY valid timeframe below 1D = VALID + SUB_DAILY_WARNING
1D, 1W and 1M = VALID + NO WARNING

IMPORTANT:
Uppercase M is intentionally preserved as MONTH.
It must NEVER be converted to lowercase before interpretation.
"""
from __future__ import annotations

import re
from typing import Any, Dict

_TIMEFRAME_RE = re.compile(
    r"^\s*(\d+(?:\.\d+)?)\s*([mMhHdDwW])\s*$"
)


def parse_timeframe(timeframe: str) -> Dict[str, Any]:
    if not isinstance(timeframe, str):
        return {
            "valid": False,
            "warning": None,
            "error": "TECHNICAL_VALIDATION_ERROR",
            "normalized": None,
            "minutes": None,
        }

    match = _TIMEFRAME_RE.match(timeframe)
    if not match:
        return {
            "valid": False,
            "warning": None,
            "error": "TECHNICAL_VALIDATION_ERROR",
            "normalized": None,
            "minutes": None,
        }

    amount = float(match.group(1))
    raw_unit = match.group(2)

    if amount <= 0:
        return {
            "valid": False,
            "warning": None,
            "error": "TECHNICAL_VALIDATION_ERROR",
            "normalized": None,
            "minutes": None,
        }

    # IMPORTANT:
    # Do NOT lowercase before checking for uppercase M.
    if raw_unit == "M":
        unit = "M"
    else:
        unit = raw_unit.lower()

    multipliers = {
        "m": 1,
        "h": 60,
        "d": 1440,
        "w": 10080,
        "M": 43200,   # engineering representation: 30 days
    }

    minutes = amount * multipliers[unit]

    normalized = (
        f"{int(amount) if amount.is_integer() else amount:g}{unit}"
    )

    if minutes < 1440:
        return {
            "valid": True,
            "warning": "SUB_DAILY_WARNING",
            "error": None,
            "normalized": normalized,
            "minutes": minutes,
        }

    return {
        "valid": True,
        "warning": None,
        "error": None,
        "normalized": normalized,
        "minutes": minutes,
    }