from app.data.capture.market_data import (
    BinancePublicAdapter,
    BinanceProviderUnavailable,
    CoinbasePublicAdapter,
    CoinbaseProviderUnavailable,
    provider_symbol,
    positive_decimal,
    non_negative_decimal,
    utc_now,
    now_ms,
    rolling_range,
    build_record,
    validate_records,
    capture_with_priority,
    calculate_rolling_volume,
    fetch_from_provider,
)
from app.config.market_data import (
    SYMBOLS,
    INTERVAL,
    CANDLES_PER_SYMBOL,
    REQUESTED_DURATION_MINUTES,
    REQUESTED_RANGE_MODE,
    PROVIDER_PRIORITY,
    TRADING_ENABLED,
    ORDERS_ENABLED,
    STRATEGY_ENABLED,
)

import pytest
import app.data.capture.market_data as u05_module


def test_constants():

    assert SYMBOLS == [
        "BTCUSDT",
        "ETHUSDT",
        "SOLUSDT",
        "XRPUSDT",
        "ADAUSDT",
    ]

    assert INTERVAL == "1m"
    assert CANDLES_PER_SYMBOL == 100
    assert REQUESTED_DURATION_MINUTES == 60
    assert REQUESTED_RANGE_MODE == "ROLLING_END_AT_NOW"
    assert PROVIDER_PRIORITY == [
        "BINANCE_SPOT_PUBLIC",
        "COINBASE_EXCHANGE_PUBLIC",
    ]
    assert TRADING_ENABLED is False
    assert ORDERS_ENABLED is False
    assert STRATEGY_ENABLED is False


def test_binance_adapter_exists():

    adapter = BinancePublicAdapter()

    assert adapter.provider_name == "BINANCE_SPOT_PUBLIC"
    assert len(adapter.BASE_URLS) == 5


def test_coinbase_adapter_exists():

    adapter = CoinbasePublicAdapter()

    assert adapter.provider_name == "COINBASE_EXCHANGE_PUBLIC"
    assert adapter.BASE_URL == "https://api.exchange.coinbase.com"


def test_provider_symbol_binance_passthrough():

    assert (
        provider_symbol("BINANCE_SPOT_PUBLIC", "BTCUSDT")
        == "BTCUSDT"
    )

    assert (
        provider_symbol("BINANCE_SPOT_PUBLIC", "ETHUSDT")
        == "ETHUSDT"
    )


def test_provider_symbol_coinbase_usdt():

    assert (
        provider_symbol(
            "COINBASE_EXCHANGE_PUBLIC", "BTCUSDT"
        )
        == "BTC-USD"
    )

    assert (
        provider_symbol(
            "COINBASE_EXCHANGE_PUBLIC", "ETHUSDT"
        )
        == "ETH-USD"
    )


def test_provider_symbol_coinbase_usd():

    assert (
        provider_symbol(
            "COINBASE_EXCHANGE_PUBLIC", "BTCUSD"
        )
        == "BTC-USD"
    )


def test_provider_symbol_unknown_provider():

    with pytest.raises(ValueError):
        provider_symbol("UNKNOWN", "BTCUSDT")


def test_provider_symbol_coinbase_unsupported():

    with pytest.raises(ValueError):
        provider_symbol(
            "COINBASE_EXCHANGE_PUBLIC", "BTC"
        )


def test_positive_decimal_valid():

    assert positive_decimal(100, "test") == 100.0
    assert positive_decimal("50.5", "test") == 50.5
    assert positive_decimal(0.001, "test") == 0.001


def test_positive_decimal_zero_rejected():

    with pytest.raises(RuntimeError):
        positive_decimal(0, "test")


def test_positive_decimal_negative_rejected():

    with pytest.raises(RuntimeError):
        positive_decimal(-1, "test")


def test_positive_decimal_invalid_string():

    with pytest.raises(RuntimeError):
        positive_decimal("abc", "test")


