"""Stage 11 — Unit 11.4 — Five Strong Movers Output tests.

Deterministic/synthetic tests only. No live network calls.
"""
from __future__ import annotations

from app.analysis.stage10_usdt import UsdtPairResult
from app.analysis.stage10_btc import BtcPairResult
from app.analysis.stage11_strong_movers import (
    STRONG_MOVERS_HEADER,
    SCANNER_WARNING,
    build_strong_mover_result,
    format_strong_movers_telegram,
    StrongMoversConfig,
    StrongMoversOutput,
    run_strong_movers,
)
from app.config.quality import TOP_N


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
# Build result
# ---------------------------------------------------------------------------


def test_build_result_usdt_only():
    usdt = _make_usdt_result(valid=True)
    candidate_args = dict(
        kitchen_rank=15, symbol="SOL",
        usdt_change_pct=usdt.change_pct,
        usdt_volume=usdt.volume,
        usdt_actual_exchange="Binance",
        usdt_fallback_used=False,
        usdt_fallback_exchange=None,
        usdt_valid=True,
        btc_change_pct=None,
        btc_actual_exchange="",
        btc_fallback_used=False,
        btc_fallback_exchange=None,
        btc_available=False,
        btc_valid=False,
        movement_score=10.0,
        reliability_score=8.0,
        total_score=18.0,
        reliability_evidence={},
    )
    from app.analysis.stage11_strong_movers import StrongMoverCandidate
    candidate = StrongMoverCandidate(**candidate_args)
    result = build_strong_mover_result(candidate)
    assert result.symbol == "SOL"
    assert result.usdt_pair == "SOLUSDT"
    assert result.btc_pair == "SOLBTC"
    assert result.btc_available is False
    assert result.usdt_source == "Source: Binance"
    assert result.valid is True


def test_build_result_with_btc():
    usdt = _make_usdt_result(valid=True)
    btc = _make_btc_result(valid=True)
    candidate_args = dict(
        kitchen_rank=15, symbol="SOL",
        usdt_change_pct=usdt.change_pct,
        usdt_volume=usdt.volume,
        usdt_actual_exchange="Binance",
        usdt_fallback_used=False,
        usdt_fallback_exchange=None,
        usdt_valid=True,
        btc_change_pct=btc.change_pct,
        btc_actual_exchange="Binance",
        btc_fallback_used=False,
        btc_fallback_exchange=None,
        btc_available=True,
        btc_valid=True,
        movement_score=10.0,
        reliability_score=8.0,
        total_score=18.0,
        reliability_evidence={},
    )
    from app.analysis.stage11_strong_movers import StrongMoverCandidate
    candidate = StrongMoverCandidate(**candidate_args)
    result = build_strong_mover_result(candidate)
    assert result.btc_available is True
    assert result.btc_change_pct == 1.0


def test_build_result_fallback():
    usdt = _make_usdt_result(
        exchange="OKX", fallback_used=True, fallback_exchange="OKX"
    )
    candidate_args = dict(
        kitchen_rank=15, symbol="SOL",
        usdt_change_pct=usdt.change_pct,
        usdt_volume=usdt.volume,
        usdt_actual_exchange="OKX",
        usdt_fallback_used=True,
        usdt_fallback_exchange="OKX",
        usdt_valid=True,
        btc_change_pct=None,
        btc_actual_exchange="",
        btc_fallback_used=False,
        btc_fallback_exchange=None,
        btc_available=False,
        btc_valid=False,
        movement_score=10.0,
        reliability_score=6.0,
        total_score=16.0,
        reliability_evidence={},
    )
    from app.analysis.stage11_strong_movers import StrongMoverCandidate
    candidate = StrongMoverCandidate(**candidate_args)
    result = build_strong_mover_result(candidate)
    assert result.usdt_source == "Fallback from: OKX"
    assert result.usdt_fallback_used is True


# ---------------------------------------------------------------------------
# Telegram formatting
# ---------------------------------------------------------------------------


