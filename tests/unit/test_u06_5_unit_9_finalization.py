"""U06.5 Unit 9 — Foundation finalization, hash contracts, and consumer contracts.

Deterministic tests using dependency injection. No live network.
"""
from __future__ import annotations

import copy

import pytest

from app.config.quality import TOP_N
from app.market.ranking import dynamic_rank_assets
from app.market.finalization import (
    CELL_ID,
    SCHEMA_VERSION,
    VERSION,
    build_foundation,
    build_u07_adapter,
    build_u08_adapter,
    build_u09_adapter,
    calculate_foundation_hash,
    canonical_hash_input,
    consumer_contract_self_tests,
    credential_discovery_self_test,
    determinism_self_test,
    freeze_foundation,
    hash_contract_self_tests,
    market_engine_self_tests,
    persist_snapshot,
    rule_zero_self_test,
    run_u06_5,
    structural_self_tests,
    technical_lock_gate,
    verify_foundation_hash,
)


def _make_full_top125():
    now = "2026-09-11T16:30:00+00:00"
    assets = []
    for i in range(TOP_N):
        if i == 0:
            symbol = "BTC"
        elif i == 1:
            symbol = "ETH"
        elif i == 2:
            symbol = "USDT"
        else:
            symbol = f"A{i}"
        assets.append({
            "provider_asset_id": 1000 + i,
            "canonical_asset_id": f"cmc:{1000 + i}",
            "symbol": symbol,
            "name": symbol,
            "provider": "TEST",
            "provider_mode": "TEST",
            "provider_rank": i + 1,
            "price": 100.0,
            "market_cap": float(1_000_000_000 - i * 1_000_000),
            "volume_24h": 1_000_000.0,
            "source_timestamp": now,
            "retrieved_at": now,
            "identity_status": "VALIDATED",
        })
    return assets


def _make_injected_records():
    assets = _make_full_top125()
    ranked = dynamic_rank_assets(assets)
    return ranked["top125"]


# ---------------------------------------------------------------------------
# Structural tests
# ---------------------------------------------------------------------------

def test_u06_5_unit_9_structural_self_tests_pass():
    result = structural_self_tests()
    assert result["status"] == "PASS"
    assert result["passed"] == result["total"]
    assert result["passed"] >= 30


def test_u06_5_unit_9_rule_zero_self_test_passes():
    result = rule_zero_self_test()
    assert result["status"] == "PASS"
    assert result["pythonanywhere_portable"] is True


def test_u06_5_unit_9_credential_discovery_self_test():
    result = credential_discovery_self_test()
    assert result["status"] == "PASS"
    assert result["secret_exposed"] is False


# ---------------------------------------------------------------------------
# Hash contracts / determinism
# ---------------------------------------------------------------------------

def test_u06_5_unit_9_hash_contract_self_tests_pass():
    result = hash_contract_self_tests()
    assert result["status"] == "PASS"
    assert result["passed"] == result["total"]


def test_u06_5_unit_9_canonical_hash_excludes_adapters():
    foundation = {
        "canonical": {"a": 1},
        "adapters": {"u07": {"x": 1}},
    }
    canonical = canonical_hash_input(foundation)
    assert "adapters" not in canonical


def test_u06_5_unit_9_hash_deterministic():
    foundation = {
        "snapshot_hash": "PENDING",
        "canonical": {"x": 1},
        "snapshot": {"snapshot_id": "S", "immutable_after_creation": True},
    }
    frozen = freeze_foundation(foundation)
    h1 = calculate_foundation_hash(frozen)
    h2 = calculate_foundation_hash(copy.deepcopy(frozen))
    assert h1 == h2
    assert h1 != "PENDING"


def test_u06_5_unit_9_hash_mutation_detection():
    foundation = {
        "snapshot_hash": "PENDING",
        "canonical": {"x": 1},
        "snapshot": {"snapshot_id": "S", "immutable_after_creation": True},
    }
    frozen = freeze_foundation(foundation)
    assert verify_foundation_hash(frozen) is True

    mutated = copy.deepcopy(frozen)
    mutated["canonical"]["x"] = 2
    assert verify_foundation_hash(mutated) is False


