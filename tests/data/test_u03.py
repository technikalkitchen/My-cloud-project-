from app.data.models.candle import Candle
from app.data.validation.candles import validate_candles
from app.data.validation.normalize import normalize_candle
from app.data.capture.storage import write_candles

import pytest


def sample_candle(timestamp: int) -> Candle:

    return Candle(
        symbol="BTCUSDT",
        timestamp=timestamp,
        open=100.0,
        high=110.0,
        low=90.0,
        close=105.0,
        volume=1000.0,
    )


def test_candle_model():

    candle = sample_candle(1000)

    assert candle.symbol == "BTCUSDT"
    assert candle.close == 105.0


def test_invalid_ohlc():

    with pytest.raises(ValueError):

        Candle(
            symbol="BTCUSDT",
            timestamp=1000,
            open=120.0,
            high=110.0,
            low=90.0,
            close=105.0,
            volume=1000.0,
        )


def test_chronological_validation():

    candles = [
        sample_candle(1000),
        sample_candle(2000),
    ]

    validated = validate_candles(candles)

    assert len(validated) == 2


def test_non_chronological_rejected():

    candles = [
        sample_candle(2000),
        sample_candle(1000),
    ]

    with pytest.raises(ValueError):

        validate_candles(candles)


def test_normalization():

    candle = normalize_candle({
        "symbol": " btcusdt ",
        "timestamp": "1000",
        "open": "100",
        "high": "110",
        "low": "90",
        "close": "105",
        "volume": "1000",
    })

    assert candle.symbol == "BTCUSDT"
    assert candle.open == 100.0


def test_jsonl_storage(tmp_path):

    path = tmp_path / "candles.jsonl"

    count = write_candles(
        [
            sample_candle(1000),
            sample_candle(2000),
        ],
        path,
    )

    assert count == 2
    assert path.exists()
    assert len(
        path.read_text(
            encoding="utf-8"
        ).splitlines()
    ) == 2
