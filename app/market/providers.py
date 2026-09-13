"""U09 — Provider contracts and acquisition.

CoinGecko primary, CoinMarketCap secondary. Providers are abstract
contracts; concrete implementations fetch via requests (stdlib + requests
already in requirements.txt). TradingView is forbidden.

Layer A only: provider dataclasses, abstract contracts, fetch, normalize.
Layer B (segmentation, dominance, relative strength, brain) is NOT here.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from app.config.market_universe import (
    COINGECKO_API_KEY,
    COINMARKETCAP_API_KEY,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.astimezone(timezone.utc).isoformat() if dt else None


def parse_ts(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            x = float(value)
            if x > 10_000_000_000:
                x /= 1000.0
            return datetime.fromtimestamp(x, tz=timezone.utc)
        except Exception:
            return None
    if isinstance(value, str):
        s = value.strip().replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(s)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except Exception:
            return None
    return None


def finite_nonnegative(value: Any) -> bool:
    try:
        x = float(value)
        return math.isfinite(x) and x >= 0.0
    except Exception:
        return False


@dataclass
class ProviderHealth:
    provider_id: str
    state: str = "AVAILABLE"
    failure_count: int = 0
    last_failure_at: Optional[str] = None
    cooldown_until: Optional[str] = None
    last_success_at: Optional[str] = None
    last_error: Optional[str] = None

    def in_cooldown(self, now: datetime) -> bool:
        dt = parse_ts(self.cooldown_until)
        return bool(dt and now < dt)


@dataclass
class ProviderAttempt:
    provider_id: str
    attempt: int
    request_timestamp: str
    response_timestamp: Optional[str]
    http_status: Optional[int]
    health_state: str
    error: Optional[str]
    endpoint: str


@dataclass
class ProviderSnapshot:
    provider_id: str
    primary_provider: str
    fallback_used: bool
    fallback_chain: List[str]
    fallback_reason: Optional[str]
    provider_status: str
    provider_timestamp: Optional[str]
    request_timestamp: str
    response_timestamp: str
    provider_schema_version: str
    provider_endpoint: str
    provider_request_status: str
    raw_assets: List[Dict[str, Any]]
    attempts: List[Dict[str, Any]]


class ProviderError(RuntimeError):
    def __init__(self, state: str, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.state = state
        self.status_code = status_code


class BaseProvider:
    provider_id = "BASE"
    schema_version = "unknown"
    endpoint = ""

    def headers(self) -> Dict[str, str]:
        return {"Accept": "application/json", "User-Agent": "KitchenAssistant-U09/3.1"}

    def fetch(self, session: requests.Session, limit: int, timeout: int) -> Tuple[List[Dict[str, Any]], Optional[datetime], Dict[str, Any]]:
        raise NotImplementedError

    def normalize(self, payload: Any) -> Tuple[List[Dict[str, Any]], Optional[datetime], Dict[str, Any]]:
        raise NotImplementedError


class CoinGeckoProvider(BaseProvider):
    provider_id = "COINGECKO"
    schema_version = "coins/markets"
    endpoint = "https://api.coingecko.com/api/v3/coins/markets"

    def headers(self) -> Dict[str, str]:
        h = super().headers()
        if COINGECKO_API_KEY:
            h["x-cg-demo-api-key"] = COINGECKO_API_KEY
        return h

    def fetch(self, session: requests.Session, limit: int, timeout: int):
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": min(limit, 250),
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h",
        }
        req_ts = utc_now()
        try:
            r = session.get(self.endpoint, params=params, headers=self.headers(), timeout=timeout)
        except requests.Timeout as e:
            raise ProviderError("TIMEOUT", str(e))
        except requests.RequestException as e:
            raise ProviderError("UNAVAILABLE", str(e))
        resp_ts = utc_now()
        if r.status_code == 429:
            raise ProviderError("RATE_LIMITED", "HTTP 429", 429)
        if r.status_code in (401, 403):
            raise ProviderError("AUTH_FAILED", f"HTTP {r.status_code}", r.status_code)
        if r.status_code >= 500:
            raise ProviderError("UNAVAILABLE", f"HTTP {r.status_code}", r.status_code)
        if r.status_code != 200:
            raise ProviderError("UNAVAILABLE", f"HTTP {r.status_code}", r.status_code)
        try:
            payload = r.json()
        except Exception as e:
            raise ProviderError("MALFORMED", f"JSON decode failed: {e}")
        assets, provider_ts, meta = self.normalize(payload)
        meta.update({"request_timestamp": iso(req_ts), "response_timestamp": iso(resp_ts)})
        return assets, provider_ts, meta

    def normalize(self, payload):
        if not isinstance(payload, list):
            raise ProviderError("MALFORMED", "CoinGecko response is not a list")
        out = []
        for item in payload:
            if not isinstance(item, dict):
                raise ProviderError("MALFORMED", "CoinGecko asset item is not an object")
            out.append({
                "provider_asset_id": item.get("id"),
                "symbol": item.get("symbol"),
                "name": item.get("name"),
                "price_usd": item.get("current_price"),
                "market_cap_usd": item.get("market_cap"),
                "provider_rank": item.get("market_cap_rank"),
                "price_change_24h_pct": item.get("price_change_percentage_24h"),
                "market_cap_change_24h_pct": item.get("market_cap_change_percentage_24h"),
                "provider_timestamp": item.get("last_updated"),
            })
        stamps = [parse_ts(x.get("provider_timestamp")) for x in out]
        stamps = [x for x in stamps if x]
        provider_ts = min(stamps) if stamps else None
        return out, provider_ts, {"response_type": "list", "field_count_checked": True}


class CoinMarketCapProvider(BaseProvider):
    provider_id = "COINMARKETCAP"
    schema_version = "v3/listings_latest"
    endpoint_keyless = "https://pro-api.coinmarketcap.com/public-api/v3/cryptocurrency/listings/latest"
    endpoint_keyed = "https://pro-api.coinmarketcap.com/v3/cryptocurrency/listings/latest"

    @property
    def endpoint(self):
        return self.endpoint_keyed if COINMARKETCAP_API_KEY else self.endpoint_keyless

    def headers(self):
        h = super().headers()
        if COINMARKETCAP_API_KEY:
            h["X-CMC_PRO_API_KEY"] = COINMARKETCAP_API_KEY
        return h

    def fetch(self, session: requests.Session, limit: int, timeout: int):
        params = {"start": 1, "limit": min(limit, 200), "convert": "USD"}
        req_ts = utc_now()
        try:
            r = session.get(self.endpoint, params=params, headers=self.headers(), timeout=timeout)
        except requests.Timeout as e:
            raise ProviderError("TIMEOUT", str(e))
        except requests.RequestException as e:
            raise ProviderError("UNAVAILABLE", str(e))
        resp_ts = utc_now()
        if r.status_code == 429:
            raise ProviderError("RATE_LIMITED", "HTTP 429", 429)
        if r.status_code in (401, 403):
            raise ProviderError("AUTH_FAILED", f"HTTP {r.status_code}", r.status_code)
        if r.status_code >= 500:
            raise ProviderError("UNAVAILABLE", f"HTTP {r.status_code}", r.status_code)
        if r.status_code != 200:
            raise ProviderError("UNAVAILABLE", f"HTTP {r.status_code}", r.status_code)
        try:
            payload = r.json()
        except Exception as e:
            raise ProviderError("MALFORMED", f"JSON decode failed: {e}")
        assets, provider_ts, meta = self.normalize(payload)
        meta.update({"request_timestamp": iso(req_ts), "response_timestamp": iso(resp_ts)})
        return assets, provider_ts, meta

    def normalize(self, payload):
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            raise ProviderError("MALFORMED", "CoinMarketCap response/data shape invalid")
        status = payload.get("status") or {}
        code = status.get("error_code")
        if code is not None and str(code) != "0":
            raise ProviderError("UNAVAILABLE", str(status.get("error_message") or code))
        out = []
        for item in payload["data"]:
            if not isinstance(item, dict):
                raise ProviderError("MALFORMED", "CMC asset item is not an object")
            quote = ((item.get("quote") or {}).get("USD") or {})
            out.append({
                "provider_asset_id": item.get("id"),
                "symbol": item.get("symbol"),
                "name": item.get("name"),
                "price_usd": quote.get("price"),
                "market_cap_usd": quote.get("market_cap"),
                "provider_rank": item.get("cmc_rank"),
                "price_change_24h_pct": quote.get("percent_change_24h"),
                "market_cap_change_24h_pct": None,
                "provider_timestamp": status.get("timestamp"),
            })
        provider_ts = parse_ts(status.get("timestamp"))
        return out, provider_ts, {"response_type": "object", "field_count_checked": True, "status_error_code": str(code) if code is not None else None}


PROVIDER_REGISTRY: Dict[str, Dict[str, Any]] = {
    "COINGECKO": {"provider": CoinGeckoProvider(), "priority": 1, "health": ProviderHealth("COINGECKO")},
    "COINMARKETCAP": {"provider": CoinMarketCapProvider(), "priority": 2, "health": ProviderHealth("COINMARKETCAP")},
}
