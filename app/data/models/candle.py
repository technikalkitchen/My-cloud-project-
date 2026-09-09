from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Candle:

    symbol: str
    timestamp: int

    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self):

        if not self.symbol:
            raise ValueError("symbol cannot be empty")

        values = [
            self.open,
            self.high,
            self.low,
            self.close,
            self.volume,
        ]

        if any(
            not isinstance(value, (int, float))
            for value in values
        ):
            raise TypeError(
                "OHLCV values must be numeric"
            )

        if self.timestamp <= 0:
            raise ValueError(
                "timestamp must be positive"
            )

        if self.high < self.low:
            raise ValueError(
                "high cannot be lower than low"
            )

        if self.open < self.low:
            raise ValueError(
                "open cannot be below low"
            )

        if self.open > self.high:
            raise ValueError(
                "open cannot be above high"
            )

        if self.close < self.low:
            raise ValueError(
                "close cannot be below low"
            )

        if self.close > self.high:
            raise ValueError(
                "close cannot be above high"
            )

        if self.volume < 0:
            raise ValueError(
                "volume cannot be negative"
            )


def candle_to_dict(candle: Candle) -> dict[str, Any]:

    return {
        "symbol": candle.symbol,
        "timestamp": candle.timestamp,
        "open": candle.open,
        "high": candle.high,
        "low": candle.low,
        "close": candle.close,
        "volume": candle.volume,
    }


def candle_from_dict(data: dict[str, Any]) -> Candle:

    return Candle(
        symbol=str(data["symbol"]),
        timestamp=int(data["timestamp"]),
        open=float(data["open"]),
        high=float(data["high"]),
        low=float(data["low"]),
        close=float(data["close"]),
        volume=float(data["volume"]),
    )
