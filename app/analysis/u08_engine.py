"""Stage 8 (U08) final Cell 8 engine.

Wires together all U08.0–U08.9 components into the complete
BTC + BTC.D Context & Relative-Movement Engine.
Mirrors Kitchen Assistant v3.1.4.ipynb Cell 8 `run_cell_08`.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.analysis.enums import Direction
from app.analysis.u08_config import CELL08_CONFIG
from app.analysis.u08_narratives import get_narrative
from app.analysis.u08_normalize import _safe_float, _normalize_direction
from app.analysis.u08_ranking import add_absolute_direction
from app.analysis.u08_altcoin import (
    build_altcoin_structure_context,
    build_scenario_ranking,
)
from app.analysis.u08_relative import enrich_relative_performance
from app.analysis.u08_result import Cell08Result
from app.analysis.u08_scenario import resolve_scenario


def run_cell_08(
    *,
    btc_direction: Any,
    btc_d_direction: Any,
    btc_change_pct: Optional[float],
    assets: List[Dict[str, Any]],
    pattern_index: int = 1,
    total2: Optional[Dict[str, Any]] = None,
    total3: Optional[Dict[str, Any]] = None,
    others_d: Optional[Dict[str, Any]] = None,
) -> Cell08Result:
    """Execute the complete Cell 8 analysis pipeline.

    Args:
        btc_direction: BTC direction (Direction enum or alias string)
        btc_d_direction: BTC.D direction (Direction enum or alias string)
        btc_change_pct: BTC percentage change for relative calculations
        assets: List of asset dicts with symbol, change_pct, volume, etc.
        pattern_index: Narrative pattern to select (1, 2, or 3)
        total2: Optional TOTAL2 index data
        total3: Optional TOTAL3 index data
        others_d: Optional OTHERS.D index data

    Returns:
        Cell08Result with complete analysis output.

    Raises:
        TypeError: If assets is not a list.
        ValueError: If pattern_index is invalid.
        RuntimeError: If no canonical scenario exists for the direction pair.
    """

    # --------------------------------------------------------
    # INPUT VALIDATION
    # --------------------------------------------------------

    btc_direction = _normalize_direction(btc_direction)
    btc_d_direction = _normalize_direction(btc_d_direction)

    if not isinstance(assets, list):
        raise TypeError("CELL08_ERROR: assets must be a list.")

    btc_change_pct = _safe_float(btc_change_pct)

    # --------------------------------------------------------
    # SCENARIO RESOLUTION
    # --------------------------------------------------------

    scenario = resolve_scenario(btc_direction, btc_d_direction)

    scenario_id = scenario["scenario_id"]
    scenario_type = scenario["scenario_type"]

    # --------------------------------------------------------
    # ASSET PREPARATION
    # --------------------------------------------------------

    prepared_assets = add_absolute_direction(assets)
    prepared_assets = enrich_relative_performance(prepared_assets, btc_change_pct)
    prepared_assets = _ensure_volume_fields_for_engine(prepared_assets)

    # --------------------------------------------------------
    # RANKING
    # --------------------------------------------------------

    ranking = build_scenario_ranking(
        prepared_assets,
        btc_direction,
        btc_d_direction,
    )

    # --------------------------------------------------------
    # ALTCOIN STRUCTURE
    # --------------------------------------------------------

    altcoin_structure = build_altcoin_structure_context(
        btc_direction,
        btc_d_direction,
        total2=total2,
        total3=total3,
        others_d=others_d,
    )

    # --------------------------------------------------------
    # PATTERN SELECTION
    # --------------------------------------------------------

    selected_pattern = get_narrative(scenario_id, pattern_index)

    # --------------------------------------------------------
    # OPPOSITE DIRECTION
    # --------------------------------------------------------

    opposite = (
        btc_direction == Direction.INCREASE and btc_d_direction == Direction.DECREASE
    ) or (
        btc_direction == Direction.DECREASE and btc_d_direction == Direction.INCREASE
    )

    # --------------------------------------------------------
    # AUDIT
    # --------------------------------------------------------

    audit = {
        "engine": "CELL_08",
        "engine_version": "V3.1",
        "execution": "ANALYSIS_ONLY",
        "trading_enabled": False,
        "orders_enabled": False,
        "strategy_enabled": False,
        "portfolio_actions_enabled": False,
        "scenarios_locked": True,
        "narratives_locked": True,
        "narrative_pattern_count": 27,
        "btc_is_benchmark": True,
        "absolute_direction_preserved": True,
        "relative_performance_is_complementary": True,
        "btc_pair_analysis_enabled": True,
        "altcoin_structure_used_only_when_required": True,
        "opposite_direction": opposite,
        "volume_required": CELL08_CONFIG.volume_required,
    }

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    return Cell08Result(
        engine="CELL_08",
        version="V3.1",
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        scenario_id=scenario_id,
        scenario_type=scenario_type,
        btc_direction=btc_direction.value,
        btc_d_direction=btc_d_direction.value,
        context=ranking["context"],
        opposite_direction=opposite,
        selected_pattern=selected_pattern,
        top_10_assets=ranking["top_10_assets"],
        strong_movers=ranking["strong_movers"],
        relative_movers=ranking["relative_movers"],
        altcoin_structure=altcoin_structure,
        audit=audit,
    )


def _ensure_volume_fields_for_engine(
    assets: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Internal volume field normalization for engine pipeline.

    Uses the same logic as u08_altcoin.ensure_volume_fields but keeps
    the engine self-contained for the pipeline.
    Strips BTC-pair volume fields per Cell 8 volume law (USDT pair only).
    """
    output = []
    for asset in assets:
        asset = dict(asset)
        # Strip BTC-pair volume fields - Cell 8 only uses USDT-pair volume
        asset.pop("btc_pair_volume", None)
        asset.pop("btc_pair_change_pct", None)

        asset["volume"] = _safe_float(asset.get("volume"))

        if CELL08_CONFIG.volume_required and asset["volume"] is None:
            asset["volume_status"] = "UNAVAILABLE"
        else:
            asset["volume_status"] = "AVAILABLE"

        output.append(asset)
    return output


