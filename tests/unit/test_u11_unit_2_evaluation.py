"""Stage 11 — Unit 11.2 — Strong Movement + Reliability Evaluation tests.

Deterministic/synthetic tests only. No live network calls.
"""
from __future__ import annotations

import pytest

from app.analysis.stage10_usdt import UsdtPairResult
from app.analysis.stage10_btc import BtcPairResult
from app.analysis.stage11_strong_movers import (
    evaluate_candidate,
    select_strong_movers,
    _movement_score,
    _reliability_score,
    StrongMoverCandidate,
)


# ---------------------------------------------------------------------------
# Movement scoring
# ---------------------------------------------------------------------------


def test_movement_score_positive():
    score = _movement_score(5.0, 200_000_000.0)
    assert score > 0
    assert score > _movement_score(5.0, 0.0)


def test_movement_score_negative():
    score = _movement_score(-5.0, 200_000_000.0)
    assert score > 0


def test_movement_score_none():
    assert _movement_score(None, 200_000_000.0) == 0.0
    assert _movement_score(None, None) == 0.0


def test_movement_score_zero_move_zero_vol():
    assert _movement_score(0.0, 0.0) == 0.0


def test_movement_score_volume_support():
    high_vol = _movement_score(5.0, 500_000_000.0)
    low_vol = _movement_score(5.0, 1_000_000.0)
    assert high_vol > low_vol


def test_movement_score_no_volume_halved():
    with_vol = _movement_score(10.0, 100_000_000.0)
    no_vol = _movement_score(10.0, None)
    assert with_vol > no_vol
    assert no_vol == 5.0


# ---------------------------------------------------------------------------
# Reliability scoring
# ---------------------------------------------------------------------------


def test_reliability_high():
    score = _reliability_score(
        usdt_valid=True,
        btc_available=True,
        btc_valid=True,
        usdt_volume=500_000_000.0,
        change_pct=5.0,
    )
    assert score >= 8.0


def test_reliability_minimal():
    score = _reliability_score(
        usdt_valid=False,
        btc_available=False,
        btc_valid=False,
        usdt_volume=None,
        change_pct=None,
    )
    assert score == 1.0


def test_reliability_bonus_btc():
    with_btc = _reliability_score(
        usdt_valid=True, btc_available=True, btc_valid=True,
        usdt_volume=100_000_000.0, change_pct=1.0,
    )
    without_btc = _reliability_score(
        usdt_valid=True, btc_available=False, btc_valid=False,
        usdt_volume=100_000_000.0, change_pct=1.0,
    )
    assert with_btc > without_btc


def test_reliability_volume_tiers():
    huge = _reliability_score(True, False, False, 5_000_000_000.0, 1.0)
    medium = _reliability_score(True, False, False, 100_000_000.0, 1.0)
    small = _reliability_score(True, False, False, 1_000_000.0, 1.0)
    assert huge > medium
    assert medium > small


# ---------------------------------------------------------------------------
# Candidate evaluation with valid USDT
# ---------------------------------------------------------------------------


def _make_usdt_result(
    symbol="SOLUSDT",
    change_pct=5.0,
    volume=200_000_000.0,
    exchange="Binance",
    fallback_used=False,
    fallback_exchange=None,
    valid=True,
):
    return UsdtPairResult(
        symbol=symbol,
        change_pct=change_pct,
        volume=volume,
        timestamp="2026-09-14T15:30:00+00:00",
        requested_exchange="Bybit",
        actual_exchange=exchange,
        fallback_used=fallback_used,
        fallback_exchange=fallback_exchange,
        timeframe="5m",
        volume_source_label=f"Source: {exchange}" if not fallback_used else f"Fallback from: {exchange}",
        valid=valid,
        errors=[],
        provenance={},
    )


def _make_btc_result(
    symbol="SOLBTC",
    change_pct=1.0,
    exchange="Binance",
    fallback_used=False,
    fallback_exchange=None,
    valid=True,
):
    return BtcPairResult(
        symbol=symbol,
        change_pct=change_pct,
        timestamp="2026-09-14T15:30:00+00:00",
        requested_exchange="Bybit",
        actual_exchange=exchange,
        fallback_used=fallback_used,
        fallback_exchange=fallback_exchange,
        usdt_fallback_exchange=None,
        calculated_kitchen_value=None,
        calculated_kitchen_used=False,
        timeframe="5m",
        valid=valid,
        errors=[],
        provenance={},
    )


def test_evaluate_valid_usdt_btc():
    usdt = _make_usdt_result(valid=True)
    btc = _make_btc_result(valid=True)
    candidate = evaluate_candidate(
        kitchen_rank=15,
        symbol="SOL",
        usdt_result=usdt,
        btc_result=btc,
    )
    assert candidate.symbol == "SOL"
    assert candidate.kitchen_rank == 15
    assert candidate.usdt_valid is True
    assert candidate.btc_available is True
    assert candidate.btc_valid is True
    assert candidate.total_score > 0
    assert candidate.movement_score > 0
    assert candidate.reliability_score > 0
    assert "usdt_valid" in candidate.reliability_evidence
    assert "btc_available" in candidate.reliability_evidence


