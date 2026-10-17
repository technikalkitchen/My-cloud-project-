"""Small, explicit configuration for the TEST001 market-history MVP."""
from __future__ import annotations

from dataclasses import dataclass

TIMEFRAMES = {"5m": 300, "1h": 3600}
EXCHANGES = ("binance", "okx", "bitstamp", "coinbase", "crypto_com")
QUOTE_ASSETS = ("USDT", "BTC")
REQUEST_TIMEOUT_SECONDS = 20
USER_AGENT = "KitchenAssistantBot-TEST001/0.1"


@dataclass(frozen=True)
class ExchangeConfig:
    name: str
    base_url: str


EXCHANGE_CONFIGS = {
    "binance": ExchangeConfig("binance", "https://api.binance.com"),
    "okx": ExchangeConfig("okx", "https://www.okx.com"),
    "bitstamp": ExchangeConfig("bitstamp", "https://www.bitstamp.net"),
    "coinbase": ExchangeConfig("coinbase", "https://api.exchange.coinbase.com"),
    "crypto_com": ExchangeConfig("crypto_com", "https://api.crypto.com/exchange/v1"),
}