def cell08_self_tests() -> Dict[str, Any]:
    """Run deterministic self-tests for the Cell 8 engine."""
    from app.analysis.enums import Context

    tests = {}

    # Test 1: Basic execution produces valid Cell08Result
    assets = [
        {"symbol": "BTCUSDT", "change_pct": 2.0, "volume": 1000.0},
        {"symbol": "ETHUSDT", "change_pct": 5.0, "volume": 500.0},
        {"symbol": "SOLUSDT", "change_pct": -1.0, "volume": 200.0},
    ]
    result = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=assets,
        pattern_index=1,
    )
    tests["basic_execution"] = (
        isinstance(result, Cell08Result)
        and result.engine == "CELL_08"
        and result.version == "V3.1"
        and result.scenario_id == 2
        and result.context == "BULLISH"
        and result.opposite_direction is True
    )

    # Test 2: All output fields present and correct types
    tests["output_fields"] = (
        isinstance(result.top_10_assets, list)
        and isinstance(result.strong_movers, list)
        and isinstance(result.relative_movers, list)
        and isinstance(result.altcoin_structure, dict)
        and isinstance(result.audit, dict)
        and isinstance(result.selected_pattern, dict)
        and "pattern" in result.selected_pattern
        and "title" in result.selected_pattern
        and "text" in result.selected_pattern
    )

    # Test 3: Altcoin structure enabled when opposite
    tests["altcoin_enabled_when_opposite"] = result.altcoin_structure["enabled"] is True

    # Test 4: Altcoin structure disabled when not opposite
    result2 = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="INCREASE",
        btc_change_pct=2.0,
        assets=assets,
        pattern_index=1,
    )
    tests["altcoin_disabled_when_not_opposite"] = result2.altcoin_structure["enabled"] is False

    # Test 5: Ranking respects context (BULLISH)
    tests["ranking_bullish_context"] = result.context == "BULLISH"

    # Test 6: Ranking respects context (BEARISH)
    result3 = run_cell_08(
        btc_direction="DECREASE",
        btc_d_direction="RANGE",
        btc_change_pct=-2.0,
        assets=assets,
        pattern_index=1,
    )
    tests["ranking_bearish_context"] = result3.context == "BEARISH"

    # Test 7: Ranking respects context (RANGE)
    result4 = run_cell_08(
        btc_direction="RANGE",
        btc_d_direction="RANGE",
        btc_change_pct=0.0,
        assets=assets,
        pattern_index=1,
    )
    tests["ranking_range_context"] = result4.context == "RANGE"

    # Test 8: Assets without change_pct are filtered
    assets_with_none = assets + [{"symbol": "XRPUSDT", "change_pct": None, "volume": 100.0}]
    result5 = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="INCREASE",
        btc_change_pct=2.0,
        assets=assets_with_none,
        pattern_index=1,
    )
    tests["filters_none_change"] = all(
        a.get("change_pct") is not None
        for a in result5.top_10_assets + result5.strong_movers + result5.relative_movers
    )

    # Test 9: Volume status present on all output assets
    all_output_assets = (
        result.top_10_assets + result.strong_movers + result.relative_movers
    )
    tests["volume_status_present"] = all(
        "volume_status" in a for a in all_output_assets
    )

    # Test 10: Relative performance calculated when btc_change_pct provided
    tests["relative_performance_calculated"] = any(
        "relative_btc_performance_pct" in a for a in result.relative_movers
    )

    # Test 11: Pattern index selection works
    result_p1 = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=assets,
        pattern_index=1,
    )
    result_p2 = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=assets,
        pattern_index=2,
    )
    result_p3 = run_cell_08(
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        btc_change_pct=2.0,
        assets=assets,
        pattern_index=3,
    )
    tests["pattern_index_1"] = result_p1.selected_pattern["pattern"] == "Pattern 1"
    tests["pattern_index_2"] = result_p2.selected_pattern["pattern"] == "Pattern 2"
    tests["pattern_index_3"] = result_p3.selected_pattern["pattern"] == "Pattern 3"

    # Test 12: Invalid pattern index raises
    try:
        run_cell_08(
            btc_direction="INCREASE",
            btc_d_direction="DECREASE",
            btc_change_pct=2.0,
            assets=assets,
            pattern_index=4,
        )
        tests["invalid_pattern_rejected"] = False
    except ValueError:
        tests["invalid_pattern_rejected"] = True

    # Test 13: Invalid assets type raises
    try:
        run_cell_08(
            btc_direction="INCREASE",
            btc_d_direction="DECREASE",
            btc_change_pct=2.0,
            assets="not a list",
            pattern_index=1,
        )
        tests["invalid_assets_rejected"] = False
    except TypeError:
        tests["invalid_assets_rejected"] = True

    # Test 14: Audit contains all required safety flags
    required_audit_keys = [
        "engine", "trading_enabled", "orders_enabled", "strategy_enabled",
        "portfolio_actions_enabled", "scenarios_locked", "narratives_locked",
        "narrative_pattern_count", "btc_is_benchmark", "opposite_direction",
    ]
    tests["audit_complete"] = all(k in result.audit for k in required_audit_keys)

    # Test 15: Serialization works
    from app.analysis.u08_result import cell08_to_dict, cell08_to_json
    d = cell08_to_dict(result)
    tests["to_dict_works"] = isinstance(d, dict) and d["engine"] == "CELL_08"
    s = cell08_to_json(result)
    tests["to_json_works"] = isinstance(s, str) and "CELL_08" in s

    passed = sum(tests.values())
    total = len(tests)

    return {
        "status": "PASS" if passed == total else "FAIL",
        "passed": passed,
        "total": total,
        "tests": tests,
    }