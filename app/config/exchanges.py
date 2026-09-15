"""Exchange configuration for U06.5-A.

Layer A owns all exchange/venue configuration: provider priority, multi-exchange
specs, coverage contracts, and the U05 symbol->product mapping. Layer B reads
these constants as parameters and never re-derives them.

Portable: stdlib only. No Colab, no notebook-host paths, no secrets.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Tuple


# ---------------------------------------------------------------------------
# Coverage contract (immutable architectural constants)
# ---------------------------------------------------------------------------
TARGET_EXCHANGE_COUNT = 8
MIN_VALIDATED_EXCHANGE_COUNT = 7
# 8 is the preferred Core; 7 is the minimum acceptance threshold.
# Environment variables cannot silently change the architectural contract.

MULTI_EXCHANGE_PROBE_SYMBOL = "BTCUSDT"


# ---------------------------------------------------------------------------
# U05 symbol -> exchange product mapping (Binance-primary / Coinbase-fallback).
# ---------------------------------------------------------------------------
U05_EXCHANGE_SYMBOLS: Dict[str, str] = {
    "BTCUSDT": "BTC-USDT",
    "ETHUSDT": "ETH-USDT",
    "SOLUSDT": "SOL-USDT",
    "XRPUSDT": "XRP-USDT",
    "ADAUSDT": "ADA-USDT",
}


# ---------------------------------------------------------------------------
# Kline contracts
# ---------------------------------------------------------------------------
EXCHANGE_KLINE_INTERVAL = "5m"
EXCHANGE_KLINE_LIMIT = int(os.getenv("KITCHEN_EXCHANGE_KLINE_LIMIT", "2"))
HISTORICAL_PAGE_LIMIT = int(os.getenv("KITCHEN_HISTORICAL_PAGE_LIMIT", "300"))

_EXCHANGE_INTERVAL_MIN = int(EXCHANGE_KLINE_INTERVAL.replace("m", ""))
_EXCHANGE_GRANULARITY_SECONDS = _EXCHANGE_INTERVAL_MIN * 60


# ---------------------------------------------------------------------------
# Provider policy
# ---------------------------------------------------------------------------
PROVIDER_PRIORITY: Dict[str, List[str]] = {
    "global": ["coinmarketcap", "coingecko"],
    "exchange": [
        "binance", "okx", "bybit", "kucoin",
        "coinbase", "gate", "upbit", "bitget",
    ],
}

FORBIDDEN_RUNTIME_PROVIDERS = {
    "tradingview",
    "tradingview_reference",
    "tv",
}


# ---------------------------------------------------------------------------
# Multi-exchange specs (8 core public spot venues)
# ---------------------------------------------------------------------------
MULTI_EXCHANGE_SPECS: Dict[str, Dict[str, Any]] = {
    "binance": {
        "mode": "PUBLIC_SPOT",
        "symbol": "BTCUSDT",
        "url": "https://api.binance.com/api/v3/klines",
        "params": {
            "symbol": "BTCUSDT",
            "interval": EXCHANGE_KLINE_INTERVAL,
            "limit": EXCHANGE_KLINE_LIMIT,
        },
    },
    "okx": {
        "mode": "PUBLIC_SPOT",
        "symbol": "BTC-USDT",
        "url": "https://www.okx.com/api/v5/market/history-candles",
        "params": {
            "instId": "BTC-USDT",
            "bar": EXCHANGE_KLINE_INTERVAL,
            "limit": EXCHANGE_KLINE_LIMIT,
        },
    },
    "bybit": {
        "mode": "PUBLIC_SPOT",
        "symbol": "BTCUSDT",
        "url": "https://api.bybit.com/v5/market/kline",
        "params": {
            "category": "spot",
            "symbol": "BTCUSDT",
            "interval": _EXCHANGE_INTERVAL_MIN,
            "limit": EXCHANGE_KLINE_LIMIT,
        },
    },
    "kucoin": {
        "mode": "PUBLIC_SPOT",
        "symbol": "BTC-USDT",
        "url": "https://api.kucoin.com/api/v1/market/candles",
        "params": {
            "symbol": "BTC-USDT",
            "type": f"{_EXCHANGE_INTERVAL_MIN}min",
            "limit": EXCHANGE_KLINE_LIMIT,
        },
    },
    "coinbase": {
        "mode": "PUBLIC_SPOT",
        "symbol": "BTC-USDT",
        "url": "https://api.exchange.coinbase.com/products/BTC-USDT/candles",
        "params": {
            "granularity": _EXCHANGE_GRANULARITY_SECONDS,
        },
    },
    "gate": {
        "mode": "PUBLIC_SPOT",
        "symbol": "BTC_USDT",
        "url": "https://api.gateio.ws/api/v4/spot/candlesticks",
        "params": {
            "currency_pair_id": "BTC_USDT",
            "interval": EXCHANGE_KLINE_INTERVAL,
            "limit": EXCHANGE_KLINE_LIMIT,
        },
    },
    "upbit": {
        "mode": "PUBLIC_SPOT",
        "symbol": "USDT-BTC",
        "url": "https://api.upbit.com/v1/candles/minutes/5",
        "params": {
            "market": "USDT-BTC",
            "count": EXCHANGE_KLINE_LIMIT,
        },
    },
    "bitget": {
        "mode": "PUBLIC_SPOT",
        "symbol": "BTCUSDT",
        "url": "https://api.bitget.com/api/v2/spot/market/history-candles",
        "params": {
            "symbol": "BTCUSDT",
            "period": f"{_EXCHANGE_INTERVAL_MIN}min",
            "limit": EXCHANGE_KLINE_LIMIT,
        },
    },
}


# ---------------------------------------------------------------------------
# Order-book endpoints (8 core public spot venues, parallel probes).
# ---------------------------------------------------------------------------
ORDERBOOK_SPECS: Dict[str, Dict[str, Any]] = {
    "binance": {
        "mode": "PUBLIC_SPOT",
        "symbol": "BTCUSDT",
        "url": "https://api.binance.com/api/v3/depth",
        "params": {"symbol": "BTCUSDT", "limit": 100},
    },
    "okx": {
        "mode": "PUBLIC_SPOT",
        "symbol": "BTC-USDT",
        "url": "https://www.okx.com/api/v5/market/books",
        "params": {"instId": "BTC-USDT", "sz": 100},
    },
    "bybit": {
        "mode": "PUBLIC_SPOT",
        "symbol": "BTCUSDT",
        "url": "https://api.bybit.com/v5/market/orderbook",
        "params": {"category": "spot", "symbol": "BTCUSDT", "limit": 100},
    },
    "kucoin": {
        "mode": "PUBLIC_SPOT",
        "symbol": "BTC-USDT",
        "url": "https://api.kucoin.com/api/v1/market/orderbook/level2_100",
        "params": {"symbol": "BTC-USDT"},
    },
    "coinbase": {
        "mode": "PUBLIC_SPOT",
        "symbol": "BTC-USDT",
        "url": "https://api.exchange.coinbase.com/products/BTC-USDT/book",
        "params": {"limit": 100},
    },
    "gate": {
        "mode": "PUBLIC_SPOT",
        "symbol": "BTC_USDT",
        "url": "https://api.gateio.ws/api/v4/spot/order_book",
        "params": {"currency_pair_id": "BTC_USDT", "limit": 100},
    },
    "upbit": {
        "mode": "PUBLIC_SPOT",
        "symbol": "USDT-BTC",
        "url": "https://api.upbit.com/v1/orderbook",
        "params": {"markets": "USDT-BTC"},
    },
    "bitget": {
        "mode": "PUBLIC_SPOT",
        "symbol": "BTCUSDT",
        "url": "https://api.bitget.com/api/v2/spot/market/orderbook",
        "params": {"symbol": "BTCUSDT", "limit": 100},
    },
}