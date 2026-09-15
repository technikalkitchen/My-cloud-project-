import pytest

from app.market import global_providers as providers
from app.market.http import HTTPResult


def test_cmc_response_shaping():
    payload = {"status": {"error_code": 0}, "data": [{"id": 1}]}

    assert providers.cmc_status_ok(payload) is True
    assert providers.cmc_status_ok({"status": {"error_code": 1}}) is False
    assert providers.cmc_status_ok([]) is False
    assert providers.cmc_data(payload) == [{"id": 1}]
    assert providers.cmc_data([]) is None


def test_cmc_quote_shapes():
    assert providers.cmc_quote({"quote": {"USD": {"price": 1}}}) == {
        "price": 1,
    }
    assert providers.cmc_quote({"quote": {"price": 2}}) == {"price": 2}
    assert providers.cmc_quote({
        "quote": [{"USD": {"market_cap": 3}}, {"price": 4}],
    }) == {"market_cap": 3}
    assert providers.cmc_quote({"quote": [{"price": 4}]}) == {"price": 4}
    assert providers.cmc_quote({}) == {}


def test_cmc_asset_records():
    assert providers.cmc_asset_records([{"id": 1}, "bad", {"id": 2}]) == [
        {"id": 1},
        {"id": 2},
    ]
    assert providers.cmc_asset_records({"id": 1}) == []


def test_cmc_headers_and_authenticated_guard(monkeypatch):
    assert providers.cmc_headers(False) == {}

    monkeypatch.setattr(providers, "CMC_API_KEY", "test-key")
    assert providers.cmc_headers(True) == {"X-CMC_PRO_API_KEY": "test-key"}

    monkeypatch.setattr(providers, "CMC_API_KEY", "")
    with pytest.raises(RuntimeError, match="without CMC_API_KEY"):
        providers.cmc_headers(True)


def test_acquire_cmc_routes(monkeypatch):
    calls = []

    def fake_http_json(url, params=None, headers=None):
        calls.append((url, params, headers))
        return HTTPResult(
            ok=True,
            status=200,
            payload={"data": []},
            retrieved_at="2026-09-10T20:00:00+00:00",
            elapsed_seconds=0.0,
        )

    monkeypatch.setattr(providers, "http_json", fake_http_json)
    monkeypatch.setattr(providers, "CMC_API_KEY", "test-key")

    providers.acquire_cmc_top125()
    providers.acquire_cmc_quotes((1, 1027))
    providers.acquire_cmc_global()
    providers.acquire_cmc_simple_price((825,))
    providers.acquire_cmc("/custom", {"x": 1}, authenticated=True)

    assert calls[0][0] == (
        "https://pro-api.coinmarketcap.com/public-api"
        "/v3/cryptocurrency/listings/latest"
    )
    assert calls[0][1] == {"start": 1, "limit": 125, "convert": "USD"}
    assert calls[0][2] == {}
    assert calls[1][1]["id"] == "1,1027"
    assert calls[2][0].endswith("/v1/global-metrics/quotes/latest")
    assert calls[3][0].endswith("/v1/simple/price")
    assert calls[4][0] == (
        "https://pro-api.coinmarketcap.com/custom"
    )
    assert calls[4][2] == {"X-CMC_PRO_API_KEY": "test-key"}


def test_acquire_coingecko_top125(monkeypatch):
    captured = {}

    def fake_http_json(url, params=None, headers=None):
        captured["url"] = url
        captured["params"] = params
        captured["headers"] = headers
        return HTTPResult(
            ok=True,
            status=200,
            payload=[],
            retrieved_at="2026-09-10T20:00:00+00:00",
            elapsed_seconds=0.0,
        )

    monkeypatch.setattr(providers, "http_json", fake_http_json)

    result = providers.acquire_coingecko_top125()

    assert result.ok is True
    assert result.payload == []
    assert captured["url"] == "https://api.coingecko.com/api/v3/coins/markets"
    assert captured["params"] == {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 125,
        "page": 1,
        "sparkline": "false",
    }
    assert captured["headers"] is None
