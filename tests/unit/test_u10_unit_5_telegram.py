"""Stage 10 — Unit 10.5 — Telegram Output + RTL/LTR tests.

Deterministic/synthetic tests only. No live network calls.
"""
from __future__ import annotations

from app.analysis.stage10_telegram import (
    TelegramFormatter,
    TelegramOutput,
    format_top10_telegram,
    SOURCE_LABEL,
    FALLBACK_LABEL,
    VOLUME_LABEL,
    TOP10_HEADER,
)
from app.analysis.stage10_usdt import UsdtPairResult
from app.analysis.stage10_btc import BtcPairResult


def _make_usdt_result(
    exchange: str = "Binance",
    fallback_used: bool = False,
    change_pct: float = 1.84,
    volume: float = 284_600_000.0,
) -> UsdtPairResult:
    return UsdtPairResult(
        symbol="SOLUSDT",
        change_pct=change_pct,
        volume=volume,
        timestamp="2026-09-14T15:30:00+00:00",
        requested_exchange="OKX" if fallback_used else exchange,
        actual_exchange=exchange,
        fallback_used=fallback_used,
        fallback_exchange=exchange if fallback_used else None,
        timeframe="5m",
        volume_source_label="",
        valid=True,
        errors=[],
        provenance={},
    )


def _make_btc_result(
    exchange: str = "Binance",
    fallback_used: bool = False,
    change_pct: float = 0.72,
) -> BtcPairResult:
    return BtcPairResult(
        symbol="SOLBTC",
        change_pct=change_pct,
        timestamp="2026-09-14T15:30:00+00:00",
        requested_exchange="OKX" if fallback_used else exchange,
        actual_exchange=exchange,
        fallback_used=fallback_used,
        fallback_exchange=exchange if fallback_used else None,
        usdt_fallback_exchange=None,
        calculated_kitchen_value=None,
        calculated_kitchen_used=False,
        timeframe="5m",
        valid=True,
        errors=[],
        provenance={},
    )


def _make_assets(count: int = 3):
    return [
        {"kitchen_rank": i + 2, "symbol": s}
        for i, s in enumerate(["SOL", "ETH", "XRP"][:count])
    ]


# ---------------------------------------------------------------------------
# Normal Source
# ---------------------------------------------------------------------------


def test_normal_source():
    formatter = TelegramFormatter(view="EXCHANGE")
    result = formatter.format_top10(
        _make_assets(1),
        {"SOLUSDT": _make_usdt_result("Binance")},
        {"SOLBTC": _make_btc_result("Binance")},
    )
    assert SOURCE_LABEL + ": Binance" in result.message
    assert FALLBACK_LABEL not in result.message
    assert result.source_label == SOURCE_LABEL + ": Binance"


# ---------------------------------------------------------------------------
# Fallback
# ---------------------------------------------------------------------------


def test_fallback():
    formatter = TelegramFormatter(view="EXCHANGE")
    result = formatter.format_top10(
        _make_assets(1),
        {"SOLUSDT": _make_usdt_result("OKX", fallback_used=True)},
        {"SOLBTC": _make_btc_result("OKX", fallback_used=True)},
    )
    assert FALLBACK_LABEL + ": OKX" in result.message
    assert SOURCE_LABEL + ":" not in result.message
    assert result.fallback_label is not None


# ---------------------------------------------------------------------------
# Mixed Source/Fallback
# ---------------------------------------------------------------------------


def test_mixed_source_fallback():
    formatter = TelegramFormatter(view="EXCHANGE")
    result = formatter.format_top10(
        _make_assets(1),
        {"SOLUSDT": _make_usdt_result("Binance")},
        {"SOLBTC": _make_btc_result("OKX", fallback_used=True)},
    )
    assert SOURCE_LABEL + ": Binance" in result.message
    assert FALLBACK_LABEL + ": OKX" in result.message


# ---------------------------------------------------------------------------
# Same fallback
# ---------------------------------------------------------------------------


def test_same_fallback():
    formatter = TelegramFormatter(view="EXCHANGE")
    result = formatter.format_top10(
        _make_assets(1),
        {"SOLUSDT": _make_usdt_result("Bybit", fallback_used=True)},
        {"SOLBTC": _make_btc_result("Bybit", fallback_used=True)},
    )
    assert FALLBACK_LABEL + ": Bybit" in result.message


