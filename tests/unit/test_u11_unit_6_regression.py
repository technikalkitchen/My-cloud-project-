"""Stage 11 — Unit 11.6 — Full Integration + Regression tests.

Deterministic/synthetic tests only. No live network calls.
"""
from __future__ import annotations

import pytest

from app.analysis.stage11_strong_movers import (
    STRONG_MOVERS_HEADER,
    SCANNER_WARNING,
    run_strong_movers,
    build_candidate_universe,
    evaluate_candidate,
    select_strong_movers,
    prepare_for_top3,
    format_strong_movers_telegram,
    StrongMoversConfig,
)
from app.analysis.stage10_consumer import (
    DISPLAY_FALLBACK_PRIORITY,
    Exchange,
)
from app.analysis.stage10_router import ExchangeRouter
from app.analysis.stage10_usdt import UsdtPairResult, UsdtPairProcessor
from app.analysis.stage10_btc import BtcPairResult, BtcPairProcessor
from app.config.quality import TOP_N
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
    for i in range(TOP_N):
        if i == 0: symbol = "BTC"
        elif i == 1: symbol = "ETH"
        elif i == 2: symbol = "USDT"
        else: symbol = f"A{i}"
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
    exchange="Binance", valid=True, fallback_used=False,
    fallback_exchange=None, **kwargs,
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


# ---------------------------------------------------------------------------
# Full integration
# ---------------------------------------------------------------------------


def test_full_pipeline_5_movers():
    assets = _make_full_top125()
    usdt_r = {}
    btc_r = {}
    for i in range(11, 16):
        sym = f"A{i}"
        usdt_r[f"{sym}USDT"] = _make_usdt_result(
            symbol=f"{sym}USDT", change_pct=float(i), valid=True,
        )
        btc_r[f"{sym}BTC"] = _make_btc_result(
            symbol=f"{sym}BTC", valid=True,
        )
    output = run_strong_movers(
        assets, config=StrongMoversConfig(selected_exchange="Bybit"),
        usdt_results=usdt_r, btc_results=btc_r,
    )
    assert output.valid is True
    assert len(output.strong_movers) == 5
    assert output.selected_count == 5
    assert output.candidate_count == 115
    for m in output.strong_movers:
        assert m.valid is True


def test_full_pipeline_different_exchanges():
    assets = _make_full_top125()
    for exc in ["Binance", "OKX", "Bybit", "KuCoin", "Coinbase", "Gate", "Upbit", "Bitget"]:
        usdt_r = {}
        btc_r = {}
        for i in range(11, 16):
            sym = f"A{i}"
            usdt_r[f"{sym}USDT"] = _make_usdt_result(
                symbol=f"{sym}USDT", change_pct=float(i), valid=True,
                exchange=exc,
            )
            btc_r[f"{sym}BTC"] = _make_btc_result(
                symbol=f"{sym}BTC", valid=True, exchange=exc,
            )
        output = run_strong_movers(
            assets, config=StrongMoversConfig(selected_exchange=exc),
            usdt_results=usdt_r, btc_results=btc_r,
        )
        assert output.valid is True
        assert len(output.strong_movers) == 5


# ---------------------------------------------------------------------------
# U06.5 regression
# ---------------------------------------------------------------------------


def test_u065_ranking_unchanged():
    assets = _make_full_top125()
    ranking = dynamic_rank_assets(assets)
    assert ranking["status"] == "VALIDATED"
    assert len(ranking["top125"]) == TOP_N
    btc_asset = next((a for a in ranking["top125"] if a.get("symbol") == "BTC"), None)
    assert btc_asset is not None
    assert int(btc_asset["calculated_rank"]) == 1


def test_u065_deterministic():
    assets = _make_full_top125()
    ranking1 = dynamic_rank_assets(assets)
    ranking2 = dynamic_rank_assets(assets)
    assert [a["symbol"] for a in ranking1["top125"]] == [a["symbol"] for a in ranking2["top125"]]


# ---------------------------------------------------------------------------
# Stage 10 regression
# ---------------------------------------------------------------------------


def test_stage10_router_still_works():
    router = ExchangeRouter(Exchange.BITGET)
    chain = router.get_fallback_chain()
    assert len(chain) == 8
    result = router.route(lambda ex: (True, []) if ex == "Binance" else (False, []))
    assert result.valid is True


def test_stage10_usdt_processor_still_works():
    from datetime import datetime, timedelta, timezone
    fresh = (datetime.now(timezone.utc) - timedelta(seconds=60)).isoformat()
    processor = UsdtPairProcessor("Binance", "5m")
    data = {
        "symbol": "SOLUSDT", "close": 165.50, "change_pct": 1.84,
        "volume": 284_600_000.0,
        "timestamp": fresh,
        "volume_source": "PROVIDER_SUPPLIED_TRADED_BASE_VOLUME",
        "exchange": "Binance", "timeframe": "5m",
    }
    result = processor.process(data)
    assert result.valid is True


