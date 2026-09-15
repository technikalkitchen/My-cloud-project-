from app.config import quality


def test_u06_5_identity_and_universe_contract():
    assert quality.CELL_ID == "U06.5"
    assert quality.TOP_N == 125
    assert quality.TIMEFRAME == "5m"
    assert quality.SUPPORTED_TIMEFRAMES == ("1m", "5m", "15m", "1h", "4h", "1d")


def test_u06_5_provider_policy():
    assert quality.PROVIDER_PRIORITY["global"] == ["coinmarketcap", "coingecko"]
    assert quality.PROVIDER_PRIORITY["exchange"] == [
        "binance",
        "okx",
        "bybit",
        "kucoin",
        "coinbase",
        "gate",
        "upbit",
        "bitget",
    ]
    assert "tradingview" in quality.FORBIDDEN_RUNTIME_PROVIDERS
    assert len(quality.MULTI_EXCHANGE_SPECS) == 8


def test_u06_5_exchange_params_present():
    required_keys = {"mode", "symbol", "url", "params"}
    for exchange, spec in quality.MULTI_EXCHANGE_SPECS.items():
        missing = required_keys - set(spec.keys())
        assert not missing, f"{exchange} missing keys: {missing}"
        assert isinstance(spec["params"], dict)
        assert len(spec["params"]) >= 1

    binance = quality.MULTI_EXCHANGE_SPECS["binance"]
    assert binance["params"]["symbol"] == "BTCUSDT"
    assert binance["params"]["interval"] == quality.EXCHANGE_KLINE_INTERVAL

    okx = quality.MULTI_EXCHANGE_SPECS["okx"]
    assert okx["params"]["instId"] == "BTC-USDT"
    assert okx["params"]["bar"] == quality.EXCHANGE_KLINE_INTERVAL

    coinbase = quality.MULTI_EXCHANGE_SPECS["coinbase"]
    assert coinbase["params"]["granularity"] == 300

    upbit = quality.MULTI_EXCHANGE_SPECS["upbit"]
    assert upbit["params"]["market"] == "USDT-BTC"
    assert "count" in upbit["params"]


def test_u06_5_exchange_acceptance_contract():
    assert quality.TARGET_EXCHANGE_COUNT == 8
    assert quality.MIN_VALIDATED_EXCHANGE_COUNT == 7
    assert quality.MULTI_EXCHANGE_PROBE_SYMBOL == "BTCUSDT"
    assert quality.EXCHANGE_KLINE_INTERVAL == "5m"


def test_u06_5_quality_thresholds():
    assert quality.QUALITY_CONFIG["max_source_age_seconds"] == 900
    assert quality.QUALITY_CONFIG["max_orderbook_age_seconds"] == 30.0
    assert quality.QUALITY_CONFIG["min_reference_exchanges"] == 2
    assert quality.QUALITY_CONFIG["preferred_reference_exchanges"] == 3


def test_u06_5_safety_locks():
    assert quality.TRADING_ENABLED is False
    assert quality.ORDERS_ENABLED is False
    assert quality.STRATEGY_ENABLED is False
    assert quality.PORTFOLIO_ACTIONS_ENABLED is False
    assert quality.AUTO_PERSIST_SNAPSHOT is False
