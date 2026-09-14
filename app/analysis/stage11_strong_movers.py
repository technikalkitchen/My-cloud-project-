"""Stage 11 — Strong Movers.

Kitchen Assistant — Scanner Subsystem.

Single-file Kilo implementation contract for Stage 11.

Pipeline:
    U06.5 / Kitchen Dynamic Top-125
             ↓
    exclude BTC rank 1
             ↓
    candidate ranks 11–125
             ↓
    Strong Movement + Reliability evaluation
             ↓
    Exchange Contract (reuses Stage 10)
             ↓
    5 Strong Movers

DO NOT implement Top-3 Reliable Movers here.
Top-3 belongs to the NEXT stage.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from app.analysis.stage10_consumer import Exchange, DISPLAY_FALLBACK_PRIORITY
from app.analysis.stage10_router import ExchangeRouter
from app.analysis.stage10_usdt import UsdtPairResult
from app.analysis.stage10_btc import BtcPairResult
from app.market.ranking import dynamic_rank_assets


SCANNER_WARNING = (
    "⚠️ توجه: اطلاعات و انتخاب‌های ارائه‌شده توسط Scanner "
    "به‌هیچ‌وجه سیگنال ورود یا خروج از معامله نیستند و نباید به‌تنهایی "
    "مبنای تصمیم معاملاتی قرار گیرند. هدف Scanner، صرفه‌جویی در زمان و "
    "مشخص‌کردن دارایی‌های برتر، جریان حرکت سرمایه و جهت کلی بازار است تا "
    "بتوانید روی گزینه‌هایی که ارزش بررسی بیشتری دارند تمرکز کنید. "
    "تصمیم نهایی برای معامله، از جمله تشخیص Setup، Entry و Trigger، "
    "بر عهده خود شماست."
)

STRONG_MOVERS_HEADER = "🏆 5 STRONG MOVERS"

DEFAULT_TIMEFRAME = "5m"


# =========================================================================
# Data Structures
# =========================================================================

@dataclass
class StrongMoverCandidate:
    """A candidate asset from ranks 11-125 with evaluation data."""

    kitchen_rank: int
    symbol: str
    usdt_change_pct: Optional[float]
    usdt_volume: Optional[float]
    usdt_actual_exchange: str
    usdt_fallback_used: bool
    usdt_fallback_exchange: Optional[str]
    usdt_valid: bool
    btc_change_pct: Optional[float]
    btc_actual_exchange: str
    btc_fallback_used: bool
    btc_fallback_exchange: Optional[str]
    btc_available: bool
    btc_valid: bool
    movement_score: float
    reliability_score: float
    total_score: float
    reliability_evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrongMoverResult:
    """Final result for one Strong Mover."""

    kitchen_rank: int
    symbol: str
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
class StrongMoversOutput:
    """Complete Stage 11 output."""

    selected_exchange: Optional[str]
    display_fallback_priority: List[str]
    timeframe: str
    ranking_version: str
    strong_movers: List[StrongMoverResult]
    candidate_count: int
    selected_count: int
    scanner_warning: str
    valid: bool
    errors: List[str] = field(default_factory=list)


@dataclass
class StrongMoversConfig:
    """Stage 11 configuration."""

    selected_exchange: Optional[str] = None
    timeframe: str = DEFAULT_TIMEFRAME
    top_n: int = 5
    min_rank: int = 11
    max_rank: int = 125


# =========================================================================
# Unit 11.1 — Stage Contract + Candidate Universe
# =========================================================================

def build_candidate_universe(
    valid_assets: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Build Stage 11 candidate universe from U06.5 Dynamic Top-125.

    Returns assets in ranks 11-125, excluding BTC rank 1.
    Computed dynamically — no caching.
    """
    ranking = dynamic_rank_assets(valid_assets)
    top125 = ranking.get("top125", [])

    candidates: List[Dict[str, Any]] = []
    for asset in top125:
        rank = asset.get("calculated_rank")
        if rank is None:
            continue
        r: int = int(rank)
        if 11 <= r <= 125:
            candidates.append(asset)

    return candidates


def get_ranking_version(
    valid_assets: List[Dict[str, Any]],
) -> str:
    """Get the ranking version from U06.5."""
    ranking = dynamic_rank_assets(valid_assets)
    return ranking.get("ranking_version", "")


# =========================================================================
# Unit 11.2 — Strong Movement + Reliability Evaluation
# =========================================================================

