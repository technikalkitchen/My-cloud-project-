"""U09 — Dynamic Market Universe configuration.

Portable: stdlib only + requests (already in requirements.txt).
No Colab, no notebook-host paths, no secrets in output.
"""
from __future__ import annotations

import os
from typing import Any, Dict


CONFIG: Dict[str, Any] = {
    "universe_limit": 125,
    "currency": "usd",
    "reference_mode": "provider_24h",
    "lookback": "24h",
    "minimum_reference_age_seconds": 20 * 60,
    "maximum_reference_age_seconds": 48 * 3600,
    "max_current_age_seconds": int(os.getenv("U09_MAX_CURRENT_AGE_SECONDS", "900")),
    "breadth_threshold_pct": 0.25,
    "breadth_flat_band_pct": 0.25,
    "dominance_partition_tolerance_pct": 0.10,
    "rank_minor_difference": 1,
    "rank_warning_difference": 3,
    "max_retries_per_provider": 1,
    "request_timeout_seconds": int(os.getenv("U09_REQUEST_TIMEOUT_SECONDS", "12")),
    "retry_backoff_seconds": 1.0,
    "provider_cooldown_seconds": 60,
    "cache_enabled": True,
    "cache_max_age_seconds": 10 * 60,
    "allow_stale_cache_for_analysis": False,
    "message_window_label": "24H",
    "message_show_dominance_current": False,
    "message_show_dominance_pp": False,
    "message_show_participation_state": False,
    "message_dominance_min_decimals": 2,
    "message_dominance_max_decimals": 6,
}

COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "").strip()
COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY", "").strip()

TRADING_ENABLED = False
ORDERS_ENABLED = False
STRATEGY_ENABLED = False
PORTFOLIO_ACTIONS_ENABLED = False

assert not TRADING_ENABLED
assert not ORDERS_ENABLED
assert not STRATEGY_ENABLED
assert not PORTFOLIO_ACTIONS_ENABLED
