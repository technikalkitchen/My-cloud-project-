"""Stage 12 — Unit 12.1 — Stage Contract + Candidate Pool tests.

Deterministic/synthetic tests only. No live network calls.
"""
from __future__ import annotations

import pytest

from app.analysis.stage12_top3 import (
    build_candidate_pool,
    TOP_N,
)
from app.config.quality import TOP_N as TOP_N_CONFIG
from app.market.ranking import dynamic_rank_assets


def _make_asset(
    symbol="A",
    market_cap=None,
    canonical_asset_id=None,
    provider_rank=None,
    **extra,
):
    asset = {
        "provider_asset_id": canonical_asset_id or f"id_{symbol}",
        "canonical_asset_id": canonical_asset_id or f"id_{symbol}",
        "symbol": symbol,
        "name": symbol,
        "provider": "TEST",
        "provider_mode": "TEST",
        "provider_rank": provider_rank,
        "price": 100.0,
        "market_cap": market_cap,
        "volume_24h": 1_000_000.0,
        "source_timestamp": "2026-09-11T16:29:00+00:00",
        "retrieved_at": "2026-09-11T16:30:00+00:00",
        "identity_status": "VALIDATED",
    }
    asset.update(extra)
    return asset


def _make_full_top125():
    assets = []
    for i in range(TOP_N_CONFIG):
        if i == 0:
            symbol = "BTC"
        elif i == 1:
            symbol = "ETH"
        elif i == 2:
            symbol = "USDT"
        else:
            symbol = f"A{i}"
        assets.append(
            _make_asset(
                symbol=symbol,
                market_cap=float(1_000_000_000 - i * 1_000_000),
                canonical_asset_id=f"cmc:{1000 + i}",
                provider_rank=i + 1,
            )
        )
    return assets


def _make_top10_assets(assets):
    from app.analysis.stage10_consumer import select_ranks
    ranking = dynamic_rank_assets(assets)
    return select_ranks(ranking["top125"], min_rank=2, max_rank=10)


def _make_strong_mover_result(symbol, rank, change=5.0, volume=200_000_000.0, valid=True):
    from app.analysis.stage12_top3 import Top3Candidate
    return Top3Candidate(
        symbol=symbol,
        kitchen_rank=rank,
        canonical_asset_id=f"cmc:{1000 + rank}",
        in_top10=False,
        in_strong_movers=True,
        usdt_change_pct=change,
        usdt_volume=volume,
        usdt_pair=f"{symbol}USDT",
        usdt_actual_exchange="Binance",
        usdt_fallback_used=False,
        usdt_fallback_exchange=None,
        usdt_valid=valid,
        usdt_source=f"Source: Binance",
        btc_change_pct=None,
        btc_pair=f"{symbol}BTC",
        btc_actual_exchange="",
        btc_fallback_used=False,
        btc_fallback_exchange=None,
        btc_available=False,
        btc_valid=False,
        btc_source="",
        movement_score=0.0,
        reliability_score=0.0,
        total_score=0.0,
        reliability_evidence={},
    )


# ---------------------------------------------------------------------------
# Pool composition
# ---------------------------------------------------------------------------


def test_pool_combines_top10_and_strong_movers():
    assets = _make_full_top125()
    top10 = _make_top10_assets(assets)
    movers = [_make_strong_mover_result(f"A{i}", i) for i in range(11, 16)]
    pool = build_candidate_pool(top10, movers, assets)
    assert len(pool) == 14  # 9 Top10 + 5 Strong (no overlap)


def test_pool_deduplicates_overlap():
    assets = _make_full_top125()
    top10 = _make_top10_assets(assets)
    movers = [_make_strong_mover_result("ETH", 2)]
    pool = build_candidate_pool(top10, movers, assets)
    symbols = [c.symbol for c in pool]
    assert symbols.count("ETH") == 1


def test_pool_preserves_canonical_identity():
    assets = _make_full_top125()
    top10 = _make_top10_assets(assets)
    movers = []
    pool = build_candidate_pool(top10, movers, assets)
    for candidate in pool:
        assert candidate.canonical_asset_id.startswith("cmc:")


def test_pool_top10_flags():
    assets = _make_full_top125()
    top10 = _make_top10_assets(assets)
    movers = []
    pool = build_candidate_pool(top10, movers, assets)
    for candidate in pool:
        assert candidate.in_top10 is True
        assert candidate.in_strong_movers is False


def test_pool_strong_mover_flags():
    assets = _make_full_top125()
    top10 = _make_top10_assets(assets)
    movers = [_make_strong_mover_result("A11", 11)]
    pool = build_candidate_pool(top10, movers, assets)
    a11 = [c for c in pool if c.symbol == "A11"]
    assert len(a11) == 1
    assert a11[0].in_strong_movers is True
    assert a11[0].in_top10 is False


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------


def test_no_duplicate_canonical_ids():
    assets = _make_full_top125()
    top10 = _make_top10_assets(assets)
    movers = []
    for i in range(5):
        movers.append(_make_strong_mover_result(f"A{i + 11}", i + 11))
    pool = build_candidate_pool(top10, movers, assets)
    canonical_ids = [c.canonical_asset_id for c in pool]
    assert len(canonical_ids) == len(set(canonical_ids))


def test_top10_takes_precedence_on_overlap():
    assets = _make_full_top125()
    top10 = _make_top10_assets(assets)
    movers = [_make_strong_mover_result("ETH", 2, valid=False)]
    pool = build_candidate_pool(top10, movers, assets)
    eth = [c for c in pool if c.symbol == "ETH"]
    assert len(eth) == 1
    assert eth[0].in_top10 is True


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_empty_pools():
    pool = build_candidate_pool([], [], [])
    assert pool == []


def test_empty_top10():
    assets = _make_full_top125()
    movers = [_make_strong_mover_result("A11", 11)]
    pool = build_candidate_pool([], movers, assets)
    assert len(pool) == 1


def test_empty_strong_movers():
    assets = _make_full_top125()
    top10 = _make_top10_assets(assets)
    pool = build_candidate_pool(top10, [], assets)
    assert len(pool) == 9


def test_pool_preserves_rank():
    assets = _make_full_top125()
    top10 = _make_top10_assets(assets)
    movers = []
    pool = build_candidate_pool(top10, movers, assets)
    for candidate in pool:
        assert candidate.kitchen_rank >= 2
        assert candidate.kitchen_rank <= 10


def test_pool_with_invalid_assets():
    assets = [_make_asset(symbol="A1", market_cap=100.0)]
    top10 = []
    movers = []
    pool = build_candidate_pool(top10, movers, assets)
    assert pool == []