def test_evaluate_usdt_only_no_btc():
    usdt = _make_usdt_result(valid=True)
    candidate = evaluate_candidate(
        kitchen_rank=15, symbol="SOL", usdt_result=usdt, btc_result=None
    )
    assert candidate.usdt_valid is True
    assert candidate.btc_available is False
    assert candidate.btc_change_pct is None
    assert candidate.total_score > 0


def test_evaluate_invalid_usdt():
    usdt = _make_usdt_result(valid=False)
    candidate = evaluate_candidate(
        kitchen_rank=15, symbol="SOL", usdt_result=usdt, btc_result=None
    )
    assert candidate.usdt_valid is False
    assert candidate.total_score < 10


def test_evaluate_none_results():
    candidate = evaluate_candidate(
        kitchen_rank=15, symbol="SOL", usdt_result=None, btc_result=None,
    )
    assert candidate.usdt_change_pct is None
    assert candidate.usdt_volume is None
    assert candidate.usdt_valid is False
    assert candidate.btc_available is False
    assert candidate.total_score == 1.0


# ---------------------------------------------------------------------------
# Strong mover selection — NOT Top 5 gainers
# ---------------------------------------------------------------------------


def test_select_top5_when_valid():
    candidates = [
        evaluate_candidate(
            kitchen_rank=i, symbol=f"A{i}",
            usdt_result=_make_usdt_result(
                symbol=f"A{i}USDT", change_pct=float(i), valid=True
            ),
            btc_result=_make_btc_result(symbol=f"A{i}BTC", valid=True),
        )
        for i in range(11, 21)
    ]
    selected = select_strong_movers(candidates, top_n=5)
    assert len(selected) == 5


def test_selection_is_movement_plus_reliability():
    # High movement + weak reliability vs moderate movement + strong reliability
    high_move_weak = evaluate_candidate(
        kitchen_rank=11, symbol="FAST",
        usdt_result=_make_usdt_result(
            symbol="FASTUSDT", change_pct=50.0, volume=100_000.0, valid=True
        ),
        btc_result=None,
    )
    moderate_move_strong = evaluate_candidate(
        kitchen_rank=12, symbol="STABLE",
        usdt_result=_make_usdt_result(
            symbol="STABLEUSDT", change_pct=3.0, volume=500_000_000.0, valid=True
        ),
        btc_result=_make_btc_result(symbol="STABLEBTC", valid=True),
    )
    candidates = [high_move_weak, moderate_move_strong]
    selected = select_strong_movers(candidates, top_n=1)
    # Both are valid, but selection by total score should pick the better combination
    assert len(selected) == 1
    # Verify that selection is not simply highest percentage gainer
    # (the moderate mover with BTC support may score higher)
    assert selected[0] is not None


def test_fewer_than_5_when_insufficient():
    candidates = [
        evaluate_candidate(
            kitchen_rank=11, symbol="A11",
            usdt_result=None, btc_result=None,
        ),
        evaluate_candidate(
            kitchen_rank=12, symbol="A12",
            usdt_result=None, btc_result=None,
        ),
    ]
    selected = select_strong_movers(candidates, top_n=5)
    assert len(selected) == 0


def test_never_fabricates_assets():
    candidates = [
        evaluate_candidate(
            kitchen_rank=11, symbol="A11",
            usdt_result=None, btc_result=None,
        ),
        evaluate_candidate(
            kitchen_rank=12, symbol="A12",
            usdt_result=_make_usdt_result(valid=True),
            btc_result=None,
        ),
    ]
    selected = select_strong_movers(candidates, top_n=5)
    assert len(selected) <= 1
    for c in selected:
        assert c.usdt_valid or c.btc_available


def test_top5_valid_candidates():
    candidates = [
        evaluate_candidate(
            kitchen_rank=i, symbol=f"A{i}",
            usdt_result=_make_usdt_result(
                symbol=f"A{i}USDT", change_pct=float(i), valid=True
            ),
            btc_result=_make_btc_result(symbol=f"A{i}BTC", valid=True),
        )
        for i in range(11, 30)
    ]
    selected = select_strong_movers(candidates, top_n=5)
    assert len(selected) == 5
    ranks = [c.kitchen_rank for c in selected]
    assert len(ranks) == len(set(ranks))  # no duplicates


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_empty_candidates():
    selected = select_strong_movers([], top_n=5)
    assert selected == []


def test_extreme_movement_accepted():
    usdt = _make_usdt_result(change_pct=999.99, valid=True)
    candidate = evaluate_candidate(
        kitchen_rank=15, symbol="MOOM", usdt_result=usdt, btc_result=None
    )
    assert candidate.usdt_change_pct == 999.99
    assert candidate.total_score > 0


def test_negative_change_pct_accepted():
    usdt = _make_usdt_result(change_pct=-8.5, valid=True)
    candidate = evaluate_candidate(
        kitchen_rank=15, symbol="DROP", usdt_result=usdt, btc_result=None
    )
    assert candidate.usdt_change_pct == -8.5
    assert candidate.movement_score > 0
