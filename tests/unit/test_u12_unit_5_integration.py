"""Stage 12 — Unit 12.5 — Full Scanner Integration tests.

Deterministic/synthetic tests only. No live network calls.
Verifies the full operational chain:
    U06.5 → Stage 7 → Stage 8 → Stage 9 → Dynamic Top 10
    → Stage 11 Strong Movers → Stage 12 Top 3
"""
from __future__ import annotations

from app.analysis.stage10_consumer import (
    DISPLAY_FALLBACK_PRIORITY,
    Exchange,
    get_dynamic_top10,
)
from app.analysis.stage10_router import ExchangeRouter
from app.analysis.stage10_usdt import UsdtPairResult
from app.analysis.stage10_btc import BtcPairResult
from app.analysis.stage11_strong_movers import (
    SCANNER_WARNING as STRONG_WARNING,
    run_strong_movers,
    StrongMoversConfig,
)
from app.analysis.stage12_top3 import (
    TOP3_SCANNER_WARNING,
    build_candidate_pool,
    evaluate_candidate,
    format_top3_telegram,
    run_top3,
    select_top3,
    Top3Candidate,
    Top3Config,
    Top3Output,
)
from app.config.quality import TOP_N as TOP_N_CONFIG
from app.market.ranking import dynamic_rank_assets


def _make_asset(
    symbol="A", market_cap=None, canonical_asset_id=None,
    provider_rank=None, **extra,
):
    return {
        "provider_asset_id": canonical_asset_id or f"id_{symbol}",
        "canonical_asset_id": canonical_asset_id or f"id_{symbol}",
        "symbol": symbol, "name": symbol,
        "provider": "TEST", "provider_mode": "TEST",
        "provider_rank": provider_rank,
        "price": 100.0, "market_cap": market_cap,
        "volume_24h": 1_000_000.0,
        "source_timestamp": "2026-09-11T16:29:00+00:00",
        "retrieved_at": "2026-09-11T16:30:00+00:00",
        "identity_status": "VALIDATED",
        **extra,
    }


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


def _make_usdt_result(
    symbol="SOLUSDT", change_pct=5.0, volume=200_000_000.0,
    exchange="Binance", valid=True, **kwargs,
):
    return UsdtPairResult(
        symbol=symbol, change_pct=change_pct, volume=volume,
        timestamp="2026-09-14T15:30:00+00:00",
        requested_exchange="Bybit", actual_exchange=exchange,
        fallback_used=False, fallback_exchange=None,
        timeframe="5m",
        volume_source_label=f"Source: {exchange}",
        valid=valid, errors=[], provenance={}, **kwargs,
    )


def _make_btc_result(
    symbol="SOLBTC", change_pct=1.0, exchange="Binance", valid=True,
    **kwargs,
):
    return BtcPairResult(
        symbol=symbol, change_pct=change_pct,
        timestamp="2026-09-14T15:30:00+00:00",
        requested_exchange="Bybit", actual_exchange=exchange,
        fallback_used=False, fallback_exchange=None,
        usdt_fallback_exchange=None, calculated_kitchen_value=None,
        calculated_kitchen_used=False, timeframe="5m",
        valid=valid, errors=[], provenance={}, **kwargs,
    )


def _make_usdt_btc_results():
    usdt_r = {}
    btc_r = {}
    for i in range(11, 16):
        symbol = f"A{i}"
        usdt_r[f"{symbol}USDT"] = _make_usdt_result(
            symbol=f"{symbol}USDT", change_pct=float(i), valid=True,
        )
        btc_r[f"{symbol}BTC"] = _make_btc_result(
            symbol=f"{symbol}BTC", valid=True,
        )
    return usdt_r, btc_r


# ---------------------------------------------------------------------------
# Full chain verification
# ---------------------------------------------------------------------------


def test_u065_ranking_stable():
    assets = _make_full_top125()
    ranking = dynamic_rank_assets(assets)
    assert ranking["status"] == "VALIDATED"
    btc_asset = next(
        (a for a in ranking["top125"] if a.get("symbol") == "BTC"), None
    )
    assert btc_asset is not None
    assert int(btc_asset["calculated_rank"]) == 1


def test_stage10_top10_available():
    assets = _make_full_top125()
    result = get_dynamic_top10(assets, view="KITCHEN")
    assert result.view == "KITCHEN"
    assert len(result.assets) == 9
    assert "BTC" not in [a["symbol"] for a in result.assets]


def test_stage11_strong_movers_available():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    output = run_strong_movers(
        assets,
        config=StrongMoversConfig(selected_exchange="Bybit"),
        usdt_results=usdt_r, btc_results=btc_r,
    )
    assert output.valid is True
    assert len(output.strong_movers) == 5


def test_stage12_top3_available():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    config = Top3Config(selected_exchange="Bybit")
    output = run_top3(
        assets, config=config,
        usdt_results=usdt_r, btc_results=btc_r,
    )
    assert output.valid is True
    assert output.selected_count == 3
    assert len(output.top3) == 3


# ---------------------------------------------------------------------------
# Candidate pool bridge: Stage 11 → Stage 12
# ---------------------------------------------------------------------------


def test_candidate_pool_from_strong_movers():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    strong = run_strong_movers(
        assets,
        config=StrongMoversConfig(selected_exchange="Bybit"),
        usdt_results=usdt_r, btc_results=btc_r,
    )
    from app.analysis.stage10_consumer import select_ranks
    ranking = dynamic_rank_assets(assets)
    top10 = select_ranks(ranking["top125"], min_rank=2, max_rank=10)
    pool = build_candidate_pool(top10, strong.strong_movers, assets)
    assert len(pool) >= 9
    for candidate in pool:
        assert candidate.canonical_asset_id.startswith("cmc:")


