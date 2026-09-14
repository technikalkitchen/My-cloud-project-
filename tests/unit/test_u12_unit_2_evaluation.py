"""Stage 12 — Unit 12.2 — Strong Movement + Reliability Evaluation tests.

Deterministic/synthetic tests only. No live network calls.
"""
from __future__ import annotations

import pytest

from app.analysis.stage10_usdt import UsdtPairResult
from app.analysis.stage10_btc import BtcPairResult
from app.analysis.stage12_top3 import (
    evaluate_candidate,
    select_top3,
    _top3_movement_score,
    _top3_reliability_score,
    Top3Candidate,
)


# ---------------------------------------------------------------------------
# Movement scoring
# ---------------------------------------------------------------------------


def test_movement_score_positive():
    score = _top3_movement_score(5.0, 200_000_000.0)
    assert score > 0
    assert score > _top3_movement_score(5.0, 0.0)


def test_movement_score_negative():
    score = _top3_movement_score(-5.0, 200_000_000.0)
    assert score > 0


def test_movement_score_none():
    assert _top3_movement_score(None, 200_000_000.0) == 0.0
    assert _top3_movement_score(None, None) == 0.0


def test_movement_score_zero_move_zero_vol():
    assert _top3_movement_score(0.0, 0.0) == 0.0


def test_movement_score_volume_support():
    high_vol = _top3_movement_score(5.0, 500_000_000.0)
    low_vol = _top3_movement_score(5.0, 1_000_000.0)
    assert high_vol > low_vol


def test_movement_score_no_volume_halved():
    with_vol = _top3_movement_score(10.0, 100_000_000.0)
    no_vol = _top3_movement_score(10.0, None)
    assert with_vol > no_vol
    assert no_vol == 5.0


# ---------------------------------------------------------------------------
# Reliability scoring
# ---------------------------------------------------------------------------


def test_reliability_high():
    score = _top3_reliability_score(
        usdt_valid=True,
        btc_available=True,
        btc_valid=True,
        usdt_volume=500_000_000.0,
        change_pct=5.0,
    )
    assert score >= 8.0


def test_reliability_minimal():
    score = _top3_reliability_score(
        usdt_valid=False,
        btc_available=False,
        btc_valid=False,
        usdt_volume=None,
        change_pct=None,
    )
    assert score == 1.0


def test_reliability_bonus_btc():
    with_btc = _top3_reliability_score(
        usdt_valid=True, btc_available=True, btc_valid=True,
        usdt_volume=100_000_000.0, change_pct=1.0,
    )
    without_btc = _top3_reliability_score(
        usdt_valid=True, btc_available=False, btc_valid=False,
        usdt_volume=100_000_000.0, change_pct=1.0,
    )
    assert with_btc > without_btc


def test_reliability_volume_tiers():
    huge = _top3_reliability_score(True, False, False, 5_000_000_000.0, 1.0)
    medium = _top3_reliability_score(True, False, False, 100_000_000.0, 1.0)
    small = _top3_reliability_score(True, False, False, 1_000_000.0, 1.0)
    assert huge > medium
    assert medium > small


# ---------------------------------------------------------------------------
# Candidate evaluation
# ---------------------------------------------------------------------------


def _make_usdt_result(
    symbol="SOLUSDT", change_pct=5.0, volume=200_000_000.0,
    exchange="Binance", fallback_used=False,
    fallback_exchange=None, valid=True, **kwargs,
):
    return UsdtPairResult(
        symbol=symbol, change_pct=change_pct, volume=volume,
        timestamp="2026-09-14T15:30:00+00:00",
        requested_exchange="Bybit", actual_exchange=exchange,
        fallback_used=fallback_used, fallback_exchange=fallback_exchange,
        timeframe="5m",
        volume_source_label=f"Source: {exchange}" if not fallback_used else f"Fallback from: {exchange}",
        valid=valid, errors=[], provenance={}, **kwargs,
    )


def _make_btc_result(
    symbol="SOLBTC", change_pct=1.0, exchange="Binance", valid=True,
    fallback_used=False, fallback_exchange=None, **kwargs,
):
    return BtcPairResult(
        symbol=symbol, change_pct=change_pct,
        timestamp="2026-09-14T15:30:00+00:00",
        requested_exchange="Bybit", actual_exchange=exchange,
        fallback_used=fallback_used, fallback_exchange=fallback_exchange,
        usdt_fallback_exchange=None, calculated_kitchen_value=None,
        calculated_kitchen_used=False, timeframe="5m",
        valid=valid, errors=[], provenance={}, **kwargs,
    )


