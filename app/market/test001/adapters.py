"""Minimal public-API adapters for TEST001.

The adapters deliberately return raw, normalized candle timestamps and short status
strings. They do not claim a pair is absent when the API request itself failed.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import time

import requests

from .config import EXCHANGE_CONFIGS, REQUEST_TIMEOUT_SECONDS, TIMEFRAMES, USER_AGENT


class AdapterError(RuntimeError):
    """A request failed or an exchange returned an unusable response."""


class BaseAdapter:
    name = "base"

    def __init__(self, session: requests.Session | None = None):
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
        self.base_url = EXCHANGE_CONFIGS[self.name].base_url

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        try:
            response = self.session.get(
                self.base_url + path,
                params=params,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise AdapterError(f"{self.name}: request/JSON error: {exc}") from exc
        return payload

    @staticmethod
    def _utc_ms(value: Any) -> int:
        """Normalize common millisecond, microsecond, nanosecond or ISO timestamps."""
        if isinstance(value, str) and not value.strip().isdigit():
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return int(parsed.timestamp() * 1000)
        stamp = int(value)
        if stamp > 10**17:  # nanoseconds
            return stamp // 1_000_000
        if stamp > 10**14:  # microseconds
            return stamp // 1_000
        if stamp < 10**11:  # seconds
            return stamp * 1000
        return stamp

    @staticmethod
    def _iso(ms: int | None) -> str | None:
        if ms is None:
            return None
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z")

    def markets(self) -> set[str]:
        """Return exchange-native market IDs. Subclasses implement this."""
        raise NotImplementedError

    def candles(self, market: str, timeframe: str, start_ms: int, end_ms: int) -> list[tuple[int, float | None]]:
        """Return available candles in [start_ms, end_ms], sorted ascending."""
        raise NotImplementedError

    def inspect_market(self, market: str, timeframe: str) -> dict[str, Any]:
        """Estimate first/last candle with bounded probes; never hide request failures.

        The first probe asks the exchange for its oldest data in a very broad range.
        Endpoint semantics differ, so adapters override _first_probe where necessary.
        """
        if timeframe not in TIMEFRAMES:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        try:
            latest = self._last_probe(market, timeframe)
            first = self._first_probe(market, timeframe, latest)
            if latest is None:
                return {"status": "NO_DATA", "first": None, "last": None}
            if first is None:
                return {"status": "PARTIAL", "first": None, "last": self._iso(latest)}
            return {"status": "OK", "first": self._iso(first), "last": self._iso(latest)}
        except AdapterError as exc:
            return {"status": "ERROR", "first": None, "last": None, "error": str(exc)[:300]}

    def _first_probe(self, market: str, timeframe: str, latest_ms: int) -> int | None:
        # Search by UTC day so the endpoint's row cap does not truncate a wide range.
        # A one-day window fits within 300 rows for both supported timeframes.
        day_ms = 86_400_000
        low_day, high_day = 0, latest_ms // day_ms
        while low_day < high_day:
            mid_day = (low_day + high_day) // 2
            start = mid_day * day_ms
            end = min(start + day_ms - 1, latest_ms)
            rows = self.candles(market, timeframe, start, end)
            if rows:
                high_day = mid_day
            else:
                low_day = mid_day + 1
        start = low_day * day_ms
        rows = self.candles(market, timeframe, start, min(start + day_ms - 1, latest_ms))
        return min((row[0] for row in rows), default=None)

    def _last_probe(self, market: str, timeframe: str) -> int | None:
        now = int(time.time() * 1000)
        rows = self.candles(market, timeframe, now - 3 * TIMEFRAMES[timeframe] * 1000, now)
        return rows[-1][0] if rows else None


class BinanceAdapter(BaseAdapter):
    name = "binance"

    def markets(self) -> set[str]:
        data = self._get("/api/v3/exchangeInfo")
        return {x["symbol"] for x in data.get("symbols", []) if x.get("status") == "TRADING"}

    def candles(self, market: str, timeframe: str, start_ms: int, end_ms: int) -> list[tuple[int, float | None]]:
        data = self._get("/api/v3/klines", {"symbol": market, "interval": timeframe, "startTime": start_ms, "endTime": end_ms, "limit": 1000})
        if not isinstance(data, list):
            raise AdapterError("binance: unexpected klines payload")
        return [(self._utc_ms(row[0]), float(row[4])) for row in data if isinstance(row, list) and len(row) >= 5]

    def _first_probe(self, market: str, timeframe: str, latest_ms: int) -> int | None:
        data = self._get("/api/v3/klines", {"symbol": market, "interval": timeframe, "startTime": 0, "limit": 1})
        return self._utc_ms(data[0][0]) if isinstance(data, list) and data and len(data[0]) >= 1 else None

    def _last_probe(self, market: str, timeframe: str) -> int | None:
        data = self._get("/api/v3/klines", {"symbol": market, "interval": timeframe, "limit": 1})
        return self._utc_ms(data[-1][0]) if isinstance(data, list) and data and len(data[-1]) >= 1 else None


class OKXAdapter(BaseAdapter):
    name = "okx"

    @staticmethod
    def market_id(base: str, quote: str) -> str:
        return f"{base}-{quote}"

    def markets(self) -> set[str]:
        data = self._get("/api/v5/public/instruments", {"instType": "SPOT"})
        if data.get("code") != "0":
            raise AdapterError(f"okx: API code={data.get('code')} msg={data.get('msg')}")
        return {x["instId"] for x in data.get("data", []) if x.get("state") == "live"}

    def candles(self, market: str, timeframe: str, start_ms: int, end_ms: int) -> list[tuple[int, float | None]]:
        # OKX uses uppercase H/D/W/M for these intervals and caps requests at 300 rows.
        api_bar = {"5m": "5m", "1h": "1Hutc"}[timeframe]
        data = self._get("/api/v5/market/history-candles", {"instId": market, "bar": api_bar, "after": str(end_ms), "limit": "300"})
        if data.get("code") != "0":
            raise AdapterError(f"okx: API code={data.get('code')} msg={data.get('msg')}")
        rows = []
        for row in data.get("data", []):
            if len(row) >= 5:
                rows.append((self._utc_ms(row[0]), float(row[4])))
        return sorted((x for x in rows if start_ms <= x[0] <= end_ms), key=lambda x: x[0])

    def _last_probe(self, market: str, timeframe: str) -> int | None:
        api_bar = {"5m": "5m", "1h": "1Hutc"}[timeframe]
        data = self._get("/api/v5/market/candles", {"instId": market, "bar": api_bar, "limit": "1"})
        if data.get("code") != "0":
            raise AdapterError(f"okx: API code={data.get('code')} msg={data.get('msg')}")
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
            raise AdapterError("bitstamp: unexpected trading-pairs payload")
        return {str(x.get("url_symbol", "")).lower() for x in data if x.get("trading", "Enabled") in ("Enabled", "enabled", "1", 1)}

    def candles(self, market: str, timeframe: str, start_ms: int, end_ms: int) -> list[tuple[int, float | None]]:
        step = TIMEFRAMES[timeframe]
        data = self._get(f"/api/v2/ohlc/{market}/", {"step": step, "start": start_ms // 1000, "end": end_ms // 1000, "limit": 1000})
        rows = data.get("data", {}).get("ohlc", [])
        return sorted([(self._utc_ms(x["timestamp"]), float(x["close"])) for x in rows if "timestamp" in x and "close" in x], key=lambda x: x[0])

    def _first_probe(self, market: str, timeframe: str, latest_ms: int) -> int | None:
        data = self._get(f"/api/v2/ohlc/{market}/", {"step": TIMEFRAMES[timeframe], "start": 0, "end": latest_ms // 1000, "limit": 1000})
        rows = data.get("data", {}).get("ohlc", [])
        return min((self._utc_ms(x["timestamp"]) for x in rows if "timestamp" in x), default=None)


class CoinbaseAdapter(BaseAdapter):
    name = "coinbase"

    @staticmethod
    def market_id(base: str, quote: str) -> str:
        return f"{base}-{quote}"

    def markets(self) -> set[str]:
        data = self._get("/products")
        if not isinstance(data, list):
            raise AdapterError("coinbase: unexpected products payload")
        return {x["id"] for x in data if x.get("status") == "online" and x.get("quote_currency")}

    def candles(self, market: str, timeframe: str, start_ms: int, end_ms: int) -> list[tuple[int, float | None]]:
        granularity = TIMEFRAMES[timeframe]
        data = self._get(f"/products/{market}/candles", {"granularity": granularity, "start": self._iso(start_ms), "end": self._iso(end_ms)})
        if not isinstance(data, list):
            raise AdapterError("coinbase: unexpected candles payload")
        return sorted([(self._utc_ms(row[0]), float(row[4])) for row in data if isinstance(row, list) and len(row) >= 5], key=lambda x: x[0])

class CryptoComAdapter(BaseAdapter):
    name = "crypto_com"

    @staticmethod
    def market_id(base: str, quote: str) -> str:
        return f"{base}_{quote}"

    def markets(self) -> set[str]:
        data = self._get("/public/get-instruments")
        if data.get("code") != 0:
            raise AdapterError(f"crypto_com: API code={data.get('code')} message={data.get('message')}")
        return {x["instrument_name"] for x in data.get("result", {}).get("data", []) if x.get("instrument_name")}

    def candles(self, market: str, timeframe: str, start_ms: int, end_ms: int) -> list[tuple[int, float | None]]:
        data = self._get("/public/get-candlestick", {"instrument_name": market, "timeframe": timeframe, "start_ts": start_ms, "end_ts": end_ms})
        if data.get("code") != 0:
            raise AdapterError(f"crypto_com: API code={data.get('code')} message={data.get('message')}")
        rows = data.get("result", {}).get("data", [])
        return sorted([(self._utc_ms(x["t"]), float(x["c"])) for x in rows if "t" in x and "c" in x], key=lambda x: x[0])

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
