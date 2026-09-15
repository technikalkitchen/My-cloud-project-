"""U06.5-A global-layer provider acquisition (CMC + CoinGecko).

CMC keyless is the primary current-data mode. CMC authenticated is optional
when a key is explicitly configured. CoinGecko is the fallback. TradingView is
forbidden and is never a runtime provider or reference.

Layer A only: acquisition, normalization helpers, and response shaping.
Layer B (ranking / indices / reference price / lock gate) is NOT here.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.core.u06_5 import (
    parse_timestamp,
    safe_float,
    safe_int,
    timestamp_age_seconds,
    utc_now,
)
from app.config.quality import (
    CMC_API_KEY,
    CMC_BASE_AUTH,
    CMC_BASE_KEYLESS,
    COINGECKO_BASE,
    CORE_ASSETS,
    FRESHNESS_THRESHOLD_SECONDS,
    MIN_TOP125_COVERAGE,
    TOP_N,
)
from app.market.http import HTTPResult, http_json


def cmc_status_ok(payload: Any) -> bool:
    if not isinstance(payload, dict):
        return False
    status = payload.get("status")
    if status is None:
        return True
    if isinstance(status, dict):
        code = status.get("error_code")
        return code in (0, "0", None)
    return True


def cmc_data(payload: Any) -> Any:
    if isinstance(payload, dict):
        return payload.get("data")
    return None


def cmc_quote(asset: Dict[str, Any]) -> Dict[str, Any]:
    quote = asset.get("quote") if isinstance(asset, dict) else None

    # Endpoint-specific schema: some CMC responses expose a dict.
    if isinstance(quote, dict):
        usd = quote.get("USD")
        if isinstance(usd, dict):
            return usd
        return quote

    # Endpoint-specific schema: listings/quotes may expose a list.
    if isinstance(quote, list):
        for item in quote:
            if not isinstance(item, dict):
                continue
            usd = item.get("USD")
            if isinstance(usd, dict):
                return usd
            if "price" in item or "market_cap" in item:
                return item

    return {}


def cmc_asset_records(data: Any) -> List[Dict[str, Any]]:
    if not isinstance(data, list):
        return []
    return [x for x in data if isinstance(x, dict)]


def cmc_headers(authenticated: bool) -> Dict[str, str]:
    if authenticated:
        if not CMC_API_KEY:
            raise RuntimeError(
                "CMC authenticated mode requested without CMC_API_KEY."
            )
        return {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    # Keyless mode MUST NOT attach an API-key header.
    return {}


def acquire_cmc(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    authenticated: bool = False,
) -> HTTPResult:
    base = CMC_BASE_AUTH if authenticated else CMC_BASE_KEYLESS
    return http_json(
        base.rstrip("/") + "/" + endpoint.lstrip("/"),
        params=params,
        headers=cmc_headers(authenticated),
    )


def acquire_cmc_top125(authenticated: bool = False) -> HTTPResult:
    return acquire_cmc(
        "/v3/cryptocurrency/listings/latest",
        {"start": 1, "limit": TOP_N, "convert": "USD"},
        authenticated=authenticated,
    )


def acquire_cmc_quotes(
    asset_ids: Sequence[int] = tuple(CORE_ASSETS.keys()),
    authenticated: bool = False,
) -> HTTPResult:
    return acquire_cmc(
        "/v3/cryptocurrency/quotes/latest",
        {
            "id": ",".join(str(x) for x in asset_ids),
            "convert": "USD",
        },
        authenticated=authenticated,
    )


def acquire_cmc_global(authenticated: bool = False) -> HTTPResult:
    return acquire_cmc(
        "/v1/global-metrics/quotes/latest",
        {"convert": "USD"},
        authenticated=authenticated,
    )


def acquire_cmc_simple_price(
    asset_ids: Sequence[int] = tuple(CORE_ASSETS.keys()),
    authenticated: bool = False,
) -> HTTPResult:
    return acquire_cmc(
        "/v1/simple/price",
        {
            "id": ",".join(str(x) for x in asset_ids),
            "convert": "USD",
        },
        authenticated=authenticated,
    )


def acquire_coingecko_top125() -> HTTPResult:
    return http_json(
        COINGECKO_BASE + "/coins/markets",
        {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": TOP_N,
            "page": 1,
            "sparkline": "false",
        },
    )


# ---------------------------------------------------------------------------
# U06.5 Unit 6 — Global asset normalization + validation.
# ---------------------------------------------------------------------------

REQUIRED_NUMERIC_FIELDS = (
    "price",
    "market_cap",
    "volume_24h",
    "percent_change_1h",
    "percent_change_24h",
)


def _require_dict(value: Any, label: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a dict, got {type(value).__name__}")
    return value


def normalize_cmc_asset(asset: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a CMC listing/quote asset into the U06.5-A global contract."""
    _require_dict(asset, "cmc_asset")
    quote = cmc_quote(asset)
    return {
        "provider": "coinmarketcap",
        "provider_mode": "KEYLESS_PUBLIC",
        "canonical_asset_id": safe_int(asset.get("id")) or safe_int(asset.get("slug")),
        "provider_asset_id": str(asset.get("slug") or asset.get("id") or "").strip(),
        "symbol": str(asset.get("symbol") or "").strip().upper(),
        "name": str(asset.get("name") or "").strip(),
        "price": safe_float(quote.get("price")),
        "market_cap": safe_float(quote.get("market_cap")),
        "volume_24h": safe_float(quote.get("volume_24h")),
        "percent_change_1h": safe_float(quote.get("percent_change_1h")),
        "percent_change_24h": safe_float(quote.get("percent_change_24h")),
        "rank": safe_int(asset.get("rank")) or safe_int(quote.get("rank")),
        "last_updated": str(asset.get("last_updated") or quote.get("last_updated") or "").strip(),
    }


