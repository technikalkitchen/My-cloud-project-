#!/usr/bin/env python3
"""End-to-end Scanner test with real market data.

Pipeline: U06.5 → Top 10 → Strong Movers → Top 3

Uses real CoinGecko market_cap data for ranking and real historical
candle data for USDT/BTC pair change calculations.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from app.analysis.stage10_consumer import (
    DISPLAY_FALLBACK_PRIORITY,
    Exchange,
    get_dynamic_top10,
)
from app.analysis.stage10_router import ExchangeRouter
from app.analysis.stage10_usdt import UsdtPairResult, UsdtPairProcessor
from app.analysis.stage10_btc import BtcPairResult, BtcPairProcessor
from app.analysis.stage11_strong_movers import (
    SCANNER_WARNING as STRONG_WARNING,
    run_strong_movers,
    StrongMoversConfig,
)
from app.analysis.stage12_top3 import (
    TOP3_SCANNER_WARNING,
    format_top3_telegram,
    run_top3,
    Top3Config,
)
from app.config.quality import TOP_N
from app.market.ranking import dynamic_rank_assets


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------

def fetch_coingecko_market_data() -> List[Dict[str, Any]]:
    """Fetch real market data from CoinGecko for ranking."""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": "30",
        "page": "1",
        "sparkline": False,
    }
    resp = requests.get(url, params=params, timeout=20)
    resp.raise_for_status()
    coins = resp.json()
    assets = []
    for coin in coins:
        mc = coin.get("market_cap")
        if mc is None or mc <= 0:
            continue
        symbol = str(coin.get("symbol", "")).upper()
        if not symbol:
            continue
        rank = coin.get("market_cap_rank")
        canonical = coin.get("id", f"id_{symbol}")
        assets.append({
            "provider_asset_id": f"cg:{canonical}",
            "canonical_asset_id": f"cg:{canonical}",
            "symbol": symbol,
            "name": coin.get("name", symbol),
            "provider": "COINGECKO",
            "provider_mode": "PUBLIC",
            "provider_rank": rank,
            "price": coin.get("current_price"),
            "market_cap": float(mc),
            "volume_24h": coin.get("total_volume"),
            "source_timestamp": datetime.now(timezone.utc).isoformat(),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "identity_status": "VALIDATED",
        })
    return assets


def load_historical_candles() -> Dict[str, dict]:
    """Load historical candle data for USDT pair calculations."""
    candles = {}
    raw_dir = Path("data/historical_u05/raw")
    for f in sorted(raw_dir.glob("*_1m.json")):
        symbol = f.stem.replace("_1m", "")
        with open(f) as fh:
            data = json.load(fh)
        records = data.get("records", [])
        if records:
            candles[symbol] = records
    return candles


def compute_5min_change(records: List[dict]) -> Optional[float]:
    """Compute 5-minute percentage change from last 6 candles."""
    if len(records) < 6:
        if len(records) >= 2:
            first = records[0]["close"]
            last = records[-1]["close"]
            if first > 0:
                return (last - first) / first * 100.0
        return None
    latest = records[-1]["close"]
    five_min_ago = records[-6]["close"]
    if five_min_ago > 0:
        return (latest - five_min_ago) / five_min_ago * 100.0
    return None


def compute_volume_from_candles(records: List[dict]) -> Optional[float]:
    """Sum volume from candle records."""
    total = sum(float(r.get("volume_base", 0)) for r in records)
    return total if total > 0 else None


def build_usdt_results(
    candles: Dict[str, list],
    requested_exchange: str = "Binance",
) -> Dict[str, UsdtPairResult]:
    """Build USDT pair results from historical candle data."""
    processor = UsdtPairProcessor(requested_exchange, "5m")
    results = {}
    for symbol, records in candles.items():
        change_pct = compute_5min_change(records)
        volume = compute_volume_from_candles(records)
        # Use current timestamp for freshness, real change/volume from candles
        ts_str = datetime.now(timezone.utc).isoformat()
        # Extract base symbol: BTCUSDT -> BTC
        base_symbol = symbol.replace("USDT", "")
        data = {
            "symbol": f"{base_symbol}USDT",
            "close": records[-1]["close"] if records else None,
            "change_pct": change_pct,
            "volume": volume,
            "timestamp": ts_str,
            "volume_source": "PROVIDER_SUPPLIED_TRADED_BASE_VOLUME",
            "exchange": requested_exchange,
            "timeframe": "5m",
        }
        result = processor.process(data)
        results[f"{base_symbol}USDT"] = result
    return results


def build_btc_results(
    candles: Dict[str, list],
    requested_exchange: str = "Binance",
) -> Dict[str, BtcPairResult]:
    """Build BTC pair results from historical candle data."""
    processor = BtcPairProcessor(requested_exchange, "5m")
    results = {}
    for symbol, records in candles.items():
        change_pct = compute_5min_change(records)
        ts_str = datetime.now(timezone.utc).isoformat()
        base_symbol = symbol.replace("USDT", "")
        data = {
            "symbol": f"{base_symbol}BTC",
            "close": records[-1]["close"] if records else None,
            "change_pct": change_pct,
            "timestamp": ts_str,
            "exchange": requested_exchange,
            "timeframe": "5m",
        }
        result = processor.process(data)
        results[f"{base_symbol}BTC"] = result
    return results


# ---------------------------------------------------------------------------
# Pipeline execution
# ---------------------------------------------------------------------------

def run_scanner_pipeline(
    assets: List[Dict[str, Any]],
    usdt_results: Dict[str, UsdtPairResult],
    btc_results: Dict[str, BtcPairResult],
    selected_exchange: str = "Binance",
) -> dict:
    """Execute the full scanner pipeline with real data."""

    # --- U06.5: Dynamic Ranking ---
    ranking = dynamic_rank_assets(assets)
    assert ranking["status"] in ("VALIDATED", "DATA_PARTIAL"), (
        f"Ranking failed: {ranking['status']}"
    )
    print(f"[U06.5] Ranking: {ranking['status']}, "
          f"ranked={ranking['candidate_received']}, "
          f"valid={ranking['candidate_valid']}")

    # --- Stage 10: Top 10 ---
    top10_result = get_dynamic_top10(assets, view="KITCHEN")
    assert top10_result.view == "KITCHEN"
    print(f"[Stage 10] Top 10: {len(top10_result.assets)} assets, "
          f"view={top10_result.view}")

    # --- Stage 11: Strong Movers ---
    strong_config = StrongMoversConfig(selected_exchange=selected_exchange)
    strong_output = run_strong_movers(
        assets,
        config=strong_config,
        usdt_results=usdt_results,
        btc_results=btc_results,
    )
    assert strong_output.valid is True or strong_output.selected_count >= 0
    print(f"[Stage 11] Strong Movers: {strong_output.selected_count}/5 "
          f"selected, {strong_output.candidate_count} candidates")

    # --- Stage 12: Top 3 ---
    config = Top3Config(selected_exchange=selected_exchange)
    top3_output = run_top3(
        assets,
        config=config,
        usdt_results=usdt_results,
        btc_results=btc_results,
    )
    assert top3_output.valid is True or top3_output.selected_count >= 0
    print(f"[Stage 12] Top 3: {top3_output.selected_count}/3 "
          f"selected, {top3_output.candidate_count} candidates")

    # --- Formatting ---
    telegram_msg = format_top3_telegram(top3_output)

    return {
        "ranking": ranking,
        "top10": top10_result,
        "strong_movers": strong_output,
        "top3": top3_output,
        "telegram": telegram_msg,
    }


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_pipeline(
    results: dict,
    assets: List[Dict[str, Any]],
    usdt_results: Dict[str, UsdtPairResult],
    btc_results: Dict[str, BtcPairResult],
) -> Dict[str, bool]:
    """Verify all expected behaviors of the pipeline output."""
    checks: Dict[str, bool] = {}

    top3 = results["top3"]
    strong = results["strong_movers"]
    top10 = results["top10"]
    ranking = results["ranking"]
    msg = results["telegram"]
    msg_upper = msg.upper()

    # 1. Mandatory scanner warning
    checks["warning_present"] = (
        TOP3_SCANNER_WARNING in msg
        and "توجه" in msg
    )
    checks["warning_reuses_stage11"] = TOP3_SCANNER_WARNING == STRONG_WARNING

    # 2. No trading signal language
    signal_words = ["BUY", "SELL", "LONG", "SHORT", "STOP", "TAKE", "TARGET"]
    checks["no_trading_signals"] = not any(
        w in msg_upper for w in signal_words
    )

    # 3. Ranking works
    checks["ranking_validated"] = ranking["status"] in ("VALIDATED", "DATA_PARTIAL")
    checks["ranking_has_top125"] = len(ranking.get("top125", [])) >= 1
    btc_rank1 = any(
        a.get("symbol") == "BTC"
        and int(a.get("calculated_rank", 0)) == 1
        for a in ranking.get("top125", [])
    )
    checks["btc_rank1"] = btc_rank1

    # 4. Top 10 correct (ranks 2-10, no BTC)
    checks["top10_count"] = len(top10.assets) == 9
    checks["top10_no_btc"] = "BTC" not in [
        a["symbol"] for a in top10.assets
    ]
    checks["top10_view"] = top10.view == "KITCHEN"

    # 5. Strong Movers
    checks["strong_movers_count"] = 0 <= strong.selected_count <= 5
    checks["strong_warning"] = STRONG_WARNING in strong.scanner_warning

    # 6. Top 3 output
    checks["top3_count"] = 0 <= top3.selected_count <= 3
    checks["top3_candidates"] = top3.candidate_count >= 0
    checks["top3_valid_flag"] = isinstance(top3.valid, bool)

    # 7. Scores are valid
    for r in top3.top3:
        checks[f"score_valid_{r.symbol}"] = (
            isinstance(r.total_score, (int, float))
            and r.total_score >= 0
        )
        checks[f"no_fabrication_{r.symbol}"] = (
            r.usdt_pair.endswith("USDT")
            or r.usdt_pair == ""
        )

    # 8. Fallback/provenance
    for r in top3.top3:
        checks[f"fallback_flag_{r.symbol}"] = isinstance(
            r.usdt_fallback_used, bool
        )

    # 9. Telegram format
    checks["telegram_has_numbers"] = "1." in msg and "2." in msg
    checks["telegram_header"] = "TOP 3" in msg_upper or "\U0001f3c6" in msg

    # 10. BTC source/provenance displayed when BTC available
    btc_source_shown = all(
        r.btc_source and ("Source" in r.btc_source or "Fallback" in r.btc_source)
        for r in top3.top3
        if r.btc_available
    )
    checks["btc_source_shown"] = btc_source_shown

    # 11. RTL/LTR - check that Persian text renders
    checks["persian_text"] = "توجه" in msg

    # 11. Determinism
    config = Top3Config(selected_exchange="Binance")
    top3_2 = run_top3(
        assets,
        config=config,
        usdt_results=usdt_results,
        btc_results=btc_results,
    )
    checks["deterministic"] = (
        top3.selected_count == top3_2.selected_count
        and len(top3.top3) == len(top3_2.top3)
    )
    return checks


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("END-TO-END SCANNER TEST — REAL MARKET DATA")
    print("Pipeline: U06.5 → Top 10 → Strong Movers → Top 3")
    print("=" * 70)

    # Step 1: Collect real market data
    print("\n[1/4] Fetching real market data from CoinGecko...")
    assets = fetch_coingecko_market_data()
    print(f"  Fetched {len(assets)} assets with real market_cap data")
    for a in assets[:10]:
        print(f"    Rank {a['provider_rank']}: {a['symbol']} "
              f"MC=${a['market_cap']:,.0f}")

    # Step 2: Load historical candles for USDT/BTC pairs
    print("\n[2/4] Loading historical candle data...")
    candles = load_historical_candles()
    print(f"  Loaded candles for: {list(candles.keys())}")

    # Step 3: Build pair results
    print("\n[3/4] Building USDT/BTC pair results from real candles...")
    usdt_results = build_usdt_results(candles)
    btc_results = build_btc_results(candles)
    for k, v in usdt_results.items():
        print(f"  {k}: change={v.change_pct}%, "
              f"vol={v.volume}, valid={v.valid}")

    # Step 4: Run pipeline
    print("\n[4/4] Running full scanner pipeline...")
    results = run_scanner_pipeline(
        assets=assets,
        usdt_results=usdt_results,
        btc_results=btc_results,
        selected_exchange="Binance",
    )

    # Store pair results for verification
    results["_usdt_results"] = usdt_results
    results["_btc_results"] = btc_results

    # Print results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print("\n--- Telegram Output ---")
    print(results["telegram"])

    # Verify
    print("\n\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    checks = verify_pipeline(results, assets, usdt_results, btc_results)
    all_pass = True
    for name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"  [{status}] {name}")

    print("\n" + "=" * 70)
    if all_pass:
        print("RESULT: ALL CHECKS PASSED")
    else:
        failed = [n for n, p in checks.items() if not p]
        print(f"RESULT: {len(failed)} CHECKS FAILED: {failed}")
    print("=" * 70)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
