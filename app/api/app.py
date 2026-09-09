from flask import Flask, jsonify
from datetime import datetime

from app.core.version import (
    PROJECT_NAME,
    PROJECT_VERSION,
    EXECUTION_UNIT,
)


# ============================================================
# TIMEFRAME / RANGE VALIDATION
# ============================================================

STANDARD_TIMEFRAMES = {
    "M1": 60,
    "M5": 5 * 60,
    "M15": 15 * 60,
    "H1": 60 * 60,
    "H4": 4 * 60 * 60,
    "D1": 24 * 60 * 60,
    "D7": 7 * 24 * 60 * 60,
}


SUB_DAILY_WARNING = (
    "⚠️ WARNING: The selected timeframe/range is below daily (D1). "
    "Sub-daily data may contain higher noise and lower structural "
    "reliability. Structural market interpretation should be treated "
    "with caution and confirmed with daily (D1) or higher data."
)


def _parse_custom_range(value: str):
    """
    Parse the canonical Custom Range format:

        DD-MM-YYYY HH:MM

    Returns a datetime object or None.
    """

    try:
        return datetime.strptime(
            value.strip(),
            "%d-%m-%Y %H:%M",
        )
    except (TypeError, ValueError):
        return None


def validate_timeframe_guard(
    timeframe: str,
    custom_start: str = None,
    custom_end: str = None,
) -> dict:
    """
    Technical timeframe/range validation boundary.

    This function does NOT perform market analysis.

    Rules:
    1. Every recognized standard timeframe below D1 is VALID
       but receives a WARNING.
    2. D1 and higher are VALID without the sub-daily warning.
    3. Custom Range is supported using:
           DD-MM-YYYY HH:MM
       If the selected range is below 24 hours, it is VALID
       but receives the same sub-daily WARNING.
    4. A Custom Range of 24 hours or more is VALID without
       the sub-daily warning.
    5. Invalid or incomplete timeframe/range input remains INVALID.
    6. No specific hardcoded list of low timeframes is used
       to determine the warning.
    """

    if not isinstance(timeframe, str):
        return {
            "valid": False,
            "warning": None,
            "reason": "INVALID_TIMEFRAME_TYPE",
            "is_sub_daily": False,
        }

    normalized = timeframe.strip().upper()

    # --------------------------------------------------------
    # Standard Timeframe
    # --------------------------------------------------------

    if normalized in STANDARD_TIMEFRAMES:

        duration_seconds = STANDARD_TIMEFRAMES[
            normalized
        ]

        is_sub_daily = (
            duration_seconds < 24 * 60 * 60
        )

        if is_sub_daily:

            return {
                "valid": True,
                "warning": SUB_DAILY_WARNING,
                "reason": "SUB_DAILY_TIMEFRAME",
                "is_sub_daily": True,
            }

        return {
            "valid": True,
            "warning": None,
            "reason": "DAILY_OR_HIGHER",
            "is_sub_daily": False,
        }

    # --------------------------------------------------------
    # Custom Range
    # --------------------------------------------------------

    if normalized in {
        "CUSTOM",
        "CUSTOM_RANGE",
        "CUSTOM RANGE",
    }:

        if not custom_start or not custom_end:

            return {
                "valid": False,
                "warning": None,
                "reason": "CUSTOM_RANGE_ENDPOINTS_REQUIRED",
                "is_sub_daily": False,
            }

        start = _parse_custom_range(
            custom_start
        )

        end = _parse_custom_range(
            custom_end
        )

        if start is None or end is None:

            return {
                "valid": False,
                "warning": None,
                "reason": "INVALID_CUSTOM_RANGE_FORMAT",
                "is_sub_daily": False,
            }

        if end <= start:

            return {
                "valid": False,
                "warning": None,
                "reason": "INVALID_CUSTOM_RANGE_ORDER",
                "is_sub_daily": False,
            }

        duration_seconds = (
            end - start
        ).total_seconds()

        is_sub_daily = (
            duration_seconds < 24 * 60 * 60
        )

        if is_sub_daily:

            return {
                "valid": True,
                "warning": SUB_DAILY_WARNING,
                "reason": "SUB_DAILY_CUSTOM_RANGE",
                "is_sub_daily": True,
                "duration_seconds": duration_seconds,
            }

        return {
            "valid": True,
            "warning": None,
            "reason": "DAILY_OR_HIGHER_CUSTOM_RANGE",
            "is_sub_daily": False,
            "duration_seconds": duration_seconds,
        }

    # --------------------------------------------------------
    # Invalid / unsupported timeframe
    # --------------------------------------------------------

    return {
        "valid": False,
        "warning": None,
        "reason": "UNSUPPORTED_TIMEFRAME",
        "is_sub_daily": False,
    }


def create_app():

    app = Flask(__name__)

    @app.get("/health")
    def health():

        return jsonify({
            "status": "ok",
            "project": PROJECT_NAME,
            "version": PROJECT_VERSION,
            "execution_unit": EXECUTION_UNIT,
        })

    @app.get("/")
    def root():

        return jsonify({
            "service": PROJECT_NAME,
            "version": PROJECT_VERSION,
            "status": "running",
        })

    return app


app = create_app()