# ---------------------------------------------------------------------------
# run_u06_5 full pipeline
# ---------------------------------------------------------------------------

def test_u06_5_unit_9_run_with_injection():
    records = _make_injected_records()
    result = run_u06_5(
        injected={
            "records": records,
            "validation": {
                "status": "VALIDATED",
                "records": records,
                "failures": [],
            },
            "selected_provider": "coinmarketcap",
            "selected_mode": "SNAPSHOT",
            "global_metrics": {"btc_price": 100_000.0},
            "errors": [],
            "warnings": [],
        },
        skip_self_tests=True,
    )
    assert result["status"] == "FROZEN"
    foundation = result["data_foundation"]
    assert foundation["snapshot_hash"] != "PENDING"
    assert foundation["snapshot_hash"] != "PENDING"
    assert foundation["snapshot"]["frozen"] is True
    assert foundation["snapshot"]["integrity_verified"] is True
    assert "u07" in result["adapters"]
    assert "u08" in result["adapters"]
    assert "u09" in result["adapters"]
    assert result["technical_lock"]["status"] == "LOCK_ACQUIRED"
    assert result["snapshot"]["integrity_verified"] is True
    assert result["snapshot"]["persisted"] is False


def test_u06_5_unit_9_run_lock_gate_rejects_errors():
    records = _make_injected_records()
    result = run_u06_5(
        injected={
            "records": records,
            "validation": {
                "status": "VALIDATED",
                "records": records,
                "failures": [],
            },
            "selected_provider": "coinmarketcap",
            "selected_mode": "SNAPSHOT",
            "global_metrics": {"btc_price": 100_000.0},
            "errors": ["a critical error occurred"],
            "warnings": [],
        },
        skip_self_tests=True,
    )
    assert result["technical_lock"]["status"] == "LOCK_REJECTED"
    assert any(
        "critical error" in e
        for e in result["technical_lock"]["errors"]
    )


def test_u06_5_unit_9_technical_lock_gate_on_validated_foundation():
    records = _make_injected_records()
    foundation_inputs = {
        "run_id": "T",
        "snapshot_id": "S",
        "selected_provider": "coinmarketcap",
        "selected_mode": "SNAPSHOT",
        "selected_records": records,
        "validation": {
            "status": "VALIDATED",
            "records": records,
            "failures": [],
        },
        "attempts": [],
        "fallback_used": False,
        "fallback_reason": None,
        "global_metrics": {"btc_price": 100_000.0},
        "cross_source": {"BTC": {}},
        "exchange_evidence": {},
        "multi_exchange_evidence": {},
        "live_price_foundation": {},
        "market_index_series": {},
        "reference_validation": {"status": "VALIDATED"},
        "raw_artifacts": [],
        "errors": [],
        "warnings": [],
    }
    foundation = build_foundation(**foundation_inputs)
    frozen = freeze_foundation(foundation)
    gate = technical_lock_gate(frozen)
    assert gate["status"] == "LOCK_ACQUIRED"
    assert gate["lock_acquired"] is True


# ---------------------------------------------------------------------------
# Consumer contract / adapter wiring
# ---------------------------------------------------------------------------

def test_u06_5_unit_9_consumer_contract_self_tests():
    records = _make_injected_records()
    result = run_u06_5(
        injected={
            "records": records,
            "validation": {
                "status": "VALIDATED",
                "records": records,
                "failures": [],
            },
            "selected_provider": "coinmarketcap",
            "selected_mode": "SNAPSHOT",
            "global_metrics": {"btc_price": 100_000.0},
            "errors": [],
            "warnings": [],
        },
        skip_self_tests=True,
    )
    tests = consumer_contract_self_tests({
        "data_foundation": result["data_foundation"],
        "adapters": result["adapters"],
    })
    assert tests["status"] == "PASS"
    assert tests["passed"] == tests["total"]


