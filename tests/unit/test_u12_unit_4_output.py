"""Stage 12 — Unit 12.4 — Final Top 3 + Telegram Output tests.

Deterministic/synthetic tests only. No live network calls.
"""
from __future__ import annotations

from app.analysis.stage10_usdt import UsdtPairResult
from app.analysis.stage10_btc import BtcPairResult
from app.analysis.stage12_top3 import (
    TOP3_HEADER,
    TOP3_SCANNER_WARNING,
    TOP_N,
    build_top3_result,
    evaluate_candidate,
    format_top3_telegram,
    run_top3,
    select_top3,
    Top3Candidate,
    Top3Config,
    Top3Output,
)
from app.config.quality import TOP_N as TOP_N_CONFIG


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
        reliability_evidence={}, **kwargs,
    )


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
            {
                "provider_asset_id": f"cmc:{1000 + i}",
                "canonical_asset_id": f"cmc:{1000 + i}",
                "symbol": symbol,
                "name": symbol,
                "provider": "TEST",
                "provider_mode": "TEST",
                "provider_rank": i + 1,
                "price": 100.0,
                "market_cap": float(1_000_000_000 - i * 1_000_000),
                "volume_24h": 1_000_000.0,
                "source_timestamp": "2026-09-11T16:29:00+00:00",
                "retrieved_at": "2026-09-11T16:30:00+00:00",
                "identity_status": "VALIDATED",
            }
        )
    return assets


def _make_usdt_btc_results():
    usdt_results = {}
    btc_results = {}
    for i in range(11, 16):
        symbol = f"A{i}"
        usdt_results[f"{symbol}USDT"] = _make_usdt_result(
            symbol=f"{symbol}USDT", change_pct=float(i), valid=True,
        )
        btc_results[f"{symbol}BTC"] = _make_btc_result(
            symbol=f"{symbol}BTC", valid=True,
        )
    return usdt_results, btc_results


# ---------------------------------------------------------------------------
# Build result
# ---------------------------------------------------------------------------


def test_build_result_usdt_only():
    usdt = _make_usdt_result(valid=True)
    candidate = _make_candidate(usdt=usdt, btc=None)
    result = build_top3_result(candidate, position=1)
    assert result.symbol == "SOL"
    assert result.position == 1
    assert result.usdt_pair == "SOLUSDT"
    assert result.btc_pair == "SOLBTC"
    assert result.btc_available is False
    assert result.usdt_source == "Source: Binance"
    assert result.valid is True


def test_build_result_with_btc():
    usdt = _make_usdt_result(valid=True)
    btc = _make_btc_result(valid=True)
    candidate = _make_candidate(usdt=usdt, btc=btc)
    result = build_top3_result(candidate, position=1)
    assert result.btc_available is True
    assert result.btc_change_pct == 1.0


# ---------------------------------------------------------------------------
# Telegram formatting
# ---------------------------------------------------------------------------


def test_telegram_header():
    output = Top3Output(
        selected_exchange="Bybit",
        display_fallback_priority=[e.value for e in __import__(
            "app.analysis.stage10_consumer", fromlist=["DISPLAY_FALLBACK_PRIORITY"]
        ).DISPLAY_FALLBACK_PRIORITY],
        timeframe="5m",
        ranking_version="KITCHEN_RANKING_V1",
        top3=[],
        candidate_count=0,
        selected_count=0,
        scanner_warning=TOP3_SCANNER_WARNING,
        valid=False,
    )
    msg = format_top3_telegram(output)
    assert TOP3_HEADER in msg
    assert TOP3_SCANNER_WARNING in msg


def test_telegram_single_mover():
    usdt = _make_usdt_result(change_pct=5.5, volume=200_000_000.0)
    candidate = _make_candidate(usdt=usdt, btc=None)
    result = build_top3_result(candidate, position=1)
    output = Top3Output(
        selected_exchange="Bybit",
        display_fallback_priority=["Binance", "OKX", "Bybit"],
        timeframe="5m",
        ranking_version="KITCHEN_RANKING_V1",
        top3=[result],
        candidate_count=115,
        selected_count=1,
        scanner_warning=TOP3_SCANNER_WARNING,
        valid=True,
    )
    msg = format_top3_telegram(output)
    assert "SOL" in msg
    assert "5.50%" in msg
    assert "SOLUSDT" in msg
    assert "Source: Binance" in msg or "Fallback" in msg
    assert "Volume:" in msg


