"""Stage 7 (U07) movement metrics.

pct_change, range_amplitude_pct, normalized_path_length,
direction_switch_count, close_dispersion_pct.
"""
from __future__ import annotations

import math
from typing import Any, List


def _is_finite_number(x: Any) -> bool:
    try:
        return math.isfinite(float(x))
    except Exception:
        return False


def pct_change(start: float, end: float) -> float:
    if start == 0:
        raise ValueError(
            "Cannot calculate percentage change from zero."
        )
    return ((end - start) / start) * 100.0


def range_amplitude_pct(series: List[float]) -> float:
    """Peak-to-trough amplitude relative to the first observation."""
    start = float(series[0])
    highest = max(series)
    lowest = min(series)
    return ((highest - lowest) / start) * 100.0


def normalized_path_length(series: List[float]) -> float:
    """Measures total internal movement relative to starting value."""
    start = float(series[0])
    if start == 0:
        return 0.0
    total_abs_move = sum(
        abs(float(series[i]) - float(series[i - 1]))
        for i in range(1, len(series))
    )
    return (total_abs_move / start) * 100.0


def direction_switch_count(series: List[float]) -> int:
    signs = []
    for i in range(1, len(series)):
        delta = float(series[i]) - float(series[i - 1])
        if delta > 0:
            signs.append(1)
        elif delta < 0:
            signs.append(-1)
    if len(signs) < 2:
        return 0
    switches = 0
    for i in range(1, len(signs)):
        if signs[i] != signs[i - 1]:
            switches += 1
    return switches


def close_dispersion_pct(series: List[float]) -> float:
    mean_value = sum(series) / len(series)
    if mean_value == 0:
        return 0.0
    variance = sum(
        (x - mean_value) ** 2
        for x in series
    ) / len(series)
    std = math.sqrt(variance)
    return (std / mean_value) * 100.0