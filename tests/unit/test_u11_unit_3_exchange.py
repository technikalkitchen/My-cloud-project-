"""Stage 11 — Unit 11.3 — Exchange Selection + Fallback Cohesion tests.

Deterministic/synthetic tests only. No live network calls.
Reuses Stage 10 exchange contracts.
"""
from __future__ import annotations

from app.analysis.stage10_consumer import (
    DISPLAY_FALLBACK_PRIORITY,
    Exchange,
)
from app.analysis.stage10_router import (
    ExchangeRouter,
    ExchangeRoutingResult,
)
from app.analysis.stage11_strong_movers import (
    get_fallback_chain,
    is_higher_priority,
    validate_fallback_direction,
    route_exchange,
)


# ---------------------------------------------------------------------------
# Fallback chain — reuse Stage 10 contract
# ---------------------------------------------------------------------------


def test_fallback_chain_binance():
    chain = get_fallback_chain("Binance")
    assert chain == ["Binance"]


def test_fallback_chain_okx():
    chain = get_fallback_chain("OKX")
    assert chain == ["OKX", "Binance"]


def test_fallback_chain_bybit():
    chain = get_fallback_chain("Bybit")
    assert chain == ["Bybit", "OKX", "Binance"]


def test_fallback_chain_bitget():
    chain = get_fallback_chain("Bitget")
    assert chain == [
        "Bitget", "Upbit", "Gate", "Coinbase",
        "KuCoin", "Bybit", "OKX", "Binance",
    ]


def test_fallback_chain_none():
    chain = get_fallback_chain(None)
    assert len(chain) == 8


def test_fallback_chain_matches_stage10():
    router = ExchangeRouter(Exchange.BITGET)
    expected = router.get_fallback_chain()
    chain = get_fallback_chain("Bitget")
    assert chain == expected


# ---------------------------------------------------------------------------
# Higher priority checks
# ---------------------------------------------------------------------------


def test_binance_highest():
    assert is_higher_priority("Binance", "OKX") is True
    assert is_higher_priority("Binance", "Bybit") is True


def test_bitget_lowest():
    assert is_higher_priority("Binance", "Bitget") is True
    assert is_higher_priority("OKX", "Bitget") is True
    assert is_higher_priority("Upbit", "Bitget") is True


def test_bitget_not_higher_than_okx():
    assert is_higher_priority("Bitget", "OKX") is False


# ---------------------------------------------------------------------------
# Fallback direction validation
# ---------------------------------------------------------------------------


def test_fallback_direction_valid_okx_to_binance():
    valid, reason = validate_fallback_direction("OKX", "Binance")
    assert valid is True


def test_fallback_direction_valid_same():
    valid, reason = validate_fallback_direction("Binance", "Binance")
    assert valid is True


def test_fallback_direction_invalid_bybit_to_lower():
    valid, reason = validate_fallback_direction("Bybit", "KuCoin")
    assert valid is False
    assert "lower priority" in reason.lower()


def test_fallback_direction_invalid_bitget_to_lower():
    valid, reason = validate_fallback_direction("OKX", "Bybit")
    assert valid is False


# ---------------------------------------------------------------------------
# Exchange routing (Stage 10 router)
# ---------------------------------------------------------------------------


def test_route_selected_valid():
    router = ExchangeRouter("Binance")
    result = route_exchange("Binance", lambda ex: (True, []))
    assert result.valid is True
    assert result.actual_exchange == "Binance"
    assert result.fallback_used is False


def test_route_fallback_to_binance():
    router = ExchangeRouter("OKX")
    result = route_exchange("OKX", lambda ex: (True, []) if ex == "Binance" else (False, [f"{ex}: unavailable"]))
    assert result.valid is True
    assert result.actual_exchange == "Binance"
    assert result.fallback_used is True
    assert result.fallback_exchange == "Binance"


def test_route_no_valid_source():
    router = ExchangeRouter("Binance")
    result = route_exchange("Binance", lambda ex: (False, [f"{ex}: unavailable"]))
    assert result.valid is False


def test_route_bitget_multi_step():
    router = ExchangeRouter("Bitget")
    result = route_exchange("Bitget", lambda ex: (True, []) if ex == "Binance" else (False, [f"{ex}: no data"]))
    assert result.valid is True
    assert result.actual_exchange == "Binance"
    assert result.fallback_used is True


# ---------------------------------------------------------------------------
# All 8 exchanges testable
# ---------------------------------------------------------------------------


def test_all_exchanges_fallback_chains():
    for exc in DISPLAY_FALLBACK_PRIORITY:
        chain = get_fallback_chain(exc.value)
        assert chain[0] == exc.value
        assert len(chain) >= 1
        for i in range(len(chain) - 1):
            assert is_higher_priority(chain[i + 1], chain[i])


def test_no_lower_priority_fallback():
    for exc in DISPLAY_FALLBACK_PRIORITY:
        chain = get_fallback_chain(exc.value)
        router = ExchangeRouter(exc)
        for i in range(len(chain)):
            for j in range(i):
                assert is_higher_priority(chain[i], chain[j])
