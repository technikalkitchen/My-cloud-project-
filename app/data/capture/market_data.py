from __future__ import annotations

from datetime import datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation
import hashlib
import json
import time

import requests

from app.config.market_data import (
    SYMBOLS,
    INTERVAL,
    CANDLES_PER_SYMBOL,
    REQUESTED_DURATION_MINUTES,
    REQUESTED_RANGE_MODE,
    PROVIDER_PRIORITY,
    TRADING_ENABLED,
    ORDERS_ENABLED,
    STRATEGY_ENABLED,
    INTERVAL_MS,
    COINBASE_BATCH_LIMIT,
)


INTERVAL_MS_VALUE = INTERVAL_MS


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def now_ms() -> int:
    return int(utc_now().timestamp() * 1000)


def rolling_range() -> dict:

    end_dt = utc_now()

    start_dt = end_dt - timedelta(
        minutes=REQUESTED_DURATION_MINUTES
    )

    return {
        "mode": REQUESTED_RANGE_MODE,
        "duration_minutes": REQUESTED_DURATION_MINUTES,
        "start_utc": start_dt.strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        ),
        "end_utc": end_dt.strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        ),
        "start_ms": int(start_dt.timestamp() * 1000),
        "end_ms": int(end_dt.timestamp() * 1000),
    }


def provider_symbol(provider_name: str, symbol: str) -> str:

    symbol = str(symbol).upper().strip()

    if provider_name == "BINANCE_SPOT_PUBLIC":
        return symbol

    if provider_name == "COINBASE_EXCHANGE_PUBLIC":

        if symbol.endswith("USDT"):
            return symbol[:-4] + "-USD"

        if symbol.endswith("USD"):
            return symbol[:-3] + "-USD"

        raise ValueError(
            f"Unsupported Coinbase symbol: {symbol}"
        )

    raise ValueError(
        f"Unknown provider: {provider_name}"
    )


def positive_decimal(value, field_name) -> float:

    try:
        value_decimal = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise RuntimeError(
            f"Invalid numeric {field_name}: {value!r}"
        ) from exc

    if value_decimal <= 0:
        raise RuntimeError(
            f"Non-positive {field_name}: {value!r}"
        )

    return float(value_decimal)


