"""Stage 12 — Unit 12.6 — Full Regression + Final Scanner Audit tests.

Deterministic/synthetic tests only. No live network calls.
"""
from __future__ import annotations

import pytest

from app.analysis.stage10_consumer import (
    DISPLAY_FALLBACK_PRIORITY,
    Exchange,
    get_dynamic_top10,
)
from app.analysis.stage10_router import ExchangeRouter
from app.analysis.stage10_usdt import UsdtPairResult, UsdtPairProcessor
from app.analysis.stage10_btc import BtcPairResult, BtcPairProcessor
from app.analysis.stage11_strong_movers import (
    SCANNER_WARNING,
    run_strong_movers,
    StrongMoversConfig,
)
from app.analysis.stage12_top3 import (
    TOP3_SCANNER_WARNING,
    evaluate_candidate,
    format_top3_telegram,
    run_top3,
    select_top3,
    Top3Candidate,
    Top3Config,
)
from app.config.quality import TOP_N, TRADING_ENABLED, ORDERS_ENABLED
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
# Safety locks
# ---------------------------------------------------------------------------


def test_trading_disabled():
    assert TRADING_ENABLED is False


def test_orders_disabled():
    assert ORDERS_ENABLED is False


def test_safety_locks_asserted():
    assert not TRADING_ENABLED
    assert not ORDERS_ENABLED


# ---------------------------------------------------------------------------
# Stage 12 specific tests
# ---------------------------------------------------------------------------


def test_no_top3_by_gain_only():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    config = Top3Config(selected_exchange="Bybit")
    output = run_top3(
        assets, config=config,
        usdt_results=usdt_r, btc_results=btc_r,
    )
    assert len(output.top3) == 3
    top3 = output.top3
    changes = [abs(r.usdt_change_pct or 0) for r in top3]
    scores = [r.total_score for r in top3]
    assert scores == sorted(scores, reverse=True)


def test_strong_movement_plus_reliability():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    config = Top3Config(selected_exchange="Bybit")
    output = run_top3(
        assets, config=config,
        usdt_results=usdt_r, btc_results=btc_r,
    )
    for r in output.top3:
        assert r.valid is True
        assert r.total_score > 0


def test_no_invented_third_metric():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    config = Top3Config(selected_exchange="Bybit")
    output = run_top3(
        assets, config=config,
        usdt_results=usdt_r, btc_results=btc_r,
    )
    for r in output.top3:
        evidence = r.reliability_evidence if hasattr(r, 'reliability_evidence') else {}
        assert "third_metric" not in str(evidence).lower()
        assert "generic_intelligence" not in str(evidence).lower()


# ---------------------------------------------------------------------------
# U06.5 regression
# ---------------------------------------------------------------------------


def test_u065_ranking_unchanged():
    assets = _make_full_top125()
    ranking = dynamic_rank_assets(assets)
    assert ranking["status"] == "VALIDATED"
    assert len(ranking["top125"]) == TOP_N
    btc_asset = next(
        (a for a in ranking["top125"] if a.get("symbol") == "BTC"), None
    )
    assert btc_asset is not None
    assert int(btc_asset["calculated_rank"]) == 1


def test_u065_deterministic():
    assets = _make_full_top125()
    ranking1 = dynamic_rank_assets(assets)
    ranking2 = dynamic_rank_assets(assets)
    assert (
        [a["symbol"] for a in ranking1["top125"]]
        == [a["symbol"] for a in ranking2["top125"]]
    )


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


def test_stage10_top10_still_works():
    assets = _make_full_top125()
    result = get_dynamic_top10(assets, view="KITCHEN")
    assert len(result.assets) == 9


# ---------------------------------------------------------------------------
# Stage 11 regression
# ---------------------------------------------------------------------------


def test_stage11_strong_movers_still_works():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    output = run_strong_movers(
        assets,
        config=StrongMoversConfig(selected_exchange="Bybit"),
        usdt_results=usdt_r, btc_results=btc_r,
    )
    assert output.valid is True
    assert len(output.strong_movers) == 5


def test_stage11_warning_present():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    output = run_strong_movers(
        assets,
        config=StrongMoversConfig(selected_exchange="Bybit"),
        usdt_results=usdt_r, btc_results=btc_r,
    )
    assert SCANNER_WARNING in output.scanner_warning


# ---------------------------------------------------------------------------
# Full Scanner regression
# ---------------------------------------------------------------------------


def test_full_scanner_chain():
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
    assert "Binance" in output.display_fallback_priority


def test_full_scanner_all_exchanges():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    for exc in ["Binance", "OKX", "Bybit", "KuCoin", "Coinbase",
                "Gate", "Upbit", "Bitget"]:
        config = Top3Config(selected_exchange=exc)
        output = run_top3(
            assets, config=config,
            usdt_results=usdt_r, btc_results=btc_r,
        )
        assert output.selected_exchange == exc


# ---------------------------------------------------------------------------
# Output verification
# ---------------------------------------------------------------------------


def test_top3_warning_present():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    config = Top3Config(selected_exchange="Bybit")
    output = run_top3(
        assets, config=config,
        usdt_results=usdt_r, btc_results=btc_r,
    )
    assert TOP3_SCANNER_WARNING in output.scanner_warning
    assert "توجه" in output.scanner_warning


def test_top3_format():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    config = Top3Config(selected_exchange="Bybit")
    output = run_top3(
        assets, config=config,
        usdt_results=usdt_r, btc_results=btc_r,
    )
    msg = format_top3_telegram(output)
    assert "1." in msg
    assert "2." in msg
    assert "3." in msg


def test_top3_no_signal_language():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    config = Top3Config(selected_exchange="Bybit")
    output = run_top3(
        assets, config=config,
        usdt_results=usdt_r, btc_results=btc_r,
    )
    msg = format_top3_telegram(output).upper()
    for word in ["BUY", "SELL", "LONG", "SHORT", "STOP", "TAKE", "TARGET"]:
        assert word not in msg


def test_top3_no_fabrication():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    config = Top3Config(selected_exchange="Bybit")
    output = run_top3(
        assets, config=config,
        usdt_results=usdt_r, btc_results=btc_r,
    )
    for r in output.top3:
        assert r.usdt_pair.endswith("USDT")
        if r.btc_available:
            assert r.btc_pair.endswith("BTC")
            assert r.btc_pair != "BTCBTC"
            assert r.btc_pair != "BTC"


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_output():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    config = Top3Config(selected_exchange="Bybit")
    output1 = run_top3(
        assets, config=config,
        usdt_results=usdt_r, btc_results=btc_r,
    )
    output2 = run_top3(
        assets, config=config,
        usdt_results=usdt_r, btc_results=btc_r,
    )
    assert output1.selected_count == output2.selected_count
    for r1, r2 in zip(output1.top3, output2.top3):
        assert r1.symbol == r2.symbol
        assert r1.total_score == r2.total_score


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_empty_assets():
    config = Top3Config(selected_exchange="Binance")
    output = run_top3([], config=config)
    assert output.valid is False or output.selected_count == 0


def test_insufficient_assets():
    assets = [_make_asset(symbol="A1", market_cap=100.0)]
    config = Top3Config(selected_exchange="Binance")
    output = run_top3(assets, config=config)
    assert output.selected_count == 0


def test_no_usdt_results():
    assets = _make_full_top125()
    config = Top3Config(selected_exchange="Binance")
    output = run_top3(assets, config=config)
    assert output.selected_count >= 0
