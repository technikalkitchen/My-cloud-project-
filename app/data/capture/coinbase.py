from __future__ import annotations

import requests

from app.data.models.candle import Candle
from app.data.validation.candles import validate_candles


class CoinbaseProviderUnavailable(Exception):
    """Raised when Coinbase cannot provide data."""


class CoinbasePublicAdapter:

    provider_name = "COINBASE_EXCHANGE_PUBLIC"

    BASE_URL = (
        "https://api.exchange.coinbase.com"
    )

    GRANULARITY_MAP = {
        "1m": 60,
        "5m": 300,
        "15m": 900,
        "1h": 3600,
        "6h": 21600,
        "1d": 86400,
    }

    def __init__(
        self,
        timeout: int = 15,
    ):
        self.timeout = timeout

    def _product_id(
        self,
        symbol: str,
    ) -> str:

        symbol = symbol.upper().strip()

        if symbol.endswith("USDT"):
            return (
                f"{symbol[:-4]}-USD"
            )

        if symbol.endswith("USD"):
            return (
                f"{symbol[:-3]}-USD"
            )

        raise ValueError(
            "unsupported symbol format"
        )

    def symbol_available(
        self,
        symbol: str,
    ) -> bool:

        product_id = self._product_id(symbol)

        url = (
            self.BASE_URL
            + f"/products/{product_id}"
        )

        try:
            response = requests.get(
                url,
                headers={
                    "Accept": "application/json",
                    "User-Agent":
                        "KitchenAssistant/2.8",
                },
                timeout=self.timeout,
            )

            return response.status_code == 200

        except Exception:
            return False

    def fetch(
        self,
        symbol: str,
        interval: str = "1m",
        limit: int = 5,
    ) -> list[Candle]:

        symbol = symbol.upper().strip()

        if interval not in self.GRANULARITY_MAP:
            raise ValueError(
                "unsupported interval"
            )

        if limit < 1:
            raise ValueError(
                "limit must be positive"
            )

        if limit > 300:
            raise ValueError(
                "limit cannot exceed provider maximum"
            )

        product_id = self._product_id(symbol)

        url = (
            self.BASE_URL
            + f"/products/{product_id}/candles"
        )

        response = requests.get(
            url,
            params={
                "granularity":
                    self.GRANULARITY_MAP[interval],
            },
            headers={
                "Accept": "application/json",
                "User-Agent":
                    "KitchenAssistant/2.8",
            },
            timeout=self.timeout,
        )

        if response.status_code != 200:
            raise CoinbaseProviderUnavailable(
                f"HTTP {response.status_code}"
            )

        payload = response.json()

        if not isinstance(payload, list):
            raise CoinbaseProviderUnavailable(
                "Coinbase response is not a list"
            )

        candles = []

        for row in payload:

            if len(row) < 6:
                raise CoinbaseProviderUnavailable(
                    "Malformed Coinbase candle"
                )

            candles.append(
                Candle(
                    symbol=symbol,
                    timestamp=int(row[0]) * 1000,
                    open=float(row[3]),
                    high=float(row[2]),
                    low=float(row[1]),
                    close=float(row[4]),
                    volume=float(row[5]),
                )
            )

        candles.sort(
            key=lambda candle:
                candle.timestamp
        )

        candles = candles[-limit:]

        if len(candles) != limit:
            raise CoinbaseProviderUnavailable(
                "Insufficient Coinbase candles"
            )

        return validate_candles(candles)