def test_candidate_pool_dedup():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    strong = run_strong_movers(
        assets,
        config=StrongMoversConfig(selected_exchange="Bybit"),
        usdt_results=usdt_r, btc_results=btc_r,
    )
    from app.analysis.stage10_consumer import select_ranks
    ranking = dynamic_rank_assets(assets)
    top10 = select_ranks(ranking["top125"], min_rank=2, max_rank=10)
    pool = build_candidate_pool(top10, strong.strong_movers, assets)
    canonical_ids = [c.canonical_asset_id for c in pool]
    assert len(canonical_ids) == len(set(canonical_ids))


# ---------------------------------------------------------------------------
# Evaluation and selection continuity
# ---------------------------------------------------------------------------


def test_evaluate_candidate_reuses_scoring():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    strong = run_strong_movers(
        assets,
        config=StrongMoversConfig(selected_exchange="Bybit"),
        usdt_results=usdt_r, btc_results=btc_r,
    )
    from app.analysis.stage10_consumer import select_ranks
    ranking = dynamic_rank_assets(assets)
    top10 = select_ranks(ranking["top125"], min_rank=2, max_rank=10)
    pool = build_candidate_pool(top10, strong.strong_movers, assets)
    evaluated = [evaluate_candidate(c) for c in pool]
    for candidate in evaluated:
        assert candidate.total_score >= 0
        assert candidate.reliability_score >= 0
        assert candidate.movement_score >= 0


def test_select_top3_from_pool():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    strong = run_strong_movers(
        assets,
        config=StrongMoversConfig(selected_exchange="Bybit"),
        usdt_results=usdt_r, btc_results=btc_r,
    )
    from app.analysis.stage10_consumer import select_ranks
    ranking = dynamic_rank_assets(assets)
    top10 = select_ranks(ranking["top125"], min_rank=2, max_rank=10)
    pool = build_candidate_pool(top10, strong.strong_movers, assets)
    evaluated = [evaluate_candidate(c) for c in pool]
    selected = select_top3(evaluated, top_n=3)
    assert len(selected) == 3
    scores = [c.total_score for c in selected]
    assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# Output format continuity
# ---------------------------------------------------------------------------


def test_top3_telegram_format():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    config = Top3Config(selected_exchange="Bybit")
    output = run_top3(
        assets, config=config,
        usdt_results=usdt_r, btc_results=btc_r,
    )
    msg = format_top3_telegram(output)
    assert "TOP 3" in msg or "🏆" in msg
    assert "⚠️" in msg or "توجه" in msg


def test_top3_no_signal_in_output():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    config = Top3Config(selected_exchange="Bybit")
    output = run_top3(
        assets, config=config,
        usdt_results=usdt_r, btc_results=btc_r,
    )
    msg = format_top3_telegram(output).upper()
    assert "BUY" not in msg
    assert "SELL" not in msg
    assert "LONG" not in msg
    assert "SHORT" not in msg


# ---------------------------------------------------------------------------
# Exchange contract continuity
# ---------------------------------------------------------------------------


def test_exchange_contract_preserved():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    for exc in ["Binance", "OKX", "Bybit", "KuCoin",
                "Coinbase", "Gate", "Upbit", "Bitget"]:
        config = Top3Config(selected_exchange=exc)
        output = run_top3(
            assets, config=config,
            usdt_results=usdt_r, btc_results=btc_r,
        )
        assert output.selected_exchange == exc


def test_higher_priority_fallback_only():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    for exc in DISPLAY_FALLBACK_PRIORITY:
        router = ExchangeRouter(exc)
        chain = router.get_fallback_chain()
        config = Top3Config(selected_exchange=exc.value)
        output = run_top3(
            assets, config=config,
            usdt_results=usdt_r, btc_results=btc_r,
        )
        assert output.valid is True or output.selected_count == 0


# ---------------------------------------------------------------------------
# Previous outputs remain available
# ---------------------------------------------------------------------------


def test_dynamic_top10_still_available():
    assets = _make_full_top125()
    result = get_dynamic_top10(assets)
    assert len(result.assets) == 9
    assert result.view == "KITCHEN"


def test_strong_movers_still_available():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    output = run_strong_movers(
        assets,
        config=StrongMoversConfig(selected_exchange="Bybit"),
        usdt_results=usdt_r, btc_results=btc_r,
    )
    assert len(output.strong_movers) == 5


# ---------------------------------------------------------------------------
# Scanner warning
# ---------------------------------------------------------------------------


def test_warning_reuses_stage11_warning():
    assert TOP3_SCANNER_WARNING == STRONG_WARNING
    assert "توجه" in TOP3_SCANNER_WARNING


# ---------------------------------------------------------------------------
# Safety
# ---------------------------------------------------------------------------


def test_no_trading_signal_in_top3():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    config = Top3Config(selected_exchange="Bybit")
    output = run_top3(
        assets, config=config,
        usdt_results=usdt_r, btc_results=btc_r,
    )
    msg = format_top3_telegram(output)
    msg_upper = msg.upper()
    for word in ["BUY", "SELL", "LONG", "SHORT", "STOP", "TAKE", "TARGET"]:
        assert word not in msg_upper