def _movement_score(
    change_pct: Optional[float],
    volume: Optional[float],
) -> float:
    """Score the movement component with volume support."""
    if change_pct is None or not math.isfinite(change_pct):
        return 0.0
    abs_move = abs(change_pct)
    if volume is not None and math.isfinite(volume) and volume > 0:
        volume_factor = min(volume / 100_000_000.0, 1.0)
        return abs_move * (0.5 + 0.5 * volume_factor)
    return abs_move * 0.5


def _reliability_score(
    usdt_valid: bool,
    btc_available: bool,
    btc_valid: bool,
    usdt_volume: Optional[float],
    change_pct: Optional[float],
) -> float:
    """Score the reliability component."""
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
    kitchen_rank: int,
    symbol: str,
    usdt_result: Optional[UsdtPairResult],
    btc_result: Optional[BtcPairResult],
) -> StrongMoverCandidate:
    """Evaluate a single candidate for Strong Mover candidacy.

    Applies Strong Movement + Reliability principle.
    """
    usdt_change: Optional[float] = None
    usdt_vol: Optional[float] = None
    usdt_valid = False
    usdt_actual = ""
    usdt_fallback = False
    usdt_fallback_ex: Optional[str] = None

    if usdt_result is not None:
        usdt_change = usdt_result.change_pct
        usdt_vol = usdt_result.volume
        usdt_valid = usdt_result.valid
        usdt_actual = usdt_result.actual_exchange
        usdt_fallback = usdt_result.fallback_used
        usdt_fallback_ex = usdt_result.fallback_exchange

    btc_change: Optional[float] = None
    btc_available = False
    btc_valid = False
    btc_actual = ""
    btc_fallback = False
    btc_fallback_ex: Optional[str] = None

    if btc_result is not None:
        btc_change = btc_result.change_pct
        btc_available = True
        btc_valid = btc_result.valid
        btc_actual = btc_result.actual_exchange
        btc_fallback = btc_result.fallback_used
        btc_fallback_ex = btc_result.fallback_exchange

    movement = _movement_score(usdt_change, usdt_vol)
    reliability = _reliability_score(
        usdt_valid=usdt_valid,
        btc_available=btc_available,
        btc_valid=btc_valid,
        usdt_volume=usdt_vol,
        change_pct=usdt_change,
    )
    total = movement + reliability

    evidence: Dict[str, Any] = {
        "movement_score": movement,
        "reliability_score": reliability,
        "usdt_valid": usdt_valid,
        "btc_available": btc_available,
        "btc_valid": btc_valid,
        "usdt_volume": usdt_vol,
        "usdt_change_pct": usdt_change,
        "actual_exchange": usdt_actual,
        "btc_actual_exchange": btc_actual,
    }

    return StrongMoverCandidate(
        kitchen_rank=kitchen_rank,
        symbol=symbol,
        usdt_change_pct=usdt_change,
        usdt_volume=usdt_vol,
        usdt_actual_exchange=usdt_actual,
        usdt_fallback_used=usdt_fallback,
        usdt_fallback_exchange=usdt_fallback_ex,
        usdt_valid=usdt_valid,
        btc_change_pct=btc_change,
        btc_actual_exchange=btc_actual,
        btc_fallback_used=btc_fallback,
        btc_fallback_exchange=btc_fallback_ex,
        btc_available=btc_available,
        btc_valid=btc_valid,
        movement_score=movement,
        reliability_score=reliability,
        total_score=total,
        reliability_evidence=evidence,
    )


def select_strong_movers(
    candidates: List[StrongMoverCandidate],
    top_n: int = 5,
) -> List[StrongMoverCandidate]:
    """Select top N Strong Movers by total_score (movement + reliability).

    Never fabricates. Returns fewer than top_n only when valid data
    is insufficient.
    """
    scored = sorted(
        candidates, key=lambda c: c.total_score, reverse=True
    )

    strong: List[StrongMoverCandidate] = []
    for candidate in scored:
        if candidate.usdt_valid or candidate.btc_available:
            strong.append(candidate)
        if len(strong) >= top_n:
            break

    return strong


# =========================================================================
# Unit 11.3 — Exchange Selection + Fallback (reuses Stage 10 contracts)
# =========================================================================

def get_fallback_chain(
    selected_exchange: Optional[str],
) -> List[str]:
    """Return exchanges in fallback order (selected → highest priority)."""
    if not selected_exchange:
        return [e.value for e in DISPLAY_FALLBACK_PRIORITY]
    router = ExchangeRouter(selected_exchange)
    return router.get_fallback_chain()


def is_higher_priority(a: str, b: str) -> bool:
    """Return True if exchange a has higher priority than b."""
    router = ExchangeRouter(Exchange.BINANCE)
    return router.is_higher_priority(a, b)


