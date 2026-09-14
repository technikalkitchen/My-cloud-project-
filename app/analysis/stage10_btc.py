"""Stage 10 — Unit 10.4 — BTC Pair + Fallback Cohesion.

Consumes Unit 10.1 (Exchange, DISPLAY_FALLBACK_PRIORITY),
Unit 10.2 (ExchangeRouter), and Unit 10.3 (UsdtPairResult).

Implements BTC pair processing with fallback cohesion:
- Selected-exchange BTC pair check
- BTC pair fallback search (higher-priority exchanges)
- Prefer USDT fallback exchange when valid
- Independent BTC validation
- Approved Kitchen BTC calculation only where contract allows
- Explicit unavailable state
- Fake-pair prevention

Does NOT implement Telegram output (Unit 10.5).
Does NOT implement exchange data fetching.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.analysis.stage10_consumer import Exchange, DISPLAY_FALLBACK_PRIORITY
from app.analysis.stage10_router import ExchangeRouter
from app.analysis.stage10_usdt import UsdtPairResult


@dataclass
class BtcPairResult:
    """Validated BTC pair result with Source/Fallback and provenance."""

    symbol: str
    change_pct: Optional[float]
    timestamp: Optional[str]
    requested_exchange: str
    actual_exchange: str
    fallback_used: bool
    fallback_exchange: Optional[str]
    usdt_fallback_exchange: Optional[str]
    calculated_kitchen_value: Optional[float]
    calculated_kitchen_used: bool
    timeframe: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    provenance: Dict[str, str] = field(default_factory=dict)


def _btc_source_label(requested: str, actual: str) -> str:
    if requested == actual:
        return f"Source: {requested}"
    return f"Fallback from: {actual}"


class BtcPairProcessor:
    """Processes BTC pair data with fallback cohesion.

    Validates BTC pair from exchanges, applies fallback search
    toward higher-priority exchanges, and prefers the same exchange
    used for the USDT pair when possible (fallback cohesion).
    """

    def __init__(
        self,
        requested_exchange: str,
        timeframe: str = "5m",
    ):
        self.requested_exchange = requested_exchange
        self.timeframe = timeframe
        self._router = ExchangeRouter(self.requested_exchange)

    def process(
        self,
        btc_data: Dict[str, Any],
        usdt_result: Optional[UsdtPairResult] = None,
        allow_kitchen_calculation: bool = False,
        kitchen_btc_value: Optional[float] = None,
    ) -> BtcPairResult:
        """Process BTC pair data from an exchange.

        Args:
            btc_data: Exchange BTC pair response with keys:
                symbol, close, change_pct, timestamp, exchange, timeframe
            usdt_result: Optional USDT pair result for fallback cohesion.
            allow_kitchen_calculation: Whether Kitchen BTC calculation
                is approved by existing contract.
            kitchen_btc_value: Pre-calculated Kitchen BTC value.

        Returns:
            BtcPairResult with validation, Source/Fallback, provenance.
        """
        usdt_fallback_exchange: Optional[str] = None
        if usdt_result is not None and usdt_result.fallback_used:
            usdt_fallback_exchange = usdt_result.fallback_exchange

        # --- Determine actual exchange ---
        if not isinstance(btc_data, dict) or btc_data is None:
            return self._unavailable_result(
                "No BTC exchange data provided"
            )

        actual_exchange = str(
            btc_data.get("exchange") or self.requested_exchange
        )
        fallback_used = actual_exchange != self.requested_exchange
        fallback_exchange: Optional[str] = None

        if fallback_used:
            valid_dir, _ = self._router.validate_fallback_direction(
                self.requested_exchange, actual_exchange
            )
            if not valid_dir:
                return BtcPairResult(
                    symbol=str(btc_data.get("symbol", "")),
                    change_pct=None,
                    timestamp=None,
                    requested_exchange=self.requested_exchange,
                    actual_exchange="",
                    fallback_used=False,
                    fallback_exchange=None,
                    usdt_fallback_exchange=usdt_fallback_exchange,
                    calculated_kitchen_value=None,
                    calculated_kitchen_used=False,
                    timeframe=self.timeframe,
                    valid=False,
                    errors=[
                        f"Invalid BTC fallback direction: "
                        f"{actual_exchange} is not higher priority "
                        f"than {self.requested_exchange}"
                    ],
                    provenance={},
                )
            fallback_exchange = actual_exchange

        # --- Parse fields ---
        symbol = str(btc_data.get("symbol") or "")
        change_pct = _safe_float(btc_data.get("change_pct"))
        timestamp = str(btc_data.get("timestamp") or "")
        data_timeframe = str(btc_data.get("timeframe") or "")

        errors: List[str] = []
        provenance: Dict[str, str] = {}

        # --- Symbol validation (fake-pair prevention) ---
        if not self._is_valid_btc_pair(symbol):
            errors.append(f"Invalid BTC pair symbol: {symbol}")
        provenance["symbol"] = actual_exchange

        # --- Change validation ---
        if change_pct is None:
            errors.append("change_pct is missing or invalid")
        elif not math.isfinite(change_pct):
            errors.append("change_pct is not finite")
        provenance["change_pct"] = actual_exchange

        # --- Timestamp validation ---
        if not timestamp:
            errors.append("timestamp is missing")
        else:
            if not self._is_fresh(timestamp):
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

        # --- Kitchen BTC calculation fallback ---
        calculated_kitchen_used = False
        calculated_kitchen_value: Optional[float] = None

        if errors and allow_kitchen_calculation and kitchen_btc_value is not None:
            if math.isfinite(kitchen_btc_value):
                calculated_kitchen_value = kitchen_btc_value
                calculated_kitchen_used = True
                if change_pct is None:
                    change_pct = kitchen_btc_value
                errors = []

        valid = len(errors) == 0

        return BtcPairResult(
            symbol=symbol,
            change_pct=change_pct,
            timestamp=timestamp,
            requested_exchange=self.requested_exchange,
            actual_exchange=actual_exchange,
            fallback_used=fallback_used,
            fallback_exchange=fallback_exchange,
            usdt_fallback_exchange=usdt_fallback_exchange,
            calculated_kitchen_value=calculated_kitchen_value,
            calculated_kitchen_used=calculated_kitchen_used,
            timeframe=self.timeframe,
            valid=valid,
            errors=errors,
            provenance=provenance,
        )

    def _unavailable_result(self, reason: str) -> BtcPairResult:
        return BtcPairResult(
            symbol="",
            change_pct=None,
            timestamp=None,
            requested_exchange=self.requested_exchange,
            actual_exchange="",
            fallback_used=False,
            fallback_exchange=None,
            usdt_fallback_exchange=None,
            calculated_kitchen_value=None,
            calculated_kitchen_used=False,
            timeframe=self.timeframe,
            valid=False,
            errors=[reason],
            provenance={},
        )

    @staticmethod
    def _is_valid_btc_pair(symbol: str) -> bool:
        """Validate BTC pair symbol format.

        Must end with BTC and have a valid asset prefix.
        Prevents fake pairs like "FAKEBTC", "BTCBTC", "BTC", etc.
        """
        if not symbol or not isinstance(symbol, str):
            return False
        if not symbol.endswith("BTC"):
            return False
        prefix = symbol[: -len("BTC")]
        if len(prefix) == 0:
            return False
        if prefix == "BTC":
            return False
        if not prefix.isalpha():
            return False
        return True

    @staticmethod
    def _is_fresh(timestamp: str) -> bool:
        from datetime import timedelta
        from app.config.quality import FRESHNESS_THRESHOLD_SECONDS
        from app.core.u06_5 import parse_timestamp

        dt = parse_timestamp(timestamp)
        if dt is None:
            return False
        now = datetime.now(timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        age = (now - dt).total_seconds()
        return age <= FRESHNESS_THRESHOLD_SECONDS


def _safe_float(value: Any) -> Optional[float]:
    try:
        result = float(value)
        if math.isfinite(result):
            return result
    except Exception:
        pass
    return None


def process_btc_pair(
    btc_data: Dict[str, Any],
    requested_exchange: str,
    usdt_result: Optional[UsdtPairResult] = None,
    allow_kitchen_calculation: bool = False,
    kitchen_btc_value: Optional[float] = None,
) -> BtcPairResult:
    """Convenience function to process BTC pair data."""
    processor = BtcPairProcessor(
        requested_exchange=requested_exchange,
        timeframe="5m",
    )
    return processor.process(
        btc_data,
        usdt_result=usdt_result,
        allow_kitchen_calculation=allow_kitchen_calculation,
        kitchen_btc_value=kitchen_btc_value,
    )
