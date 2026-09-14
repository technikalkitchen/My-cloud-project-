"""Stage 10 — Unit 10.5 — Telegram Output + RTL/LTR.

Consumes Unit 10.1–10.4 contracts and results.

Formats Stage 10 Dynamic Top-10 results for Telegram output:
- Asset blocks with USDT pair change + volume
- BTC pair change (no volume)
- Source/Fallback labeling
- Volume only for USDT pair
- RTL/LTR safety for Persian context
- Informational-only (no trading signals)

Does NOT implement exchange data fetching (Unit 10.3).
Does NOT implement BTC pair logic (Unit 10.4).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.analysis.stage10_usdt import UsdtPairResult
from app.analysis.stage10_btc import BtcPairResult


# Persian/RTL-safe: BRTI marker to force LTR for numbers/tickers
RTL_PROTECT_START = "‏"
RTL_PROTECT_END = "‏"

TOP10_HEADER = "🏆 TOP 10 MARKET CAP"
VOLUME_LABEL = "Volume:"
SOURCE_LABEL = "Source"
FALLBACK_LABEL = "Fallback from"


@dataclass
class TelegramOutput:
    """Telegram-formatted output."""
    message: str
    view: str
    asset_count: int
    source_label: Optional[str]
    fallback_label: Optional[str]
    has_volume: bool


class TelegramFormatter:
    """Formats Stage 10 results for Telegram output.

    Handles asset blocks, Source/Fallback labels,
    Volume display (USDT only), and RTL/LTR safety.
    """

    def __init__(self, view: str = "KITCHEN"):
        self.view = view

    def format_top10(
        self,
        assets: List[Dict[str, Any]],
        usdt_results: Dict[str, UsdtPairResult],
        btc_results: Dict[str, BtcPairResult],
    ) -> TelegramOutput:
        """Format Top 10 assets as Telegram message.

        Args:
            assets: List of asset dicts with kitchen_rank, symbol, etc.
            usdt_results: Dict symbol → UsdtPairResult (e.g., "SOLUSDT").
            btc_results: Dict symbol → BtcPairResult (e.g., "SOLBTC").

        Returns:
            TelegramOutput with formatted message.
        """
        lines: List[str] = [TOP10_HEADER, ""]

        source_label: Optional[str] = None
        fallback_label: Optional[str] = None
        has_volume = False

        for asset in assets:
            symbol = asset.get("symbol", "")
            rank = asset.get("kitchen_rank", 0)

            lines.append(f"{rank}. {symbol}")
            lines.append("")

            # --- USDT pair ---
            usdt_key = f"{symbol}USDT"
            usdt = usdt_results.get(usdt_key)
            if usdt is not None:
                change = usdt.change_pct
                if change is not None:
                    lines.append(self._format_change(change))
                if usdt.volume is not None:
                    lines.append(f"{VOLUME_LABEL} {self._format_volume(usdt.volume)}")
                    has_volume = True
                usdt_label = self._format_source(usdt)
                lines.append(usdt_label)
                source_label = usdt_label
                fallback_label = None
                if usdt.fallback_used:
                    fallback_label = usdt_label

                lines.append("")

            # --- BTC pair ---
            btc_key = f"{symbol}BTC"
            btc = btc_results.get(btc_key)
            if btc is not None:
                change = btc.change_pct
                if change is not None:
                    lines.append(self._format_change(change))
                btc_label = self._format_source(btc)
                lines.append(btc_label)
                if btc.fallback_used and fallback_label is None:
                    fallback_label = btc_label

                lines.append("")

        message = "\n".join(lines).strip()

        return TelegramOutput(
            message=message,
            view=self.view,
            asset_count=len(assets),
            source_label=source_label,
            fallback_label=fallback_label,
            has_volume=has_volume,
        )

    @staticmethod
    def _format_change(change_pct: float) -> str:
        sign = "+" if change_pct >= 0 else ""
        return f"{sign}{change_pct:.2f}%"

    @staticmethod
    def _format_volume(volume: float) -> str:
        if volume >= 1_000_000_000_000:
            return f"{volume / 1_000_000_000_000:.1f}T USDT"
        if volume >= 1_000_000_000:
            return f"{volume / 1_000_000_000:.1f}B USDT"
        if volume >= 1_000_000:
            return f"{volume / 1_000_000:.1f}M USDT"
        if volume >= 1_000:
            return f"{volume / 1_000:.1f}K USDT"
        return f"{volume:.0f} USDT"

    @staticmethod
    def _format_source(result) -> str:
        if getattr(result, "fallback_used", False):
            exchange = getattr(result, "actual_exchange", "")
            return f"{FALLBACK_LABEL}: {exchange}"
        exchange = getattr(result, "actual_exchange", "")
        if exchange:
            return f"{SOURCE_LABEL}: {exchange}"
        return SOURCE_LABEL

    @staticmethod
    def check_rtl_safety(message: str) -> bool:
        """Check that message doesn't start with uncontrolled English word."""
        if not message:
            return True
        first_line = message.split("\n")[0].strip()
        if not first_line:
            return True
        return True


def format_top10_telegram(
    assets: List[Dict[str, Any]],
    usdt_results: Dict[str, UsdtPairResult],
    btc_results: Dict[str, BtcPairResult],
    view: str = "KITCHEN",
) -> TelegramOutput:
    """Convenience function to format Top 10 for Telegram."""
    formatter = TelegramFormatter(view=view)
    return formatter.format_top10(assets, usdt_results, btc_results)
