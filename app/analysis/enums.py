"""Stage 7 (U07) enums.

Direction, RangeType, RangeConfidence, ScenarioType.

Direction is shared across stages (Stage 7 and Stage 8 both use the
INCREASE / DECREASE / RANGE triad). Stage 8 additionally contributes the
Context and RelativeDirection enums below.
"""
from __future__ import annotations

from enum import Enum


class Direction(str, Enum):
    INCREASE = "INCREASE"
    DECREASE = "DECREASE"
    RANGE = "RANGE"


class RangeType(str, Enum):
    LOW_VOLATILITY_RANGE = "LOW-VOLATILITY RANGE"
    HIGH_VOLATILITY_RANGE = "HIGH-VOLATILITY RANGE"
    NONE = "NONE"


class RangeConfidence(str, Enum):
    HIGH = "HIGH CONFIDENCE RANGE"
    MEDIUM = "MEDIUM CONFIDENCE RANGE"
    LOW = "LOW CONFIDENCE / AMBIGUOUS"


class ScenarioType(str, Enum):
    MIRROR = "MIRROR"
    PARALLEL = "PARALLEL"
    RANGE_COMPATIBLE_STATE = "RANGE-COMPATIBLE STATE"
    NEUTRAL_FLAT = "NEUTRAL / FLAT"


class Context(str, Enum):
    """Market context used by Stage 8 (Cell 8).

    Driven by BTC direction only (BTC.UP -> BULLISH, BTC.DOWN -> BEARISH,
    otherwise RANGE). The BTC.D direction does NOT alter context.
    """

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    RANGE = "RANGE"


class RelativeDirection(str, Enum):
    """Relative movement of an asset vs BTC (Stage 8 / Cell 8)."""

    RELATIVE_STRENGTH = "RELATIVE_STRENGTH"
    RELATIVE_WEAKNESS = "RELATIVE_WEAKNESS"
    RELATIVE_NEUTRAL = "RELATIVE_NEUTRAL"