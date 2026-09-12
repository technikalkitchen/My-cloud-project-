"""Stage 8 (U08) altcoin structure and volume helpers."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.analysis.enums import Direction
from app.analysis.u08_config import CELL08_CONFIG
from app.analysis.u08_context import classify_context
from app.analysis.u08_normalize import _safe_float
from app.analysis.u08_ranking import (
    is_opposite_direction,
    rank_relative_movers,
    rank_strong_movers,
    rank_top_assets,
)


def build_altcoin_structure_context(
    btc_direction: Direction,
    btc_d_direction: Direction,
    total2: Optional[Dict[str, Any]] = None,
    total3: Optional[Dict[str, Any]] = None,
    others_d: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Expose altcoin structure only when BTC and BTC.D oppose."""

    opposite = is_opposite_direction(
        btc_direction,
        btc_d_direction,
    )

    if not opposite:
        return {
            "enabled": False,
            "reason": "BTC and BTC.D are not in opposite directions.",
            "total2": total2,
            "total3": total3,
            "others_d": others_d,
        }

    return {
        "enabled": True,
        "reason": "BTC and BTC.D are in opposite directions.",
        "total2": total2,
        "total3": total3,
        "others_d": others_d,
    }


def volume_record(asset: Dict[str, Any]) -> Dict[str, Any]:
    """Build the asset volume output record without BTC-pair volume."""

    return {
        "symbol": asset.get("symbol"),
        "direction": asset.get("direction"),
        "price": asset.get("price"),
        "change_pct": asset.get("change_pct"),
        "volume": asset.get("volume"),
        "relative_btc_performance_pct": asset.get(
            "relative_btc_performance_pct"
        ),
    }


def ensure_volume_fields(
    assets: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Normalize asset volume and mark required volume availability."""

    output = []

    for asset in assets:
        asset = dict(asset)
        asset["volume"] = _safe_float(asset.get("volume"))

        if CELL08_CONFIG.volume_required and asset["volume"] is None:
            asset["volume_status"] = "UNAVAILABLE"
        else:
            asset["volume_status"] = "AVAILABLE"

        output.append(asset)

    return output


def build_strong_movers(
    assets: List[Dict[str, Any]],
    market_context,
) -> List[Dict[str, Any]]:
    """Rank absolute movers and attach volume status."""

    movers = rank_strong_movers(
        assets,
        market_context,
        CELL08_CONFIG.strong_movers_n,
    )
    return ensure_volume_fields(movers)


def build_relative_movers(
    assets: List[Dict[str, Any]],
    market_context,
) -> List[Dict[str, Any]]:
    """Rank BTC-relative movers and attach volume status."""

    movers = rank_relative_movers(
        assets,
        market_context,
        CELL08_CONFIG.relative_movers_n,
    )
    return ensure_volume_fields(movers)


def build_scenario_ranking(
    assets: List[Dict[str, Any]],
    btc_direction: Direction,
    btc_d_direction: Direction,
) -> Dict[str, Any]:
    """Build Cell 8's scenario-specific ranking output."""

    context = classify_context(
        btc_direction,
        btc_d_direction,
    )

    strong_movers = build_strong_movers(
        assets,
        context,
    )
    relative_movers = build_relative_movers(
        assets,
        context,
    )
    top_assets = rank_top_assets(
        assets,
        context,
        CELL08_CONFIG.top_n,
    )

    return {
        "context": context.value,
        "strong_movers": strong_movers,
        "relative_movers": relative_movers,
        "top_10_assets": ensure_volume_fields(top_assets),
    }
