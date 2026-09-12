"""Stage 8 (U08) relative performance versus BTC."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.analysis.enums import RelativeDirection
from app.analysis.u08_config import CELL08_CONFIG
from app.analysis.u08_normalize import _safe_float, normalize_asset


def calculate_relative_btc_performance(
    asset_change_pct: Any,
    btc_change_pct: Any,
) -> Optional[float]:
    """Return asset percentage change minus BTC percentage change."""

    asset_change_pct = _safe_float(asset_change_pct)
    btc_change_pct = _safe_float(btc_change_pct)

    if asset_change_pct is None or btc_change_pct is None:
        return None

    return asset_change_pct - btc_change_pct


def classify_relative_performance(
    asset_change_pct: Any,
    btc_change_pct: Any,
    epsilon_pct: float = 0.0,
) -> RelativeDirection:
    """Classify relative movement using an epsilon neutral band."""

    relative = calculate_relative_btc_performance(
        asset_change_pct,
        btc_change_pct,
    )

    if relative is None:
        return RelativeDirection.RELATIVE_NEUTRAL

    if relative > epsilon_pct:
        return RelativeDirection.RELATIVE_STRENGTH

    if relative < -epsilon_pct:
        return RelativeDirection.RELATIVE_WEAKNESS

    return RelativeDirection.RELATIVE_NEUTRAL


def enrich_relative_performance(
    assets: List[Dict[str, Any]],
    btc_change_pct: Optional[float],
) -> List[Dict[str, Any]]:
    """Add relative BTC performance fields to each valid asset."""

    output: List[Dict[str, Any]] = []

    for raw_asset in assets:
        asset = normalize_asset(raw_asset)
        if asset is None:
            continue

        asset_change = asset.get("change_pct")
        relative_change = calculate_relative_btc_performance(
            asset_change,
            btc_change_pct,
        )
        relative_direction = classify_relative_performance(
            asset_change,
            btc_change_pct,
            CELL08_CONFIG.relative_strength_epsilon_pct,
        )

        asset["relative_btc_performance_pct"] = relative_change
        asset["relative_direction"] = relative_direction.value
        output.append(asset)

    return output


def relative_performance_self_tests() -> Dict[str, Any]:
    """Run deterministic checks for relative BTC performance."""

    tests = {
        "difference": calculate_relative_btc_performance(-1.0, -3.0) == 2.0,
        "strength": (
            classify_relative_performance(-1.0, -3.0)
            == RelativeDirection.RELATIVE_STRENGTH
        ),
        "weakness": (
            classify_relative_performance(1.0, 3.0)
            == RelativeDirection.RELATIVE_WEAKNESS
        ),
        "neutral": (
            classify_relative_performance(1.0, 1.0)
            == RelativeDirection.RELATIVE_NEUTRAL
        ),
        "missing_input": calculate_relative_btc_performance(None, 1.0) is None,
    }

    enriched = enrich_relative_performance(
        [{"symbol": "TEST", "change_pct": -1.0}],
        -3.0,
    )
    tests["enrichment"] = (
        len(enriched) == 1
        and enriched[0]["relative_btc_performance_pct"] == 2.0
        and enriched[0]["relative_direction"]
        == RelativeDirection.RELATIVE_STRENGTH.value
    )

    return {
        "status": "PASS" if all(tests.values()) else "FAIL",
        "passed": sum(tests.values()),
        "total": len(tests),
        "tests": tests,
    }
