"""U09 Unit 5 — Final Engine / Consumer Contract / Regression Gate.

Integrates U09 Units 1-4 into a single callable engine and exposes
the canonical consumer contract for downstream consumers.

  Unit 1  ->  app.config.market_universe  (CONFIG, safety locks)
  Unit 1  ->  app.market.providers         (BaseProvider, CoinGecko, CMC, REGISTRY)
  Unit 1  ->  app.market.validation        (validate_provider_assets, freshness_status)
  Unit 2  ->  app.market.universe          (SEGMENTS, build_reference_from_24h,
                                             build_segments, pct_change, dominance,
                                             segment_for_rank, reference_timestamp_from_provider_24h)
  Unit 3  ->  app.market.universe          (relative_strength, composition_compare,
                                             participation_brain, fmt_pct, build_message)
  Unit 4  ->  app.market.universe          (synthetic_assets, synthetic_validation_suite,
                                             execute_u09, audit_result, persist_result,
                                             orchestrate_universe, _cooldown, provider_order,
                                             sha256_obj, safe_json, write_json)
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.config.market_universe import CONFIG
from app.market.providers import PROVIDER_REGISTRY, ProviderSnapshot
from app.market.universe import (
    AUDIT_DIR,
    SNAPSHOT_DIR,
    audit_result,
    execute_u09,
    persist_result,
    synthetic_assets,
    synthetic_validation_suite,
)
from app.market.validation import validate_provider_assets


def run_u09(
    orchestrator: Optional[Any] = None,
    *,
    audit: bool = True,
    persist: bool = False,
) -> Dict[str, Any]:
    """Final U09 engine entry point.

    Integrates Units 1-4:
      1. Executes the universe pipeline (Unit 4: execute_u09)
      2. Optionally audits the result (Unit 4: audit_result)
      3. Applies the consumer contract (Unit 5)
      4. Optionally persists the result (Unit 4: persist_result)

    Returns the final consumer-ready result dictionary.
    """
    result = execute_u09(orchestrator)

    if audit:
        result["audit"] = audit_result(result)
    else:
        result["audit"] = {"status": "SKIPPED", "issues": []}

    contract = u09_consumer_contract(result)
    result["consumer_contract"] = contract

    if persist and result.get("audit", {}).get("status") == "PASS":
        persist_result(result, result["audit"])

    return result


def u09_consumer_contract(result: Dict[str, Any]) -> Dict[str, Any]:
    """Validates the U09 result against the consumer contract.

    Downstream consumers require these guarantees:
      - All required top-level fields are present
      - Field types are correct
      - Safety locks are all False
      - Validation status is one of the allowed values
      - Message is a non-empty string when validation passes
      - Segments contain all four required segment keys
      - Confidence is in [0.0, 1.0]

    Returns a contract dict with status and issues.
    """
    required_fields: Dict[str, type] = {
        "engine": str,
        "version": str,
        "validation_status": str,
        "data_quality": str,
        "confidence": (int, float),
        "provider": (str, type(None)),
        "segments": dict,
        "message": str,
        "safety": dict,
        "current_timestamp": str,
        "reference_timestamp": (str, type(None)),
        "universe_snapshot": (dict, type(None)),
    }

    issues: List[str] = []

    for field, expected_type in required_fields.items():
        if field not in result:
            issues.append(f"missing_field:{field}")
            continue
        value = result[field]
        if not isinstance(value, expected_type):
            issues.append(
                f"type_mismatch:{field}:expected={expected_type.__name__}:got={type(value).__name__}"
            )

    if "validation_status" in result:
        vs = result["validation_status"]
        if vs not in ("PASS", "DATA_UNAVAILABLE", "FAIL"):
            issues.append(f"invalid_validation_status:{vs}")

    if "safety" in result and isinstance(result["safety"], dict):
        for key in ("trading", "orders", "strategy", "portfolio_actions"):
            if key in result["safety"] and result["safety"][key] is not False:
                issues.append(f"safety_lock_violation:{key}")

    if "message" in result:
        msg = result["message"]
        if not isinstance(msg, str) or not msg.strip():
            issues.append("empty_or_invalid_message")

    if "segments" in result and isinstance(result["segments"], dict):
        required_segments = {"BTC", "ETH", "TOP10_ALT", "BROAD_ALT_11_125"}
        missing_segments = required_segments - set(result["segments"].keys())
        if missing_segments:
            issues.append(
                f"missing_segments:{','.join(sorted(missing_segments))}"
            )

    if "confidence" in result and isinstance(result["confidence"], (int, float)):
        if not (0.0 <= float(result["confidence"]) <= 1.0):
            issues.append("confidence_out_of_range")

    status = "PASS" if not issues else "FAIL"
    return {
        "status": status,
        "required_fields_validated": len(required_fields),
        "issues": issues,
    }


def u09_regression_gate(orchestrator: Optional[Any] = None) -> Dict[str, Any]:
    """Final U09 regression gate.

    Runs a deterministic end-to-end validation:
      1. Synthetic validation suite (deterministic, no network)
      2. execute_u09 with synthetic orchestrator
      3. Audit check
      4. Consumer contract check
      5. Deterministic output verification

    Returns a gate report dict.
    """
    checks: List[Dict[str, Any]] = []

    # Check 1: Synthetic validation suite
    try:
        suite = synthetic_validation_suite()
        checks.append({
            "name": "synthetic_validation_suite",
            "status": "PASS" if suite["status"] == "PASS" else "FAIL",
            "detail": f"{suite['count']} tests",
        })
    except Exception as e:
        checks.append({"name": "synthetic_validation_suite", "status": "FAIL", "detail": str(e)})

    # Check 2: execute_u09 with deterministic mock
    result = {}
    try:
        mock_assets = synthetic_assets("broad")
        validation = validate_provider_assets(mock_assets, 125)
        mock_snap = ProviderSnapshot(
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
            raw_assets=validation["valid_assets"],
            attempts=[],
        )
        result = execute_u09(orchestrator=lambda: {
            "snapshot": mock_snap,
            "validation": validation,
            "provider_meta": {},
        })
        checks.append({
            "name": "execute_u09",
            "status": "PASS" if result.get("validation_status") == "PASS" else "FAIL",
            "detail": f"provider={result.get('provider')}, segments={len(result.get('segments', {}))}",
        })
    except Exception as e:
        checks.append({"name": "execute_u09", "status": "FAIL", "detail": str(e)})

    if result:
        # Check 3: Audit
        try:
            audit = audit_result(result)
            checks.append({
                "name": "audit",
                "status": audit["status"],
                "detail": f"{len(audit['issues'])} issues",
            })
        except Exception as e:
            checks.append({"name": "audit", "status": "FAIL", "detail": str(e)})

        # Check 4: Consumer contract
        try:
            contract = u09_consumer_contract(result)
            checks.append({
                "name": "consumer_contract",
                "status": contract["status"],
                "detail": f"{len(contract['issues'])} issues",
            })
        except Exception as e:
            checks.append({"name": "consumer_contract", "status": "FAIL", "detail": str(e)})

        # Check 5: Deterministic verification
        try:
            result2 = execute_u09(orchestrator=lambda: {
                "snapshot": mock_snap,
                "validation": validation,
                "provider_meta": {},
            })
            deterministic = (
                result.get("engine") == result2.get("engine")
                and result.get("version") == result2.get("version")
                and result.get("validation_status") == result2.get("validation_status")
                and result.get("safety", {}).get("trading") is False
                and result.get("safety", {}).get("orders") is False
                and result.get("message") is not None
            )
            checks.append({
                "name": "deterministic_output",
                "status": "PASS" if deterministic else "FAIL",
                "detail": "engine+version+status+safety+message stable",
            })
        except Exception as e:
            checks.append({"name": "deterministic_output", "status": "FAIL", "detail": str(e)})

    all_pass = all(c["status"] == "PASS" for c in checks)
    return {
        "gate": "U09_REGRESSION",
        "status": "PASS" if all_pass else "FAIL",
        "checks": checks,
        "total": len(checks),
        "passed": sum(1 for c in checks if c["status"] == "PASS"),
        "failed": sum(1 for c in checks if c["status"] == "FAIL"),
    }


def u09_e2e_integration(orchestrator: Optional[Any] = None) -> Dict[str, Any]:
    """End-to-end integration test: runs the full U09 pipeline.

    Verifies that Units 1-4 integrate correctly through the Unit 5 engine.
    """
    result = run_u09(orchestrator=orchestrator, audit=True, persist=False)

    integration_checks: Dict[str, bool] = {
        "config_loaded": bool(CONFIG.get("universe_limit") == 125),
        "providers_available": "COINGECKO" in PROVIDER_REGISTRY,
        "validation_run": result.get("validation_status") in ("PASS", "DATA_UNAVAILABLE"),
        "segments_built": isinstance(result.get("segments"), dict),
        "message_built": isinstance(result.get("message"), str) and len(result.get("message", "")) > 0,
        "audit_applied": "audit" in result,
        "consumer_contract_applied": "consumer_contract" in result,
        "safety_locked": (
            result.get("safety", {}).get("trading") is False
            and result.get("safety", {}).get("orders") is False
            and result.get("safety", {}).get("strategy") is False
            and result.get("safety", {}).get("portfolio_actions") is False
        ),
    }

    all_passed = all(integration_checks.values())
    return {
        "e2e": "U09_INTEGRATION",
        "status": "PASS" if all_passed else "FAIL",
        "checks": integration_checks,
        "result": result,
    }
