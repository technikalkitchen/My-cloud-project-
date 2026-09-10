from app.data.capture.binance import (
    BinancePublicAdapter,
    BinanceProviderUnavailable,
)

from app.data.capture.coinbase import (
    CoinbasePublicAdapter,
    CoinbaseProviderUnavailable,
)

from app.data.capture.router import (
    ProviderRouter,
)

import pytest


def test_binance_adapter_exists():

    adapter = BinancePublicAdapter()

    assert (
        adapter.provider_name
        == "BINANCE_SPOT_PUBLIC"
    )

    assert len(adapter.BASE_URLS) == 5


def test_binance_limit_validation_zero():

    adapter = BinancePublicAdapter()

    with pytest.raises(ValueError):

        adapter.fetch(
            "BTCUSDT",
            "1m",
            0,
        )


def test_binance_excessive_limit():

    adapter = BinancePublicAdapter()

    with pytest.raises(ValueError):

        adapter.fetch(
            "BTCUSDT",
            "1m",
            1001,
        )


def test_binance_interval_validation():

    adapter = BinancePublicAdapter()

    with pytest.raises(ValueError):

        adapter.fetch(
            "BTCUSDT",
            "2m",
            5,
        )


def test_binance_granularity_map_complete():

    expected = {
        "1m",
        "3m",
        "5m",
        "15m",
        "30m",
        "1h",
        "2h",
        "4h",
        "6h",
        "8h",
        "12h",
        "1d",
    }

    assert (
        set(BinancePublicAdapter.GRANULARITY_MAP.keys())
        == expected
    )


def test_coinbase_adapter_exists():

    adapter = CoinbasePublicAdapter()

    assert (
        adapter.provider_name
        == "COINBASE_EXCHANGE_PUBLIC"
    )

    assert CoinbasePublicAdapter.BASE_URL == (
        "https://api.exchange.coinbase.com"
    )


def test_coinbase_product_id_normalization():

    adapter = CoinbasePublicAdapter()

    assert adapter._product_id("BTCUSDT") == "BTC-USD"
    assert adapter._product_id("ETHUSDT") == "ETH-USD"
    assert adapter._product_id("BTCUSD") == "BTC-USD"


def test_coinbase_interval_validation():

    adapter = CoinbasePublicAdapter()

    with pytest.raises(ValueError):

        adapter.fetch(
            "BTCUSDT",
            "2m",
            5,
        )


def test_coinbase_limit_validation_zero():

    adapter = CoinbasePublicAdapter()

    with pytest.raises(ValueError):

        adapter.fetch(
            "BTCUSDT",
            "1m",
            0,
        )


def test_router_exists():

    router = ProviderRouter()

    assert router.binance is not None
    assert router.coinbase is not None


def test_provider_priority():

    router = ProviderRouter()

    assert (
        router.binance.provider_name
        == "BINANCE_SPOT_PUBLIC"
    )

    assert (
        router.coinbase.provider_name
        == "COINBASE_EXCHANGE_PUBLIC"
    )
