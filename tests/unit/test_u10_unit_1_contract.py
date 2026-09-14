"""Stage 10 — Unit 10.1 — Stage Contract + Dynamic Top-10 Consumer tests.

Deterministic/synthetic tests only. No live network calls.
"""
from __future__ import annotations

from app.analysis.stage10_consumer import (
    DISPLAY_FALLBACK_PRIORITY,
    Exchange,
    View,
    get_dynamic_top10,
    select_ranks,
    Stage10Config,
)
from app.config.quality import TOP_N


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
    """Generate 125 assets with BTC at rank 1, ETH rank 2, etc."""
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
# View selection
# ---------------------------------------------------------------------------


def test_kitchen_view_default():
    cfg = Stage10Config()
    assert cfg.view == View.KITCHEN


def test_view_exchange_explicit():
    cfg = Stage10Config(view=View.EXCHANGE, selected_exchange=Exchange.BINANCE)
    assert cfg.view == View.EXCHANGE
    assert cfg.selected_exchange == Exchange.BINANCE


def test_display_fallback_priority_has_8_exchanges():
    assert len(DISPLAY_FALLBACK_PRIORITY) == 8
    names = [e.value for e in DISPLAY_FALLBACK_PRIORITY]
    assert names == [
        "Binance", "OKX", "Bybit", "KuCoin",
        "Coinbase", "Gate", "Upbit", "Bitget",
    ]


# ---------------------------------------------------------------------------
# Rank 1 excluded, ranks 2-10 selected
# ---------------------------------------------------------------------------


def test_rank_1_excluded():
    assets = _make_full_top125()
    result = get_dynamic_top10(assets, view="KITCHEN")
    symbols = [a["symbol"] for a in result.assets]
    assert "BTC" not in symbols


def test_ranks_2_10_selected():
    assets = _make_full_top125()
    result = get_dynamic_top10(assets, view="KITCHEN")
    assert len(result.assets) == 9
    ranks = [a["kitchen_rank"] for a in result.assets]
    assert ranks == list(range(2, 11))


def test_top_assets_are_eth_usdt_and_alts():
    assets = _make_full_top125()
    result = get_dynamic_top10(assets, view="KITCHEN")
    symbols = [a["symbol"] for a in result.assets]
    assert symbols[0] == "ETH"
    assert symbols[1] == "USDT"


# ---------------------------------------------------------------------------
# Dynamic refresh — changed ranking on new request
# ---------------------------------------------------------------------------


def test_changed_ranking_appears_on_new_request():
    assets_v1 = _make_full_top125()
    result_v1 = get_dynamic_top10(assets_v1, view="KITCHEN")
    symbols_v1 = [a["symbol"] for a in result_v1.assets]

    assets_v2 = _make_full_top125()
    for a in assets_v2:
        if a["symbol"] == "ETH":
            a["market_cap"] = 500_000_000.0
        if a["symbol"] == "A3":
            a["market_cap"] = 995_000_000.0

    result_v2 = get_dynamic_top10(assets_v2, view="KITCHEN")
    symbols_v2 = [a["symbol"] for a in result_v2.assets]

    assert symbols_v2 != symbols_v1


def test_no_permanently_stale_top10():
    assets = _make_full_top125()
    result_1 = get_dynamic_top10(assets, view="KITCHEN")

    for a in assets:
        if a["symbol"] == "A4":
            a["market_cap"] = 900_000_000.0
        if a["symbol"] == "A5":
            a["market_cap"] = 800_000_000.0

    result_2 = get_dynamic_top10(assets, view="KITCHEN")

    symbols_1 = {a["symbol"] for a in result_1.assets}
    symbols_2 = {a["symbol"] for a in result_2.assets}
    assert symbols_1 != symbols_2


# ---------------------------------------------------------------------------
# select_ranks helper
# ---------------------------------------------------------------------------


def test_select_ranks_2_10():
    assets = _make_full_top125()
    from app.market.ranking import dynamic_rank_assets
    ranking = dynamic_rank_assets(assets)
    selected = select_ranks(ranking["top125"], min_rank=2, max_rank=10)
    assert len(selected) == 9
    ranks = [a["kitchen_rank"] for a in selected]
    assert ranks == list(range(2, 11))


def test_select_ranks_excludes_rank_1():
    assets = _make_full_top125()
    from app.market.ranking import dynamic_rank_assets
    ranking = dynamic_rank_assets(assets)
    selected = select_ranks(ranking["top125"], min_rank=2, max_rank=10)
    symbols = [a["symbol"] for a in selected]
    assert "BTC" not in symbols


# ---------------------------------------------------------------------------
# Stage 10 result contract
# ---------------------------------------------------------------------------


def test_result_has_view_and_fallback():
    assets = _make_full_top125()
    result = get_dynamic_top10(assets, view="EXCHANGE", selected_exchange="OKX")
    assert result.view == "EXCHANGE"
    assert result.selected_exchange == "OKX"
    assert isinstance(result.display_fallback_priority, list)
    assert len(result.display_fallback_priority) == 8
    assert result.raw_ranking_status in ("VALIDATED", "DATA_PARTIAL")


def test_result_tracking():
    assets = _make_full_top125()
    result = get_dynamic_top10(assets, view="KITCHEN")
    assert result.total_ranked == TOP_N
    assert result.ranking_version != ""
    assert len(result.assets) == 9