def test_telegram_header():
    output = StrongMoversOutput(
        selected_exchange="Bybit",
        display_fallback_priority=[e.value for e in __import__(
            "app.analysis.stage10_consumer", fromlist=["DISPLAY_FALLBACK_PRIORITY"]
        ).DISPLAY_FALLBACK_PRIORITY],
        timeframe="5m",
        ranking_version="KITCHEN_RANKING_V1",
        strong_movers=[],
        candidate_count=0,
        selected_count=0,
        scanner_warning=SCANNER_WARNING,
        valid=False,
    )
    msg = format_strong_movers_telegram(output)
    assert STRONG_MOVERS_HEADER in msg
    assert SCANNER_WARNING in msg


def test_telegram_single_mover():
    usdt = _make_usdt_result(change_pct=5.5, volume=200_000_000.0)
    candidate_args = dict(
        kitchen_rank=15, symbol="SOL",
        usdt_change_pct=usdt.change_pct,
        usdt_volume=usdt.volume,
        usdt_actual_exchange="Binance",
        usdt_fallback_used=False,
        usdt_fallback_exchange=None,
        usdt_valid=True,
        btc_change_pct=None,
        btc_actual_exchange="",
        btc_fallback_used=False,
        btc_fallback_exchange=None,
        btc_available=False,
        btc_valid=False,
        movement_score=10.0,
        reliability_score=8.0,
        total_score=18.0,
        reliability_evidence={},
    )
    from app.analysis.stage11_strong_movers import StrongMoverCandidate, build_strong_mover_result
    candidate = StrongMoverCandidate(**candidate_args)
    result = build_strong_mover_result(candidate)

    output = StrongMoversOutput(
        selected_exchange="Bybit",
        display_fallback_priority=["Binance", "OKX", "Bybit"],
        timeframe="5m",
        ranking_version="KITCHEN_RANKING_V1",
        strong_movers=[result],
        candidate_count=115,
        selected_count=1,
        scanner_warning=SCANNER_WARNING,
        valid=True,
    )
    msg = format_strong_movers_telegram(output)
    assert "SOL" in msg
    assert "5.50%" in msg
    assert "SOLUSDT" in msg
    assert "Source: Binance" in msg
    assert "Volume:" in msg
    assert "SOLBTC" not in msg


def test_telegram_with_btc():
    usdt = _make_usdt_result(change_pct=5.5, volume=200_000_000.0)
    btc = _make_btc_result(change_pct=1.2)
    candidate_args = dict(
        kitchen_rank=15, symbol="SOL",
        usdt_change_pct=usdt.change_pct,
        usdt_volume=usdt.volume,
        usdt_actual_exchange="Binance",
        usdt_fallback_used=False,
        usdt_fallback_exchange=None,
        usdt_valid=True,
        btc_change_pct=btc.change_pct,
        btc_actual_exchange="Binance",
        btc_fallback_used=False,
        btc_fallback_exchange=None,
        btc_available=True,
        btc_valid=True,
        movement_score=10.0,
        reliability_score=8.0,
        total_score=18.0,
        reliability_evidence={},
    )
    from app.analysis.stage11_strong_movers import StrongMoverCandidate, build_strong_mover_result
    candidate = StrongMoverCandidate(**candidate_args)
    result = build_strong_mover_result(candidate)

    output = StrongMoversOutput(
        selected_exchange="Bybit",
        display_fallback_priority=["Binance", "OKX", "Bybit"],
        timeframe="5m",
        ranking_version="KITCHEN_RANKING_V1",
        strong_movers=[result],
        candidate_count=115,
        selected_count=1,
        scanner_warning=SCANNER_WARNING,
        valid=True,
    )
    msg = format_strong_movers_telegram(output)
    assert "SOLBTC" in msg
    assert "1.20%" in msg


def test_telegram_fallback():
    usdt = _make_usdt_result(
        change_pct=5.5, volume=200_000_000.0,
        exchange="OKX", fallback_used=True, fallback_exchange="OKX"
    )
    candidate_args = dict(
        kitchen_rank=15, symbol="SOL",
        usdt_change_pct=usdt.change_pct,
        usdt_volume=usdt.volume,
        usdt_actual_exchange="OKX",
        usdt_fallback_used=True,
        usdt_fallback_exchange="OKX",
        usdt_valid=True,
        btc_change_pct=None,
        btc_actual_exchange="",
        btc_fallback_used=False,
        btc_fallback_exchange=None,
        btc_available=False,
        btc_valid=False,
        movement_score=10.0,
        reliability_score=6.0,
        total_score=16.0,
        reliability_evidence={},
    )
    from app.analysis.stage11_strong_movers import StrongMoverCandidate, build_strong_mover_result
    candidate = StrongMoverCandidate(**candidate_args)
    result = build_strong_mover_result(candidate)

    output = StrongMoversOutput(
        selected_exchange="Bybit",
        display_fallback_priority=["Binance", "OKX", "Bybit"],
        timeframe="5m",
        ranking_version="KITCHEN_RANKING_V1",
        strong_movers=[result],
        candidate_count=115,
        selected_count=1,
        scanner_warning=SCANNER_WARNING,
        valid=True,
    )
    msg = format_strong_movers_telegram(output)
    assert "Fallback from: OKX" in msg


