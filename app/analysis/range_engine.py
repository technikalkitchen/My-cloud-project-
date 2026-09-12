"""Stage 7 (U07) Range Analysis engine.

analyze_range — core range analysis engine.
DMI / ADX are SUPPORTING FEATURES ONLY.
They do not independently define Range.
If insufficient data exists, values remain None.
"""
from __future__ import annotations

from typing import List, Optional

from app.analysis.enums import (
    Direction,
    RangeConfidence,
    RangeType,
)
from app.analysis.metrics import (
    close_dispersion_pct,
    direction_switch_count,
    pct_change,
    range_amplitude_pct,
    normalized_path_length,
)
from app.analysis.range_analysis import RangeAnalysis
from app.analysis.validation import (
    validate_ohlc_structure,
    validate_series,
)
from app.analysis.dmi import calculate_dmi_adx
from app.analysis.config import DEFAULT_RANGE_CONFIG, RangeConfig


def analyze_range(
    values: List[float],
    highs: Optional[List[float]] = None,
    lows: Optional[List[float]] = None,
    closes: Optional[List[float]] = None,
    config: RangeConfig = DEFAULT_RANGE_CONFIG,
) -> RangeAnalysis:

    validate_series(values, "values")

    values = [
        float(v)
        for v in values
    ]

    if closes is None:
        closes = values.copy()

    if highs is None:
        highs = values.copy()

    if lows is None:
        lows = values.copy()

    validate_series(highs, "highs")
    validate_series(lows, "lows")
    validate_series(closes, "closes")

    if not (
        len(values)
        == len(highs)
        == len(lows)
        == len(closes)
    ):
        raise ValueError(
            "values/highs/lows/closes must have equal lengths."
        )

    validate_ohlc_structure(
        highs,
        lows,
        closes,
        "RangeAnalysis",
    )

    start = values[0]
    end = values[-1]

    net_change = pct_change(
        start,
        end,
    )

    amplitude = range_amplitude_pct(
        values
    )

    path_length = normalized_path_length(
        values
    )

    switches = direction_switch_count(
        values
    )

    dispersion = close_dispersion_pct(
        values
    )

    dmi = calculate_dmi_adx(
        highs,
        lows,
        closes,
        period=config.dmi_period,
        adx_period=config.adx_period,
    )

    di_plus = dmi["di_plus"]
    di_minus = dmi["di_minus"]
    adx = dmi["adx"]

    # --------------------------------------------------------
    # ZERO-MOVEMENT EDGE CASE
    # --------------------------------------------------------

    zero_net = (
        abs(net_change)
        <= config.flat_threshold_pct
    )

    # --------------------------------------------------------
    # INTERNAL STRUCTURE FEATURES
    # --------------------------------------------------------

    internal_chop = False

    if len(values) >= 4:

        internal_chop = (
            switches >= 2
            and path_length > max(
                abs(net_change) * 1.5,
                config.flat_threshold_pct,
            )
        )

    dmi_balanced = None

    if (
        di_plus is not None
        and di_minus is not None
    ):

        dmi_balanced = (
            abs(di_plus - di_minus)
            <= config.dmi_balance_threshold
        )

    weak_adx = (
        adx is not None
        and adx < config.low_adx_threshold
    )

    strong_adx = (
        adx is not None
        and adx >= config.high_adx_threshold
    )

    # --------------------------------------------------------
    # RANGE SCORING
    # --------------------------------------------------------

    score_components = []

    # 1. Net movement
    if zero_net:

        score_components.append(1.0)

    elif abs(net_change) < config.direction_threshold_pct:

        score_components.append(0.80)

    else:

        score_components.append(0.0)

    # 2. Direction switching / internal back-and-forth
    if internal_chop:

        score_components.append(1.0)

    elif switches >= 1:

        score_components.append(0.65)

    else:

        score_components.append(0.20)

    # 3. DMI balance
    if dmi_balanced is True:

        score_components.append(1.0)

    elif dmi_balanced is False:

        score_components.append(0.0)

    else:

        score_components.append(0.50)

    # 4. ADX
    #
    # Low ADX strongly supports Range.
    # High ADX lowers confidence but does not invalidate Range.
    if weak_adx:

        score_components.append(1.0)

    elif strong_adx:

        score_components.append(0.35)

    elif adx is not None:

        score_components.append(0.65)

    else:

        score_components.append(0.50)

    # 5. Relative volatility / amplitude
    if amplitude <= config.low_volatility_pct:

        score_components.append(1.0)

    elif amplitude >= config.high_volatility_pct:

        score_components.append(0.45)

    else:

        score_components.append(0.70)

    range_score = (
        sum(score_components)
        / len(score_components)
    )

    # --------------------------------------------------------
    # DIRECTIONAL STRUCTURE
    # --------------------------------------------------------

    direction = None

    if net_change > config.direction_threshold_pct:

        direction = Direction.INCREASE

    elif net_change < -config.direction_threshold_pct:

        direction = Direction.DECREASE

    # --------------------------------------------------------
    # CONTRADICTION DETECTION
    # --------------------------------------------------------

    contradictory = False

    if direction is not None:

        if internal_chop and strong_adx:

            contradictory = True

        if (
            dmi_balanced is True
            and abs(net_change)
            < config.direction_threshold_pct * 2
        ):

            contradictory = True

    # --------------------------------------------------------
    # RANGE DECISION
    # --------------------------------------------------------

    range_candidate = (
        range_score >= config.range_score_threshold
        or zero_net
        or internal_chop
    )

    ambiguous = False
    reasons = []

    if contradictory:

        ambiguous = True

        reasons.append(
            "Directional movement and range-supporting structure "
            "produce conflicting evidence."
        )

    if strong_adx and internal_chop:

        reasons.append(
            "ADX is elevated while internal movement remains "
            "strongly back-and-forth."
        )

    if amplitude >= config.high_volatility_pct:

        reasons.append(
            "High internal volatility detected."
        )

    if zero_net:

        reasons.append(
            "Net Start→End movement is approximately zero; "
            "internal structure was evaluated."
        )

    # --------------------------------------------------------
    # FINAL CLASSIFICATION
    # --------------------------------------------------------

    if range_candidate:

        if amplitude >= config.high_volatility_pct:

            range_type = (
                RangeType.HIGH_VOLATILITY_RANGE
            )

        else:

            range_type = (
                RangeType.LOW_VOLATILITY_RANGE
            )

        if (
            ambiguous
            or range_score
            < config.medium_confidence_score
        ):

            confidence = RangeConfidence.LOW
            ambiguous = True

        elif range_score >= config.high_confidence_score:

            confidence = RangeConfidence.HIGH

        else:

            confidence = RangeConfidence.MEDIUM

        # If a strong directional move is unmistakable and
        # range evidence is insufficient, preserve direction.
        if (
            direction is not None
            and not zero_net
            and not internal_chop
            and range_score
            < config.range_score_threshold
        ):

            return RangeAnalysis(
                direction=direction,
                range_type=RangeType.NONE,
                confidence=RangeConfidence.LOW,
                confidence_score=range_score,
                net_change_pct=net_change,
                amplitude_pct=amplitude,
                path_length_pct=path_length,
                switch_count=switches,
                close_dispersion_pct=dispersion,
                di_plus=di_plus,
                di_minus=di_minus,
                adx=adx,
                ambiguous=False,
                reasons=reasons,
            )

        return RangeAnalysis(
            direction=Direction.RANGE,
            range_type=range_type,
            confidence=confidence,
            confidence_score=range_score,
            net_change_pct=net_change,
            amplitude_pct=amplitude,
            path_length_pct=path_length,
            switch_count=switches,
            close_dispersion_pct=dispersion,
            di_plus=di_plus,
            di_minus=di_minus,
            adx=adx,
            ambiguous=ambiguous,
            reasons=reasons,
        )

    if direction is None:

        return RangeAnalysis(
            direction=Direction.RANGE,
            range_type=RangeType.LOW_VOLATILITY_RANGE,
            confidence=RangeConfidence.LOW,
            confidence_score=range_score,
            net_change_pct=net_change,
            amplitude_pct=amplitude,
            path_length_pct=path_length,
            switch_count=switches,
            close_dispersion_pct=dispersion,
            di_plus=di_plus,
            di_minus=di_minus,
            adx=adx,
            ambiguous=True,
            reasons=[
                "Movement does not satisfy a sufficiently strong "
                "directional threshold."
            ],
        )

    return RangeAnalysis(
        direction=direction,
        range_type=RangeType.NONE,
        confidence=RangeConfidence.LOW,
        confidence_score=range_score,
        net_change_pct=net_change,
        amplitude_pct=amplitude,
        path_length_pct=path_length,
        switch_count=switches,
        close_dispersion_pct=dispersion,
        di_plus=di_plus,
        di_minus=di_minus,
        adx=adx,
        ambiguous=False,
        reasons=reasons,
    )
