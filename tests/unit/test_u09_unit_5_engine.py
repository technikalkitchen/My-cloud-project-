"""U09 Unit 5 — Final Engine / Consumer Contract / Regression Gate tests."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

from app.config.market_universe import CONFIG
from app.market.providers import ProviderSnapshot
from app.market.u09_engine import (
    u09_consumer_contract,
    u09_e2e_integration,
    u09_regression_gate,
    run_u09,
)
from app.market.universe import (
    ProviderSnapshot as _PS,
    execute_u09,
    synthetic_assets,
    validate_provider_assets,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_orchestrator():
    assets = synthetic_assets("broad")
    v = validate_provider_assets(assets, 125)
    snap = ProviderSnapshot(
        provider_id="COINGECKO",
        primary_provider="COINGECKO",
        fallback_used=False,
        fallback_chain=["COINGECKO"],
        fallback_reason=None,
        provider_status="ACTIVE",
        provider_timestamp=datetime.now(timezone.utc).isoformat(),
        request_timestamp=datetime.now(timezone.utc).isoformat(),
        response_timestamp=datetime.now(timezone.utc).isoformat(),
        provider_schema_version="test",
        provider_endpoint="http://test",
        provider_request_status="SUCCESS",
        raw_assets=v["valid_assets"],
        attempts=[],
    )
    return {"snapshot": snap, "validation": v, "provider_meta": {}}


# ---------------------------------------------------------------------------
# run_u09
# ---------------------------------------------------------------------------

class TestRunU09:
    def test_run_u09_returns_dict(self):
        result = run_u09(orchestrator=_mock_orchestrator, audit=True, persist=False)
        assert isinstance(result, dict)

    def test_run_u09_has_engine_field(self):
        result = run_u09(orchestrator=_mock_orchestrator, audit=True, persist=False)
        assert result["engine"] == "U09_DYNAMIC_MARKET_UNIVERSE"

    def test_run_u09_has_version(self):
        result = run_u09(orchestrator=_mock_orchestrator, audit=True, persist=False)
        assert isinstance(result["version"], str)

    def test_run_u09_with_audit(self):
        result = run_u09(orchestrator=_mock_orchestrator, audit=True, persist=False)
        assert "audit" in result
        assert result["audit"]["status"] == "PASS"

    def test_run_u09_without_audit(self):
        result = run_u09(orchestrator=_mock_orchestrator, audit=False, persist=False)
        assert "audit" in result
        assert result["audit"]["status"] == "SKIPPED"

    def test_run_u09_has_consumer_contract(self):
        result = run_u09(orchestrator=_mock_orchestrator, audit=True, persist=False)
        assert "consumer_contract" in result
        assert result["consumer_contract"]["status"] == "PASS"

    def test_run_u09_persist_pass(self, tmp_path):
        from app.market import universe as uni_mod
        orig_snap = uni_mod.SNAPSHOT_DIR
        orig_audit = uni_mod.AUDIT_DIR
        uni_mod.SNAPSHOT_DIR = tmp_path / "snapshots" / "u09"
        uni_mod.AUDIT_DIR = tmp_path / "audit" / "u09"
        try:
            result = run_u09(orchestrator=_mock_orchestrator, audit=True, persist=True)
            assert result["audit"]["status"] == "PASS"
            snap_files = list((tmp_path / "snapshots" / "u09").glob("U09_*.json"))
            audit_files = list((tmp_path / "audit" / "u09").glob("U09_AUDIT_*.json"))
            assert len(snap_files) == 1
            assert len(audit_files) == 1
        finally:
            uni_mod.SNAPSHOT_DIR = orig_snap
            uni_mod.AUDIT_DIR = orig_audit

    def test_run_u09_persist_false_no_files(self, tmp_path):
        from app.market import universe as uni_mod
        orig_snap = uni_mod.SNAPSHOT_DIR
        orig_audit = uni_mod.AUDIT_DIR
        uni_mod.SNAPSHOT_DIR = tmp_path / "snapshots" / "u09"
        uni_mod.AUDIT_DIR = tmp_path / "audit" / "u09"
        try:
            result = run_u09(orchestrator=_mock_orchestrator, audit=True, persist=False)
            snap_files = list((tmp_path / "snapshots" / "u09").glob("U09_*.json"))
            audit_files = list((tmp_path / "audit" / "u09").glob("U09_AUDIT_*.json"))
            assert len(snap_files) == 0
            assert len(audit_files) == 0
        finally:
            uni_mod.SNAPSHOT_DIR = orig_snap
            uni_mod.AUDIT_DIR = orig_audit


# ---------------------------------------------------------------------------
# u09_consumer_contract
# ---------------------------------------------------------------------------

class TestU09ConsumerContract:
    def test_passing_result(self):
        result = execute_u09(orchestrator=_mock_orchestrator)
        contract = u09_consumer_contract(result)
        assert contract["status"] == "PASS"
        assert not contract["issues"]

    def test_missing_field(self):
        result = execute_u09(orchestrator=_mock_orchestrator)
        result.pop("engine", None)
        contract = u09_consumer_contract(result)
        assert contract["status"] == "FAIL"
        assert any("missing_field:engine" in i for i in contract["issues"])

    def test_type_mismatch(self):
        result = execute_u09(orchestrator=_mock_orchestrator)
        result["engine"] = 123
        contract = u09_consumer_contract(result)
        assert contract["status"] == "FAIL"
        assert any("type_mismatch:engine" in i for i in contract["issues"])

    def test_safety_lock_violation(self):
        result = execute_u09(orchestrator=_mock_orchestrator)
        result["safety"]["trading"] = True
        contract = u09_consumer_contract(result)
        assert contract["status"] == "FAIL"
        assert any("safety_lock_violation:trading" in i for i in contract["issues"])

    def test_invalid_validation_status(self):
        result = execute_u09(orchestrator=_mock_orchestrator)
        result["validation_status"] = "UNKNOWN"
        contract = u09_consumer_contract(result)
        assert contract["status"] == "FAIL"
        assert any("invalid_validation_status" in i for i in contract["issues"])

    def test_empty_message(self):
        result = execute_u09(orchestrator=_mock_orchestrator)
        result["message"] = ""
        contract = u09_consumer_contract(result)
        assert contract["status"] == "FAIL"
        assert any("empty_or_invalid_message" in i for i in contract["issues"])

    def test_missing_segments(self):
        result = execute_u09(orchestrator=_mock_orchestrator)
        result["segments"] = {}
        contract = u09_consumer_contract(result)
        assert contract["status"] == "FAIL"
        assert any("missing_segments" in i for i in contract["issues"])

    def test_confidence_out_of_range(self):
        result = execute_u09(orchestrator=_mock_orchestrator)
        result["confidence"] = 1.5
        contract = u09_consumer_contract(result)
        assert contract["status"] == "FAIL"
        assert any("confidence_out_of_range" in i for i in contract["issues"])

    def test_all_required_fields_validated(self):
        result = execute_u09(orchestrator=_mock_orchestrator)
        contract = u09_consumer_contract(result)
        assert contract["required_fields_validated"] == 12

    def test_data_unavailable_result(self):
        result = {
            "engine": "U09_DYNAMIC_MARKET_UNIVERSE",
            "version": "1.1",
            "validation_status": "DATA_UNAVAILABLE",
            "data_quality": "FAIL",
            "confidence": 0.0,
            "provider": None,
            "segments": {},
            "message": "U09 | DATA_UNAVAILABLE | No validated market-universe provider snapshot available.",
            "safety": {"trading": False, "orders": False, "strategy": False, "portfolio_actions": False},
            "current_timestamp": "2026-09-13T00:00:00+00:00",
            "reference_timestamp": None,
            "universe_snapshot": None,
        }
        contract = u09_consumer_contract(result)
        assert contract["status"] == "FAIL"
        assert any("missing_segments" in i for i in contract["issues"])


# ---------------------------------------------------------------------------
# u09_regression_gate
# ---------------------------------------------------------------------------

class TestU09RegressionGate:
    def test_gate_returns_dict(self):
        gate = u09_regression_gate(orchestrator=_mock_orchestrator)
        assert isinstance(gate, dict)

    def test_gate_has_required_fields(self):
        gate = u09_regression_gate(orchestrator=_mock_orchestrator)
        assert "gate" in gate
        assert gate["gate"] == "U09_REGRESSION"
        assert "status" in gate
        assert "checks" in gate
        assert "total" in gate
        assert "passed" in gate
        assert "failed" in gate

    def test_gate_passes(self):
        gate = u09_regression_gate(orchestrator=_mock_orchestrator)
        assert gate["status"] == "PASS"
        assert gate["failed"] == 0
        assert gate["passed"] == gate["total"]

    def test_gate_checks_names(self):
        gate = u09_regression_gate(orchestrator=_mock_orchestrator)
        names = [c["name"] for c in gate["checks"]]
        assert "synthetic_validation_suite" in names
        assert "execute_u09" in names
        assert "audit" in names
        assert "consumer_contract" in names
        assert "deterministic_output" in names

    def test_gate_check_structure(self):
        gate = u09_regression_gate(orchestrator=_mock_orchestrator)
        for check in gate["checks"]:
            assert "name" in check
            assert "status" in check
            assert "detail" in check
            assert check["status"] in ("PASS", "FAIL")

    def test_gate_total_matches_checks(self):
        gate = u09_regression_gate(orchestrator=_mock_orchestrator)
        assert gate["total"] == len(gate["checks"])
        assert gate["passed"] + gate["failed"] == gate["total"]


# ---------------------------------------------------------------------------
# u09_e2e_integration
# ---------------------------------------------------------------------------

class TestU09E2EIntegration:
    def test_e2e_returns_dict(self):
        e2e = u09_e2e_integration(orchestrator=_mock_orchestrator)
        assert isinstance(e2e, dict)

    def test_e2e_has_required_fields(self):
        e2e = u09_e2e_integration(orchestrator=_mock_orchestrator)
        assert "e2e" in e2e
        assert e2e["e2e"] == "U09_INTEGRATION"
        assert "status" in e2e
        assert "checks" in e2e
        assert "result" in e2e

    def test_e2e_passes(self):
        e2e = u09_e2e_integration(orchestrator=_mock_orchestrator)
        assert e2e["status"] == "PASS"

    def test_e2e_config_loaded(self):
        e2e = u09_e2e_integration(orchestrator=_mock_orchestrator)
        assert e2e["checks"]["config_loaded"] is True

    def test_e2e_providers_available(self):
        e2e = u09_e2e_integration(orchestrator=_mock_orchestrator)
        assert e2e["checks"]["providers_available"] is True

    def test_e2e_safety_locked(self):
        e2e = u09_e2e_integration(orchestrator=_mock_orchestrator)
        assert e2e["checks"]["safety_locked"] is True

    def test_e2e_audit_applied(self):
        e2e = u09_e2e_integration(orchestrator=_mock_orchestrator)
        assert e2e["checks"]["audit_applied"] is True

    def test_e2e_consumer_contract_applied(self):
        e2e = u09_e2e_integration(orchestrator=_mock_orchestrator)
        assert e2e["checks"]["consumer_contract_applied"] is True

    def test_e2e_result_contains_all_fields(self):
        e2e = u09_e2e_integration(orchestrator=_mock_orchestrator)
        result = e2e["result"]
        assert "audit" in result
        assert "consumer_contract" in result
        assert "validation_status" in result
        assert "safety" in result


# ---------------------------------------------------------------------------
# Deterministic / integration validation
# ---------------------------------------------------------------------------

class TestDeterministicValidation:
    def test_deterministic_run_u09(self):
        r1 = run_u09(orchestrator=_mock_orchestrator, audit=True, persist=False)
        r2 = run_u09(orchestrator=_mock_orchestrator, audit=True, persist=False)
        assert r1["engine"] == r2["engine"]
        assert r1["version"] == r2["version"]
        assert r1["validation_status"] == r2["validation_status"]
        assert r1["safety"] == r2["safety"]

    def test_deterministic_consumer_contract(self):
        result1 = execute_u09(orchestrator=_mock_orchestrator)
        result2 = execute_u09(orchestrator=_mock_orchestrator)
        c1 = u09_consumer_contract(result1)
        c2 = u09_consumer_contract(result2)
        assert c1["status"] == c2["status"]
        assert c1["issues"] == c2["issues"]

    def test_deterministic_regression_gate(self):
        g1 = u09_regression_gate(orchestrator=_mock_orchestrator)
        g2 = u09_regression_gate(orchestrator=_mock_orchestrator)
        assert g1["status"] == g2["status"]
        assert g1["passed"] == g2["passed"]
        assert g1["failed"] == g2["failed"]

    def test_safety_locks_preserved(self):
        result = execute_u09(orchestrator=_mock_orchestrator)
        assert result["safety"]["trading"] is False
        assert result["safety"]["orders"] is False
        assert result["safety"]["strategy"] is False
        assert result["safety"]["portfolio_actions"] is False

    def test_consumer_contract_safety_locks(self):
        result = execute_u09(orchestrator=_mock_orchestrator)
        contract = u09_consumer_contract(result)
        assert contract["status"] == "PASS"

    def test_no_forbidden_keys_in_result(self):
        result = execute_u09(orchestrator=_mock_orchestrator)
        forbidden = ["trade", "order", "position", "entry", "exit", "signal", "recommendation"]
        for key in result.keys():
            key_lower = key.lower()
            key_words = set(key_lower.replace("_", " ").split())
            for forbidden_key in forbidden:
                assert forbidden_key not in key_words, f"Forbidden key found: {key}"

    def test_no_forbidden_language_in_message(self):
        result = execute_u09(orchestrator=_mock_orchestrator)
        msg = result.get("message", "").lower()
        for banned in ("capital flow", "money flow", "capital inflow", "capital outflow", "altseason"):
            assert banned not in msg, f"Banned language in message: {banned}"


# ---------------------------------------------------------------------------
# Integration validation
# ---------------------------------------------------------------------------

class TestIntegrationValidation:
    def test_units_1_2_3_4_integrated_via_run_u09(self):
        result = run_u09(orchestrator=_mock_orchestrator, audit=True, persist=False)
        assert result["validation_status"] == "PASS"
        assert "segments" in result
        assert "message" in result
        assert "audit" in result
        assert "consumer_contract" in result
        assert result["audit"]["status"] == "PASS"
        assert result["consumer_contract"]["status"] == "PASS"

    def test_config_consistency(self):
        result = run_u09(orchestrator=_mock_orchestrator, audit=True, persist=False)
        assert CONFIG["universe_limit"] == 125
        assert result["safety"]["trading"] is False

    def test_segments_integrity(self):
        result = execute_u09(orchestrator=_mock_orchestrator)
        segments = result["segments"]
        for seg_name in ("BTC", "ETH", "TOP10_ALT", "BROAD_ALT_11_125"):
            assert seg_name in segments
            seg = segments[seg_name]
            assert "constituents" in seg
            assert "count" in seg
            assert "breadth" in seg
            assert "dominance_pct" in seg

    def test_message_contract(self):
        result = execute_u09(orchestrator=_mock_orchestrator)
        msg = result["message"]
        lines = msg.splitlines()
        assert len(lines) == 5
        assert "MARKET PARTICIPATION" in msg
        assert "24H" in msg

    def test_provider_integration(self):
        from app.market.providers import PROVIDER_REGISTRY
        assert "COINGECKO" in PROVIDER_REGISTRY
        assert "COINMARKETCAP" in PROVIDER_REGISTRY
        assert PROVIDER_REGISTRY["COINGECKO"]["priority"] == 1
        assert PROVIDER_REGISTRY["COINMARKETCAP"]["priority"] == 2