def test_telegram_volume_usdt_only():
    usdt = _make_usdt_result(change_pct=5.0, volume=200_000_000.0)
    btc = _make_btc_result(change_pct=1.0)
    from app.analysis.stage11_strong_movers import StrongMoverCandidate, build_strong_mover_result
    usdt_candidate = StrongMoverCandidate(
        kitchen_rank=15, symbol="SOL",
        usdt_change_pct=usdt.change_pct, usdt_volume=usdt.volume,
        usdt_actual_exchange="Binance", usdt_fallback_used=False,
        usdt_fallback_exchange=None, usdt_valid=True,
        btc_change_pct=btc.change_pct, btc_actual_exchange="Binance",
        btc_fallback_used=False, btc_fallback_exchange=None,
        btc_available=True, btc_valid=True,
        movement_score=10.0, reliability_score=8.0, total_score=18.0,
        reliability_evidence={},
    )
    result = build_strong_mover_result(usdt_candidate)

    output = StrongMoversOutput(
        selected_exchange="Bybit",
        display_fallback_priority=["Binance", "OKX", "Bybit"],
        timeframe="5m", ranking_version="KITCHEN_RANKING_V1",
        strong_movers=[result], candidate_count=115, selected_count=1,
        scanner_warning=SCANNER_WARNING, valid=True,
    )
    msg = format_strong_movers_telegram(output)
    usdt_block_start = msg.find("SOLUSDT")
    btc_block_start = msg.find("SOLBTC")
    if btc_block_start > 0 and usdt_block_start > 0:
        usdt_section = msg[usdt_block_start:btc_block_start]
        assert "Volume:" in usdt_section
        btc_section = msg[btc_block_start:]
        next_asset = btc_section.find("\n\n")
        if next_asset > 0:
            btc_section = btc_section[:next_asset]
        assert "Volume:" not in btc_section


def test_telegram_no_btc_volume():
    usdt = _make_usdt_result(change_pct=5.0, volume=200_000_000.0)
    btc = _make_btc_result(change_pct=1.0)
    from app.analysis.stage11_strong_movers import StrongMoverCandidate, build_strong_mover_result
    candidate = StrongMoverCandidate(
        kitchen_rank=15, symbol="SOL",
        usdt_change_pct=usdt.change_pct, usdt_volume=usdt.volume,
        usdt_actual_exchange="Binance", usdt_fallback_used=False,
        usdt_fallback_exchange=None, usdt_valid=True,
        btc_change_pct=btc.change_pct, btc_actual_exchange="Binance",
        btc_fallback_used=False, btc_fallback_exchange=None,
        btc_available=True, btc_valid=True,
        movement_score=10.0, reliability_score=8.0, total_score=18.0,
        reliability_evidence={},
    )
    result = build_strong_mover_result(candidate)
    output = StrongMoversOutput(
        selected_exchange="Bybit",
        display_fallback_priority=["Binance", "OKX", "Bybit"],
        timeframe="5m", ranking_version="KITCHEN_RANKING_V1",
        strong_movers=[result], candidate_count=115, selected_count=1,
        scanner_warning=SCANNER_WARNING, valid=True,
    )
    msg = format_strong_movers_telegram(output)
    btc_block_start = msg.find("SOLBTC")
    if btc_block_start > 0:
        btc_section = msg[btc_block_start:]
        assert "200.0M" not in btc_section


