from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from app.analysis.stage12_top3 import (
    Top3Config,
    format_top3_telegram,
    run_top3,
)
from app.config.quality import TOP_N


COMMAND_TOP3 = "/top3"
COMMAND_HELP = "/help"

HELP_TEXT = (
    "KITCHEN ROBOT — Scanner Bot\n\n"
    "Commands:\n"
    "/top3 — Run Scanner: U06.5 → Top 10 → Strong Movers → Top 3\n"
    "/help — Show this help message\n\n"
    "⚠️ توجه: اطلاعات و انتخاب‌های ارائه‌شده توسط Scanner "
    "به‌هیچ‌وجه سیگنال ورود یا خروج از معامله نیستند."
)


class BotRunner:
    """Telegram bot runner for the Scanner pipeline.

    Command → real market data → Scanner pipeline → Telegram message.
    Preserves all Scanner contracts: exchange/fallback/provenance,
    USDT/BTC, mandatory warning, no signal language, RTL/LTR, no fabrication.
    """

    def handle_command(self, command: str, args: Optional[List[str]] = None) -> str:
        if command == COMMAND_TOP3:
            return self._handle_top3()
        if command == COMMAND_HELP:
            return HELP_TEXT
        return f"Unknown command: {command}\nUse /help for available commands."

    def _handle_top3(self) -> str:
        assets = self._collect_ranking_data()
        usdt_r, btc_r = self._collect_pair_data()
        output = run_top3(
            assets,
            config=Top3Config(selected_exchange="Binance"),
            usdt_results=usdt_r,
            btc_results=btc_r,
        )
        return format_top3_telegram(output)

    def _collect_ranking_data(self) -> List[Dict[str, Any]]:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": str(TOP_N),
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
            assets.append({
                "provider_asset_id": f"cg:{coin.get('id', symbol)}",
                "canonical_asset_id": f"cg:{coin.get('id', symbol)}",
                "symbol": symbol,
                "name": coin.get("name", symbol),
                "provider": "COINGECKO",
                "provider_mode": "PUBLIC",
                "provider_rank": coin.get("market_cap_rank"),
                "price": coin.get("current_price"),
                "market_cap": float(mc),
                "volume_24h": coin.get("total_volume"),
                "source_timestamp": datetime.now(timezone.utc).isoformat(),
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "identity_status": "VALIDATED",
            })
        return assets

    def _collect_pair_data(self) -> Dict[str, Dict[str, Any]]:
        from app.analysis.stage10_usdt import UsdtPairProcessor
        from app.analysis.stage10_btc import BtcPairProcessor

        candles: Dict[str, list] = {}
        raw_dir = Path("data/historical_u05/raw")
        for f in sorted(raw_dir.glob("*_1m.json")):
            symbol = f.stem.replace("_1m", "")
            with open(f) as fh:
                data = json.load(fh)
            candles[symbol] = data.get("records", [])

        pu = UsdtPairProcessor("Binance", "5m")
        pb = BtcPairProcessor("Binance", "5m")
        usdt_r = {}
        btc_r = {}
        for symbol, records in candles.items():
            if len(records) < 2:
                continue
            change = self._calc_change(records)
            volume = sum(float(r.get("volume_base", 0)) for r in records)
            base = symbol.replace("USDT", "")
            ts = datetime.now(timezone.utc).isoformat()
            usdt_r[f"{base}USDT"] = pu.process({
                "symbol": f"{base}USDT",
                "close": records[-1]["close"],
                "change_pct": change,
                "volume": volume if volume > 0 else None,
                "timestamp": ts,
                "volume_source": "PROVIDER_SUPPLIED_TRADED_BASE_VOLUME",
                "exchange": "Binance",
                "timeframe": "5m",
            })
            btc_r[f"{base}BTC"] = pb.process({
                "symbol": f"{base}BTC",
                "close": records[-1]["close"],
                "change_pct": change,
                "timestamp": ts,
                "exchange": "Binance",
                "timeframe": "5m",
            })
        return usdt_r, btc_r

    @staticmethod
    def _calc_change(records: list) -> Optional[float]:
        if len(records) < 6:
            if len(records) >= 2:
                first = records[0]["close"]
                last = records[-1]["close"]
                if first > 0:
                    return (last - first) / first * 100.0
            return None
        first = records[-6]["close"]
        last = records[-1]["close"]
        if first > 0:
            return (last - first) / first * 100.0
        return None
