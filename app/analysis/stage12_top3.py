"""Stage 12 — Top 3 Reliable Movers.

Kitchen Assistant — Scanner Subsystem (final operational stage).

Pipeline:
    U06.5 Dynamic Top-125
             ↓
    Stage 10 — Dynamic Top 10 (ranks 2-10)
             ↓
    Stage 11 — 5 Strong Movers (ranks 11-125)
             ↓
    Stage 12 — Top 3 Reliable Movers (combined pool, deduplicated)

Business responsibility:
    Select 3 Reliable Movers from the combined pool of Dynamic Top 10 +
    five Strong Movers using the Strong Movement + Reliability principle.

This is a prioritization layer for deeper human review. It is NOT a
trading decision engine, does NOT produce entry/exit signals, and does
NOT fabricate data.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from app.analysis.stage10_consumer import (
    DISPLAY_FALLBACK_PRIORITY,
    Exchange,
    get_dynamic_top10,
)
from app.analysis.stage10_router import ExchangeRouter
from app.analysis.stage10_usdt import UsdtPairResult
from app.analysis.stage10_btc import BtcPairResult
from app.analysis.stage11_strong_movers import (
    SCANNER_WARNING,
    StrongMoversConfig,
    run_strong_movers,
)
from app.market.ranking import dynamic_rank_assets


STAGE12_HEADER = "TOP 3 RELIABLE MOVERS"
DEFAULT_TIMEFRAME = "5m"
TOP_N = 3


# =========================================================================
# Data Structures
# =========================================================================

@dataclass
class Top3Candidate:
    """A deduplicated candidate for Top 3 selection."""

    symbol: str
    kitchen_rank: int
    canonical_asset_id: str
    in_top10: bool
    in_strong_movers: bool
    usdt_change_pct: Optional[float]
    usdt_volume: Optional[float]
    usdt_pair: str
    usdt_actual_exchange: str
    usdt_fallback_used: bool
    usdt_fallback_exchange: Optional[str]
    usdt_valid: bool
    usdt_source: str
    btc_change_pct: Optional[float]
    btc_pair: str
    btc_actual_exchange: str
    btc_fallback_used: bool
    btc_fallback_exchange: Optional[str]
    btc_available: bool
    btc_valid: bool
    btc_source: str
    movement_score: float
    reliability_score: float
    total_score: float
    reliability_evidence: Dict[str, Any] = field(default_factory=dict)
    timeframe: str = DEFAULT_TIMEFRAME
    valid: bool = True


@dataclass
class Top3Result:
    """Final result for one Top 3 mover."""

    position: int
    symbol: str
    kitchen_rank: int
    usdt_pair: str
    usdt_change_pct: Optional[float]
    usdt_volume: Optional[float]
    usdt_source: str
    usdt_fallback_used: bool
    usdt_fallback_exchange: Optional[str]
    btc_pair: str
    btc_change_pct: Optional[float]
    btc_source: str
    btc_fallback_used: bool
    btc_fallback_exchange: Optional[str]
    btc_available: bool
    movement_score: float
    reliability_score: float
    total_score: float
    reliability_evidence: Dict[str, Any]
    timeframe: str
    valid: bool


@dataclass
class Top3Output:
    """Complete Stage 12 output."""

    selected_exchange: Optional[str]
    display_fallback_priority: List[str]
    timeframe: str
    ranking_version: str
    top3: List[Top3Result]
    candidate_count: int
    selected_count: int
    scanner_warning: str
    valid: bool
    errors: List[str] = field(default_factory=list)


@dataclass
class Top3Config:
    """Stage 12 configuration."""

    selected_exchange: Optional[str] = None
    timeframe: str = DEFAULT_TIMEFRAME
    top_n: int = TOP_N


# =========================================================================
# Unit 12.1 — Stage Contract + Candidate Pool
# =========================================================================

TOP3_HEADER = "🏆 TOP 3 RELIABLE MOVERS"
TOP3_SCANNER_WARNING = SCANNER_WARNING


def _asset_symbol(asset: Dict[str, Any]) -> str:
    return str(asset.get("symbol", ""))


def _asset_rank(asset: Dict[str, Any]) -> int:
    rank = asset.get("calculated_rank")
    if rank is None:
        return 0
    return int(rank)


def _asset_canonical(asset: Dict[str, Any]) -> str:
    return str(asset.get("canonical_asset_id", ""))


def build_candidate_pool(
    top10_assets: List[Dict[str, Any]],
    strong_movers: List[StrongMoverResult],
    valid_assets: List[Dict[str, Any]],
) -> List[Top3Candidate]:
    """Combine Dynamic Top 10 + Strong Movers, deduplicate by canonical asset identity.

    Args:
        top10_assets: Assets from Dynamic Top 10 (Stage 10 output).
        strong_movers: Strong mover results from Stage 11 output.
        valid_assets: Validated assets from U06.5 for canonical ID lookup.

    Returns:
        Deduplicated Top3Candidate list (unscored).
    """
    symbol_to_canonical: Dict[str, str] = {}
    for asset in valid_assets:
        sym = _asset_symbol(asset)
        can = _asset_canonical(asset)
        if sym and can:
            symbol_to_canonical[sym] = can

    seen: Dict[str, Top3Candidate] = {}

    for asset in top10_assets:
        sym = _asset_symbol(asset)
        can = symbol_to_canonical.get(sym) or _asset_canonical(asset)
        if not can or can in seen:
            continue
        candidate = Top3Candidate(
            symbol=sym,
            kitchen_rank=_asset_rank(asset),
            canonical_asset_id=can,
            in_top10=True,
            in_strong_movers=False,
            usdt_change_pct=None,
            usdt_volume=None,
            usdt_pair=f"{sym}USDT",
            usdt_actual_exchange="",
            usdt_fallback_used=False,
            usdt_fallback_exchange=None,
            usdt_valid=False,
            usdt_source="",
            btc_change_pct=None,
            btc_pair=f"{sym}BTC",
            btc_actual_exchange="",
            btc_fallback_used=False,
            btc_fallback_exchange=None,
            btc_available=False,
            btc_valid=False,
            btc_source="",
            movement_score=0.0,
            reliability_score=0.0,
            total_score=0.0,
            timeframe=DEFAULT_TIMEFRAME,
            valid=False,
        )
        seen[can] = candidate

    for mover in strong_movers:
        sym = mover.symbol
        can = symbol_to_canonical.get(sym)
        if not can or can in seen:
            continue
        candidate = Top3Candidate(
            symbol=sym,
            kitchen_rank=mover.kitchen_rank,
            canonical_asset_id=can,
            in_top10=False,
            in_strong_movers=True,
            usdt_change_pct=mover.usdt_change_pct,
            usdt_volume=mover.usdt_volume,
            usdt_pair=mover.usdt_pair,
            usdt_actual_exchange=_extract_exchange(mover.usdt_source),
            usdt_fallback_used=mover.usdt_fallback_used,
            usdt_fallback_exchange=mover.usdt_fallback_exchange,
            usdt_valid=mover.valid,
            usdt_source=mover.usdt_source,
            btc_change_pct=mover.btc_change_pct,
            btc_pair=mover.btc_pair,
            btc_actual_exchange="",
            btc_fallback_used=mover.btc_fallback_used,
            btc_fallback_exchange=mover.btc_fallback_exchange,
            btc_available=mover.btc_available,
            btc_valid=False,
            btc_source=mover.btc_source,
            movement_score=0.0,
            reliability_score=0.0,
            total_score=0.0,
            timeframe=DEFAULT_TIMEFRAME,
            valid=False,
        )
        seen[can] = candidate

    return list(seen.values())


def _extract_exchange(source_label: str) -> str:
    if not source_label:
        return ""
    for prefix in ("Source: ", "Fallback from: "):
        if source_label.startswith(prefix):
            return source_label[len(prefix):]
    return source_label


# =========================================================================
# Unit 12.2 — Strong Movement + Reliability Evaluation
# =========================================================================


def _top3_movement_score(
    change_pct: Optional[float],
    volume: Optional[float],
) -> float:
    if change_pct is None or not math.isfinite(change_pct):
        return 0.0
    abs_move = abs(change_pct)
    if volume is not None and math.isfinite(volume) and volume > 0:
        volume_factor = min(volume / 100_000_000.0, 1.0)
        return abs_move * (0.5 + 0.5 * volume_factor)
    return abs_move * 0.5


def _top3_reliability_score(
    usdt_valid: bool,
    btc_available: bool,
    btc_valid: bool,
    usdt_volume: Optional[float],
    change_pct: Optional[float],
) -> float:
    score = 0.0
    if usdt_valid:
        score += 4.0
    else:
        score += 1.0
    if btc_available and btc_valid:
        score += 2.0
    elif btc_available and not btc_valid:
        score += 0.5
    if usdt_volume is not None and math.isfinite(usdt_volume) and usdt_volume > 0:
        vol = usdt_volume
        if vol >= 1_000_000_000:
            score += 2.0
        elif vol >= 100_000_000:
            score += 1.5
        elif vol >= 10_000_000:
            score += 1.0
        else:
            score += 0.5
    if change_pct is not None and math.isfinite(change_pct):
        score += 1.0
    return score


def evaluate_candidate(
    candidate: Top3Candidate,
) -> Top3Candidate:
    """Evaluate a single candidate for Top 3 selection.

    Applies Strong Movement + Reliability principle.
    Reuses the same scoring contracts as Stage 11.
    """
    movement = _top3_movement_score(
        candidate.usdt_change_pct,
        candidate.usdt_volume,
    )
    reliability = _top3_reliability_score(
        usdt_valid=candidate.usdt_valid,
        btc_available=candidate.btc_available,
        btc_valid=candidate.btc_valid,
        usdt_volume=candidate.usdt_volume,
        change_pct=candidate.usdt_change_pct,
    )
    total = movement + reliability

    evidence: Dict[str, Any] = {
        "movement_score": movement,
        "reliability_score": reliability,
        "usdt_valid": candidate.usdt_valid,
        "btc_available": candidate.btc_available,
        "btc_valid": candidate.btc_valid,
        "usdt_volume": candidate.usdt_volume,
        "usdt_change_pct": candidate.usdt_change_pct,
        "actual_exchange": candidate.usdt_actual_exchange,
    }

    return Top3Candidate(
        symbol=candidate.symbol,
        kitchen_rank=candidate.kitchen_rank,
        canonical_asset_id=candidate.canonical_asset_id,
        in_top10=candidate.in_top10,
        in_strong_movers=candidate.in_strong_movers,
        usdt_change_pct=candidate.usdt_change_pct,
        usdt_volume=candidate.usdt_volume,
        usdt_pair=candidate.usdt_pair,
        usdt_actual_exchange=candidate.usdt_actual_exchange,
        usdt_fallback_used=candidate.usdt_fallback_used,
        usdt_fallback_exchange=candidate.usdt_fallback_exchange,
        usdt_valid=candidate.usdt_valid,
        usdt_source=candidate.usdt_source,
        btc_change_pct=candidate.btc_change_pct,
        btc_pair=candidate.btc_pair,
        btc_actual_exchange=candidate.btc_actual_exchange,
        btc_fallback_used=candidate.btc_fallback_used,
        btc_fallback_exchange=candidate.btc_fallback_exchange,
        btc_available=candidate.btc_available,
        btc_valid=candidate.btc_valid,
        btc_source=candidate.btc_source,
        movement_score=movement,
        reliability_score=reliability,
        total_score=total,
        reliability_evidence=evidence,
        timeframe=candidate.timeframe,
        valid=candidate.usdt_valid or candidate.btc_available,
    )


def select_top3(
    candidates: List[Top3Candidate],
    top_n: int = TOP_N,
) -> List[Top3Candidate]:
    """Select top N candidates by total_score (movement + reliability).

    Never fabricates. Returns fewer than top_n only when valid data
    is insufficient.
    """
    scored = sorted(
        candidates, key=lambda c: c.total_score, reverse=True
    )

    selected: List[Top3Candidate] = []
    for candidate in scored:
        if candidate.valid:
            selected.append(candidate)
        if len(selected) >= top_n:
            break

    return selected


# =========================================================================
# Unit 12.3 — Exchange + Data Contract Continuity
# =========================================================================


def validate_exchange_continuity(
    selected_exchange: Optional[str],
    candidate_exchange: Optional[str],
) -> Tuple[bool, str]:
    """Validate that candidate exchange follows higher-priority-only fallback."""
    if not selected_exchange or not candidate_exchange:
        return True, "no_exchange_constraint"
    if selected_exchange == candidate_exchange:
        return True, "preferred_source"
    router = ExchangeRouter(Exchange(selected_exchange))
    return router.validate_fallback_direction(selected_exchange, candidate_exchange)


# =========================================================================
# Unit 12.4 — Final Top 3 + Telegram Output
# =========================================================================


def _format_volume_top3(volume: Optional[float]) -> str:
    if volume is None:
        return ""
    if volume >= 1_000_000_000_000:
        return f"{volume / 1_000_000_000_000:.1f}T USDT"
    if volume >= 1_000_000_000:
        return f"{volume / 1_000_000_000:.1f}B USDT"
    if volume >= 1_000_000:
        return f"{volume / 1_000_000:.1f}M USDT"
    if volume >= 1_000:
        return f"{volume / 1_000:.1f}K USDT"
    return f"{volume:.0f} USDT"


def _btc_source_label(
    actual_exchange: str,
    fallback_used: bool,
    fallback_exchange: Optional[str],
) -> str:
    if fallback_used and fallback_exchange:
        return f"Fallback from: {fallback_exchange}"
    if actual_exchange:
        return f"Source: {actual_exchange}"
    return ""


def build_top3_result(
    candidate: Top3Candidate,
    position: int,
    timeframe: str = DEFAULT_TIMEFRAME,
) -> Top3Result:
    """Build a Top3Result from an evaluated candidate."""
    return Top3Result(
        position=position,
        symbol=candidate.symbol,
        kitchen_rank=candidate.kitchen_rank,
        usdt_pair=candidate.usdt_pair,
        usdt_change_pct=candidate.usdt_change_pct,
        usdt_volume=candidate.usdt_volume,
        usdt_source=candidate.usdt_source,
        usdt_fallback_used=candidate.usdt_fallback_used,
        usdt_fallback_exchange=candidate.usdt_fallback_exchange,
        btc_pair=candidate.btc_pair,
        btc_change_pct=candidate.btc_change_pct,
        btc_source=candidate.btc_source,
        btc_fallback_used=candidate.btc_fallback_used,
        btc_fallback_exchange=candidate.btc_fallback_exchange,
        btc_available=candidate.btc_available,
        movement_score=candidate.movement_score,
        reliability_score=candidate.reliability_score,
        total_score=candidate.total_score,
        reliability_evidence=candidate.reliability_evidence,
        timeframe=timeframe,
        valid=candidate.valid,
    )


def format_top3_telegram(
    output: Top3Output,
) -> str:
    """Format Top 3 results as Telegram message.

    Compact format per Stage 12 roadmap:
        1. SOLUSDT +8.4%
           Volume: ...
           Exchange: Binance

    Preserves Source/Fallback semantics.
    Includes mandatory scanner warning.
    No signal/recommendation language.
    """
    lines: List[str] = [TOP3_HEADER, "", TOP3_SCANNER_WARNING, ""]

    for result in output.top3:
        lines.append(f"{result.position}. {result.symbol}")
        lines.append("")

        change = result.usdt_change_pct
        if change is not None:
            sign = "+" if change >= 0 else ""
            lines.append(f"    {sign}{change:.2f}%")
        lines.append(f"    {result.usdt_pair}")

        if result.usdt_volume is not None:
            lines.append(f"    Volume: {_format_volume_top3(result.usdt_volume)}")

        if result.usdt_source:
            lines.append(f"    {result.usdt_source}")

        lines.append("")

        if result.btc_available:
            btc_change = result.btc_change_pct
            if btc_change is not None:
                sign = "+" if btc_change >= 0 else ""
                lines.append(f"    {sign}{btc_change:.2f}%")
            lines.append(f"    {result.btc_pair}")
            if result.btc_source:
                lines.append(f"    {result.btc_source}")
            lines.append("")

    return "\n".join(lines).strip()


# =========================================================================
# Unit 12.5 — Full Scanner Integration Orchestrator
# =========================================================================


def run_top3(
    valid_assets: List[Dict[str, Any]],
    config: Optional[Top3Config] = None,
    usdt_results: Optional[Dict[str, UsdtPairResult]] = None,
    btc_results: Optional[Dict[str, BtcPairResult]] = None,
) -> Top3Output:
    """Orchestrate the full Stage 12 Top 3 Reliable Movers pipeline.

    Args:
        valid_assets: Raw asset data from U06.5 validation.
        config: Stage 12 configuration.
        usdt_results: Dict symbol → UsdtPairResult for each candidate.
        btc_results: Dict symbol → BtcPairResult for each candidate.

    Returns:
        Top3Output with exactly 3 Reliable Movers (or fewer).
    """
    if config is None:
        config = Top3Config()

    errors: List[str] = []

    ranking = dynamic_rank_assets(valid_assets)
    ranking_version = ranking.get("ranking_version", "")

    from app.analysis.stage11_strong_movers import run_strong_movers, StrongMoversConfig

    top10_result = get_dynamic_top10(valid_assets)
    top10_assets = top10_result.assets

    strong_config = StrongMoversConfig(
        selected_exchange=config.selected_exchange,
        timeframe=config.timeframe,
        top_n=5,
    )
    strong_output = run_strong_movers(
        valid_assets,
        config=strong_config,
        usdt_results=usdt_results,
        btc_results=btc_results,
    )

    candidate_pool = build_candidate_pool(
        top10_assets=top10_assets,
        strong_movers=strong_output.strong_movers,
        valid_assets=valid_assets,
    )

    evaluated: List[Top3Candidate] = []
    for candidate in candidate_pool:
        usdt_key = f"{candidate.symbol}USDT"
        usdt_result: Optional[UsdtPairResult] = None
        if usdt_results and usdt_key in usdt_results:
            usdt_result = usdt_results[usdt_key]

        btc_key = f"{candidate.symbol}BTC"
        btc_result: Optional[BtcPairResult] = None
        if btc_results and btc_key in btc_results:
            btc_result = btc_results[btc_key]

        if usdt_result is not None:
            candidate = Top3Candidate(
                symbol=candidate.symbol,
                kitchen_rank=candidate.kitchen_rank,
                canonical_asset_id=candidate.canonical_asset_id,
                in_top10=candidate.in_top10,
                in_strong_movers=candidate.in_strong_movers,
                usdt_change_pct=usdt_result.change_pct,
                usdt_volume=usdt_result.volume,
                usdt_pair=usdt_result.symbol,
                usdt_actual_exchange=usdt_result.actual_exchange,
                usdt_fallback_used=usdt_result.fallback_used,
                usdt_fallback_exchange=usdt_result.fallback_exchange,
                usdt_valid=usdt_result.valid,
                usdt_source=usdt_result.volume_source_label,
                btc_change_pct=candidate.btc_change_pct,
                btc_pair=candidate.btc_pair,
                btc_actual_exchange=candidate.btc_actual_exchange,
                btc_fallback_used=candidate.btc_fallback_used,
                btc_fallback_exchange=candidate.btc_fallback_exchange,
                btc_available=candidate.btc_available,
                btc_valid=candidate.btc_valid,
                btc_source=candidate.btc_source,
                movement_score=0.0,
                reliability_score=0.0,
                total_score=0.0,
                reliability_evidence={},
                timeframe=config.timeframe,
                valid=False,
            )

        if btc_result is not None:
            candidate = Top3Candidate(
                symbol=candidate.symbol,
                kitchen_rank=candidate.kitchen_rank,
                canonical_asset_id=candidate.canonical_asset_id,
                in_top10=candidate.in_top10,
                in_strong_movers=candidate.in_strong_movers,
                usdt_change_pct=candidate.usdt_change_pct,
                usdt_volume=candidate.usdt_volume,
                usdt_pair=candidate.usdt_pair,
                usdt_actual_exchange=candidate.usdt_actual_exchange,
                usdt_fallback_used=candidate.usdt_fallback_used,
                usdt_fallback_exchange=candidate.usdt_fallback_exchange,
                usdt_valid=candidate.usdt_valid,
                usdt_source=candidate.usdt_source,
                btc_change_pct=btc_result.change_pct,
                btc_pair=btc_result.symbol,
                btc_actual_exchange=btc_result.actual_exchange,
                btc_fallback_used=btc_result.fallback_used,
                btc_fallback_exchange=btc_result.fallback_exchange,
                btc_available=True,
                btc_valid=btc_result.valid,
                btc_source=_btc_source_label(
                    btc_result.actual_exchange,
                    btc_result.fallback_used,
                    btc_result.fallback_exchange,
                ),
                movement_score=0.0,
                reliability_score=0.0,
                total_score=0.0,
                reliability_evidence={},
                timeframe=config.timeframe,
                valid=False,
            )

        evaluated_candidate = evaluate_candidate(candidate)
        evaluated.append(evaluated_candidate)

    selected_candidates = select_top3(
        evaluated, top_n=config.top_n
    )

    top3_results: List[Top3Result] = []
    for i, candidate in enumerate(selected_candidates, 1):
        result = build_top3_result(
            candidate, position=i, timeframe=config.timeframe
        )
        top3_results.append(result)

    exchange_names: List[str] = [e.value for e in DISPLAY_FALLBACK_PRIORITY]

    return Top3Output(
        selected_exchange=config.selected_exchange,
        display_fallback_priority=exchange_names,
        timeframe=config.timeframe,
        ranking_version=ranking_version,
        top3=top3_results,
        candidate_count=len(evaluated),
        selected_count=len(top3_results),
        scanner_warning=TOP3_SCANNER_WARNING,
        valid=len(top3_results) > 0,
        errors=errors,
    )
