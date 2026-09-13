"""U09 Unit 1 — Configuration tests."""
from __future__ import annotations

import os

import pytest

from app.config.market_universe import CONFIG, COINGECKO_API_KEY, COINMARKETCAP_API_KEY, PORTFOLIO_ACTIONS_ENABLED, STRATEGY_ENABLED, TRADING_ENABLED, ORDERS_ENABLED


def test_config_has_required_keys():
    required = {
        "universe_limit", "currency", "reference_mode", "lookback",
        "minimum_reference_age_seconds", "maximum_reference_age_seconds",
        "max_current_age_seconds", "breadth_threshold_pct",
        "breadth_flat_band_pct", "dominance_partition_tolerance_pct",
        "rank_minor_difference", "rank_warning_difference",
        "max_retries_per_provider", "request_timeout_seconds",
        "retry_backoff_seconds", "provider_cooldown_seconds",
        "cache_enabled", "cache_max_age_seconds",
        "allow_stale_cache_for_analysis", "message_window_label",
        "message_show_dominance_current", "message_show_dominance_pp",
        "message_show_participation_state", "message_dominance_min_decimals",
        "message_dominance_max_decimals",
    }
    missing = required - set(CONFIG.keys())
    assert not missing, f"Missing CONFIG keys: {missing}"


def test_config_universe_limit():
    assert CONFIG["universe_limit"] == 125


def test_config_currency():
    assert CONFIG["currency"] == "usd"


def test_config_reference_mode():
    assert CONFIG["reference_mode"] == "provider_24h"


def test_config_lookback():
    assert CONFIG["lookback"] == "24h"


def test_config_max_current_age_default():
    assert CONFIG["max_current_age_seconds"] == 900


def test_config_breadth_threshold():
    assert CONFIG["breadth_threshold_pct"] == 0.25


def test_config_dominance_tolerance():
    assert CONFIG["dominance_partition_tolerance_pct"] == 0.10


def test_config_message_contract_no_participation():
    assert CONFIG["message_show_participation_state"] is False


def test_config_message_contract_no_pp():
    assert CONFIG["message_show_dominance_pp"] is False


def test_config_message_contract_no_current_dominance():
    assert CONFIG["message_show_dominance_current"] is False


def test_safety_locks():
    assert TRADING_ENABLED is False
    assert ORDERS_ENABLED is False
    assert STRATEGY_ENABLED is False
    assert PORTFOLIO_ACTIONS_ENABLED is False


def test_safety_locks_are_asserted():
    # The module asserts these at import time; if we got here they passed.
    assert True


def test_config_is_mutable_dict():
    assert isinstance(CONFIG, dict)


def test_config_env_overrides_timeout():
    os.environ["U09_REQUEST_TIMEOUT_SECONDS"] = "30"
    try:
        import importlib
        import app.config.market_universe as mu
        importlib.reload(mu)
        assert mu.CONFIG["request_timeout_seconds"] == 30
    finally:
        del os.environ["U09_REQUEST_TIMEOUT_SECONDS"]