# ---------------------------------------------------------------------------
# Different fallback
# ---------------------------------------------------------------------------


def test_different_fallback():
    formatter = TelegramFormatter(view="EXCHANGE")
    result = formatter.format_top10(
        _make_assets(1),
        {"SOLUSDT": _make_usdt_result("Bybit", fallback_used=True)},
        {"SOLBTC": _make_btc_result("Upbit", fallback_used=True)},
    )
    assert FALLBACK_LABEL + ": Bybit" in result.message
    assert FALLBACK_LABEL + ": Upbit" in result.message


# ---------------------------------------------------------------------------
# Kitchen View
# ---------------------------------------------------------------------------


def test_kitchen_view():
    formatter = TelegramFormatter(view="KITCHEN")
    result = formatter.format_top10(
        _make_assets(1),
        {"SOLUSDT": _make_usdt_result("Binance")},
        {"SOLBTC": _make_btc_result("Binance")},
    )
    assert result.view == "KITCHEN"
    assert result.source_label is not None


# ---------------------------------------------------------------------------
# Exchange View
# ---------------------------------------------------------------------------


def test_exchange_view():
    formatter = TelegramFormatter(view="EXCHANGE")
    result = formatter.format_top10(
        _make_assets(1),
        {"SOLUSDT": _make_usdt_result("Binance")},
        {"SOLBTC": _make_btc_result("Binance")},
    )
    assert result.view == "EXCHANGE"


# ---------------------------------------------------------------------------
# No duplicated Volume Source
# ---------------------------------------------------------------------------


def test_no_duplicated_volume_source():
    formatter = TelegramFormatter(view="EXCHANGE")
    result = formatter.format_top10(
        _make_assets(1),
        {"SOLUSDT": _make_usdt_result("Binance")},
        {"SOLBTC": _make_btc_result("Binance")},
    )
    # Volume should only appear once (for USDT)
    volume_count = result.message.count(VOLUME_LABEL)
    assert volume_count == 1


def test_btc_has_no_volume():
    formatter = TelegramFormatter(view="EXCHANGE")
    result = formatter.format_top10(
        _make_assets(1),
        {"SOLUSDT": _make_usdt_result("Binance")},
        {"SOLBTC": _make_btc_result("Binance")},
    )
    btc_block_start = result.message.find("SOLBTC")
    usdt_block_start = result.message.find("SOLUSDT")
    if btc_block_start > 0 and usdt_block_start > 0:
        btc_section = result.message[btc_block_start:]
        next_asset = btc_section.find("\n\n")
        if next_asset > 0:
            btc_section = btc_section[:next_asset]
        assert VOLUME_LABEL not in btc_section


# ---------------------------------------------------------------------------
# Persian + ticker + numbers (RTL/LTR)
# ---------------------------------------------------------------------------


def test_persian_ticker_numbers():
    formatter = TelegramFormatter(view="KITCHEN")
    assets = [{"kitchen_rank": 2, "symbol": "SOL"}]
    usdt_results = {
        "SOLUSDT": _make_usdt_result(
            "Binance", change_pct=1.84, volume=284_600_000
        ),
    }
    btc_results = {
        "SOLBTC": _make_btc_result("Binance", change_pct=0.72),
    }
    result = formatter.format_top10(assets, usdt_results, btc_results)
    assert "SOL" in result.message
    assert "1.84%" in result.message
    assert "0.72%" in result.message
    assert "284.6M" in result.message
    assert "Binance" in result.message
    assert result.asset_count == 1


def test_rtl_safety():
    result = format_top10_telegram(
        _make_assets(1),
        {"SOLUSDT": _make_usdt_result("Binance")},
        {"SOLBTC": _make_btc_result("Binance")},
    )
    assert TelegramFormatter.check_rtl_safety(result.message)


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------


def test_convenience_function():
    result = format_top10_telegram(
        _make_assets(1),
        {"SOLUSDT": _make_usdt_result("Binance")},
        {"SOLBTC": _make_btc_result("Binance")},
    )
    assert isinstance(result, TelegramOutput)
    assert TOP10_HEADER in result.message
    assert result.asset_count == 1


def test_header():
    result = format_top10_telegram(
        _make_assets(1),
        {"SOLUSDT": _make_usdt_result("Binance")},
        {"SOLBTC": _make_btc_result("Binance")},
    )
    assert result.message.startswith(TOP10_HEADER)
