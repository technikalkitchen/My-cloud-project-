"""U06.5 Unit 5 — Independent order-book acquisition + normalization.

Deterministic/synthetic tests only. No live network calls.
"""
from __future__ import annotations

from typing import Dict
from unittest.mock import patch

import pytest

from app.config.exchanges import (
    ORDERBOOK_SPECS,
    TARGET_EXCHANGE_COUNT,
)
from app.market.exchange_evidence import acquire_multi_exchange_orderbook
from app.market.http import HTTPResult


def _ok_orderbook() -> Dict:
    return {
        "bids": [["100.0", "1.0"], ["99.5", "2.0"]],
        "asks": [["100.5", "1.5"], ["101.0", "3.0"]],
    }


def _ok_result(payload):
    return HTTPResult(
        ok=True,
        status=200,
        payload=payload,
        retrieved_at="2026-09-11T16:00:00+00:00",
        elapsed_seconds=0.1,
    )


def _fail_result(status: int, error_class: str) -> HTTPResult:
    return HTTPResult(
        ok=False,
        status=status,
        payload=None,
        retrieved_at="2026-09-11T16:00:00+00:00",
        elapsed_seconds=0.1,
        error_class=error_class,
        error_message="synthetic failure",
    )


def _patch_http_json(mapping: Dict[str, HTTPResult]):
    def fake_http_json(url, params=None, headers=None):
        return mapping.get(url, _fail_result(500, "UNAVAILABLE"))
    return fake_http_json


def test_u06_5_unit_5_valid_orderbook_response():
    mapping = {spec["url"]: _ok_result(_ok_orderbook()) for spec in ORDERBOOK_SPECS.values()}
    with patch("app.market.exchange_evidence.http_json", side_effect=_patch_http_json(mapping)):
        result = acquire_multi_exchange_orderbook()
    assert result["validated_exchange_count"] == TARGET_EXCHANGE_COUNT
    assert result["gate"]["passed"] is True
    assert result["orderbook_engine"]["fabricated_depth"] is False
    for name, entry in result["per_exchange"].items():
        assert entry["status"] == "VALIDATED"
        assert len(entry["bids"]) == 2
        assert len(entry["asks"]) == 2
        assert entry["bids"][0]["price"] == 100.0
        assert entry["asks"][0]["size"] == 1.5


def test_u06_5_unit_5_malformed_response_rejected():
    mapping = {}
    for name, spec in ORDERBOOK_SPECS.items():
        if name == "okx":
            mapping[spec["url"]] = _ok_result({"bids": [["bad"]], "asks": []})
        else:
            mapping[spec["url"]] = _ok_result(_ok_orderbook())
    with patch("app.market.exchange_evidence.http_json", side_effect=_patch_http_json(mapping)):
        result = acquire_multi_exchange_orderbook()
    assert result["per_exchange"]["okx"]["status"] == "NOT_AVAILABLE"
    assert result["per_exchange"]["okx"]["bids"] == []
    assert result["validated_exchange_count"] == TARGET_EXCHANGE_COUNT - 1


def test_u06_5_unit_5_provider_failure():
    mapping = {}
    for name, spec in ORDERBOOK_SPECS.items():
        if name == "binance":
            mapping[spec["url"]] = _fail_result(503, "UNAVAILABLE")
        else:
            mapping[spec["url"]] = _ok_result(_ok_orderbook())
    with patch("app.market.exchange_evidence.http_json", side_effect=_patch_http_json(mapping)):
        result = acquire_multi_exchange_orderbook()
    assert result["per_exchange"]["binance"]["status"] == "NOT_AVAILABLE"
    assert result["per_exchange"]["binance"]["attempts"][0]["valid"] is False
    assert result["validated_exchange_count"] == TARGET_EXCHANGE_COUNT - 1
    assert result["gate"]["passed"] is True


def test_u06_5_unit_5_normalization_contract():
    mapping = {spec["url"]: _ok_result(_ok_orderbook()) for spec in ORDERBOOK_SPECS.values()}
    with patch("app.market.exchange_evidence.http_json", side_effect=_patch_http_json(mapping)):
        result = acquire_multi_exchange_orderbook()
    entry = result["per_exchange"]["binance"]
    assert entry["selected_provider"] == "binance"
    assert entry["selected_provider_mode"] == "PUBLIC_SPOT"
    assert entry["fallback_used"] is False
    assert entry["attempts"][0]["provider"] == "binance"
    assert entry["attempts"][0]["valid"] is True
    assert entry["bids"][0]["price"] == 100.0
    assert entry["asks"][1]["price"] == 101.0
    assert result["orderbook_engine"]["mode"] == "INDEPENDENT_PARALLEL_PROBES"
    assert result["orderbook_engine"]["failover_between_exchanges"] is False