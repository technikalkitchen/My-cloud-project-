#!/usr/bin/env python3
"""
TEST003 — Kitchen Origin Check (2017)
Checks if Binance, Coinbase, and Bitstamp have historical data in 2017.
"""
import requests
import time
from datetime import datetime, timezone

USER_AGENT = "KitchenAssistantBot-TEST003/1.0"

def print_result(exchange, symbol, data_found, details):
    status = "✅ FOUND" if data_found else "❌ NOT FOUND"
    print(f"[{exchange}] {symbol}: {status} | {details}")

def check_binance():
    print("\n--- Checking Binance (BTC/USDT) ---")
    url = "https://data-api.binance.vision/api/v3/klines"
    # August 17, 2017 (Timestamp in ms)
    params = {"symbol": "BTCUSDT", "interval": "1d", "startTime": 1502928000000, "limit": 3}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=10)
        res.raise_for_status()
        data = res.json()
        if data and len(data) > 0:
            oldest_ts = min(row[0] for row in data)
            first_ts = datetime.fromtimestamp(oldest_ts/1000, tz=timezone.utc).isoformat()
            print_result("Binance", "BTC/USDT", True, f"Oldest candle found: {first_ts}")
        else:
            print_result("Binance", "BTC/USDT", False, "Empty response")
    except Exception as e:
        print_result("Binance", "BTC/USDT", False, f"Error: {e}")

def check_bitstamp():
    print("\n--- Checking Bitstamp (BTC/USD) ---")
    # August 1, 2017 (Timestamp in seconds)
    url = "https://www.bitstamp.net/api/v2/ohlc/btcusd/"
    params = {"step": 86400, "start": 1501545600, "limit": 3}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=10)
        res.raise_for_status()
        data = res.json().get("data", {}).get("ohlc", [])
        if data and len(data) > 0:
            oldest_ts = min(int(row["timestamp"]) for row in data)
            first_ts = datetime.fromtimestamp(oldest_ts, tz=timezone.utc).isoformat()
            print_result("Bitstamp", "BTC/USD", True, f"Oldest candle found: {first_ts}")
        else:
            print_result("Bitstamp", "BTC/USD", False, "Empty response")
    except Exception as e:
        print_result("Bitstamp", "BTC/USD", False, f"Error: {e}")

def check_coinbase():
    print("\n--- Checking Coinbase (BTC/USD) ---")
    url = "https://api.exchange.coinbase.com/products/BTC-USD/candles"
    # Aug 1 to Aug 5, 2017 (ISO 8601)
    params = {"granularity": 86400, "start": "2017-08-01T00:00:00Z", "end": "2017-08-05T00:00:00Z"}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=10)
        res.raise_for_status()
        data = res.json()
        if data and len(data) > 0:
            oldest_ts = min(row[0] for row in data) # Coinbase returns descending order
            first_ts = datetime.fromtimestamp(oldest_ts, tz=timezone.utc).isoformat()
            print_result("Coinbase", "BTC/USD", True, f"Oldest candle found: {first_ts}")
        else:
            print_result("Coinbase", "BTC/USD", False, "Empty response")
    except Exception as e:
        print_result("Coinbase", "BTC/USD", False, f"Error: {e}")

if __name__ == "__main__":
    print("Starting TEST003 — Kitchen Origin Check (2017)...")
    check_binance()
    time.sleep(1)
    check_bitstamp()
    time.sleep(1)
    check_coinbase()
    print("\nTEST003 Complete.")
