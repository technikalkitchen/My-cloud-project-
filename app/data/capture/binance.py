from __future__ import annotations

from typing import Optional
import requests

from app.data.models.candle import Candle
from app.data.validation.candles import validate_candles


class BinanceProviderUnavailable(Exception):
    """Raised when Binance cannot provide the requested data."""


class BinancePublicAdapter:

    provider_name = "BINANCE_SPOT_PUBLIC"

    BASE_URLS = [
        "https://api.binance.com",
        "https://api1.binance.com",
        "https://api2.binance.com",
        "https://api3.binance.com",
        "https://api4.binance.com",
    ]

    GRANULARITY_MAP = {
        "1m": "1m",
        "3m": "3m",
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1h": "1h",
        "2h": "2h",
        "4h": "4h",
        "6h": "6h",
        "8h": "8h",
        "12h": "12h",
        "1d": "1d",
    }

    def __init__(
        self,
        base_urls: Optional[list] = None,
        timeout: int = 15,
    ):
        self.base_urls = (
            base_urls
            if base_urls
            else list(self.BASE_URLS)
        )

        self.timeout = timeout

        self.last_error = None
        self.last_base_url = None

    def _request(
        self,
        path: str,
        params: dict,
    ):
        errors = []

        for base_url in self.base_urls:

            try:
                response = requests.get(
                    base_url.rstrip("/") + path,
                    params=params,
                    headers={
                        "Accept": "application/json",
                        "User-Agent":
                            "KitchenAssistant/2.8",
                    },
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    self.last_base_url = base_url
                    return response

                errors.append(
                    f"{base_url}: HTTP "
                    f"{response.status_code}"
                )

            except Exception as exc:
                errors.append(
                    f"{base_url}: {repr(exc)}"
                )

        self.last_error = "; ".join(errors)

        raise BinanceProviderUnavailable(
            self.last_error
        )

    def symbol_available(
        self,
        symbol: str,
    ) -> bool:

        symbol = symbol.upper().strip()

        response = self._request(
            "/api/v3/exchangeInfo",
            {
                "symbol": symbol,
            },
        )

        payload = response.json()

        symbols = payload.get("symbols", [])

        if not symbols:
            return False

        item = symbols[0]

        return (
            item.get("symbol") == symbol
            and item.get("status") == "TRADING"
        )

    def fetch(
        self,
        symbol: str,
        interval: str = "1m",
        limit: int = 5,
    ) -> list[Candle]:

        symbol = symbol.upper().strip()

        if not symbol:
            raise ValueError(
                "symbol cannot be empty"
            )

        if interval not in self.GRANULARITY_MAP:
            raise ValueError(
                "unsupported interval"
            )

        if limit < 1:
            raise ValueError(
                "limit must be positive"
            )

        if limit > 1000:
            raise ValueError(
                "limit cannot exceed Binance maximum"
            )

        response = self._request(
            "/api/v3/klines",
            {
                "symbol": symbol,
                "interval":
                    self.GRANULARITY_MAP[interval],
                "limit": limit,
            },
        )

        payload = response.json()

        if not isinstance(payload, list):
            raise BinanceProviderUnavailable(
                "Binance response is not a list"
            )

        candles = []

        for row in payload:

            if not isinstance(row, list):
                raise BinanceProviderUnavailable(
                    "Malformed Binance candle"
                )

            if len(row) < 6:
                raise BinanceProviderUnavailable(
                    "Incomplete Binance candle"
                )

            candles.append(
                Candle(
                    symbol=symbol,
                    timestamp=int(row[0]),
                    open=float(row[1]),
                    high=float(row[2]),
                    low=float(row[3]),
                    close=float(row[4]),
                    volume=float(row[5]),
                )
            )

        if len(candles) != limit:
            raise BinanceProviderUnavailable(
                "Binance returned "
                f"{len(candles)} candles; "
                f"expected {limit}"
            )

        candles.sort(
            key=lambda candle:
                candle.timestamp
        )

        return validate_candles(candles)
