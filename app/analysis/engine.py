"""Stage 7 (U07) Scenario Engine.

ScenarioResult dataclass + run_u07 main engine entry point.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.analysis.config import DEFAULT_RANGE_CONFIG, RangeConfig
from app.analysis.enums import (
    Direction,
    RangeConfidence,
)
from app.analysis.matrix import SCENARIO_MATRIX
from app.analysis.narratives import NARRATIVES
from app.analysis.range_engine import analyze_range
from app.analysis.timeframe import parse_timeframe
from app.analysis.validation import (
    validate_series,
    validate_user_range,
)


@dataclass
class ScenarioResult:
    scenario_id: int
    scenario_type: str

    total_classification: str
    usdt_d_classification: str

    selected_pattern: str
    pattern_index: int

    timeframe: str
    timeframe_valid: bool
    timeframe_warning: Optional[str]

    analysis_range: Dict[str, Any]

    total_range_type: str
    total_range_confidence: str
    total_range_score: float

    usdt_range_type: str
    usdt_range_confidence: str
    usdt_range_score: float

    audit: Dict[str, Any]


def run_u07(
    total_values: List[float],
    usdt_values: List[float],
    timeframe: str,
    analysis_range: Any,
    *,
    total_highs: Optional[List[float]] = None,
    total_lows: Optional[List[float]] = None,
    total_closes: Optional[List[float]] = None,
    usdt_highs: Optional[List[float]] = None,
    usdt_lows: Optional[List[float]] = None,
    usdt_closes: Optional[List[float]] = None,
    pattern_index: int = 1,
    config: RangeConfig = DEFAULT_RANGE_CONFIG,
) -> ScenarioResult:

    # --------------------------------------------------------
    # USER RANGE IS AUTHORITATIVE
    # --------------------------------------------------------

    validated_range = validate_user_range(
        analysis_range
    )

    # --------------------------------------------------------
    # TIMEFRAME VALIDATION
    # --------------------------------------------------------

    timeframe_result = parse_timeframe(
        timeframe
    )

    if not timeframe_result["valid"]:

        raise ValueError(
            "TECHNICAL_VALIDATION_ERROR: "
            "Unsupported or malformed timeframe."
        )

    # --------------------------------------------------------
    # UPSTREAM DATA VALIDATION
    # --------------------------------------------------------

    validate_series(
        total_values,
        "TOTAL",
    )

    validate_series(
        usdt_values,
        "USDT.D",
    )

    # --------------------------------------------------------
    # RANGE ANALYSIS
    # --------------------------------------------------------

    total_analysis = analyze_range(
        total_values,
        highs=total_highs,
        lows=total_lows,
        closes=total_closes,
        config=config,
    )

    usdt_analysis = analyze_range(
        usdt_values,
        highs=usdt_highs,
        lows=usdt_lows,
        closes=usdt_closes,
        config=config,
    )

    # --------------------------------------------------------
    # AMBIGUITY SAFETY
    #
    # No forced direction is created from ambiguous Range data.
    # --------------------------------------------------------

    if (
        total_analysis.ambiguous
        and total_analysis.direction == Direction.RANGE
        and total_analysis.confidence == RangeConfidence.LOW
    ):
        pass

    if (
        usdt_analysis.ambiguous
        and usdt_analysis.direction == Direction.RANGE
        and usdt_analysis.confidence == RangeConfidence.LOW
    ):
        pass

    # --------------------------------------------------------
    # EXACT 9-SCENARIO MAPPING
    # --------------------------------------------------------

    pair = (
        total_analysis.direction,
        usdt_analysis.direction,
    )

    if pair not in SCENARIO_MATRIX:

        raise RuntimeError(
            "No canonical U07 scenario mapping exists for this pair."
        )

    mapping = SCENARIO_MATRIX[pair]

    scenario_id = mapping["scenario_id"]

    scenario_type = (
        mapping["scenario_type"].value
    )

    # --------------------------------------------------------
    # NARRATIVE SELECTION
    # --------------------------------------------------------

    if pattern_index not in (1, 2, 3):

        raise ValueError(
            "pattern_index must be 1, 2, or 3."
        )

    approved_patterns = NARRATIVES[
        scenario_id
    ]

    selected_pattern = approved_patterns[
        pattern_index - 1
    ]

    # --------------------------------------------------------
    # AUDIT
    # --------------------------------------------------------

    audit = {

        "engine": "U07",

        "engine_version": "V3.1",

        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),

        "user_range_authoritative": True,

        "analysis_range": validated_range,

        "timeframe_validation": timeframe_result,

        "total": {

            "classification":
                total_analysis.direction.value,

            "range_type":
                total_analysis.range_type.value,

            "confidence":
                total_analysis.confidence.value,

            "score":
                total_analysis.confidence_score,

            "net_change_pct":
                total_analysis.net_change_pct,

            "amplitude_pct":
                total_analysis.amplitude_pct,

            "path_length_pct":
                total_analysis.path_length_pct,

            "switch_count":
                total_analysis.switch_count,

            "close_dispersion_pct":
                total_analysis.close_dispersion_pct,

            "di_plus":
                total_analysis.di_plus,

            "di_minus":
                total_analysis.di_minus,

            "adx":
                total_analysis.adx,

            "ambiguous":
                total_analysis.ambiguous,

            "reasons":
                total_analysis.reasons,
        },

        "usdt_d": {

            "classification":
                usdt_analysis.direction.value,

            "range_type":
                usdt_analysis.range_type.value,

            "confidence":
                usdt_analysis.confidence.value,

            "score":
                usdt_analysis.confidence_score,

            "net_change_pct":
                usdt_analysis.net_change_pct,

            "amplitude_pct":
                usdt_analysis.amplitude_pct,

            "path_length_pct":
                usdt_analysis.path_length_pct,

            "switch_count":
                usdt_analysis.switch_count,

            "close_dispersion_pct":
                usdt_analysis.close_dispersion_pct,

            "di_plus":
                usdt_analysis.di_plus,

            "di_minus":
                usdt_analysis.di_minus,

            "adx":
                usdt_analysis.adx,

            "ambiguous":
                usdt_analysis.ambiguous,

            "reasons":
                usdt_analysis.reasons,
        },

        "scenario": {

            "scenario_id":
                scenario_id,

            "scenario_type":
                scenario_type,

            "total":
                total_analysis.direction.value,

            "usdt_d":
                usdt_analysis.direction.value,
        },

        "approved_narrative": {

            "pattern_index":
                pattern_index,

            "total_patterns_available":
                3,
        },

        "execution_locks": {

            "trading": False,

            "orders": False,

            "strategy": False,

            "portfolio_actions": False,
        },
    }

    return ScenarioResult(

        scenario_id=scenario_id,

        scenario_type=scenario_type,

        total_classification=
            total_analysis.direction.value,

        usdt_d_classification=
            usdt_analysis.direction.value,

        selected_pattern=
            selected_pattern,

        pattern_index=
            pattern_index,

        timeframe=
            timeframe_result["normalized"],

        timeframe_valid=
            timeframe_result["valid"],

        timeframe_warning=
            timeframe_result["warning"],

        analysis_range=
            validated_range,

        total_range_type=
            total_analysis.range_type.value,

        total_range_confidence=
            total_analysis.confidence.value,

        total_range_score=
            total_analysis.confidence_score,

        usdt_range_type=
            usdt_analysis.range_type.value,

        usdt_range_confidence=
            usdt_analysis.confidence.value,

        usdt_range_score=
            usdt_analysis.confidence_score,

        audit=audit,
    )


# ---------------------------------------------------------------------------
# Unit 7.5 — Integrated Stage 7 pipeline
# ---------------------------------------------------------------------------

def run_stage7(
    adapter: Dict[str, Any],
    pattern_index: int = 1,
    *,
    max_freshness_age_seconds: Optional[float] = None,
    config: RangeConfig = DEFAULT_RANGE_CONFIG,
) -> ScenarioResult:
    """Integrated Stage 7 pipeline.

    Consumes the frozen U06.5 U07 adapter through Units 7.1-7.4 in order:
      7.1 input contract  -> 7.2 calculations -> 7.3 scenario matrix
      -> 7.4 narratives -> ScenarioResult.
    """
    from app.analysis.calculations import calculate_stage7
    from app.analysis.input_contract import validate_stage7_input
    from app.analysis.matrix import lookup_scenario
    from app.analysis.narratives import select_narrative

    contract = validate_stage7_input(
        adapter,
        max_freshness_age_seconds=max_freshness_age_seconds,
    )

    calc = calculate_stage7(contract)

    total_values = contract.total_series
    usdt_values = contract.usdt_d_series

    def _derive_ohlc(values):
        if len(values) < 3:
            return values, values, values
        highs = [
            max(values[i], values[i + 1])
            for i in range(len(values) - 1)
        ]
        lows = [
            min(values[i], values[i + 1])
            for i in range(len(values) - 1)
        ]
        closes = values[1:]
        return highs, lows, closes

    total_highs, total_lows, total_closes = _derive_ohlc(total_values)
    usdt_highs, usdt_lows, usdt_closes = _derive_ohlc(usdt_values)

    total_analysis = analyze_range(
        total_values,
        highs=total_highs,
        lows=total_lows,
        closes=total_closes,
        config=config,
    )

    usdt_analysis = analyze_range(
        usdt_values,
        highs=usdt_highs,
        lows=usdt_lows,
        closes=usdt_closes,
        config=config,
    )

    scenario = lookup_scenario(
        total_analysis.direction,
        usdt_analysis.direction,
    )

    selected_pattern = select_narrative(
        scenario["scenario_id"],
        pattern_index,
    )

    timeframe_result = parse_timeframe(contract.timeframe)
    if not timeframe_result["valid"]:
        raise ValueError(
            "TECHNICAL_VALIDATION_ERROR: "
            "Unsupported or malformed timeframe."
        )

    audit = {
        "engine": "U07",
        "engine_version": "V3.1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "pipeline": "U07.1->U07.2->U07.3->U07.4",
        "input_contract": contract.validation,
        "calculations": {
            "total_net_change_pct": calc.total_net_change_pct,
            "usdt_d_net_change_pct": calc.usdt_d_net_change_pct,
            "usdt_d_net_change_pp": calc.usdt_d_net_change_pp,
            "total_amplitude_pct": calc.total_amplitude_pct,
            "usdt_d_amplitude_pct": calc.usdt_d_amplitude_pct,
        },
        "scenario": scenario,
        "approved_narrative": {
            "pattern_index": pattern_index,
            "total_patterns_available": 3,
        },
        "execution_locks": {
            "trading": False,
            "orders": False,
            "strategy": False,
            "portfolio_actions": False,
        },
    }

    return ScenarioResult(
        scenario_id=scenario["scenario_id"],
        scenario_type=scenario["scenario_type"],
        total_classification=total_analysis.direction.value,
        usdt_d_classification=usdt_analysis.direction.value,
        selected_pattern=selected_pattern,
        pattern_index=pattern_index,
        timeframe=timeframe_result["normalized"],
        timeframe_valid=timeframe_result["valid"],
        timeframe_warning=timeframe_result["warning"],
        analysis_range=contract.analysis_range,
        total_range_type=total_analysis.range_type.value,
        total_range_confidence=total_analysis.confidence.value,
        total_range_score=total_analysis.confidence_score,
        usdt_range_type=usdt_analysis.range_type.value,
        usdt_range_confidence=usdt_analysis.confidence.value,
        usdt_range_score=usdt_analysis.confidence_score,
        audit=audit,
    )