def test_stage10_btc_processor_still_works():
    from datetime import datetime, timedelta, timezone
    fresh = (datetime.now(timezone.utc) - timedelta(seconds=60)).isoformat()
    processor = BtcPairProcessor("Binance", "5m")
    data = {
        "symbol": "SOLBTC", "close": 65000.0, "change_pct": 0.72,
        "timestamp": fresh,
        "exchange": "Binance", "timeframe": "5m",
    }
    result = processor.process(data)
    assert result.valid is True


# ---------------------------------------------------------------------------
# Safety
# ---------------------------------------------------------------------------


def test_no_trading_signal():
    assets = _make_full_top125()
    usdt_r = {}
    btc_r = {}
    for i in range(11, 16):
        sym = f"A{i}"
        usdt_r[f"{sym}USDT"] = _make_usdt_result(
            symbol=f"{sym}USDT", change_pct=float(i), valid=True,
        )
        btc_r[f"{sym}BTC"] = _make_btc_result(
            symbol=f"{sym}BTC", valid=True,
        )
    output = run_strong_movers(
        assets, usdt_results=usdt_r, btc_results=btc_r,
    )
    msg = format_strong_movers_telegram(output)
    assert "BUY" not in msg.upper()
    assert "SELL" not in msg.upper()
    assert "LONG" not in msg.upper()
    assert "SHORT" not in msg.upper()
    assert "STOP" not in msg.upper()
    assert "TAKE" not in msg.upper()
    assert "TARGET" not in msg.upper()


def test_scanner_warning_present():
    assets = _make_full_top125()
    usdt_r = {}
    btc_r = {}
    for i in range(11, 16):
        sym = f"A{i}"
        usdt_r[f"{sym}USDT"] = _make_usdt_result(
            symbol=f"{sym}USDT", change_pct=float(i), valid=True,
        )
    output = run_strong_movers(
        assets, usdt_results=usdt_r, btc_results=btc_r,
    )
    assert SCANNER_WARNING in format_strong_movers_telegram(output)
    assert "توجه" in output.scanner_warning


# ---------------------------------------------------------------------------
# No Top-3 in Stage 11
# ---------------------------------------------------------------------------


def test_no_top3_in_output():
    assets = _make_full_top125()
    usdt_r = {}
    btc_r = {}
    for i in range(11, 16):
        sym = f"A{i}"
        usdt_r[f"{sym}USDT"] = _make_usdt_result(
            symbol=f"{sym}USDT", change_pct=float(i), valid=True,
        )
        btc_r[f"{sym}BTC"] = _make_btc_result(
            symbol=f"{sym}BTC", valid=True,
        )
    output = run_strong_movers(
        assets, usdt_results=usdt_r, btc_results=btc_r,
    )
    assert not hasattr(output, "top3")
    for mover in output.strong_movers:
        assert "TOP3" not in str(mover).upper()


# ---------------------------------------------------------------------------
# Data integrity
# ---------------------------------------------------------------------------


def test_no_fabricated_pairs():
    assets = _make_full_top125()
    usdt_r = {}
    btc_r = {}
    for i in range(11, 16):
        sym = f"A{i}"
        usdt_r[f"{sym}USDT"] = _make_usdt_result(
            symbol=f"{sym}USDT", valid=True,
        )
        btc_r[f"{sym}BTC"] = _make_btc_result(
            symbol=f"{sym}BTC", valid=True,
        )
    output = run_strong_movers(
        assets, usdt_results=usdt_r, btc_results=btc_r,
    )
    for mover in output.strong_movers:
        assert mover.usdt_pair.endswith("USDT")
        if mover.btc_available:
            assert mover.btc_pair.endswith("BTC")
            assert mover.btc_pair != "BTCBTC"
            assert mover.btc_pair != "BTC"


def test_contains_header_and_warning():
    assets = _make_full_top125()
    usdt_r = {}
    btc_r = {}
    for i in range(11, 16):
        sym = f"A{i}"
        usdt_r[f"{sym}USDT"] = _make_usdt_result(
            symbol=f"{sym}USDT", change_pct=float(i), valid=True,
        )
    output = run_strong_movers(
        assets, usdt_results=usdt_r, btc_results=btc_r,
    )
    msg = format_strong_movers_telegram(output)
    assert STRONG_MOVERS_HEADER in msg
    assert SCANNER_WARNING in msg