def _btc_source_label(requested: str, actual: str, fallback_used: bool) -> str:
    if fallback_used and actual:
        return f"Fallback from: {actual}"
    if actual:
        return f"Source: {actual}"
    return "Source"


def _make_candidate(
    symbol="SOL", rank=15, usdt=None, btc=None, **kwargs,
):
    return Top3Candidate(
        symbol=symbol, kitchen_rank=rank,
        canonical_asset_id=f"cmc:{1000 + rank}",
        in_top10=False, in_strong_movers=True,
        usdt_change_pct=usdt.change_pct if usdt else None,
        usdt_volume=usdt.volume if usdt else None,
        usdt_pair=f"{symbol}USDT",
        usdt_actual_exchange=usdt.actual_exchange if usdt else "",
        usdt_fallback_used=usdt.fallback_used if usdt else False,
        usdt_fallback_exchange=usdt.fallback_exchange if usdt else None,
        usdt_valid=usdt.valid if usdt else False,
        usdt_source=usdt.volume_source_label if usdt else "",
        btc_change_pct=btc.change_pct if btc else None,
        btc_pair=f"{symbol}BTC",
        btc_actual_exchange=btc.actual_exchange if btc else "",
        btc_fallback_used=btc.fallback_used if btc else False,
        btc_fallback_exchange=btc.fallback_exchange if btc else None,
        btc_available=btc is not None,
        btc_valid=btc.valid if btc else False,
        btc_source=_btc_source_label(
            "Bybit",
            btc.actual_exchange if btc else "",
            btc.fallback_used if btc else False,
        ) if btc else "",
        movement_score=0.0, reliability_score=0.0, total_score=0.0,
        reliability_evidence={},
        valid=(usdt.valid if usdt else False) or (btc is not None),
        **kwargs,
    )


def test_evaluate_valid_usdt_btc():
    usdt = _make_usdt_result(valid=True)
    btc = _make_btc_result(valid=True)
    candidate = _make_candidate(usdt=usdt, btc=btc)
    result = evaluate_candidate(candidate)
    assert result.symbol == "SOL"
    assert result.kitchen_rank == 15
    assert result.usdt_valid is True
    assert result.btc_available is True
    assert result.btc_valid is True
    assert result.total_score > 0
    assert result.movement_score > 0
    assert result.reliability_score > 0
    assert "usdt_valid" in result.reliability_evidence
    assert "btc_available" in result.reliability_evidence


def test_evaluate_usdt_only_no_btc():
    usdt = _make_usdt_result(valid=True)
    candidate = _make_candidate(usdt=usdt, btc=None)
    result = evaluate_candidate(candidate)
    assert result.usdt_valid is True
    assert result.btc_available is False
    assert result.total_score > 0


def test_evaluate_invalid_usdt():
    usdt = _make_usdt_result(valid=False)
    candidate = _make_candidate(usdt=usdt, btc=None)
    result = evaluate_candidate(candidate)
    assert result.usdt_valid is False
    assert result.total_score < 10


def test_evaluate_none_results():
    candidate = _make_candidate(usdt=None, btc=None)
    result = evaluate_candidate(candidate)
    assert result.usdt_change_pct is None
    assert result.usdt_volume is None
    assert result.usdt_valid is False
    assert result.btc_available is False
    assert result.total_score == 1.0
    assert result.valid is False


# ---------------------------------------------------------------------------
# Top 3 selection — NOT Top 3 by gain
# ---------------------------------------------------------------------------


def test_select_top3_when_valid():
    candidates = []
    for i in range(11, 21):
        usdt = _make_usdt_result(
            symbol=f"A{i}USDT", change_pct=float(i), valid=True,
        )
        btc = _make_btc_result(symbol=f"A{i}BTC", valid=True)
        candidates.append(_make_candidate(symbol=f"A{i}", rank=i, usdt=usdt, btc=btc))
    selected = select_top3(candidates, top_n=3)
    assert len(selected) == 3


