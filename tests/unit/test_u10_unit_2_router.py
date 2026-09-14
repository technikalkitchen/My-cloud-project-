"""Stage 10 — Unit 10.2 — Exchange Selection + Fallback Router tests.

Deterministic/synthetic tests only. No live network calls.
"""
from __future__ import annotations

from app.analysis.stage10_router import (
    ExchangeRouter,
    ExchangeRoutingResult,
    build_exchange_choices,
    get_fallback_chain_for,
)
from app.analysis.stage10_consumer import Exchange


# ---------------------------------------------------------------------------
# Eight exchange choices
# ---------------------------------------------------------------------------


def test_eight_exchange_choices():
    choices = build_exchange_choices()
    assert len(choices) == 8
    assert choices == [
        "Binance", "OKX", "Bybit", "KuCoin",
        "Coinbase", "Gate", "Upbit", "Bitget",
    ]


def test_all_exchanges_valid():
    router_binance = ExchangeRouter(Exchange.BINANCE)
    for name in build_exchange_choices():
        assert router_binance.is_valid_exchange(name)


def test_invalid_exchange_rejected():
    router = ExchangeRouter(Exchange.BINANCE)
    assert not router.is_valid_exchange("FakeExchange")
    assert not router.is_valid_exchange("")
    assert not router.is_valid_exchange("CoinbasePro")


# ---------------------------------------------------------------------------
# Exchange selection
# ---------------------------------------------------------------------------


def test_binance_selection():
    router = ExchangeRouter(Exchange.BINANCE)
    assert router.selected == Exchange.BINANCE
    assert router.selected.value == "Binance"


def test_okx_selection():
    router = ExchangeRouter(Exchange.OKX)
    assert router.selected == Exchange.OKX
    assert router.selected.value == "OKX"


def test_bitget_selection():
    router = ExchangeRouter(Exchange.BITGET)
    assert router.selected == Exchange.BITGET
    assert router.selected.value == "Bitget"


# ---------------------------------------------------------------------------
# Display Fallback Priority
# ---------------------------------------------------------------------------


def test_binance_fallback_chain():
    chain = get_fallback_chain_for(Exchange.BINANCE)
    assert chain == ["Binance"]


def test_okx_fallback_chain():
    chain = get_fallback_chain_for(Exchange.OKX)
    assert chain == ["OKX", "Binance"]


def test_bitget_fallback_chain():
    chain = get_fallback_chain_for(Exchange.BITGET)
    assert chain == [
        "Bitget", "Upbit", "Gate", "Coinbase",
        "KuCoin", "Bybit", "OKX", "Binance",
    ]


# ---------------------------------------------------------------------------
# Selected source succeeds
# ---------------------------------------------------------------------------


def test_selected_source_succeeds_binance():
    router = ExchangeRouter(Exchange.BINANCE)
    validator = lambda ex: (True, []) if ex == "Binance" else (False, [f"{ex}: unavailable"])
    result = router.route(validator)
    assert result.valid is True
    assert result.requested_exchange == "Binance"
    assert result.actual_exchange == "Binance"
    assert result.fallback_used is False
    assert result.fallback_exchange is None


def test_selected_source_succeeds_okx():
    router = ExchangeRouter(Exchange.OKX)
    validator = lambda ex: (True, []) if ex == "OKX" else (False, [f"{ex}: unavailable"])
    result = router.route(validator)
    assert result.valid is True
    assert result.requested_exchange == "OKX"
    assert result.actual_exchange == "OKX"
    assert result.fallback_used is False


def test_selected_source_succeeds_bitget():
    router = ExchangeRouter(Exchange.BITGET)
    validator = lambda ex: (True, []) if ex == "Bitget" else (False, [f"{ex}: unavailable"])
    result = router.route(validator)
    assert result.valid is True
    assert result.actual_exchange == "Bitget"
    assert result.fallback_used is False


# ---------------------------------------------------------------------------
# Selected source fails
# ---------------------------------------------------------------------------


def test_selected_source_fails_binance_no_fallback():
    router = ExchangeRouter(Exchange.BINANCE)
    validator = lambda ex: (False, [f"{ex}: unavailable"])
    result = router.route(validator)
    assert result.valid is False
    assert result.actual_exchange == ""
    assert result.fallback_used is False


def test_selected_source_fails_okx_to_binance():
    router = ExchangeRouter(Exchange.OKX)

    def validator(ex):
        if ex == "OKX":
            return False, ["OKX: unavailable"]
        if ex == "Binance":
            return True, []
        return False, [f"{ex}: unavailable"]

    result = router.route(validator)
    assert result.valid is True
    assert result.requested_exchange == "OKX"
    assert result.actual_exchange == "Binance"
    assert result.fallback_used is True
    assert result.fallback_exchange == "Binance"


