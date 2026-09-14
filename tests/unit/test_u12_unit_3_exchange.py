"""Stage 12 — Unit 12.3 — Exchange + Data Contract Continuity tests.

Deterministic/synthetic tests only. No live network calls.
Reuses Stage 10 contracts.
"""
from __future__ import annotations

from app.analysis.stage10_consumer import (
    DISPLAY_FALLBACK_PRIORITY,
    Exchange,
)
from app.analysis.stage10_router import ExchangeRouter
from app.analysis.stage12_top3 import (
    validate_exchange_continuity,
)


# ---------------------------------------------------------------------------
# Exchange continuity
# ---------------------------------------------------------------------------


def test_preferred_source_no_fallback():
    valid, reason = validate_exchange_continuity("Binance", "Binance")
    assert valid is True
    assert reason == "preferred_source"


def test_higher_priority_fallback():
    valid, reason = validate_exchange_continuity("OKX", "Binance")
    assert valid is True
    assert reason == "fallback_higher_priority"


def test_lower_priority_fallback_rejected():
    valid, reason = validate_exchange_continuity("Binance", "OKX")
    assert valid is False


def test_bitget_fallback_chain():
    valid, _ = validate_exchange_continuity("Bitget", "Upbit")
    assert valid is True
    valid2, _ = validate_exchange_continuity("Bitget", "Gate")
    assert valid2 is True
    valid3, _ = validate_exchange_continuity("Bitget", "Binance")
    assert valid3 is True


def test_invalid_fallback():
    valid, reason = validate_exchange_continuity("OKX", "Bybit")
    assert valid is False


# ---------------------------------------------------------------------------
# All exchanges testable
# ---------------------------------------------------------------------------


def test_all_exchanges_self():
    for exc in DISPLAY_FALLBACK_PRIORITY:
        valid, _ = validate_exchange_continuity(exc.value, exc.value)
        assert valid is True


def test_all_higher_priority_fallbacks():
    for exc in DISPLAY_FALLBACK_PRIORITY:
        router = ExchangeRouter(exc)
        chain = router.get_fallback_chain()
        for i in range(1, len(chain)):
            valid, _ = validate_exchange_continuity(exc.value, chain[i])
            assert valid is True, f"{exc.value} → {chain[i]} should be valid"


def test_no_lower_priority_fallback():
    for exc in DISPLAY_FALLBACK_PRIORITY:
        router = ExchangeRouter(exc)
        chain = router.get_fallback_chain()
        for i in range(1, len(chain)):
            for j in range(i):
                valid, _ = validate_exchange_continuity(
                    chain[i], chain[j]
                )
                assert not valid, (
                    f"{chain[i]} → {chain[j]} should NOT be valid "
                    f"(lower priority fallback)"
                )


def test_binance_no_fallback():
    valid, _ = validate_exchange_continuity("Binance", "OKX")
    assert valid is False
    valid2, _ = validate_exchange_continuity("Binance", "Bitget")
    assert valid2 is False
