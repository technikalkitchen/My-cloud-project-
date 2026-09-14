"""Stage 10 — Unit 10.2 — Exchange Selection + Fallback Router.

Consumes Unit 10.1 contracts (Exchange, DISPLAY_FALLBACK_PRIORITY).
Implements exchange selection, Display Fallback Priority routing,
higher-priority-only fallback, and provenance tracking.

Does NOT implement exchange data fetching (Unit 10.3).
Does NOT implement USDT/BTC pair logic (Unit 10.3/10.4).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Tuple

from app.analysis.stage10_consumer import Exchange, DISPLAY_FALLBACK_PRIORITY


@dataclass
class ExchangeRoutingResult:
    """Result of exchange routing for a single asset/field."""
    requested_exchange: str
    actual_exchange: str
    fallback_used: bool
    fallback_exchange: Optional[str]
    valid: bool
    errors: List[str] = field(default_factory=list)


@dataclass
class ExchangeValidationResult:
    """Per-field validation result for an exchange."""
    exchange: str
    valid: bool
    errors: List[str] = field(default_factory=list)


ExchangeValidator = Callable[[str], Tuple[bool, List[str]]]


class ExchangeRouter:
    """Exchange Selection + Fallback Router.

    Routes data requests through the Display Fallback Priority chain.
    - Selected exchange is the Preferred Source.
    - On failure, fallback proceeds toward HIGHER-priority exchanges only.
    - NEVER falls back to lower-priority exchanges.
    """

    def __init__(self, selected_exchange: Exchange):
        if isinstance(selected_exchange, str):
            matched: Optional[Exchange] = None
            for e in DISPLAY_FALLBACK_PRIORITY:
                if e.value == selected_exchange:
                    matched = e
                    break
            if matched is None:
                raise ValueError(
                    f"Invalid exchange: {selected_exchange}. "
                    f"Must be one of: {[e.value for e in DISPLAY_FALLBACK_PRIORITY]}"
                )
            self.selected = matched
        else:
            self.selected = selected_exchange
        self._validate_selected()

    def _validate_selected(self) -> None:
        if self.selected not in DISPLAY_FALLBACK_PRIORITY:
            raise ValueError(
                f"Invalid exchange: {self.selected.value}. "
                f"Must be one of: {[e.value for e in DISPLAY_FALLBACK_PRIORITY]}"
            )

    def get_fallback_chain(self) -> List[str]:
        """Return exchanges in fallback order from selected to highest priority.

        Example: selected=Bitget → [Bitget, Upbit, Gate, Coinbase, KuCoin, Bybit, OKX, Binance]
        Example: selected=OKX → [OKX, Binance]
        Example: selected=Binance → [Binance]
        """
        selected_idx: Optional[int] = None
        for i, exc in enumerate(DISPLAY_FALLBACK_PRIORITY):
            if exc == self.selected:
                selected_idx = i
                break
        if selected_idx is None:
            return []
        return [
            e.value
            for e in reversed(DISPLAY_FALLBACK_PRIORITY[: selected_idx + 1])
        ]

    def is_valid_exchange(self, exchange_name: str) -> bool:
        return any(e.value == exchange_name for e in DISPLAY_FALLBACK_PRIORITY)

    def is_higher_priority(self, exchange_a: str, exchange_b: str) -> bool:
        """Return True if exchange_a has higher priority (lower index) than exchange_b."""
        idx_a = self._index_of(exchange_a)
        idx_b = self._index_of(exchange_b)
        if idx_a is None or idx_b is None:
            return False
        return idx_a < idx_b

    def is_lower_priority(self, exchange_a: str, exchange_b: str) -> bool:
        """Return True if exchange_a has lower priority (higher index) than exchange_b."""
        return not self.is_higher_priority(exchange_a, exchange_b)

    def validate_fallback_direction(
        self, requested: str, actual: str
    ) -> Tuple[bool, str]:
        """Verify fallback only goes toward higher-priority exchanges."""
        if requested == actual:
            return True, "no_fallback_needed"
        if not self.is_valid_exchange(requested):
            return False, f"requested_exchange_invalid: {requested}"
        if not self.is_valid_exchange(actual):
            return False, f"actual_exchange_invalid: {actual}"
        if self.is_higher_priority(actual, requested):
            return True, "fallback_higher_priority"
        return False, f"invalid_fallback: {actual} is lower priority than {requested}"

    def route(
        self,
        validator: ExchangeValidator,
    ) -> ExchangeRoutingResult:
        """Route through exchanges, selecting first valid source.

        Args:
            validator: Callable taking exchange name, returning (is_valid, errors).

        Returns:
            ExchangeRoutingResult with routing decision and provenance.
        """
        chain = self.get_fallback_chain()
        all_errors: List[str] = []

        for exchange in chain:
            is_valid, errors = validator(exchange)
            all_errors.extend(errors)
            if is_valid:
                return ExchangeRoutingResult(
                    requested_exchange=self.selected.value,
                    actual_exchange=exchange,
                    fallback_used=exchange != self.selected.value,
                    fallback_exchange=None
                    if exchange == self.selected.value
                    else exchange,
                    valid=True,
                    errors=[],
                )

        return ExchangeRoutingResult(
            requested_exchange=self.selected.value,
            actual_exchange="",
            fallback_used=False,
            fallback_exchange=None,
            valid=False,
            errors=[
                f"No valid exchange found in fallback chain for {self.selected.value}",
                *all_errors,
            ],
        )

    def route_with_provenance(
        self,
        data_sources: dict,
    ) -> ExchangeRoutingResult:
        """Route using a dict of exchange_name -> data.

        Each exchange's data is validated for basic presence and non-emptiness.
        Useful for testing and for simple exchange availability checks.
        """
        def _validate(exchange: str) -> Tuple[bool, List[str]]:
            if exchange not in data_sources:
                return False, [f"{exchange}: no data source available"]
            data = data_sources[exchange]
            if data is None:
                return False, [f"{exchange}: data is None"]
            if isinstance(data, dict) and len(data) == 0:
                return False, [f"{exchange}: empty data"]
            return True, []

        return self.route(_validate)

    @staticmethod
    def _index_of(exchange_name: str) -> Optional[int]:
        for i, exc in enumerate(DISPLAY_FALLBACK_PRIORITY):
            if exc.value == exchange_name:
                return i
        return None


def build_exchange_choices() -> List[str]:
    """Return all 8 supported exchange names in priority order."""
    return [e.value for e in DISPLAY_FALLBACK_PRIORITY]


def get_fallback_chain_for(
    selected_exchange: Exchange,
) -> List[str]:
    """Build fallback chain for a given selected exchange."""
    router = ExchangeRouter(selected_exchange)
    return router.get_fallback_chain()