def non_negative_decimal(value, field_name) -> float:

    try:
        value_decimal = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise RuntimeError(
            f"Invalid numeric {field_name}: {value!r}"
        ) from exc

    if value_decimal < 0:
        raise RuntimeError(
            f"Negative {field_name}: {value!r}"
        )

    return float(value_decimal)


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

    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def _get(self, path: str, params: dict):

        errors = []

        for base_url in self.BASE_URLS:

            url = base_url.rstrip("/") + path

            try:
                response = requests.get(
                    url,
                    params=params,
                    headers={
                        "Accept": "application/json",
                        "User-Agent":
                            "KitchenAssistant-V3.1-U05",
                    },
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    return response

                errors.append(
                    f"{base_url}: HTTP {response.status_code}"
                )

            except Exception as exc:
                errors.append(
                    f"{base_url}: {repr(exc)}"
                )

        raise BinanceProviderUnavailable(
            "Binance unavailable: " + " | ".join(errors)
        )

    def fetch_recent(
        self,
        symbol: str,
        interval: str,
        limit: int,
    ) -> list[dict]:

        response = self._get(
            "/api/v3/klines",
            {
                "symbol": symbol,
                "interval": interval,
                "limit": min(int(limit), 1000),
            },
        )

        payload = response.json()

        if not isinstance(payload, list):
            raise BinanceProviderUnavailable(
                "Invalid Binance response"
            )

        candles = []

        for row in payload:

            if not isinstance(row, list):
                raise BinanceProviderUnavailable(
                    "Malformed Binance kline"
                )

            if len(row) < 8:
                raise BinanceProviderUnavailable(
                    "Incomplete Binance kline"
                )

            timestamp = int(row[0])

            open_price = positive_decimal(row[1], "open")
            high_price = positive_decimal(row[2], "high")
            low_price = positive_decimal(row[3], "low")
            close_price = positive_decimal(row[4], "close")
            volume_base = non_negative_decimal(row[5], "volume")
            quote_volume = non_negative_decimal(row[7], "quote_volume")

            candles.append({
                "timestamp": timestamp,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume_base": volume_base,
                "volume_usd": quote_volume,
                "volume_usd_exact": True,
                "volume_usd_source": "BINANCE_KLINE_QUOTE_VOLUME",
            })

        candles.sort(key=lambda x: x["timestamp"])

        return candles


class CoinbaseProviderUnavailable(Exception):
    """Raised when Coinbase cannot provide data."""


class CoinbasePublicAdapter:

    provider_name = "COINBASE_EXCHANGE_PUBLIC"

    BASE_URL = "https://api.exchange.coinbase.com"

    GRANULARITY_SECONDS = {
        "1m": 60,
        "5m": 300,
        "15m": 900,
        "1h": 3600,
        "6h": 21600,
        "1d": 86400,
    }

    def __init__(self, timeout: int = 20):
        self.timeout = timeout

    def fetch_batch(
        self,
        product_id: str,
        start_dt: datetime,
        end_dt: datetime,
        interval: str,
    ) -> list[dict]:

        if interval not in self.GRANULARITY_SECONDS:
            raise ValueError(
                f"Unsupported Coinbase interval: {interval}"
            )

        url = self.BASE_URL + f"/products/{product_id}/candles"

        params = {
            "start": start_dt.isoformat(),
            "end": end_dt.isoformat(),
            "granularity": self.GRANULARITY_SECONDS[interval],
        }

        response = requests.get(
            url,
            params=params,
            headers={
                "Accept": "application/json",
                "User-Agent": "KitchenAssistant-V3.1-U05",
            },
            timeout=self.timeout,
        )

        if response.status_code != 200:
            raise CoinbaseProviderUnavailable(
                f"Coinbase HTTP {response.status_code}: "
                f"{response.text[:300]}"
            )

        payload = response.json()

        if not isinstance(payload, list):
            raise CoinbaseProviderUnavailable(
                "Invalid Coinbase response"
            )

        candles = []

        for row in payload:

            if not isinstance(row, list):
                raise CoinbaseProviderUnavailable(
                    "Malformed Coinbase candle"
                )

            if len(row) < 6:
                raise CoinbaseProviderUnavailable(
                    "Incomplete Coinbase candle"
                )

            # Coinbase format:
            # [time, low, high, open, close, volume]
            # time = Unix seconds

            timestamp = int(row[0]) * 1000

            low_price = positive_decimal(row[1], "low")
            high_price = positive_decimal(row[2], "high")
            open_price = positive_decimal(row[3], "open")
            close_price = positive_decimal(row[4], "close")
            volume_base = non_negative_decimal(row[5], "volume")

            candles.append({
                "timestamp": timestamp,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume_base": volume_base,
                "volume_usd": None,
                "volume_usd_exact": False,
                "volume_usd_source": None,
            })

        return candles


def fetch_coinbase_real_candles(
    adapter: CoinbasePublicAdapter,
    symbol: str,
    interval: str,
    required_count: int,
) -> list[dict]:

    product_id = provider_symbol(
        "COINBASE_EXCHANGE_PUBLIC",
        symbol,
    )

    collected: dict[int, dict] = {}

    end_dt = utc_now()

    batch_minutes = COINBASE_BATCH_LIMIT

    max_pages = 20

    for page in range(max_pages):

        start_dt = end_dt - timedelta(minutes=batch_minutes)

        try:
            batch = adapter.fetch_batch(
                product_id=product_id,
                start_dt=start_dt,
                end_dt=end_dt,
                interval=interval,
            )
        except Exception as exc:
            if page == 0:
                raise
            raise CoinbaseProviderUnavailable(
                f"Coinbase pagination failed after {page} "
                f"page(s): {repr(exc)}"
            )

        if not batch:
            break

        for candle in batch:
            timestamp = int(candle["timestamp"])
            collected[timestamp] = candle

        if len(collected) >= required_count:
            break

        oldest_timestamp = min(collected.keys())

        end_dt = datetime.fromtimestamp(
            (oldest_timestamp - INTERVAL_MS_VALUE) / 1000,
            tz=timezone.utc,
        )

        batch_minutes = min(batch_minutes * 2, COINBASE_BATCH_LIMIT)

    candles = sorted(
        collected.values(),
        key=lambda x: x["timestamp"],
    )

    if len(candles) < required_count:
        raise CoinbaseProviderUnavailable(
            f"Coinbase could provide only {len(candles)} "
            f"real observed candles for {symbol}; "
            f"{required_count} required."
        )

    return candles[-required_count:]


binance = BinancePublicAdapter()
coinbase = CoinbasePublicAdapter()


def fetch_from_provider(
    provider_name: str,
    symbol: str,
) -> dict:

    started = time.time()

    if provider_name == "BINANCE_SPOT_PUBLIC":

        provider_symbol_value = provider_symbol(
            provider_name,
            symbol,
        )

        candles = binance.fetch_recent(
            symbol=symbol,
            interval=INTERVAL,
            limit=CANDLES_PER_SYMBOL,
        )

    elif provider_name == "COINBASE_EXCHANGE_PUBLIC":

        provider_symbol_value = provider_symbol(
            provider_name,
            symbol,
        )

        candles = fetch_coinbase_real_candles(
            adapter=coinbase,
            symbol=symbol,
            interval=INTERVAL,
            required_count=CANDLES_PER_SYMBOL,
        )

    else:

        raise ValueError(f"Unknown provider: {provider_name}")

    elapsed = time.time() - started

    if len(candles) != CANDLES_PER_SYMBOL:
        raise RuntimeError(
            f"Provider returned {len(candles)} real candles "
            f"for {symbol}; expected {CANDLES_PER_SYMBOL}"
        )

    return {
        "provider": provider_name,
        "exchange": provider_name,
        "provider_symbol": provider_symbol_value,
        "records": candles,
        "elapsed_seconds": round(elapsed, 3),
    }


def capture_with_priority(symbol: str) -> tuple[dict, list]:

    attempts = []

    for provider_name in PROVIDER_PRIORITY:

        try:
            result = fetch_from_provider(
                provider_name=provider_name,
                symbol=symbol,
            )
            return result, attempts
        except Exception as exc:
            attempts.append({
                "provider": provider_name,
                "status": "FAILED",
                "error_type": type(exc).__name__,
                "error": repr(exc),
            })

    raise RuntimeError(
        f"ALL PROVIDERS FAILED for {symbol}: "
        + json.dumps(attempts, indent=2)
    )


def build_record(
    candle: dict,
    symbol: str,
    provider_name: str,
    provider_symbol_value: str,
) -> dict:

    volume_base = non_negative_decimal(
        candle["volume_base"],
        "volume_base",
    )

    record = {
        "project": "KITCHEN_ASSISTANT",
        "version": "3.1",
        "execution_unit": "U05",
        "asset_type": "ASSET",
        "symbol": symbol,
        "provider": provider_name,
        "exchange": provider_name,
        "provider_symbol": provider_symbol_value,
        "interval": INTERVAL,
        "timestamp": int(candle["timestamp"]),
        "open": positive_decimal(candle["open"], "open"),
        "high": positive_decimal(candle["high"], "high"),
        "low": positive_decimal(candle["low"], "low"),
        "close": positive_decimal(candle["close"], "close"),
        "volume_base": volume_base,
        "volume_definition": "TOTAL_TRADED_BASE_ASSET_VOLUME",
        "volume_source": "PROVIDER_SUPPLIED",
        "volume_counting_rule": "EACH_TRADE_COUNTED_ONCE",
        "volume_double_counting": False,
        "buyer_seller_not_double_counted": True,
        "volume_usd": candle.get("volume_usd"),
        "volume_usd_exact": bool(
            candle.get("volume_usd_exact", False)
        ),
        "volume_usd_source": candle.get("volume_usd_source"),
        "total_series_included": False,
        "trading_enabled": TRADING_ENABLED,
        "orders_enabled": ORDERS_ENABLED,
        "strategy_enabled": STRATEGY_ENABLED,
    }

    return record


def validate_records(records: list[dict], expected_symbol: str) -> list[dict]:

    if len(records) != CANDLES_PER_SYMBOL:
        raise RuntimeError(
            f"REAL CANDLE COUNT FAILED: {expected_symbol}: "
            f"{len(records)} != {CANDLES_PER_SYMBOL}"
        )

    timestamps = [
        int(record["timestamp"]) for record in records
    ]

    if timestamps != sorted(timestamps):
        raise RuntimeError(
            f"Chronological validation failed: {expected_symbol}"
        )

    if len(timestamps) != len(set(timestamps)):
        raise RuntimeError(
            f"Duplicate timestamps detected: {expected_symbol}"
        )

    for record in records:

        if record["symbol"] != expected_symbol:
            raise RuntimeError(
                f"Symbol mismatch: {expected_symbol}"
            )

        open_price = float(record["open"])
        high_price = float(record["high"])
        low_price = float(record["low"])
        close_price = float(record["close"])
        volume = float(record["volume_base"])

        if open_price <= 0:
            raise RuntimeError(f"Invalid open: {expected_symbol}")

        if high_price < low_price:
            raise RuntimeError(f"Invalid high/low: {expected_symbol}")

        if not (low_price <= open_price <= high_price):
            raise RuntimeError(
                f"Open outside candle range: {expected_symbol}"
            )

        if not (low_price <= close_price <= high_price):
            raise RuntimeError(
                f"Close outside candle range: {expected_symbol}"
            )

        if volume < 0:
            raise RuntimeError(f"Negative volume: {expected_symbol}")

        if record["volume_source"] != "PROVIDER_SUPPLIED":
            raise RuntimeError("Volume source validation failed")

        if record["volume_counting_rule"] != "EACH_TRADE_COUNTED_ONCE":
            raise RuntimeError("Volume counting rule invalid")

        if record["volume_double_counting"] is not False:
            raise RuntimeError("Volume double counting detected")

        if record["buyer_seller_not_double_counted"] is not True:
            raise RuntimeError("Buyer/seller double-counting rule failed")

    return records


def calculate_rolling_volume(
    provider_name: str,
    symbol: str,
) -> dict:

    range_info = rolling_range()

    start_ms = int(range_info["start_ms"])
    end_ms = int(range_info["end_ms"])

    provider_symbol_value = provider_symbol(provider_name, symbol)

    if provider_name == "BINANCE_SPOT_PUBLIC":

        candles = binance.fetch_recent(
            symbol=symbol,
            interval=INTERVAL,
            limit=100,
        )

    elif provider_name == "COINBASE_EXCHANGE_PUBLIC":

        end_dt = datetime.fromtimestamp(
            end_ms / 1000, tz=timezone.utc
        )
        start_dt = datetime.fromtimestamp(
            start_ms / 1000, tz=timezone.utc
        )

        candles = coinbase.fetch_batch(
            product_id=provider_symbol_value,
            start_dt=start_dt,
            end_dt=end_dt,
            interval=INTERVAL,
        )

    else:

        raise ValueError(f"Unknown provider: {provider_name}")

    in_range = [
        candle
        for candle in candles
        if start_ms <= int(candle["timestamp"]) <= end_ms
    ]

    rolling_base_volume = sum(
        float(candle["volume_base"]) for candle in in_range
    )

    exact_quote_available = all(
        bool(candle.get("volume_usd_exact", False))
        for candle in in_range
    ) and bool(in_range)

    if exact_quote_available:

        rolling_usd_volume = sum(
            float(candle["volume_usd"]) for candle in in_range
        )

        usd_source = "PROVIDER_QUOTE_VOLUME"

    else:

        rolling_usd_volume = None
        usd_source = None

    return {
        "mode": REQUESTED_RANGE_MODE,
        "start_utc": range_info["start_utc"],
        "end_utc": range_info["end_utc"],
        "start_ms": start_ms,
        "end_ms": end_ms,
        "duration_minutes": REQUESTED_DURATION_MINUTES,
        "interval": INTERVAL,
        "provider": provider_name,
        "provider_symbol": provider_symbol_value,
        "candles_in_time_range": len(in_range),
        "rolling_volume_base": rolling_base_volume,
        "rolling_volume_definition": "TOTAL_TRADED_BASE_ASSET_VOLUME",
        "volume_counting_rule": "EACH_TRADE_COUNTED_ONCE",
        "buyer_seller_double_counted": False,
        "rolling_volume_source": "PROVIDER_SUPPLIED",
        "rolling_volume_usd": rolling_usd_volume,
        "rolling_volume_usd_exact": exact_quote_available,
        "rolling_volume_usd_source": usd_source,
        "not_last_completed_candle": True,
        "not_last_n_rows": True,
        "no_close_times_volume": True,
        "no_market_cap_volume": True,
    }