def validate_fallback_direction(requested: str, actual: str) -> Tuple[bool, str]:
    """Validate fallback direction per Stage 10 contract."""
    router = ExchangeRouter(requested)
    return router.validate_fallback_direction(requested, actual)


def route_exchange(
    selected_exchange: str,
    validator_fn,
):
    """Route through exchange fallback chain using Stage 10 router.

    Args:
        selected_exchange: User-selected exchange name.
        validator_fn: Callable taking exchange name, returning
            (is_valid, errors).

    Returns:
        ExchangeRoutingResult from Stage 10 router.
    """
    router = ExchangeRouter(selected_exchange)
    return router.route(validator_fn)


# =========================================================================
# Unit 11.4 — Five Strong Movers Output
# =========================================================================

def _format_source_label(
    actual_exchange: str,
    fallback_used: bool,
    fallback_exchange: Optional[str],
) -> str:
    if fallback_used and fallback_exchange:
        return f"Fallback from: {fallback_exchange}"
    if actual_exchange:
        return f"Source: {actual_exchange}"
    return "Source"


def build_strong_mover_result(
    candidate: StrongMoverCandidate,
    timeframe: str = DEFAULT_TIMEFRAME,
) -> StrongMoverResult:
    """Build a StrongMoverResult from an evaluated candidate."""
    usdt_source = _format_source_label(
        candidate.usdt_actual_exchange,
        candidate.usdt_fallback_used,
        candidate.usdt_fallback_exchange,
    )
    btc_source = _format_source_label(
        candidate.btc_actual_exchange,
        candidate.btc_fallback_used,
        candidate.btc_fallback_exchange,
    )

    return StrongMoverResult(
        kitchen_rank=candidate.kitchen_rank,
        symbol=candidate.symbol,
        usdt_pair=f"{candidate.symbol}USDT",
        usdt_change_pct=candidate.usdt_change_pct,
        usdt_volume=candidate.usdt_volume,
        usdt_source=usdt_source,
        usdt_fallback_used=candidate.usdt_fallback_used,
        usdt_fallback_exchange=candidate.usdt_fallback_exchange,
        btc_pair=f"{candidate.symbol}BTC",
        btc_change_pct=candidate.btc_change_pct,
        btc_source=btc_source,
        btc_fallback_used=candidate.btc_fallback_used,
        btc_fallback_exchange=candidate.btc_fallback_exchange,
        btc_available=candidate.btc_available,
        movement_score=candidate.movement_score,
        reliability_score=candidate.reliability_score,
        total_score=candidate.total_score,
        reliability_evidence=candidate.reliability_evidence,
        timeframe=timeframe,
        valid=candidate.usdt_valid or candidate.btc_available,
    )


def _format_volume(volume: float) -> str:
    if volume >= 1_000_000_000_000:
        return f"{volume / 1_000_000_000_000:.1f}T USDT"
    if volume >= 1_000_000_000:
        return f"{volume / 1_000_000_000:.1f}B USDT"
    if volume >= 1_000_000:
        return f"{volume / 1_000_000:.1f}M USDT"
    if volume >= 1_000:
        return f"{volume / 1_000:.1f}K USDT"
    return f"{volume:.0f} USDT"


def format_strong_movers_telegram(
    output: StrongMoversOutput,
) -> str:
    """Format Strong Movers as Telegram message.

    Preserves Stage 10 semantic display order:
        Asset → USDT pair + movement → USDT volume → Source/Fallback
        BTC pair + movement → Source/Fallback

    Volume belongs only to USDT pair. No BTC volume.
    """
    lines: List[str] = [STRONG_MOVERS_HEADER, "", SCANNER_WARNING, ""]

    for i, mover in enumerate(output.strong_movers, 1):
        lines.append(f"{i}. {mover.symbol} (Rank {mover.kitchen_rank})")
        lines.append("")

        change = mover.usdt_change_pct
        if change is not None:
            sign = "+" if change >= 0 else ""
            lines.append(f"    {sign}{change:.2f}%")
        lines.append(f"    {mover.usdt_pair}")

        if mover.usdt_volume is not None:
            lines.append(f"    Volume: {_format_volume(mover.usdt_volume)}")

        lines.append(f"    {mover.usdt_source}")
        lines.append("")

        if mover.btc_available:
            btc_change = mover.btc_change_pct
            if btc_change is not None:
                sign = "+" if btc_change >= 0 else ""
                lines.append(f"    {sign}{btc_change:.2f}%")
            lines.append(f"    {mover.btc_pair}")
            lines.append(f"    {mover.btc_source}")
            lines.append("")

    return "\n".join(lines).strip()


# =========================================================================
# Unit 11.5 — Top-3 Preparation / Integration Contract
# =========================================================================