def test_u06_5_unit_9_determinism_self_test():
    records = _make_injected_records()
    result = run_u06_5(
        injected={
            "records": records,
            "validation": {
                "status": "VALIDATED",
                "records": records,
                "failures": [],
            },
            "selected_provider": "coinmarketcap",
            "selected_mode": "SNAPSHOT",
            "global_metrics": {"btc_price": 100_000.0},
            "errors": [],
            "warnings": [],
        },
        skip_self_tests=True,
    )
    tests = determinism_self_test({
        "data_foundation": result["data_foundation"],
        "adapters": result["adapters"],
    })
    assert tests["status"] == "PASS"


def test_u06_5_unit_9_adapters_source_cell():
    records = _make_injected_records()
    result = run_u06_5(
        injected={
            "records": records,
            "validation": {
                "status": "VALIDATED",
                "records": records,
                "failures": [],
            },
            "selected_provider": "coinmarketcap",
            "selected_mode": "SNAPSHOT",
            "global_metrics": {"btc_price": 100_000.0},
            "errors": [],
            "warnings": [],
        },
        skip_self_tests=True,
    )
    for name, adapter in result["adapters"].items():
        assert adapter["SOURCE_CELL"] == CELL_ID
        assert adapter["SCHEMA_VERSION"] == SCHEMA_VERSION


def test_u06_5_unit_9_adapters_hash_trace():
    records = _make_injected_records()
    result = run_u06_5(
        injected={
            "records": records,
            "validation": {
                "status": "VALIDATED",
                "records": records,
                "failures": [],
            },
            "selected_provider": "coinmarketcap",
            "selected_mode": "SNAPSHOT",
            "global_metrics": {"btc_price": 100_000.0},
            "errors": [],
            "warnings": [],
        },
        skip_self_tests=True,
    )
    foundation_hash = result["data_foundation"]["snapshot_hash"]
    for adapter in result["adapters"].values():
        assert adapter["SNAPSHOT_HASH"] == foundation_hash


# ---------------------------------------------------------------------------
# Snapshot persistence
# ---------------------------------------------------------------------------

def test_u06_5_unit_9_persist_snapshot(tmp_path):
    records = _make_injected_records()
    result = run_u06_5(
        injected={
            "records": records,
            "validation": {
                "status": "VALIDATED",
                "records": records,
                "failures": [],
            },
            "selected_provider": "coinmarketcap",
            "selected_mode": "SNAPSHOT",
            "global_metrics": {"btc_price": 100_000.0},
            "errors": [],
            "warnings": [],
        },
        skip_self_tests=True,
    )
    frozen = result["data_foundation"]
    path = persist_snapshot(frozen, storage_path=str(tmp_path))
    p = __import__("pathlib").Path(path)
    assert p.exists()
    assert frozen["snapshot"]["persisted"] is True
    assert frozen["snapshot"]["frozen"] is True
    assert "persisted_path" in frozen["snapshot"]


def test_u06_5_unit_9_run_frozen_not_persisted_by_default():
    records = _make_injected_records()
    result = run_u06_5(
        injected={
            "records": records,
            "validation": {
                "status": "VALIDATED",
                "records": records,
                "failures": [],
            },
            "selected_provider": "coinmarketcap",
            "selected_mode": "SNAPSHOT",
            "global_metrics": {"btc_price": 100_000.0},
            "errors": [],
            "warnings": [],
        },
        skip_self_tests=True,
    )
    assert result["snapshot"]["persisted"] is False
    assert result["data_foundation"]["snapshot"]["persisted"] is False


def test_u06_5_unit_9_self_tests_run_by_default_frozen():
    records = _make_injected_records()
    result = run_u06_5(
        injected={
            "records": records,
            "validation": {
                "status": "VALIDATED",
                "records": records,
                "failures": [],
            },
            "selected_provider": "coinmarketcap",
            "selected_mode": "SNAPSHOT",
            "global_metrics": {"btc_price": 100_000.0},
            "errors": [],
            "warnings": [],
        },
    )
    assert result["status"] == "FROZEN"
    for key in ("structural", "market_engine", "hash_contract",
                "consumer_contract", "determinism", "rule_zero",
                "credential_discovery"):
        assert key in result["self_tests"]
    assert result["self_tests"]["structural"]["status"] == "PASS"
    assert result["self_tests"]["market_engine"]["status"] == "PASS"
    assert result["self_tests"]["hash_contract"]["status"] == "PASS"
