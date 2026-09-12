"""Stage 7 (U07) Range Analysis dataclass."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from app.analysis.enums import (
    Direction,
    RangeConfidence,
    RangeType,
)


@dataclass
class RangeAnalysis:
    direction: Direction
    range_type: RangeType
    confidence: RangeConfidence
    confidence_score: float

    net_change_pct: float
    amplitude_pct: float
    path_length_pct: float
    switch_count: int
    close_dispersion_pct: float

    di_plus: Optional[float]
    di_minus: Optional[float]
    adx: Optional[float]

    ambiguous: bool
    reasons: List[str]
