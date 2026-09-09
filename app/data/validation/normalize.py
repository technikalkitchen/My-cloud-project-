from typing import Any

from app.data.models.candle import Candle


def normalize_candle(
    data: dict[str, Any],
) -> Candle:

    timestamp = int(data["timestamp"])

    return Candle(
        symbol=str(data["symbol"]).upper().strip(),
        timestamp=timestamp,
        open=float(data["open"]),
        high=float(data["high"]),
        low=float(data["low"]),
        close=float(data["close"]),
        volume=float(data["volume"]),
    )
