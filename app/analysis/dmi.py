"""Stage 7 (U07) Wilder-style DMI / ADX calculation.

DMI / ADX are SUPPORTING FEATURES ONLY.
They do not independently define Range.
If insufficient data exists, values remain None.
"""
from __future__ import annotations

from typing import Dict, List, Optional


def calculate_dmi_adx(
    highs: List[float],
    lows: List[float],
    closes: List[float],
    period: int = 14,
    adx_period: int = 14,
) -> Dict[str, Optional[float]]:
    if period <= 0:
        raise ValueError("period must be greater than zero.")
    if adx_period <= 0:
        raise ValueError("adx_period must be greater than zero.")
    if not (len(highs) == len(lows) == len(closes)):
        raise ValueError("highs, lows and closes must have equal lengths.")

    n = len(closes)
    if n < period + 1:
        return {"di_plus": None, "di_minus": None, "adx": None}

    tr: List[float] = []
    plus_dm: List[float] = []
    minus_dm: List[float] = []

    for i in range(1, n):
        high = float(highs[i])
        low = float(lows[i])
        prev_close = float(closes[i - 1])
        prev_high = float(highs[i - 1])
        prev_low = float(lows[i - 1])

        true_range = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close),
        )

        up_move = high - prev_high
        down_move = prev_low - low

        p_dm = (
            up_move
            if up_move > down_move and up_move > 0
            else 0.0
        )

        m_dm = (
            down_move
            if down_move > up_move and down_move > 0
            else 0.0
        )

        tr.append(true_range)
        plus_dm.append(p_dm)
        minus_dm.append(m_dm)

    if len(tr) < period:
        return {"di_plus": None, "di_minus": None, "adx": None}

    def wilder_smooth(
        values: List[float],
        p: int,
    ) -> List[float]:
        first = sum(values[:p])
        smoothed = [first]
        for value in values[p:]:
            previous = smoothed[-1]
            smoothed.append(
                previous
                - (previous / p)
                + value
            )
        return smoothed

    tr_s = wilder_smooth(tr, period)
    plus_s = wilder_smooth(plus_dm, period)
    minus_s = wilder_smooth(minus_dm, period)

    dx_values: List[float] = []
    di_plus_values: List[float] = []
    di_minus_values: List[float] = []

    for trv, pv, mv in zip(tr_s, plus_s, minus_s):
        if trv == 0:
            di_p = 0.0
            di_m = 0.0
        else:
            di_p = 100.0 * (pv / trv)
            di_m = 100.0 * (mv / trv)

        denominator = di_p + di_m
        if denominator == 0:
            dx = 0.0
        else:
            dx = (
                100.0
                * abs(di_p - di_m)
                / denominator
            )

        di_plus_values.append(di_p)
        di_minus_values.append(di_m)
        dx_values.append(dx)

    if not dx_values:
        return {"di_plus": None, "di_minus": None, "adx": None}

    if len(dx_values) < adx_period:
        adx = sum(dx_values) / len(dx_values)
    else:
        first_adx = (
            sum(dx_values[:adx_period])
            / adx_period
        )
        adx_series = [first_adx]
        for dx in dx_values[adx_period:]:
            previous = adx_series[-1]
            next_adx = (
                ((previous * (adx_period - 1)) + dx)
                / adx_period
            )
            adx_series.append(next_adx)
        adx = adx_series[-1]

    return {
        "di_plus": di_plus_values[-1],
        "di_minus": di_minus_values[-1],
        "adx": adx,
    }