"""Stage 11 — Unit 11.5 — Top-3 Preparation / Integration Contract tests.

Deterministic/synthetic tests only. No live network calls.
"""
from __future__ import annotations

from app.analysis.stage10_usdt import UsdtPairResult
from app.analysis.stage10_btc import BtcPairResult
from app.analysis.stage11_strong_movers import (
    prepare_for_top3,
    run_strong_movers,
    StrongMoversConfig,
    STRONG_MOVERS_HEADER,
)
from app.config.quality import TOP_N


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
    symbol="SOLBTC", change_pct=1.0, exchange="Binance", valid=True, **kwargs,
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


def _make_asset(symbol="A", market_cap=1_000_000_000.0, rank=11, **extra):
    return {
        "provider_asset_id": f"cmc:{1000 + rank}",
        "canonical_asset_id": f"cmc:{1000 + rank}",
        "symbol": symbol,
        "name": symbol,
        "provider": "TEST",
        "provider_mode": "TEST",
        "provider_rank": rank,
        "price": 100.0,
        "market_cap": market_cap,
        "volume_24h": 1_000_000.0,
        "source_timestamp": "2026-09-11T16:29:00+00:00",
        "retrieved_at": "2026-09-11T16:30:00+00:00",
        "identity_status": "VALIDATED",
        **extra,
    }


def _make_assets_for_top3():
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
                provider_rank=i + 1,
            )
        )
    return assets


def _make_output():
    assets = _make_assets_for_top3()
    usdt_results = {}
    btc_results = {}
    for i in range(11, 16):
        symbol = f"A{i}"
        usdt_results[f"{symbol}USDT"] = _make_usdt_result(
            symbol=f"{symbol}USDT", change_pct=float(i), valid=True
        )
        btc_results[f"{symbol}BTC"] = _make_btc_result(
            symbol=f"{symbol}BTC", valid=True
        )
    config = StrongMoversConfig(selected_exchange="Bybit")
    return run_strong_movers(
        assets, config=config,
        usdt_results=usdt_results, btc_results=btc_results,
    )


# ---------------------------------------------------------------------------
# Top-3 preparation
# ---------------------------------------------------------------------------


def test_preserve_exchange_contract():
    output = _make_output()
    data = prepare_for_top3(output)
    assert data["selected_exchange"] == "Bybit"
    assert "display_fallback_priority" in data


def test_preserve_movement_evidence():
    output = _make_output()
    data = prepare_for_top3(output)
    for mover in data["strong_movers"]:
        assert "movement_score" in mover
        assert "reliability_score" in mover
        assert "total_score" in mover
        assert "usdt_change_pct" in mover
        assert "usdt_volume" in mover


def test_preserve_reliability_evidence():
    output = _make_output()
    data = prepare_for_top3(output)
    for mover in data["strong_movers"]:
        assert "reliability_evidence" in mover
        assert isinstance(mover["reliability_evidence"], dict)


def test_preserve_timeframe():
    output = _make_output()
    data = prepare_for_top3(output)
    for mover in data["strong_movers"]:
        assert mover["timeframe"] == "5m"


def test_preserve_usdt_btc_contract():
    output = _make_output()
    data = prepare_for_top3(output)
    for mover in data["strong_movers"]:
        assert "usdt_pair" in mover
        assert "btc_pair" in mover
        assert "usdt_source" in mover
        assert "btc_source" in mover
        assert "usdt_fallback_used" in mover
        assert "btc_fallback_used" in mover


def test_preserve_source_fallback():
    output = _make_output()
    data = prepare_for_top3(output)
    for mover in data["strong_movers"]:
        assert mover["usdt_source"] != ""
        assert mover["btc_source"] != ""


def test_no_top3_selection():
    output = _make_output()
    data = prepare_for_top3(output)
    assert "top3" not in data
    assert "selected_top3" not in data
    assert data["stage"] == "strong_movers"


def test_no_invented_third_metric():
    output = _make_output()
    data = prepare_for_top3(output)
    for mover in data["strong_movers"]:
        assert set(mover.keys()) == {
            "kitchen_rank", "symbol", "usdt_pair", "usdt_change_pct",
            "usdt_volume", "usdt_source", "usdt_fallback_used",
            "usdt_fallback_exchange", "btc_pair", "btc_change_pct",
            "btc_source", "btc_fallback_used", "btc_fallback_exchange",
            "btc_available", "movement_score", "reliability_score",
            "total_score", "reliability_evidence", "timeframe", "valid",
        }


def test_downstream_can_consume():
    output = _make_output()
    data = prepare_for_top3(output)
    assert data["strong_movers"] is not None
    assert len(data["strong_movers"]) == 5
    for mover in data["strong_movers"]:
        assert "usdt_change_pct" in mover
        assert "btc_available" in mover
        assert "total_score" in mover


# ---------------------------------------------------------------------------
# Integration with run_strong_movers
# ---------------------------------------------------------------------------


def test_output_strong_movers_for_top3():
    output = _make_output()
    data = prepare_for_top3(output)
    assert data["stage"] == "strong_movers"
    for mover in data["strong_movers"]:
        assert mover["valid"] is True
        assert mover["usdt_change_pct"] is not None


def test_exchange_remains_traceable():
    output = _make_output()
    data = prepare_for_top3(output)
    assert data["selected_exchange"] is not None
    for mover in data["strong_movers"]:
        assert mover["usdt_source"] is not None
        assert mover["btc_source"] is not None


def test_no_lossy_transformation():
    output = _make_output()
    data = prepare_for_top3(output)
    for orig, prep in zip(output.strong_movers, data["strong_movers"]):
        assert orig.usdt_change_pct == prep["usdt_change_pct"]
        assert orig.usdt_volume == prep["usdt_volume"]
        assert orig.btc_available == prep["btc_available"]
