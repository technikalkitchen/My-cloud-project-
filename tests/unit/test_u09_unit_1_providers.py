"""U09 Unit 1 — Provider contract tests."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta

from app.market.providers import (
    BaseProvider,
    CoinGeckoProvider,
    CoinMarketCapProvider,
    ProviderAttempt,
    ProviderError,
    ProviderHealth,
    ProviderSnapshot,
    PROVIDER_REGISTRY,
    utc_now,
    parse_ts,
    finite_nonnegative,
    iso,
)
from app.config.market_universe import CONFIG


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def test_utc_now_returns_datetime():
    from app.market.providers import utc_now as providers_utc_now
    now = providers_utc_now()
    assert isinstance(now, datetime)
    assert now.tzinfo is not None


def test_iso_with_datetime():
    dt = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    result = iso(dt)
    assert result == "2026-09-12T12:00:00+00:00"


def test_iso_with_none():
    assert iso(None) is None


def test_parse_ts_iso_string():
    result = parse_ts("2026-09-12T12:00:00+00:00")
    assert result is not None
    assert result.year == 2026


def test_parse_ts_iso_z_string():
    result = parse_ts("2026-09-12T12:00:00Z")
    assert result is not None
    assert result.tzinfo is not None


def test_parse_ts_none():
    assert parse_ts(None) is None


def test_parse_ts_milliseconds():
    result = parse_ts(1726142400000)
    assert result is not None
    expected = datetime(2024, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    assert abs((result - expected).total_seconds()) < 1


def test_parse_ts_seconds():
    result = parse_ts(1726142400)
    assert result is not None
    expected = datetime(2024, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    assert abs((result - expected).total_seconds()) < 1


def test_finite_nonnegative_true():
    assert finite_nonnegative(1.0) is True
    assert finite_nonnegative(0.0) is True
    assert finite_nonnegative(100.0) is True


def test_finite_nonnegative_false():
    assert finite_nonnegative(-1.0) is False
    assert finite_nonnegative(float("nan")) is False
    assert finite_nonnegative(float("inf")) is False
    assert finite_nonnegative(None) is False
    assert finite_nonnegative("abc") is False


# ---------------------------------------------------------------------------
# Provider dataclasses
# ---------------------------------------------------------------------------

def test_provider_health_defaults():
    h = ProviderHealth("TEST")
    assert h.provider_id == "TEST"
    assert h.state == "AVAILABLE"
    assert h.failure_count == 0
    assert h.last_failure_at is None
    assert h.cooldown_until is None
    assert h.last_success_at is None
    assert h.last_error is None


def test_provider_health_in_cooldown():
    now = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    future = iso(now + timedelta(minutes=5))
    h = ProviderHealth("TEST", state="AVAILABLE", cooldown_until=future)
    assert h.in_cooldown(now) is True


def test_provider_health_not_in_cooldown():
    now = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    past = iso(now - timedelta(hours=2))
    h = ProviderHealth("TEST", state="AVAILABLE", cooldown_until=past)
    assert h.in_cooldown(now) is False


def test_provider_health_in_cooldown_none():
    h = ProviderHealth("TEST")
    now = utc_now()
    assert h.in_cooldown(now) is False


def test_provider_attempt_fields():
    attempt = ProviderAttempt(
        provider_id="TEST",
        attempt=1,
        request_timestamp="2026-09-12T12:00:00+00:00",
        response_timestamp="2026-09-12T12:00:01+00:00",
        http_status=200,
        health_state="AVAILABLE",
        error=None,
        endpoint="/test",
    )
    assert attempt.provider_id == "TEST"
    assert attempt.attempt == 1
    assert attempt.http_status == 200


def test_provider_snapshot_fields():
    snap = ProviderSnapshot(
        provider_id="TEST",
        primary_provider="PRIMARY",
        fallback_used=False,
        fallback_chain=["TEST"],
        fallback_reason=None,
        provider_status="ACTIVE",
        provider_timestamp="2026-09-12T12:00:00+00:00",
        request_timestamp="2026-09-12T12:00:00+00:00",
        response_timestamp="2026-09-12T12:00:01+00:00",
        provider_schema_version="v1",
        provider_endpoint="/test",
        provider_request_status="SUCCESS",
        raw_assets=[],
        attempts=[],
    )
    assert snap.provider_id == "TEST"
    assert snap.fallback_used is False
    assert snap.raw_assets == []


def test_provider_error_has_state_and_code():
    err = ProviderError("TIMEOUT", "connection timeout", status_code=408)
    assert err.state == "TIMEOUT"
    assert err.status_code == 408
    assert str(err) == "connection timeout"


def test_provider_error_without_code():
    err = ProviderError("UNAVAILABLE", "no conn")
    assert err.state == "UNAVAILABLE"
    assert err.status_code is None


# ---------------------------------------------------------------------------
# BaseProvider abstract
# ---------------------------------------------------------------------------

def test_base_provider_fetch_raises():
    with pytest.raises(NotImplementedError):
        BaseProvider().fetch(None, 10, 12)


def test_base_provider_normalize_raises():
    with pytest.raises(NotImplementedError):
        BaseProvider().normalize(None)


def test_base_provider_defaults():
    p = BaseProvider()
    assert p.provider_id == "BASE"
    assert p.schema_version == "unknown"
    assert p.endpoint == ""


def test_base_provider_headers():
    h = BaseProvider().headers()
    assert h["Accept"] == "application/json"
    assert "User-Agent" in h


# ---------------------------------------------------------------------------
# CoinGeckoProvider
# ---------------------------------------------------------------------------

def test_coingecko_provider_attributes():
    p = CoinGeckoProvider()
    assert p.provider_id == "COINGECKO"
    assert p.schema_version == "coins/markets"
    assert p.endpoint == "https://api.coingecko.com/api/v3/coins/markets"


def test_coingecko_provider_headers_without_key():
    h = CoinGeckoProvider().headers()
    assert "x-cg-demo-api-key" not in h


def test_coingecko_provider_headers_with_key(monkeypatch):
    monkeypatch.setenv("COINGECKO_API_KEY", "test-key")
    import importlib
    import app.config.market_universe as mu
    importlib.reload(mu)
    from app.market import providers as prov_mod
    importlib.reload(prov_mod)
    CoinGeckoProvider = prov_mod.CoinGeckoProvider
    h = CoinGeckoProvider().headers()
    assert h["x-cg-demo-api-key"] == "test-key"


# ---------------------------------------------------------------------------
# CoinMarketCapProvider
# ---------------------------------------------------------------------------

def test_coinmarketcap_provider_attributes():
    p = CoinMarketCapProvider()
    assert p.provider_id == "COINMARKETCAP"
    assert p.schema_version == "v3/listings_latest"


def test_coinmarketcap_provider_keyless_endpoint():
    p = CoinMarketCapProvider()
    assert p.endpoint == "https://pro-api.coinmarketcap.com/public-api/v3/cryptocurrency/listings/latest"


# ---------------------------------------------------------------------------
# PROVIDER_REGISTRY
# ---------------------------------------------------------------------------

def test_provider_registry_has_two_providers():
    assert len(PROVIDER_REGISTRY) == 2
    assert "COINGECKO" in PROVIDER_REGISTRY
    assert "COINMARKETCAP" in PROVIDER_REGISTRY


def test_provider_registry_priority():
    cg = PROVIDER_REGISTRY["COINGECKO"]
    cmc = PROVIDER_REGISTRY["COINMARKETCAP"]
    assert cg["priority"] == 1
    assert cmc["priority"] == 2


def test_provider_registry_health():
    cg = PROVIDER_REGISTRY["COINGECKO"]
    cmc = PROVIDER_REGISTRY["COINMARKETCAP"]
    assert isinstance(cg["health"], ProviderHealth)
    assert isinstance(cmc["health"], ProviderHealth)
    assert cg["health"].provider_id == "COINGECKO"
    assert cmc["health"].provider_id == "COINMARKETCAP"


def test_provider_registry_coingecko_instance():
    assert isinstance(PROVIDER_REGISTRY["COINGECKO"]["provider"], CoinGeckoProvider)


def test_provider_registry_coinmarketcap_instance():
    assert isinstance(PROVIDER_REGISTRY["COINMARKETCAP"]["provider"], CoinMarketCapProvider)
