"""Stage 7 (U07) enums.

Direction, RangeType, RangeConfidence, ScenarioType.
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