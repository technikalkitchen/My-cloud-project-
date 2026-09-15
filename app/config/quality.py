"""U06.5-A configuration constants.

Layer A owns all acquisition/normalization/validation configuration.
Layer B reads these constants as parameters and never re-derives them.

Portable: stdlib only. No Colab, no notebook-host paths, no secrets.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Tuple


# ---------------------------------------------------------------------------
# Identity / schema
# ---------------------------------------------------------------------------
CELL_ID = "U06.5"
PROJECT = "KITCHEN ASSISTANT V3.1"
VERSION = "8.4.5"
SCHEMA_VERSION = "U06_5_SCHEMA_V6_0"

# ---------------------------------------------------------------------------
# Provider endpoints
# ---------------------------------------------------------------------------
CMC_BASE_KEYLESS = "https://pro-api.coinmarketcap.com/public-api"
CMC_BASE_AUTH = "https://pro-api.coinmarketcap.com"
COINGECKO_BASE = "https://api.coingecko.com/api/v3"

# ---------------------------------------------------------------------------
# Universe / timeframe contracts
# ---------------------------------------------------------------------------
TOP_N = 125
TIMEFRAME = "5m"
SUPPORTED_TIMEFRAMES = ("1m", "5m", "15m", "1h", "4h", "1d")

_DATASET_MODE = os.getenv("KITCHEN_DATASET_MODE", "SNAPSHOT").strip().upper()
DATASET_MODE = _DATASET_MODE if _DATASET_MODE in {"SNAPSHOT", "HISTORICAL"} else "SNAPSHOT"

# ---------------------------------------------------------------------------
# Runtime behaviour
# ---------------------------------------------------------------------------
MAX_RETRIES_PER_PROVIDER = 1
HTTP_TIMEOUT_SECONDS = 20
FRESHNESS_THRESHOLD_SECONDS = 15 * 60
MIN_TOP125_COVERAGE = 1.0

TARGET_CANDIDATE_POOL = int(os.getenv("KITCHEN_TARGET_CANDIDATE_POOL", "1250"))

# ---------------------------------------------------------------------------
# Exchange / venue configuration (single source of truth in exchanges.py).
# Re-exported here so existing `from app.config.quality import ...` paths and
# the U06.5-A tests continue to resolve unchanged.
# ---------------------------------------------------------------------------
from app.config.exchanges import (  # noqa: E402
    TARGET_EXCHANGE_COUNT,
    MIN_VALIDATED_EXCHANGE_COUNT,
    MULTI_EXCHANGE_PROBE_SYMBOL,
    U05_EXCHANGE_SYMBOLS,
    EXCHANGE_KLINE_INTERVAL,
    EXCHANGE_KLINE_LIMIT,
    HISTORICAL_PAGE_LIMIT,
    PROVIDER_PRIORITY,
    FORBIDDEN_RUNTIME_PROVIDERS,
    MULTI_EXCHANGE_SPECS,
    ORDERBOOK_SPECS,
)

# ---------------------------------------------------------------------------
# Credentials — portable discovery, never printed or persisted.
# ---------------------------------------------------------------------------
CMC_API_KEY_ENV = "CMC_API_KEY"


def _discover_cmc_api_key() -> Tuple[str, str]:
    env_candidates = (
        ("CMC_API_KEY", os.getenv("CMC_API_KEY", "")),
        ("KITCHEN_CMC_API_KEY", os.getenv("KITCHEN_CMC_API_KEY", "")),
        ("COINMARKETCAP_API_KEY", os.getenv("COINMARKETCAP_API_KEY", "")),
        ("CMC_PRO_API_KEY", os.getenv("CMC_PRO_API_KEY", "")),
    )
    for name, value in env_candidates:
        value = str(value).strip()
        if value:
            return value, f"ENV:{name}"
    return "", "NONE"


CMC_API_KEY, CMC_API_KEY_SOURCE = _discover_cmc_api_key()

CG_API_KEY_ENV = "COINGECKO_API_KEY"
CG_API_KEY = (
    os.getenv("COINGECKO_API_KEY", "").strip()
    or os.getenv("KITCHEN_COINGECKO_API_KEY", "").strip()
)

# ---------------------------------------------------------------------------
# Provider policy
# ---------------------------------------------------------------------------
CORE_ASSETS: Dict[int, str] = {
    1: "BTC",
    1027: "ETH",
    825: "USDT",
}

# ---------------------------------------------------------------------------
# Reference / cross-source
# ---------------------------------------------------------------------------
REFERENCE_STATUS = "REFERENCE_NOT_USED"
REFERENCE_PROVIDER = "coingecko"
REFERENCE_MAX_PRICE_DEVIATION_PCT = 1.0
REFERENCE_MIN_OVERLAP = 0.80

# ---------------------------------------------------------------------------
# Historical time-series
# ---------------------------------------------------------------------------
TIME_SERIES_LOOKBACK_DAYS = int(os.getenv("KITCHEN_TIME_SERIES_LOOKBACK_DAYS", "1"))

# Historical global-index time-series is a capability requirement only when
# HISTORICAL mode is explicitly requested. A SNAPSHOT run must not fail merely
# because a provider does not expose historical 5m global-index data.
HISTORICAL_TIME_SERIES_REQUIRED = True

# CoinGecko cross-source reference is evidence, not a foundation dependency.
REFERENCE_REQUIRED_FOR_LOCK = False

# ---------------------------------------------------------------------------
# Explicit, configurable market-quality thresholds.
# ---------------------------------------------------------------------------
QUALITY_CONFIG: Dict[str, object] = {
    "max_source_age_seconds": FRESHNESS_THRESHOLD_SECONDS,
    "max_price_deviation_pct_from_median": 5.0,
    "max_robust_z": 6.0,
    "min_volume_usd_24h": 0.0,
    "min_markets_for_aggregate": 1,
    "mad_epsilon": 1e-12,
    "max_orderbook_age_seconds": 30.0,
    "depth_bands_pct": (0.05, 0.10, 0.25, 0.50, 1.00),
    "spread_soft_limit_bps": 20.0,
    "price_impact_notional_usd": (10_000.0, 100_000.0),
    "reliability_component_weights": {
        "data_integrity": 0.15,
        "freshness": 0.10,
        "volume": 0.15,
        "near_depth": 0.20,
        "far_depth": 0.10,
        "spread": 0.10,
        "price_impact": 0.10,
        "cross_exchange_consistency": 0.10,
    },
    "min_reference_exchanges": 2,
    "preferred_reference_exchanges": 3,
}

# No automatic snapshot creation.
AUTO_PERSIST_SNAPSHOT = False

# ---------------------------------------------------------------------------
# Safety locks — asserted at import time, preserved across U05-U09.
# ---------------------------------------------------------------------------
TRADING_ENABLED = False
ORDERS_ENABLED = False
STRATEGY_ENABLED = False
PORTFOLIO_ACTIONS_ENABLED = False

assert not TRADING_ENABLED
assert not ORDERS_ENABLED
assert not STRATEGY_ENABLED
assert not PORTFOLIO_ACTIONS_ENABLED