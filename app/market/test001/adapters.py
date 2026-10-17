"""Minimal public-API adapters for TEST001.

The adapters return normalized candle timestamps and short status strings.
They do not claim a pair is absent when the API request itself failed.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import time

import requests

from .config import (
    EXCHANGE_CONFIGS,
    REQUEST_TIMEOUT_SECONDS,
    TIMEFRAMES,
    USER_AGENT,
)


class AdapterError(RuntimeError):
    """A request failed or an exchange returned an unusable response."""


class BaseAdapter:
    name = "base"

    def __init__(self, session: requests.Session | None = None):
        self.session = session or requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        })
        self.base_url = EXCHANGE_CONFIGS[self.name].base_url

    def _get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        # Keep a small delay between requests to reduce rate-limit errors.
        time.sleep(0.2)

        try:
            response = self.session.get(
                self.base_url + path,
                params=params,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise AdapterError(
                f"{self.name}: request/JSON error: {exc}"
            ) from exc

        return payload

    @staticmethod
    def _utc_ms(value: Any) -> int:
        """Normalize millisecond, microsecond, nanosecond or ISO timestamps."""
        if isinstance(value, str) and not value.strip().isdigit():
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return int(parsed.timestamp() * 1000)

        stamp = int(value)

        if stamp > 10**17:
            return stamp // 1_000_000
        if stamp > 10**14:
            return stamp // 1_000
        if stamp < 10**11:
            return stamp * 1000

        return stamp

    @staticmethod
    def _iso(ms: int | None) -> str | None:
        if ms is None:
            return None

        return (
            datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )

    def markets(self) -> set[str]:
        """Return exchange-native market IDs."""
        raise NotImplementedError

    def candles(
        self,
        market: str,
        timeframe: str,
        start_ms: int,
        end_ms: int,
    ) -> list[tuple[int, float | None]]:
        """Return available candles in [start_ms, end_ms], sorted ascending."""
        raise NotImplementedError

    def inspect_market(
        self,
        market: str,
        timeframe: str,
    ) -> dict[str, Any]:
        """Estimate first and last candles using bounded probes."""
        if timeframe not in TIMEFRAMES:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        try:
            latest = self._last_probe(market, timeframe)

            if latest is None:
                return {
                    "status": "NO_DATA",
                    "first": None,
                    "last": None,
                }

            first = self._first_probe(market, timeframe, latest)

            if first is None:
                return {
                    "status": "PARTIAL",
                    "first": None,
                    "last": self._iso(latest),
                }

            return {
                "status": "OK",
                "first": self._iso(first),
                "last": self._iso(latest),
            }

        except AdapterError as exc:
            return {
                "status": "ERROR",
                "first": None,
                "last": None,
                "error": str(exc)[:300],
            }

    def _first_probe(
        self,
        market: str,
        timeframe: str,
        latest_ms: int | None,
    ) -> int | None:
        if latest_ms is None:
            return None

        # Search by UTC day to avoid exchange endpoint row limits.
        day_ms = 86_400_000
        low_day = 0
        high_day = latest_ms // day_ms

        while low_day < high_day:
            mid_day = (low_day + high_day) // 2
            start = mid_day * day_ms
            end = min(start + day_ms - 1, latest_ms)

            rows = self.candles(
                market,
                timeframe,
                start,
                end,
            )

            if rows:
                high_day = mid_day
            else:
                low_day = mid_day + 1

        start = low_day * day_ms
        rows = self.candles(
            market,
            timeframe,
            start,
            min(start + day_ms - 1, latest_ms),
        )

        return min((row[0] for row in rows), default=None)

    def _last_probe(
        self,
        market: str,
        timeframe: str,
    ) -> int | None:
        now = int(time.time() * 1000)
        interval_ms = TIMEFRAMES[timeframe] * 1000

        rows = self.candles(
            market,
            timeframe,
            now - 3 * interval_ms,
            now,
        )

        return rows[-1][0] if rows else None


class BinanceAdapter(BaseAdapter):
    name = "binance"

    def markets(self) -> set[str]:
        data = self._get("/api/v3/exchangeInfo")

        return {
            item["symbol"]
            for item in data.get("symbols", [])
            if item.get("status") == "TRADING"
            and item.get("symbol")
        }

    def candles(
        self,
        market: str,
        timeframe: str,
        start_ms: int,
        end_ms: int,
    ) -> list[tuple[int, float | None]]:
        data = self._get(
            "/api/v3/klines",
            {
                "symbol": market,
                "interval": timeframe,
                "startTime": start_ms,
                "endTime": end_ms,
                "limit": 1000,
            },
        )

        if not isinstance(data, list):
            raise AdapterError("binance: unexpected klines payload")

        return [
            (self._utc_ms(row[0]), float(row[4]))
            for row in data
            if isinstance(row, list) and len(row) >= 5
        ]

    def _first_probe(
        self,
        market: str,
        timeframe: str,
        latest_ms: int | None,
    ) -> int | None:
        if latest_ms is None:
            return None

        data = self._get(
            "/api/v3/klines",
            {
                "symbol": market,
                "interval": timeframe,
                "startTime": 0,
                "limit": 1,
            },
        )

        if isinstance(data, list) and data and len(data[0]) >= 1:
            return self._utc_ms(data[0][0])

        return None

    def _last_probe(
        self,
        market: str,
        timeframe: str,
    ) -> int | None:
        data = self._get(
            "/api/v3/klines",
            {
                "symbol": market,
                "interval": timeframe,
                "limit": 1,
            },
        )

        if isinstance(data, list) and data and len(data[-1]) >= 1:
            return self._utc_ms(data[-1][0])

        return None


class OKXAdapter(BaseAdapter):
    name = "okx"

    @staticmethod
    def market_id(base: str, quote: str) -> str:
        return f"{base}-{quote}"

    def markets(self) -> set[str]:
        data = self._get(
            "/api/v5/public/instruments",
            {"instType": "SPOT"},
        )

        if data.get("code") != "0":
            raise AdapterError(
                f"okx: API code={data.get('code')} msg={data.get('msg')}"
            )

        return {
            item["instId"]
            for item in data.get("data", [])
            if item.get("state") == "live" and item.get("instId")
        }

    def candles(
        self,
        market: str,
        timeframe: str,
        start_ms: int,
        end_ms: int,
    ) -> list[tuple[int, float | None]]:
        # The history-candles endpoint uses "1H" for hourly candles.
        api_bar = {
            "5m": "5m",
            "1h": "1H",
        }[timeframe]

        data = self._get(
            "/api/v5/market/history-candles",
            {
                "instId": market,
                "bar": api_bar,
                "after": str(end_ms),
                "limit": "300",
            },
        )

        if data.get("code") != "0":
            raise AdapterError(
                f"okx: API code={data.get('code')} msg={data.get('msg')}"
            )

        rows = []
        for row in data.get("data", []):
            if len(row) >= 5:
                rows.append((self._utc_ms(row[0]), float(row[4])))

        return sorted(
            (
                row
                for row in rows
                if start_ms <= row[0] <= end_ms
            ),
            key=lambda row: row[0],
        )

    def _last_probe(
        self,
        market: str,
        timeframe: str,
    ) -> int | None:
        api_bar = {
            "5m": "5m",
            "1h": "1H",
        }[timeframe]

        data = self._get(
            "/api/v5/market/candles",
            {
                "instId": market,
                "bar": api_bar,
                "limit": "1",
            },
        )

        if data.get("code") != "0":
            raise AdapterError(
                f"okx: API code={data.get('code')} msg={data.get('msg')}"
            )

        rows = data.get("data", [])
        return self._utc_ms(rows[0][0]) if rows else None


class BitstampAdapter(BaseAdapter):
    name = "bitstamp"

    @staticmethod
    def market_id(base: str, quote: str) -> str:
        return (base + quote).lower()

    def markets(self) -> set[str]:
        data = self._get("/api/v2/trading-pairs-info/")

        if not isinstance(data, list):
            raise AdapterError(
                "bitstamp: unexpected trading-pairs payload"
            )

        return {
            str(item.get("url_symbol", "")).lower()
            for item in data
            if item.get("url_symbol")
            and item.get("trading", "Enabled")
            in ("Enabled", "enabled", "1", 1)
        }

    def candles(
        self,
        market: str,
        timeframe: str,
        start_ms: int,
        end_ms: int,
    ) -> list[tuple[int, float | None]]:
        data = self._get(
            f"/api/v2/ohlc/{market}/",
            {
                "step": TIMEFRAMES[timeframe],
                "start": start_ms // 1000,
                "end": end_ms // 1000,
                "limit": 1000,
            },
        )

        if not isinstance(data, dict):
            raise AdapterError("bitstamp: unexpected OHLC payload")

        rows = data.get("data", {}).get("ohlc", [])

        return sorted(
            [
                (
                    self._utc_ms(item["timestamp"]),
                    float(item["close"]),
                )
                for item in rows
                if "timestamp" in item and "close" in item
            ],
            key=lambda row: row[0],
        )


class CoinbaseAdapter(BaseAdapter):
    name = "coinbase"

    @staticmethod
    def market_id(base: str, quote: str) -> str:
        return f"{base}-{quote}"

    def markets(self) -> set[str]:
        data = self._get("/products")

        if not isinstance(data, list):
            raise AdapterError("coinbase: unexpected products payload")

        return {
            item["id"]
            for item in data
            if item.get("status") == "online"
            and item.get("quote_currency")
            and item.get("id")
        }

    def candles(
        self,
        market: str,
        timeframe: str,
        start_ms: int,
        end_ms: int,
    ) -> list[tuple[int, float | None]]:
        granularity = TIMEFRAMES[timeframe]

        data = self._get(
            f"/products/{market}/candles",
            {
                "granularity": granularity,
                "start": self._iso(start_ms),
                "end": self._iso(end_ms),
            },
        )

        if not isinstance(data, list):
            raise AdapterError("coinbase: unexpected candles payload")

        return sorted(
            [
                (self._utc_ms(row[0]), float(row[4]))
                for row in data
                if isinstance(row, list) and len(row) >= 5
            ],
            key=lambda row: row[0],
        )


class CryptoComAdapter(BaseAdapter):
    name = "crypto_com"

    @staticmethod
    def market_id(base: str, quote: str) -> str:
        return f"{base}_{quote}"

    @staticmethod
    def normalize_products(data: Any) -> set[str]:
        """Normalize Crypto.com instrument records into BASE_QUOTE IDs."""
        if not isinstance(data, dict):
            raise AdapterError(
                "crypto_com: unexpected instruments payload"
            )

        if data.get("code") != 0:
            raise AdapterError(
                f"crypto_com: API code={data.get('code')} "
                f"message={data.get('message')}"
            )

        result = data.get("result")
        if not isinstance(result, dict):
            raise AdapterError(
                "crypto_com: missing instruments result"
            )

        products = result.get("data", [])
        if not isinstance(products, list):
            raise AdapterError(
                "crypto_com: unexpected instruments data"
            )

        markets: set[str] = set()

        for item in products:
            if not isinstance(item, dict):
                continue

            # Public instrument metadata can expose these fields in
            # different combinations; normalize case before filtering.
            inst_type = str(
                item.get("inst_type")
                or item.get("instrument_type")
                or item.get("type")
                or ""
            ).strip().upper()

            if inst_type and inst_type not in {
                "CCY_PAIR",
                "SPOT",
                "SPOT_TRADING",
            }:
                continue

            tradable = item.get("tradable")
            if tradable is not None:
                if isinstance(tradable, str):
                    is_tradable = tradable.strip().lower() in {
                        "true",
                        "1",
                        "yes",
                    }
                else:
                    is_tradable = bool(tradable)

                if not is_tradable:
                    continue

            instrument_name = str(
                item.get("instrument_name") or ""
            ).strip().upper()

            base = str(
                item.get("base_currency")
                or item.get("base")
                or ""
            ).strip().upper()

            quote = str(
                item.get("quote_currency")
                or item.get("quote")
                or ""
            ).strip().upper()

            if base and quote:
                normalized = f"{base}_{quote}"
                if instrument_name:
                    # Ignore malformed metadata where the explicit
                    # instrument ID contradicts base/quote fields.
                    if instrument_name != normalized:
                        continue
                markets.add(normalized)
                continue

            # Fall back to the exchange-native symbol if the API
            # does not include separate base/quote fields.
            if instrument_name and "_" in instrument_name:
                parts = instrument_name.split("_")
                if len(parts) == 2 and all(parts):
                    markets.add(instrument_name)

        return markets

    def markets(self) -> set[str]:
        data = self._get("/public/get-instruments")
        return self.normalize_products(data)

    def candles(
        self,
        market: str,
        timeframe: str,
        start_ms: int,
        end_ms: int,
    ) -> list[tuple[int, float | None]]:
        data = self._get(
            "/public/get-candlestick",
            {
                "instrument_name": market,
                "timeframe": timeframe,
                "start_ts": start_ms,
                "end_ts": end_ms,
            },
        )

        if not isinstance(data, dict):
            raise AdapterError(
                "crypto_com: unexpected candlestick payload"
            )

        if data.get("code") != 0:
            raise AdapterError(
                f"crypto_com: API code={data.get('code')} "
                f"message={data.get('message')}"
            )

        result = data.get("result", {})
        rows = result.get("data", []) if isinstance(result, dict) else []

        return sorted(
            [
                (self._utc_ms(item["t"]), float(item["c"]))
                for item in rows
                if isinstance(item, dict)
                and "t" in item
                and "c" in item
            ],
            key=lambda row: row[0],
        )


ADAPTERS = {
    "binance": BinanceAdapter,
    "okx": OKXAdapter,
    "bitstamp": BitstampAdapter,
    "coinbase": CoinbaseAdapter,
    "crypto_com": CryptoComAdapter,
}


def make_adapter(name: str) -> BaseAdapter:
    try:
        return ADAPTERS[name]()
    except KeyError as exc:
        raise ValueError(f"Unknown exchange: {name}") from exc
