"""Stage 10 — Unit 10.3 — USDT Pair + Volume.

Consumes Unit 10.1 (Exchange, DISPLAY_FALLBACK_PRIORITY) and
Unit 10.2 (ExchangeRouter) contracts.

Processes USDT pair data from exchanges with:
- Symbol identity validation
- Provider-supplied volume (not fabricated)
- Freshness / staleness check
- Timeframe enforcement
- Source/Fallback presentation
- Per-field provenance tracking

Does NOT implement BTC pair logic (Unit 10.4).
Does NOT implement exchange data fetching (Unit 10.3 processes
exchange data, does not acquire it).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.analysis.stage10_consumer import Exchange, DISPLAY_FALLBACK_PRIORITY
from app.analysis.stage10_router import ExchangeRouter
from app.config.quality import FRESHNESS_THRESHOLD_SECONDS
from app.core.u06_5 import safe_float, utc_now

VALID_VOLUME_SOURCE = "PROVIDER_SUPPLIED_TRADED_BASE_VOLUME"


@dataclass
class UsdtPairResult:
    """Validated USDT pair result with Source/Fallback and provenance."""

    symbol: str
    change_pct: Optional[float]
    volume: Optional[float]
    timestamp: Optional[str]
    requested_exchange: str
    actual_exchange: str
    fallback_used: bool
    fallback_exchange: Optional[str]
    timeframe: str
    volume_source_label: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    provenance: Dict[str, str] = field(default_factory=dict)


def _source_label(requested: str, actual: str) -> str:
    if requested == actual:
        return f"Source: {requested}"
    return f"Fallback from: {actual}"


class UsdtPairProcessor:
    """Processes USDT pair data from exchanges.

    Validates symbol, price, volume, timestamp, and timeframe.
    Tracks per-field provenance and Source/Fallback labeling.
    """

    def __init__(
        self,
        requested_exchange: str,
        timeframe: str = "5m",
    ):
        self.requested_exchange = requested_exchange
        self.timeframe = timeframe
        self._router = ExchangeRouter(self.requested_exchange)

    def process(self, data: Dict[str, Any]) -> UsdtPairResult:
        """Process USDT pair data from an exchange.

        Args:
            data: Exchange response data with keys:
                symbol, close, change_pct, volume, timestamp,
                volume_source, exchange, timeframe

        Returns:
            UsdtPairResult with validation and provenance.
        """
        if not isinstance(data, dict) or data is None:
            return UsdtPairResult(
                symbol="",
                change_pct=None,
                volume=None,
                timestamp=None,
                requested_exchange=self.requested_exchange,
                actual_exchange="",
                fallback_used=False,
                fallback_exchange=None,
                timeframe=self.timeframe,
                volume_source_label="",
                valid=False,
                errors=["No exchange data provided"],
                provenance={},
            )

        actual_exchange = str(
            data.get("exchange") or self.requested_exchange
        )
        fallback_used = actual_exchange != self.requested_exchange
        fallback_exchange = None
        if fallback_used:
            valid_direction, _ = self._router.validate_fallback_direction(
                self.requested_exchange, actual_exchange
            )
            if not valid_direction:
                fallback_exchange = None
            else:
                fallback_exchange = actual_exchange

        symbol = str(data.get("symbol") or "")
        change_pct = safe_float(data.get("change_pct"))
        volume = safe_float(data.get("volume"))
        timestamp = str(data.get("timestamp") or "")
        data_timeframe = str(data.get("timeframe") or "")
        volume_source = str(data.get("volume_source") or "")

        errors: List[str] = []
        provenance: Dict[str, str] = {}

        # --- Symbol validation ---
        if not symbol.endswith("USDT"):
            errors.append(f"Invalid USDT pair symbol: {symbol}")
        provenance["symbol"] = actual_exchange

        # --- Change validation ---
        if change_pct is None:
            errors.append("change_pct is missing or invalid")
        elif not math.isfinite(change_pct):
            errors.append("change_pct is not finite")
        provenance["change_pct"] = actual_exchange

        # --- Volume validation ---
        if volume is None:
            errors.append("volume is missing or invalid")
        elif not math.isfinite(volume):
            errors.append("volume is not finite")
        elif volume < 0:
            errors.append("volume is negative")
        if volume_source != VALID_VOLUME_SOURCE:
            errors.append(
                f"volume_source is not {VALID_VOLUME_SOURCE}: "
                f"got {volume_source!r}"
            )
        provenance["volume"] = actual_exchange

        # --- Timestamp validation ---
        if not timestamp:
            errors.append("timestamp is missing")
        else:
            timestamp_valid = self._is_fresh(timestamp)
            if not timestamp_valid:
                errors.append("timestamp is stale")
        provenance["timestamp"] = actual_exchange

        # --- Timeframe validation ---
        if not data_timeframe:
            errors.append("timeframe is missing")
        elif data_timeframe != self.timeframe:
            errors.append(
                f"timeframe mismatch: requested {self.timeframe}, "
                f"got {data_timeframe}"
            )
        provenance["timeframe"] = actual_exchange

        # --- Fallback direction validation ---
        if fallback_used:
            valid_dir, dir_error = self._router.validate_fallback_direction(
                self.requested_exchange, actual_exchange
            )
            if not valid_dir:
                errors.append(dir_error)
                fallback_exchange = None

        # --- Zero volume check ---
        if volume is not None and volume == 0.0:
            errors.append("volume is zero")

        valid = len(errors) == 0

        return UsdtPairResult(
            symbol=symbol,
            change_pct=change_pct,
            volume=volume,
            timestamp=timestamp,
            requested_exchange=self.requested_exchange,
            actual_exchange=actual_exchange,
            fallback_used=fallback_used,
            fallback_exchange=fallback_exchange,
            timeframe=self.timeframe,
            volume_source_label=_source_label(
                self.requested_exchange, actual_exchange
            ),
            valid=valid,
            errors=errors,
            provenance=provenance,
        )

    def _is_fresh(self, timestamp: str) -> bool:
        try:
            dt = datetime.fromisoformat(timestamp)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            age = (now - dt).total_seconds()
            return age <= FRESHNESS_THRESHOLD_SECONDS
        except Exception:
            return False


def process_usdt_pair(
    data: Dict[str, Any],
    requested_exchange: str,
    timeframe: str = "5m",
) -> UsdtPairResult:
    """Convenience function to process USDT pair data."""
    processor = UsdtPairProcessor(
        requested_exchange=requested_exchange,
        timeframe=timeframe,
    )
    return processor.process(data)
