"""Stage 10 — Unit 10.3 — USDT Pair + Volume tests.

Deterministic/synthetic tests only. No live network calls.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

from app.analysis.stage10_usdt import (
    UsdtPairProcessor,
    UsdtPairResult,
    process_usdt_pair,
    VALID_VOLUME_SOURCE,
)
from app.analysis.stage10_consumer import Exchange
from app.analysis.stage10_router import ExchangeRouter
from app.config.quality import FRESHNESS_THRESHOLD_SECONDS


def _fresh_timestamp(seconds_ago: int = 60) -> str:
    return (
        datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)
    ).isoformat()


def _make_usdt_data(
    symbol: str = "SOLUSDT",
    change_pct: float = 1.84,
    volume: float = 284_600_000.0,
    timestamp: str = "",
    exchange: str = "Binance",
    timeframe: str = "5m",
    volume_source: str = VALID_VOLUME_SOURCE,
    **extra,
) -> dict:
    data = {
        "symbol": symbol,
        "close": 165.50,
        "change_pct": change_pct,
        "volume": volume,
        "timestamp": timestamp or _fresh_timestamp(),
        "volume_source": volume_source,
        "exchange": exchange,
        "timeframe": timeframe,
    }
    data.update(extra)
    return data


# ---------------------------------------------------------------------------
# Valid pair
# ---------------------------------------------------------------------------


def test_valid_pair():
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process(_make_usdt_data())
    assert result.valid is True
    assert result.symbol == "SOLUSDT"
    assert result.change_pct == 1.84
    assert result.volume == 284_600_000.0
    assert result.volume_source_label == "Source: Binance"
    assert result.fallback_used is False
    assert result.actual_exchange == "Binance"
    assert result.provenance["change_pct"] == "Binance"
    assert result.provenance["volume"] == "Binance"
    assert result.provenance["timestamp"] == "Binance"


def test_valid_pair_convenience_function():
    result = process_usdt_pair(
        _make_usdt_data(exchange="OKX"),
        requested_exchange="OKX",
        timeframe="5m",
    )
    assert result.valid is True
    assert result.requested_exchange == "OKX"
    assert result.actual_exchange == "OKX"


# ---------------------------------------------------------------------------
# Missing pair
# ---------------------------------------------------------------------------


def test_missing_pair_none():
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process(None)
    assert result.valid is False
    assert "No exchange data provided" in result.errors


def test_missing_pair_empty():
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process({})
    assert result.valid is False
    assert result.symbol == ""
    assert any("USDT" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Stale data
# ---------------------------------------------------------------------------


def test_stale_data():
    stale = (
        datetime.now(timezone.utc)
        - timedelta(seconds=FRESHNESS_THRESHOLD_SECONDS + 60)
    ).isoformat()
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process(
        _make_usdt_data(timestamp=stale)
    )
    assert result.valid is False
    assert any("stale" in e.lower() for e in result.errors)


def test_fresh_data():
    fresh = _fresh_timestamp(seconds_ago=30)
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process(
        _make_usdt_data(timestamp=fresh)
    )
    assert result.valid is True


def test_fresh_boundary():
    fresh = _fresh_timestamp(seconds_ago=int(FRESHNESS_THRESHOLD_SECONDS / 2))
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process(_make_usdt_data(timestamp=fresh))
    assert result.valid is True


# ---------------------------------------------------------------------------
# Invalid data
# ---------------------------------------------------------------------------


def test_invalid_change_pct_none():
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process(_make_usdt_data(change_pct=None))
    assert result.valid is False
    assert any("change_pct" in e for e in result.errors)


def test_invalid_change_pct_nan():
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process(_make_usdt_data(change_pct=float("nan")))
    assert result.valid is False
    assert result.change_pct is None
    assert any("change_pct" in e for e in result.errors)


def test_invalid_volume_none():
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process(_make_usdt_data(volume=None))
    assert result.valid is False
    assert any("volume" in e for e in result.errors)


def test_invalid_volume_negative():
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process(_make_usdt_data(volume=-100.0))
    assert result.valid is False
    assert any("negative" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Correct timeframe
# ---------------------------------------------------------------------------


def test_correct_timeframe():
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process(
        _make_usdt_data(timeframe="5m")
    )
    assert result.valid is True
    assert result.timeframe == "5m"


# ---------------------------------------------------------------------------
# No 24h substitution
# ---------------------------------------------------------------------------


def test_no_24h_substitution():
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process(
        _make_usdt_data(timeframe="24h")
    )
    assert result.valid is False
    assert any("timeframe" in e.lower() for e in result.errors)
    assert any("5m" in e for e in result.errors)


def test_timeframe_mismatch_1h():
    processor = UsdtPairProcessor("Binance", "1h")
    result = processor.process(
        _make_usdt_data(timeframe="5m")
    )
    assert result.valid is False
    assert any("mismatch" in e for e in result.errors)


# ---------------------------------------------------------------------------
# No fabricated volume
# ---------------------------------------------------------------------------


def test_no_fabricated_volume_source():
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process(
        _make_usdt_data(
            volume_source="CALCULATED_VOLUME"
        )
    )
    assert result.valid is False
    assert any("PROVIDER_SUPPLIED" in e for e in result.errors)


def test_no_close_times_volume():
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process(
        _make_usdt_data(
            volume_source="CLOSE_TIMES_VOLUME",
            volume=1_000_000.0,
        )
    )
    assert result.valid is False
    assert any("PROVIDER_SUPPLIED" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Source / Fallback presentation
# ---------------------------------------------------------------------------


def test_source_label_when_requested_used():
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process(
        _make_usdt_data(exchange="Binance")
    )
    assert result.volume_source_label == "Source: Binance"
    assert result.fallback_used is False


def test_fallback_from_label():
    processor = UsdtPairProcessor("OKX", "5m")
    result = processor.process(
        _make_usdt_data(exchange="Binance")
    )
    assert result.volume_source_label == "Fallback from: Binance"
    assert result.fallback_used is True
    assert result.fallback_exchange == "Binance"


def test_fallback_direction_valid():
    router = ExchangeRouter(Exchange.OKX)
    result = router.route_with_provenance({"Binance": {"ok": True}})
    assert result.fallback_used is True
    assert result.actual_exchange == "Binance"


def test_fallback_direction_invalid():
    processor = UsdtPairProcessor("OKX", "5m")
    result = processor.process(
        _make_usdt_data(exchange="Bybit")
    )
    assert result.valid is False
    assert any("fallback" in e.lower() for e in result.errors)


# ---------------------------------------------------------------------------
# Per-field provenance
# ---------------------------------------------------------------------------


def test_provenance_tracking():
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process(
        _make_usdt_data(exchange="Binance")
    )
    assert result.provenance["symbol"] == "Binance"
    assert result.provenance["change_pct"] == "Binance"
    assert result.provenance["volume"] == "Binance"
    assert result.provenance["timestamp"] == "Binance"
    assert result.provenance["timeframe"] == "Binance"


def test_provenance_fallback():
    processor = UsdtPairProcessor("OKX", "5m")
    result = processor.process(
        _make_usdt_data(exchange="Binance")
    )
    assert result.provenance["change_pct"] == "Binance"
    assert result.provenance["volume"] == "Binance"


# ---------------------------------------------------------------------------
# USDT symbol validation
# ---------------------------------------------------------------------------


def test_usdt_symbol_valid():
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process(_make_usdt_data(symbol="ETHUSDT"))
    assert result.valid is True or "USDT pair" not in str(result.errors)


def test_usdt_symbol_btc_rejected():
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process(_make_usdt_data(symbol="BTCUSD"))
    assert result.valid is False
    assert any("USDT pair" in e for e in result.errors)


def test_usdt_symbol_missing():
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process(_make_usdt_data(symbol=""))
    assert result.valid is False
    assert any("USDT pair" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_zero_volume_rejected():
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process(_make_usdt_data(volume=0.0))
    assert result.valid is False


def test_extreme_change_pct_accepted():
    processor = UsdtPairProcessor("Binance", "5m")
    result = processor.process(_make_usdt_data(change_pct=999.99))
    assert result.change_pct == 999.99


def test_processor_different_exchanges():
    for exc in ["Binance", "OKX", "Bybit", "KuCoin", "Coinbase", "Gate", "Upbit", "Bitget"]:
        processor = UsdtPairProcessor(exc, "5m")
        result = processor.process(_make_usdt_data(exchange=exc))
        assert result.valid is True, f"Failed for {exc}"
        assert result.volume_source_label == f"Source: {exc}"
