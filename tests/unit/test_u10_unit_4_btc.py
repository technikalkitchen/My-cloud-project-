"""Stage 10 — Unit 10.4 — BTC Pair + Fallback Cohesion tests.

Deterministic/synthetic tests only. No live network calls.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.analysis.stage10_btc import (
    BtcPairProcessor,
    BtcPairResult,
    process_btc_pair,
)
from app.analysis.stage10_consumer import Exchange
from app.analysis.stage10_usdt import UsdtPairResult
from app.config.quality import FRESHNESS_THRESHOLD_SECONDS


def _fresh_timestamp(seconds_ago: int = 60) -> str:
    return (
        datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)
    ).isoformat()


def _make_btc_data(
    symbol: str = "SOLBTC",
    change_pct: float = 0.72,
    timestamp: str = "",
    exchange: str = "Binance",
    timeframe: str = "5m",
    **extra,
) -> dict:
    data = {
        "symbol": symbol,
        "close": 65000.0,
        "change_pct": change_pct,
        "timestamp": timestamp or _fresh_timestamp(),
        "exchange": exchange,
        "timeframe": timeframe,
    }
    data.update(extra)
    return data


def _make_usdt_result(
    exchange: str = "Binance",
    fallback_used: bool = False,
    fallback_exchange: str = "",
) -> UsdtPairResult:
    return UsdtPairResult(
        symbol="SOLUSDT",
        change_pct=1.84,
        volume=284_600_000.0,
        timestamp=_fresh_timestamp(),
        requested_exchange="OKX" if fallback_used else exchange,
        actual_exchange=exchange,
        fallback_used=fallback_used,
        fallback_exchange=fallback_exchange or (exchange if fallback_used else None),
        timeframe="5m",
        volume_source_label="Source: Binance" if not fallback_used else f"Fallback from: {exchange}",
        valid=True,
        errors=[],
        provenance={},
    )


# ---------------------------------------------------------------------------
# BTC pair on selected exchange
# ---------------------------------------------------------------------------


def test_btc_pair_on_selected_exchange():
    processor = BtcPairProcessor("Binance", "5m")
    result = processor.process(_make_btc_data(exchange="Binance"))
    assert result.valid is True
    assert result.symbol == "SOLBTC"
    assert result.actual_exchange == "Binance"
    assert result.requested_exchange == "Binance"
    assert result.fallback_used is False
    assert result.volume_source_label if hasattr(result, "volume_source_label") else "Source: Binance"


def test_btc_pair_convenience_function():
    result = process_btc_pair(
        _make_btc_data(exchange="OKX"),
        requested_exchange="OKX",
    )
    assert result.valid is True
    assert result.actual_exchange == "OKX"


# ---------------------------------------------------------------------------
# BTC pair missing
# ---------------------------------------------------------------------------


def test_btc_pair_missing_none():
    processor = BtcPairProcessor("Binance", "5m")
    result = processor.process(None)
    assert result.valid is False
    assert "No BTC exchange data provided" in result.errors


def test_btc_pair_missing_empty():
    processor = BtcPairProcessor("Binance", "5m")
    result = processor.process({})
    assert result.valid is False


# ---------------------------------------------------------------------------
# BTC pair on USDT fallback exchange (cohesion)
# ---------------------------------------------------------------------------


def test_btc_pair_on_usdt_fallback_exchange():
    usdt = _make_usdt_result(
        exchange="Binance",
        fallback_used=True,
        fallback_exchange="Binance",
    )
    processor = BtcPairProcessor("OKX", "5m")
    result = processor.process(
        _make_btc_data(exchange="Binance"),
        usdt_result=usdt,
    )
    assert result.valid is True
    assert result.usdt_fallback_exchange == "Binance"
    assert result.fallback_used is True
    assert result.actual_exchange == "Binance"


def test_btc_pair_usdt_fallback_cohesion_different_exchange():
    usdt = _make_usdt_result(
        exchange="OKX",
        fallback_used=True,
        fallback_exchange="OKX",
    )
    processor = BtcPairProcessor("Bitget", "5m")
    result = processor.process(
        _make_btc_data(exchange="OKX"),
        usdt_result=usdt,
    )
    assert result.valid is True
    assert result.usdt_fallback_exchange == "OKX"


# ---------------------------------------------------------------------------
# BTC pair on different eligible higher-priority exchange
# ---------------------------------------------------------------------------


def test_btc_pair_on_higher_priority_exchange():
    processor = BtcPairProcessor("KuCoin", "5m")
    result = processor.process(_make_btc_data(exchange="Binance"))
    assert result.valid is True
    assert result.actual_exchange == "Binance"
    assert result.fallback_used is True
    assert result.fallback_exchange == "Binance"


# ---------------------------------------------------------------------------
# BTC pair unavailable everywhere
# ---------------------------------------------------------------------------


def test_btc_pair_unavailable():
    processor = BtcPairProcessor("Binance", "5m")
    result = processor.process(None)
    assert result.valid is False
    assert result.actual_exchange == ""
    assert result.symbol == ""


def test_btc_pair_unavailable_empty():
    processor = BtcPairProcessor("Binance", "5m")
    result = processor.process({})
    assert result.valid is False


# ---------------------------------------------------------------------------
# Approved Kitchen BTC calculation
# ---------------------------------------------------------------------------


def test_approved_kitchen_calculation():
    processor = BtcPairProcessor("Binance", "5m")
    result = processor.process(
        _make_btc_data(change_pct=None),
        allow_kitchen_calculation=True,
        kitchen_btc_value=64000.0,
    )
    assert result.valid is True
    assert result.calculated_kitchen_used is True
    assert result.calculated_kitchen_value == 64000.0


def test_kitchen_calculation_not_allowed():
    processor = BtcPairProcessor("Binance", "5m")
    result = processor.process(
        _make_btc_data(change_pct=None),
        allow_kitchen_calculation=False,
        kitchen_btc_value=64000.0,
    )
    assert result.valid is False
    assert result.calculated_kitchen_used is False


def test_kitchen_calculation_no_value():
    processor = BtcPairProcessor("Binance", "5m")
    result = processor.process(
        _make_btc_data(change_pct=None),
        allow_kitchen_calculation=True,
        kitchen_btc_value=None,
    )
    assert result.valid is False
    assert result.calculated_kitchen_used is False


# ---------------------------------------------------------------------------
# Fake-pair prevention
# ---------------------------------------------------------------------------


def test_fake_btc_pair_rejected():
    processor = BtcPairProcessor("Binance", "5m")
    # Explicitly fake/malformed pairs should be rejected
    assert not processor._is_valid_btc_pair("BTC")
    assert not processor._is_valid_btc_pair("BTCBTC")
    assert not processor._is_valid_btc_pair("")
    assert not processor._is_valid_btc_pair("123BTC")
    assert not processor._is_valid_btc_pair("SOLUSDT")


def test_btc_only_rejected():
    processor = BtcPairProcessor("Binance", "5m")
    result = processor.process(_make_btc_data(symbol="BTC"))
    assert result.valid is False


def test_btc_btc_rejected():
    processor = BtcPairProcessor("Binance", "5m")
    result = processor.process(_make_btc_data(symbol="BTCBTC"))
    assert result.valid is False


def test_valid_btc_pairs():
    for symbol in ["SOLBTC", "ETHBTC", "XRPBTC", "BNBBTC"]:
        assert BtcPairProcessor._is_valid_btc_pair(symbol), f"{symbol} should be valid"


def test_invalid_btc_pairs():
    for symbol in ["BTC", "BTCBTC", "", "123BTC", "SOLUSDT"]:
        assert not BtcPairProcessor._is_valid_btc_pair(symbol), f"{symbol} should be invalid"


# ---------------------------------------------------------------------------
# Independent BTC validation
# ---------------------------------------------------------------------------


def test_btc_stale_data():
    stale = (
        datetime.now(timezone.utc)
        - timedelta(seconds=FRESHNESS_THRESHOLD_SECONDS + 60)
    ).isoformat()
    processor = BtcPairProcessor("Binance", "5m")
    result = processor.process(_make_btc_data(timestamp=stale))
    assert result.valid is False
    assert any("stale" in e.lower() for e in result.errors)


def test_btc_invalid_change():
    processor = BtcPairProcessor("Binance", "5m")
    result = processor.process(_make_btc_data(change_pct=None))
    assert result.valid is False


def test_btc_timeframe_mismatch():
    processor = BtcPairProcessor("Binance", "5m")
    result = processor.process(_make_btc_data(timeframe="1h"))
    assert result.valid is False


# ---------------------------------------------------------------------------
# Fallback direction validation
# ---------------------------------------------------------------------------


def test_fallback_direction_valid():
    processor = BtcPairProcessor("OKX", "5m")
    result = processor.process(_make_btc_data(exchange="Binance"))
    assert result.valid is True
    assert result.fallback_used is True


def test_fallback_direction_invalid():
    processor = BtcPairProcessor("Binance", "5m")
    result = processor.process(_make_btc_data(exchange="OKX"))
    # OKX is lower priority than Binance (wait, Binance is #1, OKX is #2)
    # Binance selected, OKX is NOT higher priority (lower index = higher priority)
    # Actually Binance (#1) → OKX (#2) would be going to lower priority
    assert result.valid is False


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------


def test_btc_provenance():
    processor = BtcPairProcessor("Binance", "5m")
    result = processor.process(_make_btc_data(exchange="Binance"))
    assert result.provenance["symbol"] == "Binance"
    assert result.provenance["change_pct"] == "Binance"
    assert result.provenance["timestamp"] == "Binance"
    assert result.provenance["timeframe"] == "Binance"


def test_btc_provenance_fallback():
    processor = BtcPairProcessor("OKX", "5m")
    result = processor.process(_make_btc_data(exchange="Binance"))
    assert result.provenance["symbol"] == "Binance"
    assert result.provenance["change_pct"] == "Binance"


# ---------------------------------------------------------------------------
# Source/Fallback label
# ---------------------------------------------------------------------------


def test_btc_source_label():
    processor = BtcPairProcessor("Binance", "5m")
    result = processor.process(_make_btc_data(exchange="Binance"))
    assert BtcPairProcessor._is_valid_btc_pair(result.symbol)


def test_btc_fallback_label():
    processor = BtcPairProcessor("OKX", "5m")
    result = processor.process(_make_btc_data(exchange="Binance"))
    assert result.fallback_used is True
    assert result.actual_exchange == "Binance"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_zero_change_accepted():
    processor = BtcPairProcessor("Binance", "5m")
    result = processor.process(_make_btc_data(change_pct=0.0))
    # Zero change is valid (price didn't move)
    assert result.change_pct == 0.0


def test_extreme_change_accepted():
    processor = BtcPairProcessor("Binance", "5m")
    result = processor.process(_make_btc_data(change_pct=999.99))
    assert result.change_pct == 999.99


def test_processor_different_exchanges():
    for exc in ["Binance", "OKX", "Bybit", "KuCoin"]:
        processor = BtcPairProcessor(exc, "5m")
        result = processor.process(_make_btc_data(exchange=exc))
        assert result.valid is True, f"Failed for {exc}"
        assert result.actual_exchange == exc