def test_selection_is_movement_plus_reliability():
    high_move_weak = _make_candidate(
        symbol="FAST", rank=11,
        usdt=_make_usdt_result(
            symbol="FASTUSDT", change_pct=50.0, volume=100_000.0, valid=True
        ),
        btc=None,
    )
    moderate_move_strong = _make_candidate(
        symbol="STABLE", rank=12,
        usdt=_make_usdt_result(
            symbol="STABLEUSDT", change_pct=3.0, volume=500_000_000.0, valid=True
        ),
        btc=_make_btc_result(symbol="STABLEBTC", valid=True),
    )
    candidates = [high_move_weak, moderate_move_strong]
    selected = select_top3(candidates, top_n=1)
    assert len(selected) == 1


def test_fewer_than_3_when_insufficient():
    candidates = [
        _make_candidate(symbol="A11", rank=11, usdt=None, btc=None),
        _make_candidate(symbol="A12", rank=12, usdt=None, btc=None),
    ]
    selected = select_top3(candidates, top_n=3)
    assert len(selected) == 0


def test_never_fabricates_assets():
    candidates = [
        _make_candidate(symbol="A11", rank=11, usdt=None, btc=None),
        _make_candidate(
            symbol="A12", rank=12,
            usdt=_make_usdt_result(valid=True), btc=None,
        ),
    ]
    selected = select_top3(candidates, top_n=3)
    assert len(selected) <= 1
    for c in selected:
        assert c.usdt_valid or c.btc_available


def test_top3_exactly_three():
    candidates = []
    for i in range(11, 21):
        usdt = _make_usdt_result(
            symbol=f"A{i}USDT", change_pct=float(i), valid=True,
        )
        btc = _make_btc_result(symbol=f"A{i}BTC", valid=True)
        candidates.append(_make_candidate(symbol=f"A{i}", rank=i, usdt=usdt, btc=btc))
    selected = select_top3(candidates, top_n=3)
    assert len(selected) == 3


def test_deterministic_ordering():
    candidates = []
    for i in range(11, 21):
        usdt = _make_usdt_result(
            symbol=f"A{i}USDT", change_pct=float(i), valid=True,
        )
        btc = _make_btc_result(symbol=f"A{i}BTC", valid=True)
        candidates.append(_make_candidate(symbol=f"A{i}", rank=i, usdt=usdt, btc=btc))
    selected1 = select_top3(candidates, top_n=3)
    selected2 = select_top3(candidates, top_n=3)
    for c1, c2 in zip(selected1, selected2):
        assert c1.total_score == c2.total_score
        assert c1.symbol == c2.symbol


def test_no_duplicate_symbols():
    candidates = []
    for i in range(11, 21):
        usdt = _make_usdt_result(
            symbol=f"A{i}USDT", change_pct=float(i), valid=True,
        )
        btc = _make_btc_result(symbol=f"A{i}BTC", valid=True)
        candidates.append(_make_candidate(symbol=f"A{i}", rank=i, usdt=usdt, btc=btc))
    selected = select_top3(candidates, top_n=3)
    symbols = [c.symbol for c in selected]
    assert len(symbols) == len(set(symbols))


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_empty_candidates():
    selected = select_top3([], top_n=3)
    assert selected == []


def test_extreme_movement_accepted():
    usdt = _make_usdt_result(change_pct=999.99, valid=True)
    candidate = _make_candidate(symbol="MOOM", rank=15, usdt=usdt, btc=None)
    result = evaluate_candidate(candidate)
    assert result.usdt_change_pct == 999.99
    assert result.total_score > 0


def test_negative_change_pct_accepted():
    usdt = _make_usdt_result(change_pct=-8.5, valid=True)
    candidate = _make_candidate(symbol="DROP", rank=15, usdt=usdt, btc=None)
    result = evaluate_candidate(candidate)
    assert result.usdt_change_pct == -8.5
    assert result.movement_score > 0


def test_no_signal_language_in_scores():
    candidates = []
    for i in range(11, 16):
        usdt = _make_usdt_result(
            symbol=f"A{i}USDT", change_pct=float(i), valid=True,
        )
        btc = _make_btc_result(symbol=f"A{i}BTC", valid=True)
        candidates.append(_make_candidate(symbol=f"A{i}", rank=i, usdt=usdt, btc=btc))
    selected = select_top3(candidates, top_n=3)
    for c in selected:
        assert "BUY" not in str(c.reliability_evidence).upper()
        assert "SELL" not in str(c.reliability_evidence).upper()
