"""Stage 7 (U07) configuration.

Configurable engineering parameters. These are NOT presented as universal
market truths.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RangeConfig:
    # Minimum absolute net movement to classify a directional move.
    direction_threshold_pct: float = 0.50

    # Maximum net movement for the zero/flat edge case.
    flat_threshold_pct: float = 0.10

    # Relative amplitude threshold separating lower/higher
    # volatility structures.
    low_volatility_pct: float = 2.00

    # Minimum range score required before RANGE can be considered.
    range_score_threshold: float = 0.60

    # High-volatility range threshold.
    high_volatility_pct: float = 5.00

    # DMI/ADX parameters.
    dmi_period: int = 14
    adx_period: int = 14

    # Difference between DI+ and DI- considered "close".
    dmi_balance_threshold: float = 5.0

    # ADX below this level is supportive of weak trend.
    low_adx_threshold: float = 20.0

    # ADX above this level means strong movement, but DOES NOT
    # automatically invalidate Range.
    high_adx_threshold: float = 35.0

    # Minimum confidence score for high confidence.
    high_confidence_score: float = 0.78

    # Minimum confidence score for medium confidence.
    medium_confidence_score: float = 0.62


DEFAULT_RANGE_CONFIG = RangeConfig()