def test_non_negative_decimal_valid():

    assert non_negative_decimal(100, "test") == 100.0
    assert non_negative_decimal(0, "test") == 0.0
    assert non_negative_decimal("0.0", "test") == 0.0


def test_non_negative_decimal_negative_rejected():

    with pytest.raises(RuntimeError):
        non_negative_decimal(-1, "test")


def test_non_negative_decimal_invalid_string():

    with pytest.raises(RuntimeError):
        non_negative_decimal("xyz", "test")


def test_utc_now_returns_aware_datetime():

    dt = utc_now()

    assert dt is not None
    assert dt.tzinfo is not None


def test_now_ms_positive():

    ts = now_ms()

    assert ts > 0
    assert isinstance(ts, int)


def test_rolling_range_structure():

    rr = rolling_range()

    assert rr["mode"] == "ROLLING_END_AT_NOW"
    assert rr["duration_minutes"] == 60
    assert rr["start_ms"] < rr["end_ms"]
    assert isinstance(rr["start_ms"], int)
    assert isinstance(rr["end_ms"], int)


def test_rolling_range_duration():

    rr = rolling_range()

    diff_ms = rr["end_ms"] - rr["start_ms"]

    assert diff_ms == 60 * 60 * 1000


def test_build_record():

    candle = {
        "timestamp": 1700000000000,
        "open": 50000.0,
        "high": 50100.0,
        "low": 49900.0,
        "close": 50050.0,
        "volume_base": 100.0,
        "volume_usd": 5000000.0,
        "volume_usd_exact": True,
        "volume_usd_source": "BINANCE_KLINE_QUOTE_VOLUME",
    }

    record = build_record(
        candle=candle,
        symbol="BTCUSDT",
        provider_name="BINANCE_SPOT_PUBLIC",
        provider_symbol_value="BTCUSDT",
    )

    assert record["symbol"] == "BTCUSDT"
    assert record["provider"] == "BINANCE_SPOT_PUBLIC"
    assert record["interval"] == "1m"
    assert record["timestamp"] == 1700000000000
    assert record["open"] == 50000.0
    assert record["high"] == 50100.0
    assert record["low"] == 49900.0
    assert record["close"] == 50050.0
    assert record["volume_base"] == 100.0
    assert record["volume_definition"] == (
        "TOTAL_TRADED_BASE_ASSET_VOLUME"
    )
    assert record["volume_source"] == "PROVIDER_SUPPLIED"
    assert record["volume_counting_rule"] == (
        "EACH_TRADE_COUNTED_ONCE"
    )
    assert record["volume_double_counting"] is False
    assert record["buyer_seller_not_double_counted"] is True
    assert record["total_series_included"] is False
    assert record["trading_enabled"] is False
    assert record["orders_enabled"] is False
    assert record["strategy_enabled"] is False


def _make_record(
    timestamp: int,
    symbol: str = "BTCUSDT",
) -> dict:

    return build_record(
        candle={
            "timestamp": timestamp,
            "open": 50000.0,
            "high": 50100.0,
            "low": 49900.0,
            "close": 50050.0,
            "volume_base": 100.0,
            "volume_usd": 5000000.0,
            "volume_usd_exact": True,
            "volume_usd_source": "TEST",
        },
        symbol=symbol,
        provider_name="BINANCE_SPOT_PUBLIC",
        provider_symbol_value="BTCUSDT",
    )


def _make_records(n: int, symbol: str = "BTCUSDT") -> list[dict]:

    return [
        _make_record(
            timestamp=1700000000000 + i * 60000,
            symbol=symbol,
        )
        for i in range(n)
    ]


def test_validate_records_valid(monkeypatch):

    monkeypatch.setattr(
        u05_module, "CANDLES_PER_SYMBOL", 3
    )

    records = _make_records(3)

    result = validate_records(records, "BTCUSDT")

    assert len(result) == 3


