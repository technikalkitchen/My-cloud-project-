from __future__ import annotations

from app.data.capture.binance import (
    BinancePublicAdapter,
    BinanceProviderUnavailable,
)

from app.data.capture.coinbase import (
    CoinbasePublicAdapter,
    CoinbaseProviderUnavailable,
)


class ProviderRouter:

    def __init__(self):

        self.binance = (
            BinancePublicAdapter()
        )

        self.coinbase = (
            CoinbasePublicAdapter()
        )

        self.selected_provider = None
        self.last_error = None

    def fetch(
        self,
        symbol: str,
        interval: str = "1m",
        limit: int = 5,
    ):

        # ----------------------------------------------------
        # PRIORITY 1 — BINANCE
        # ----------------------------------------------------

        try:

            candles = self.binance.fetch(
                symbol=symbol,
                interval=interval,
                limit=limit,
            )

            self.selected_provider = (
                "BINANCE_SPOT_PUBLIC"
            )

            return candles

        except Exception as exc:

            self.last_error = repr(exc)

        # ----------------------------------------------------
        # PRIORITY 2 — COINBASE
        # ----------------------------------------------------

        try:

            candles = self.coinbase.fetch(
                symbol=symbol,
                interval=interval,
                limit=limit,
            )

            self.selected_provider = (
                "COINBASE_EXCHANGE_PUBLIC"
            )

            return candles

        except Exception as exc:

            self.last_error = (
                self.last_error
                + " | Coinbase: "
                + repr(exc)
            )

            raise RuntimeError(
                "ALL MARKET DATA PROVIDERS FAILED: "
                + self.last_error
            )
