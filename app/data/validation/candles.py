from collections.abc import Iterable

from app.data.models.candle import Candle


def validate_candles(
    candles: Iterable[Candle],
) -> list[Candle]:

    validated = list(candles)

    if not validated:
        raise ValueError(
            "candle collection cannot be empty"
        )

    previous_timestamp = None

    for candle in validated:

        if not isinstance(
            candle,
            Candle
        ):
            raise TypeError(
                "all records must be Candle instances"
            )

        if (
            previous_timestamp is not None
            and candle.timestamp <= previous_timestamp
        ):
            raise ValueError(
                "candles must be strictly chronological"
            )

        previous_timestamp = candle.timestamp

    return validated