def test_validate_records_count_mismatch(monkeypatch):

    monkeypatch.setattr(
        u05_module, "CANDLES_PER_SYMBOL", 100
    )

    records = _make_records(3)

    with pytest.raises(RuntimeError, match="CANDLE COUNT"):
        validate_records(records, "BTCUSDT")


def test_validate_records_non_chronological(monkeypatch):

    monkeypatch.setattr(
        u05_module, "CANDLES_PER_SYMBOL", 3
    )

    records = [
        _make_record(170000000360000),
        _make_record(1700000000000),
        _make_record(170000000100),
    ]

    with pytest.raises(RuntimeError, match="Chronological"):
        validate_records(records, "BTCUSDT")


def test_validate_records_duplicate_timestamps(monkeypatch):

    monkeypatch.setattr(
        u05_module, "CANDLES_PER_SYMBOL", 3
    )

    records = _make_records(3)
    records[1]["timestamp"] = records[0]["timestamp"]

    with pytest.raises(RuntimeError, match="Duplicate"):
        validate_records(records, "BTCUSDT")


def test_validate_records_symbol_mismatch(monkeypatch):

    monkeypatch.setattr(
        u05_module, "CANDLES_PER_SYMBOL", 3
    )

    records = _make_records(3, "ETHUSDT")

    with pytest.raises(RuntimeError, match="Symbol mismatch"):
        validate_records(records, "BTCUSDT")


def test_validate_records_ohlc_bounds(monkeypatch):

    monkeypatch.setattr(
        u05_module, "CANDLES_PER_SYMBOL", 3
    )

    records = _make_records(3)
    records[0]["open"] = 0

    with pytest.raises(RuntimeError, match="Invalid open"):
        validate_records(records, "BTCUSDT")


def test_validate_records_high_below_low(monkeypatch):

    monkeypatch.setattr(
        u05_module, "CANDLES_PER_SYMBOL", 3
    )

    records = _make_records(3)
    records[0]["high"] = 49000.0
    records[0]["low"] = 50000.0

    with pytest.raises(RuntimeError, match="Invalid high/low"):
        validate_records(records, "BTCUSDT")


def test_validate_records_volume_contract(monkeypatch):

    monkeypatch.setattr(
        u05_module, "CANDLES_PER_SYMBOL", 3
    )

    records = _make_records(3)
    records[0]["volume_source"] = "ESTIMATED"

    with pytest.raises(
        RuntimeError, match="Volume source"
    ):
        validate_records(records, "BTCUSDT")


def test_validate_records_double_counting(monkeypatch):

    monkeypatch.setattr(
        u05_module, "CANDLES_PER_SYMBOL", 3
    )

    records = _make_records(3)
    records[0]["volume_double_counting"] = True

    with pytest.raises(
        RuntimeError, match="double counting"
    ):
        validate_records(records, "BTCUSDT")


def test_validate_records_buyer_seller_flag(monkeypatch):

    monkeypatch.setattr(
        u05_module, "CANDLES_PER_SYMBOL", 3
    )

    records = _make_records(3)
    records[0]["buyer_seller_not_double_counted"] = False

    with pytest.raises(
        RuntimeError, match="Buyer/seller"
    ):
        validate_records(records, "BTCUSDT")


def test_validate_records_negative_volume(monkeypatch):

    monkeypatch.setattr(
        u05_module, "CANDLES_PER_SYMBOL", 3
    )

    records = _make_records(3)
    records[0]["volume_base"] = -10.0

    with pytest.raises(RuntimeError, match="Negative volume"):
        validate_records(records, "BTCUSDT")


def test_safety_locks_importable():

    from app.config.market_data import (
        TRADING_ENABLED,
        ORDERS_ENABLED,
        STRATEGY_ENABLED,
    )

    assert TRADING_ENABLED is False
    assert ORDERS_ENABLED is False
    assert STRATEGY_ENABLED is False
