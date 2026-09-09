import json
from pathlib import Path
from typing import Iterable

from app.data.models.candle import (
    Candle,
    candle_to_dict,
)


def write_candles(
    candles: Iterable[Candle],
    path: Path,
) -> int:

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    count = 0

    with path.open(
        "w",
        encoding="utf-8"
    ) as handle:

        for candle in candles:

            handle.write(
                json.dumps(
                    candle_to_dict(candle),
                    separators=(",", ":")
                )
                + "\n"
            )

            count += 1

    return count
