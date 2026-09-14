"""Stage 11 — Unit 11.1 — Stage Contract + Candidate Universe tests.

Deterministic/synthetic tests only. No live network calls.
"""
from __future__ import annotations

import pytest

from app.analysis.stage11_strong_movers import (
    build_candidate_universe,
    get_ranking_version,
    StrongMoversConfig,
)
from app.config.quality import TOP_N
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
    """Generate 125 assets: BTC rank 1, ETH rank 2, USDT rank 3, alts 4-125."""
    assets = []
    for i in range(TOP_N):
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


# ---------------------------------------------------------------------------
# Candidate range
# ---------------------------------------------------------------------------


def test_candidates_are_ranks_11_to_125():
    assets = _make_full_top125()
    candidates = build_candidate_universe(assets)
    ranks = [int(a["calculated_rank"]) for a in candidates]
    assert min(ranks) == 11
    assert max(ranks) == 125


def test_candidate_count_115():
    assets = _make_full_top125()
    candidates = build_candidate_universe(assets)
    assert len(candidates) == 115


def test_btc_rank_1_excluded():
    assets = _make_full_top125()
    candidates = build_candidate_universe(assets)
    symbols = [a["symbol"] for a in candidates]
    assert "BTC" not in symbols


def test_rank_10_excluded():
    assets = _make_full_top125()
    candidates = build_candidate_universe(assets)
    ranks = [int(a["calculated_rank"]) for a in candidates]
    assert 10 not in ranks


def test_rank_126_excluded():
    assets = _make_full_top125()
    assets.append(
        _make_asset(
            symbol="A126",
            market_cap=0.0,
            canonical_asset_id="cmc:1126",
            provider_rank=126,
        )
    )
    candidates = build_candidate_universe(assets)
    ranks = [int(a["calculated_rank"]) for a in candidates]
    assert 126 not in ranks


def test_rank_11_included():
    assets = _make_full_top125()
    candidates = build_candidate_universe(assets)
    ranks = [int(a["calculated_rank"]) for a in candidates]
    assert 11 in ranks


def test_rank_125_included():
    assets = _make_full_top125()
    candidates = build_candidate_universe(assets)
    ranks = [int(a["calculated_rank"]) for a in candidates]
    assert 125 in ranks


def test_candidates_sorted_by_rank():
    assets = _make_full_top125()
    candidates = build_candidate_universe(assets)
    ranks = [int(a["calculated_rank"]) for a in candidates]
    assert ranks == sorted(ranks)


# ---------------------------------------------------------------------------
# Dynamic refresh — changed ranking reflected
# ---------------------------------------------------------------------------


def test_changed_ranking_reflected():
    assets_v1 = _make_full_top125()
    candidates_v1 = build_candidate_universe(assets_v1)
    symbols_v1 = [a["symbol"] for a in candidates_v1]

    assets_v2 = _make_full_top125()
    for a in assets_v2:
        if a["symbol"] == "A11":
            a["market_cap"] = 2_000_000_000.0
        if a["symbol"] == "A12":
            a["market_cap"] = 500_000.0

    candidates_v2 = build_candidate_universe(assets_v2)
    symbols_v2 = [a["symbol"] for a in candidates_v2]

    assert symbols_v1 != symbols_v2


def test_no_permanently_cached_candidates():
    assets = _make_full_top125()
    result_1 = build_candidate_universe(assets)
    symbols_1 = {a["symbol"] for a in result_1}

    for a in assets:
        if a["symbol"] == "A11":
            a["market_cap"] = 2_000_000_000.0

    result_2 = build_candidate_universe(assets)
    symbols_2 = {a["symbol"] for a in result_2}
    assert symbols_1 != symbols_2


# ---------------------------------------------------------------------------
# Ranking version
# ---------------------------------------------------------------------------


def test_ranking_version_present():
    assets = _make_full_top125()
    version = get_ranking_version(assets)
    assert version != ""


def test_ranking_version_from_u065():
    assets = _make_full_top125()
    from app.market.ranking import RANKING_VERSION
    version = get_ranking_version(assets)
    assert version == RANKING_VERSION


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_empty_assets_returns_empty():
    candidates = build_candidate_universe([])
    assert candidates == []


def test_insufficient_assets():
    assets = [_make_asset(symbol="A1", market_cap=100.0)]
    candidates = build_candidate_universe(assets)
    assert candidates == []