def normalize_coingecko_asset(asset: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a CoinGecko markets asset into the U06.5-A global contract."""
    _require_dict(asset, "cg_asset")
    return {
        "provider": "coingecko",
        "provider_mode": "PUBLIC",
        "canonical_asset_id": safe_int(asset.get("id")) or safe_int(asset.get("market_cap_rank")),
        "provider_asset_id": str(asset.get("id") or "").strip(),
        "symbol": str(asset.get("symbol") or "").strip().upper(),
        "name": str(asset.get("name") or "").strip(),
        "price": safe_float(asset.get("current_price")),
        "market_cap": safe_float(asset.get("market_cap")),
        "volume_24h": safe_float(asset.get("total_volume")),
        "percent_change_1h": safe_float(asset.get("price_change_percentage_1h_in_currency")),
        "percent_change_24h": safe_float(asset.get("price_change_percentage_24h_in_currency")),
        "rank": safe_int(asset.get("market_cap_rank")),
        "last_updated": str(asset.get("last_updated") or "").strip(),
    }


def validate_identity(record: Dict[str, Any]) -> List[str]:
    """Validate required identity fields. Returns a list of failure reasons."""
    failures: List[str] = []
    if not record.get("provider"):
        failures.append("missing provider")
    if not record.get("symbol"):
        failures.append("missing symbol")
    if record.get("canonical_asset_id") is None:
        failures.append("missing canonical_asset_id")
    return failures


def validate_numeric_market_fields(record: Dict[str, Any]) -> List[str]:
    """Validate required numeric market fields. Returns a list of failure reasons."""
    failures: List[str] = []
    for field in REQUIRED_NUMERIC_FIELDS:
        value = record.get(field)
        if value is None:
            failures.append(f"missing {field}")
    return failures


def validate_timestamp_fields(
    record: Dict[str, Any],
    retrieved_at: Any,
) -> List[str]:
    """Validate timestamp/freshness. Returns a list of failure reasons."""
    failures: List[str] = []
    last_updated = record.get("last_updated")
    if not last_updated:
        failures.append("missing last_updated")
        return failures
    age = timestamp_age_seconds(last_updated, retrieved_at)
    if age is None:
        failures.append("unparseable last_updated")
        return failures
    if age > FRESHNESS_THRESHOLD_SECONDS:
        failures.append(f"stale source age {age:.1f}s > {FRESHNESS_THRESHOLD_SECONDS}s")
    return failures


def freshness_status(
    source_timestamp: Any,
    retrieved_at: Any,
) -> str:
    """Return FRESH / STALE / UNAVAILABLE."""
    age = timestamp_age_seconds(source_timestamp, retrieved_at)
    if age is None:
        return "UNAVAILABLE"
    if age <= FRESHNESS_THRESHOLD_SECONDS:
        return "FRESH"
    return "STALE"


def validate_ranked_universe(
    records: List[Dict[str, Any]],
    expected_count: int = TOP_N,
) -> List[str]:
    """Validate Top-125 rank completeness. Returns a list of failure reasons."""
    failures: List[str] = []
    if not isinstance(records, list):
        return ["records must be a list"]
    if len(records) < expected_count:
        failures.append(
            f"record count {len(records)} < expected {expected_count}"
        )
    seen_ranks = set()
    for record in records:
        rank = record.get("rank")
        if rank is None:
            failures.append("missing rank on a record")
            continue
        if not isinstance(rank, int) or rank < 1:
            failures.append(f"invalid rank {rank!r}")
            continue
        if rank in seen_ranks:
            failures.append(f"duplicate rank {rank}")
        seen_ranks.add(rank)
    coverage = len(seen_ranks) / expected_count if expected_count else 0.0
    if coverage < MIN_TOP125_COVERAGE:
        failures.append(
            f"rank coverage {coverage:.4f} < {MIN_TOP125_COVERAGE}"
        )
    return failures


def validate_core_assets(records: List[Dict[str, Any]]) -> List[str]:
    """Validate BTC/ETH/USDT core asset presence. Returns failure reasons."""
    failures: List[str] = []
    if not isinstance(records, list):
        return ["records must be a list"]
    symbols = {
        str(r.get("symbol", "")).strip().upper()
        for r in records
        if isinstance(r, dict)
    }
    for core in CORE_ASSETS.values():
        if core not in symbols:
            failures.append(f"missing core asset {core}")
    return failures


def validate_record(
    record: Dict[str, Any],
    retrieved_at: Any,
) -> Dict[str, Any]:
    """Run all per-record validations. Returns a result dict."""
    failures: List[str] = []
    failures.extend(validate_identity(record))
    failures.extend(validate_numeric_market_fields(record))
    failures.extend(validate_timestamp_fields(record, retrieved_at))
    return {
        "symbol": record.get("symbol"),
        "provider": record.get("provider"),
        "rank": record.get("rank"),
        "valid": not failures,
        "failures": failures,
        "freshness": freshness_status(record.get("last_updated"), retrieved_at),
    }