def prepare_for_top3(
    output: StrongMoversOutput,
) -> Dict[str, Any]:
    """Preserve Strong Movers result for downstream Top-3 stage.

    Does NOT implement Top-3 selection. Only prepares structured data.
    """
    return {
        "stage": "strong_movers",
        "selected_exchange": output.selected_exchange,
        "display_fallback_priority": output.display_fallback_priority,
        "timeframe": output.timeframe,
        "ranking_version": output.ranking_version,
        "strong_movers": [
            {
                "kitchen_rank": m.kitchen_rank,
                "symbol": m.symbol,
                "usdt_pair": m.usdt_pair,
                "usdt_change_pct": m.usdt_change_pct,
                "usdt_volume": m.usdt_volume,
                "usdt_source": m.usdt_source,
                "usdt_fallback_used": m.usdt_fallback_used,
                "usdt_fallback_exchange": m.usdt_fallback_exchange,
                "btc_pair": m.btc_pair,
                "btc_change_pct": m.btc_change_pct,
                "btc_source": m.btc_source,
                "btc_fallback_used": m.btc_fallback_used,
                "btc_fallback_exchange": m.btc_fallback_exchange,
                "btc_available": m.btc_available,
                "movement_score": m.movement_score,
                "reliability_score": m.reliability_score,
                "total_score": m.total_score,
                "reliability_evidence": m.reliability_evidence,
                "timeframe": m.timeframe,
                "valid": m.valid,
            }
            for m in output.strong_movers
        ],
        "candidate_count": output.candidate_count,
        "selected_count": output.selected_count,
        "scanner_warning": output.scanner_warning,
    }


# =========================================================================
# Unit 11.6 — Orchestrator
# =========================================================================

def run_strong_movers(
    valid_assets: List[Dict[str, Any]],
    config: Optional[StrongMoversConfig] = None,
    usdt_results: Optional[Dict[str, UsdtPairResult]] = None,
    btc_results: Optional[Dict[str, BtcPairResult]] = None,
) -> StrongMoversOutput:
    """Orchestrate the full Stage 11 Strong Movers pipeline.

    Args:
        valid_assets: Raw asset data from U06.5 validation.
        config: Stage 11 configuration.
        usdt_results: Dict symbol → UsdtPairResult for each candidate.
        btc_results: Dict symbol → BtcPairResult for each candidate.

    Returns:
        StrongMoversOutput with exactly 5 Strong Movers (or fewer).
    """
    if config is None:
        config = StrongMoversConfig()

    errors: List[str] = []
    ranking_version = get_ranking_version(valid_assets)

    candidates = build_candidate_universe(valid_assets)

    if not candidates:
        return StrongMoversOutput(
            selected_exchange=config.selected_exchange,
            display_fallback_priority=[e.value for e in DISPLAY_FALLBACK_PRIORITY],
            timeframe=config.timeframe,
            ranking_version=ranking_version,
            strong_movers=[],
            candidate_count=0,
            selected_count=0,
            scanner_warning=SCANNER_WARNING,
            valid=False,
            errors=["No candidate assets from U06.5 Dynamic Top-125"],
        )

    evaluated: List[StrongMoverCandidate] = []
    for asset in candidates:
        symbol = str(asset.get("symbol", ""))
        kitchen_rank = int(asset.get("calculated_rank", 0))

        usdt_key = f"{symbol}USDT"
        usdt_result: Optional[UsdtPairResult] = None
        if usdt_results and usdt_key in usdt_results:
            usdt_result = usdt_results[usdt_key]

        btc_key = f"{symbol}BTC"
        btc_result: Optional[BtcPairResult] = None
        if btc_results and btc_key in btc_results:
            btc_result = btc_results[btc_key]

        candidate = evaluate_candidate(
            kitchen_rank=kitchen_rank,
            symbol=symbol,
            usdt_result=usdt_result,
            btc_result=btc_result,
        )
        evaluated.append(candidate)

    strong_candidates = select_strong_movers(
        evaluated, top_n=config.top_n
    )

    strong_results: List[StrongMoverResult] = []
    for candidate in strong_candidates:
        result = build_strong_mover_result(
            candidate, timeframe=config.timeframe
        )
        strong_results.append(result)

    return StrongMoversOutput(
        selected_exchange=config.selected_exchange,
        display_fallback_priority=[e.value for e in DISPLAY_FALLBACK_PRIORITY],
        timeframe=config.timeframe,
        ranking_version=ranking_version,
        strong_movers=strong_results,
        candidate_count=len(candidates),
        selected_count=len(strong_results),
        scanner_warning=SCANNER_WARNING,
        valid=len(strong_results) > 0,
        errors=errors,
    )