def test_telegram_multiple_movers():
    movers = []
    for i, rank in enumerate([15, 20, 25, 30, 35], 1):
        usdt = _make_usdt_result(
            symbol=f"A{rank}USDT", change_pct=float(i) * 2.0,
            volume=100_000_000.0 * i,
        )
        from app.analysis.stage11_strong_movers import StrongMoverCandidate, build_strong_mover_result
        candidate = StrongMoverCandidate(
            kitchen_rank=rank, symbol=f"A{rank}",
            usdt_change_pct=usdt.change_pct, usdt_volume=usdt.volume,
            usdt_actual_exchange="Binance", usdt_fallback_used=False,
            usdt_fallback_exchange=None, usdt_valid=True,
            btc_change_pct=None, btc_actual_exchange="",
            btc_fallback_used=False, btc_fallback_exchange=None,
            btc_available=False, btc_valid=False,
            movement_score=5.0, reliability_score=5.0, total_score=10.0,
            reliability_evidence={},
        )
        result = build_strong_mover_result(candidate)
        movers.append(result)

    output = StrongMoversOutput(
        selected_exchange="Bybit",
        display_fallback_priority=["Binance", "OKX", "Bybit"],
        timeframe="5m", ranking_version="KITCHEN_RANKING_V1",
        strong_movers=movers, candidate_count=115, selected_count=5,
        scanner_warning=SCANNER_WARNING, valid=True,
    )
    msg = format_strong_movers_telegram(output)
    for i in range(1, 6):
        assert f"{i}." in msg
    assert msg.count("Source:") >= 5


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def test_run_5_movers_from_valid():
    assets = _make_full_top125()
    usdt_results = {}
    btc_results = {}
    for i in range(11, 26):
        symbol = f"A{i}"
        usdt_results[f"{symbol}USDT"] = _make_usdt_result(
            symbol=f"{symbol}USDT", change_pct=float(i), valid=True
        )
        btc_results[f"{symbol}BTC"] = _make_btc_result(
            symbol=f"{symbol}BTC", valid=True
        )

    config = StrongMoversConfig(selected_exchange="Bybit")
    output = run_strong_movers(
        assets, config=config,
        usdt_results=usdt_results, btc_results=btc_results,
    )
    assert output.valid is True
    assert output.selected_count == 5
    assert len(output.strong_movers) == 5


def test_run_fewer_when_insufficient():
    assets = _make_full_top125()
    usdt_results = {}
    btc_results = {}
    for i in range(11, 14):
        symbol = f"A{i}"
        usdt_results[f"{symbol}USDT"] = _make_usdt_result(
            symbol=f"{symbol}USDT", change_pct=float(i), valid=True
        )

    config = StrongMoversConfig(selected_exchange="Bybit")
    output = run_strong_movers(
        assets, config=config,
        usdt_results=usdt_results, btc_results=btc_results,
    )
    assert output.selected_count <= 3


def test_run_no_candidates():
    assets = [_make_asset(symbol="A1", market_cap=100.0)]
    config = StrongMoversConfig(selected_exchange="Binance")
    output = run_strong_movers(assets, config=config)
    assert output.valid is False
    assert output.selected_count == 0


def test_run_binance_no_fallback():
    assets = _make_full_top125()
    usdt_results = {}
    btc_results = {}
    for i in range(11, 16):
        symbol = f"A{i}"
        usdt_results[f"{symbol}USDT"] = _make_usdt_result(
            symbol=f"{symbol}USDT", change_pct=float(i), valid=True,
            exchange="Binance",
        )
        btc_results[f"{symbol}BTC"] = _make_btc_result(
            symbol=f"{symbol}BTC", valid=True, exchange="Binance",
        )

    config = StrongMoversConfig(selected_exchange="Binance")
    output = run_strong_movers(
        assets, config=config,
        usdt_results=usdt_results, btc_results=btc_results,
    )
    assert output.valid is True
    for mover in output.strong_movers:
        assert mover.usdt_source == "Source: Binance"


def test_run_preserves_timeframe():
    assets = _make_full_top125()
    usdt_results = {}
    btc_results = {}
    for i in range(11, 16):
        symbol = f"A{i}"
        usdt_results[f"{symbol}USDT"] = _make_usdt_result(
            symbol=f"{symbol}USDT", change_pct=float(i), valid=True
        )

    config = StrongMoversConfig(selected_exchange="Bybit", timeframe="1h")
    output = run_strong_movers(assets, config=config)
    for mover in output.strong_movers:
        assert mover.timeframe == "1h"
