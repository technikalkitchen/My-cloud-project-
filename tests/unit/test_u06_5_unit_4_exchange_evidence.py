"""U06.5 Unit 4 — Independent 8-exchange OHLCV acquisition + 7-of-8 gate.

Deterministic/synthetic tests only. No live network calls.
"""
from __future__ import annotations

import io
from typing import Any, Dict, List
from unittest.mock import patch

import pytest

from app.config.exchanges import (
    MIN_VALIDATED_EXCHANGE_COUNT,
    MULTI_EXCHANGE_SPECS,
    TARGET_EXCHANGE_COUNT,
)
from app.market.exchange_evidence import acquire_multi_exchange_evidence
from app.market.http import HTTPResult


def _binance_row(open_ms: int) -> List[Any]:
    return [
        open_ms,
        "100.0",
        "110.0",
        "90.0",
        "105.0",
        "10.0",
        1000,
        "1050.0",
    ]


def _ok_result(payload: List[List[Any]]) -> HTTPResult:
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


def test_u06_5_unit_4_all_exchanges_validated():
    payload = [_binance_row(1_700_000_000_000 + i * 300_000) for i in range(2)]
    mapping = {spec["url"]: _ok_result(payload) for spec in MULTI_EXCHANGE_SPECS.values()}
    with patch("app.market.exchange_evidence.http_json", side_effect=_patch_http_json(mapping)):
        result = acquire_multi_exchange_evidence()
    assert result["validated_exchange_count"] == TARGET_EXCHANGE_COUNT
    assert result["gate"]["passed"] is True
    assert result["gate"]["status"] == "PASSED"
    assert result["exchange_evidence_engine"]["failover_between_exchanges"] is False
    for name, entry in result["per_exchange"].items():
        assert entry["status"] == "VALIDATED"
        assert entry["ohlcv"], f"{name} missing ohlcv rows"


def test_u06_5_unit_4_partial_failure_still_passes_gate():
    payload = [_binance_row(1_700_000_000_000 + i * 300_000) for i in range(2)]
    mapping = {}
    for name, spec in MULTI_EXCHANGE_SPECS.items():
        if name == "bitget":
            mapping[spec["url"]] = _fail_result(503, "UNAVAILABLE")
        else:
            mapping[spec["url"]] = _ok_result(payload)
    with patch("app.market.exchange_evidence.http_json", side_effect=_patch_http_json(mapping)):
        result = acquire_multi_exchange_evidence()
    assert result["validated_exchange_count"] == TARGET_EXCHANGE_COUNT - 1
    assert result["validated_exchange_count"] >= MIN_VALIDATED_EXCHANGE_COUNT
    assert result["gate"]["passed"] is True
    assert result["per_exchange"]["bitget"]["status"] == "NOT_AVAILABLE"


def test_u06_5_unit_4_gate_failure_when_below_minimum():
    payload = [_binance_row(1_700_000_000_000 + i * 300_000) for i in range(2)]
    mapping = {}
    failed = 0
    for name, spec in MULTI_EXCHANGE_SPECS.items():
        if failed < (TARGET_EXCHANGE_COUNT - MIN_VALIDATED_EXCHANGE_COUNT + 1):
            mapping[spec["url"]] = _fail_result(503, "UNAVAILABLE")
            failed += 1
        else:
            mapping[spec["url"]] = _ok_result(payload)
    with patch("app.market.exchange_evidence.http_json", side_effect=_patch_http_json(mapping)):
        result = acquire_multi_exchange_evidence()
    assert result["validated_exchange_count"] < MIN_VALIDATED_EXCHANGE_COUNT
    assert result["gate"]["passed"] is False
    assert result["gate"]["status"] == "FAILED"


def test_u06_5_unit_4_malformed_data_rejected():
    mapping = {}
    for name, spec in MULTI_EXCHANGE_SPECS.items():
        if name == "okx":
            mapping[spec["url"]] = _ok_result([["not", "a", "row"]])
        else:
            mapping[spec["url"]] = _ok_result([_binance_row(1_700_000_000_000)])
    with patch("app.market.exchange_evidence.http_json", side_effect=_patch_http_json(mapping)):
        result = acquire_multi_exchange_evidence()
    assert result["per_exchange"]["okx"]["status"] == "NOT_AVAILABLE"
    assert result["per_exchange"]["okx"]["ohlcv"] == []
    assert result["validated_exchange_count"] == TARGET_EXCHANGE_COUNT - 1
    assert result["gate"]["passed"] is True