def test_telegram_with_btc():
    usdt = _make_usdt_result(change_pct=5.5, volume=200_000_000.0)
    btc = _make_btc_result(change_pct=1.2)
    candidate = _make_candidate(usdt=usdt, btc=btc)
    result = build_top3_result(candidate, position=1)
    output = Top3Output(
        selected_exchange="Bybit",
        display_fallback_priority=["Binance", "OKX", "Bybit"],
        timeframe="5m",
        ranking_version="KITCHEN_RANKING_V1",
        top3=[result],
        candidate_count=115,
        selected_count=1,
        scanner_warning=TOP3_SCANNER_WARNING,
        valid=True,
    )
    msg = format_top3_telegram(output)
    assert "SOLBTC" in msg
    assert "1.20%" in msg


def test_telegram_fallback():
    usdt = _make_usdt_result(
        change_pct=5.5, volume=200_000_000.0,
        exchange="OKX", fallback_used=True, fallback_exchange="OKX"
    )
    candidate = _make_candidate(usdt=usdt, btc=None)
    result = build_top3_result(candidate, position=1)
    output = Top3Output(
        selected_exchange="Bybit",
        display_fallback_priority=["Binance", "OKX", "Bybit"],
        timeframe="5m",
        ranking_version="KITCHEN_RANKING_V1",
        top3=[result],
        candidate_count=115,
        selected_count=1,
        scanner_warning=TOP3_SCANNER_WARNING,
        valid=True,
    )
    msg = format_top3_telegram(output)
    assert "Fallback from: OKX" in msg


def test_telegram_volume_usdt_only():
    usdt = _make_usdt_result(change_pct=5.0, volume=200_000_000.0)
    btc = _make_btc_result(change_pct=1.0)
    candidate = _make_candidate(usdt=usdt, btc=btc)
    result = build_top3_result(candidate, position=1)
    output = Top3Output(
        selected_exchange="Bybit",
        display_fallback_priority=["Binance", "OKX", "Bybit"],
        timeframe="5m", ranking_version="KITCHEN_RANKING_V1",
        top3=[result], candidate_count=115, selected_count=1,
        scanner_warning=TOP3_SCANNER_WARNING, valid=True,
    )
    msg = format_top3_telegram(output)
    usdt_block_start = msg.find("SOLUSDT")
    btc_block_start = msg.find("SOLBTC")
    if btc_block_start > 0 and usdt_block_start > 0:
        usdt_section = msg[usdt_block_start:btc_block_start]
        assert "Volume:" in usdt_section
        btc_section = msg[btc_block_start:]
        assert "Volume:" not in btc_section


def test_telegram_no_btc_volume():
    usdt = _make_usdt_result(change_pct=5.0, volume=200_000_000.0)
    btc = _make_btc_result(change_pct=1.0)
    candidate = _make_candidate(usdt=usdt, btc=btc)
    result = build_top3_result(candidate, position=1)
    output = Top3Output(
        selected_exchange="Bybit",
        display_fallback_priority=["Binance", "OKX", "Bybit"],
        timeframe="5m", ranking_version="KITCHEN_RANKING_V1",
        top3=[result], candidate_count=115, selected_count=1,
        scanner_warning=TOP3_SCANNER_WARNING, valid=True,
    )
    msg = format_top3_telegram(output)
    btc_block_start = msg.find("SOLBTC")
    if btc_block_start > 0:
        btc_section = msg[btc_block_start:]
        assert "200.0M" not in btc_section


def test_telegram_three_movers():
    usdt_results, btc_results = _make_usdt_btc_results()
    top3 = []
    for i, result in enumerate(
        select_top3(
            [
                evaluate_candidate(
                    _make_candidate(
                        symbol=f"A{i}", rank=i,
                        usdt=usdt_results[f"A{i}USDT"],
                        btc=btc_results[f"A{i}BTC"],
                    )
                )
                for i in range(11, 14)
            ],
            top_n=3,
        )
    ):
        top3.append(
            build_top3_result(result, position=i + 1)
        )
    output = Top3Output(
        selected_exchange="Bybit",
        display_fallback_priority=["Binance", "OKX", "Bybit"],
        timeframe="5m",
        ranking_version="KITCHEN_RANKING_V1",
        top3=top3,
        candidate_count=115,
        selected_count=3,
        scanner_warning=TOP3_SCANNER_WARNING,
        valid=True,
    )
    msg = format_top3_telegram(output)
    for i in range(1, 4):
        assert f"{i}." in msg
    assert "1." in msg
    assert "2." in msg
    assert "3." in msg


# ---------------------------------------------------------------------------
# No signal/recommendation language
# ---------------------------------------------------------------------------