# ---------------------------------------------------------------------------
# One-step fallback
# ---------------------------------------------------------------------------


def test_one_step_fallback_okx_to_binance():
    router = ExchangeRouter(Exchange.OKX)
    validator = lambda ex: (True, []) if ex == "Binance" else (False, [f"{ex}: no data"])
    result = router.route(validator)
    assert result.valid is True
    assert result.fallback_used is True
    assert result.actual_exchange == "Binance"
    assert result.fallback_exchange == "Binance"


# ---------------------------------------------------------------------------
# Multi-step fallback
# ---------------------------------------------------------------------------


def test_multi_step_fallback_bitget_to_binance():
    router = ExchangeRouter(Exchange.BITGET)

    def validator(ex):
        if ex == "Binance":
            return True, []
        return False, [f"{ex}: no data"]

    result = router.route(validator)
    assert result.valid is True
    assert result.actual_exchange == "Binance"
    assert result.fallback_used is True
    assert result.fallback_exchange == "Binance"


def test_multi_step_fallback_bitget_to_upbit():
    router = ExchangeRouter(Exchange.BITGET)
    validator = lambda ex: (True, []) if ex == "Upbit" else (False, [f"{ex}: no data"])
    result = router.route(validator)
    assert result.valid is True
    assert result.actual_exchange == "Upbit"
    assert result.fallback_used is True


# ---------------------------------------------------------------------------
# No invalid fallback
# ---------------------------------------------------------------------------


def test_no_lower_priority_fallback():
    router = ExchangeRouter(Exchange.OKX)

    result_okx = router.route_with_provenance({"OKX": {"data": 1}})
    assert result_okx.valid is True
    assert result_okx.actual_exchange == "OKX"
    assert result_okx.fallback_used is False

    chain = router.get_fallback_chain()
    okx_idx = chain.index("OKX")
    for i in range(okx_idx + 1, len(chain)):
        higher = chain[i]
        assert router.is_higher_priority(higher, "OKX")


def test_invalid_exchange_raises():
    try:
        ExchangeRouter("FakeExchange")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


# ---------------------------------------------------------------------------
# Fallback direction validation
# ---------------------------------------------------------------------------


def test_fallback_direction_valid():
    router = ExchangeRouter(Exchange.OKX)
    valid, reason = router.validate_fallback_direction("OKX", "Binance")
    assert valid is True

    valid2, reason2 = router.validate_fallback_direction("OKX", "OKX")
    assert valid2 is True


def test_fallback_direction_invalid():
    router = ExchangeRouter(Exchange.OKX)
    valid, reason = router.validate_fallback_direction("OKX", "Bybit")
    assert valid is False
    assert "lower priority" in reason


def test_fallback_direction_binance_no_fallback():
    router = ExchangeRouter(Exchange.BINANCE)
    valid, reason = router.validate_fallback_direction("Binance", "Binance")
    assert valid is True


# ---------------------------------------------------------------------------
# Priority comparisons
# ---------------------------------------------------------------------------


def test_binance_highest_priority():
    router = ExchangeRouter(Exchange.BINANCE)
    for exc in Exchange:
        if exc == Exchange.BINANCE:
            continue
        assert router.is_higher_priority("Binance", exc.value)
        assert router.is_lower_priority(exc.value, "Binance")


def test_bitget_lowest_priority():
    router = ExchangeRouter(Exchange.BITGET)
    for exc in Exchange:
        if exc == Exchange.BITGET:
            continue
        assert router.is_higher_priority(exc.value, "Bitget")
        assert router.is_lower_priority("Bitget", exc.value)


def test_priority_direction_consistency():
    router = ExchangeRouter(Exchange.OKX)
    chain = router.get_fallback_chain()
    for i in range(len(chain) - 1):
        assert router.is_higher_priority(chain[i + 1], chain[i])


# ---------------------------------------------------------------------------
# Route with provenance (data sources dict)
# ---------------------------------------------------------------------------


def test_route_with_provenance_success():
    router = ExchangeRouter(Exchange.BINANCE)
    result = router.route_with_provenance({"Binance": {"price": 50000}})
    assert result.valid is True
    assert result.actual_exchange == "Binance"


def test_route_with_provenance_fallback():
    router = ExchangeRouter(Exchange.OKX)
    result = router.route_with_provenance({"Binance": {"price": 50000}})
    assert result.valid is True
    assert result.actual_exchange == "Binance"
    assert result.fallback_used is True


def test_route_with_provenance_no_data():
    router = ExchangeRouter(Exchange.BINANCE)
    result = router.route_with_provenance({})
    assert result.valid is False