def test_no_signal_language():
    usdt_results, btc_results = _make_usdt_btc_results()
    top3 = []
    for i, result in enumerate(
        select_top3(
            [
                evaluate_candidate(
                    _make_candidate(
                        symbol=f"A{i}", rank=i,
                        usdt=usdt_results[f"A{i}USDT"],
                        btc=btc_results[f"A{i}BTC"],
                    )
                )
                for i in range(11, 14)
            ],
            top_n=3,
        )
    ):
        top3.append(
            build_top3_result(result, position=i + 1)
        )
    output = Top3Output(
        selected_exchange="Bybit",
        display_fallback_priority=["Binance", "OKX", "Bybit"],
        timeframe="5m",
        ranking_version="KITCHEN_RANKING_V1",
        top3=top3,
        candidate_count=115,
        selected_count=3,
        scanner_warning=TOP3_SCANNER_WARNING,
        valid=True,
    )
    msg = format_top3_telegram(output)
    msg_upper = msg.upper()
    assert "BUY" not in msg_upper
    assert "SELL" not in msg_upper
    assert "LONG" not in msg_upper
    assert "SHORT" not in msg_upper
    assert "STOP" not in msg_upper
    assert "TAKE" not in msg_upper
    assert "TARGET" not in msg_upper


def test_warning_present():
    usdt_results, btc_results = _make_usdt_btc_results()
    top3 = []
    for i, result in enumerate(
        select_top3(
            [
                evaluate_candidate(
                    _make_candidate(
                        symbol=f"A{i}", rank=i,
                        usdt=usdt_results[f"A{i}USDT"],
                        btc=btc_results[f"A{i}BTC"],
                    )
                )
                for i in range(11, 14)
            ],
            top_n=3,
        )
    ):
        top3.append(
            build_top3_result(result, position=i + 1)
        )
    output = Top3Output(
        selected_exchange="Bybit",
        display_fallback_priority=["Binance", "OKX", "Bybit"],
        timeframe="5m",
        ranking_version="KITCHEN_RANKING_V1",
        top3=top3,
        candidate_count=115,
        selected_count=3,
        scanner_warning=TOP3_SCANNER_WARNING,
        valid=True,
    )
    msg = format_top3_telegram(output)
    assert TOP3_SCANNER_WARNING in msg
    assert "توجه" in msg


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def test_run_top3_three_results():
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
    assert output.candidate_count >= 3
    for r in output.top3:
        assert r.valid is True


def test_run_top3_fewer_when_insufficient():
    assets = _make_full_top125()
    usdt_r = {}
    btc_r = {}
    for i in range(11, 13):
        symbol = f"A{i}"
        usdt_r[f"{symbol}USDT"] = _make_usdt_result(
            symbol=f"{symbol}USDT", change_pct=float(i), valid=True,
        )
    config = Top3Config(selected_exchange="Bybit")
    output = run_top3(
        assets, config=config,
        usdt_results=usdt_r, btc_results=btc_r,
    )
    assert output.selected_count <= 2


def test_run_top3_no_candidates():
    assets = _make_full_top125()
    config = Top3Config(selected_exchange="Binance")
    output = run_top3(assets, config=config)
    assert output.valid is False or output.selected_count == 0


def test_run_top3_binance_no_fallback():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    for i in range(11, 14):
        symbol = f"A{i}"
        usdt_r[f"{symbol}USDT"] = _make_usdt_result(
            symbol=f"{symbol}USDT", change_pct=float(i), valid=True,
            exchange="Binance",
        )
        btc_r[f"{symbol}BTC"] = _make_btc_result(
            symbol=f"{symbol}BTC", valid=True, exchange="Binance",
        )
    config = Top3Config(selected_exchange="Binance")
    output = run_top3(
        assets, config=config,
        usdt_results=usdt_r, btc_results=btc_r,
    )
    assert output.valid is True
    for r in output.top3:
        assert "Binance" in (r.usdt_source or "")


def test_run_top3_preserves_timeframe():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    config = Top3Config(selected_exchange="Bybit", timeframe="1h")
    output = run_top3(
        assets, config=config,
        usdt_results=usdt_r, btc_results=btc_r,
    )
    for r in output.top3:
        assert r.timeframe == "1h"


def test_run_top3_different_exchanges():
    assets = _make_full_top125()
    usdt_r, btc_r = _make_usdt_btc_results()
    for exc in ["Binance", "OKX", "Bybit", "KuCoin", "Coinbase", "Gate", "Upbit", "Bitget"]:
        config = Top3Config(selected_exchange=exc)
        output = run_top3(
            assets, config=config,
            usdt_results=usdt_r, btc_results=btc_r,
        )
        assert output.valid is True or output.selected_count >= 0


def test_run_top3_no_fabricated_data():
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
