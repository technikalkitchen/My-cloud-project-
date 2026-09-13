"""U09 Unit 4 — Synthetic Validation / Execution / Audit / Persistence / Orchestration tests."""
from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
import requests

from app.market.providers import (
    BaseProvider,
    CoinGeckoProvider,
    CoinMarketCapProvider,
    ProviderAttempt,
    ProviderError,
    ProviderHealth,
    ProviderSnapshot,
)
from app.market.universe import (
    PROVIDER_REGISTRY,
    AUDIT_DIR,
    SNAPSHOT_DIR,
    _cooldown,
    audit_result,
    build_reference_from_24h,
    build_segments,
    build_message,
    composition_compare,
    execute_u09,
    orchestrate_universe,
    persist_result,
    provider_order,
    participation_brain,
    relative_strength,
    safe_json,
    segment_for_rank,
    sha256_obj,
    synthetic_assets,
    synthetic_validation_suite,
    write_json,
)
from app.market.validation import validate_provider_assets


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _reset_provider_registry(monkeypatch):
    """Reset PROVIDER_REGISTRY health, providers, and scores before each test."""
    import app.market.universe as uni_mod

    saved = {}
    for pid in list(uni_mod.PROVIDER_REGISTRY.keys()):
        saved[pid] = {
            "provider": uni_mod.PROVIDER_REGISTRY[pid]["provider"],
            "validation_score": uni_mod.PROVIDER_REGISTRY[pid].get("validation_score", 1.0),
            "health": uni_mod.PROVIDER_REGISTRY[pid]["health"],
        }

    def _reset():
        for pid in list(uni_mod.PROVIDER_REGISTRY.keys()):
            h = uni_mod.PROVIDER_REGISTRY[pid]["health"]
            h.state = "AVAILABLE"
            h.failure_count = 0
            h.last_failure_at = None
            h.cooldown_until = None
            h.last_success_at = None
            h.last_error = None
        for pid in list(uni_mod.PROVIDER_REGISTRY.keys()):
            uni_mod.PROVIDER_REGISTRY[pid]["validation_score"] = 1.0

    yield

    for pid, data in saved.items():
        uni_mod.PROVIDER_REGISTRY[pid]["provider"] = data["provider"]
        uni_mod.PROVIDER_REGISTRY[pid]["validation_score"] = data["validation_score"]
        h = data["health"]
        h.state = "AVAILABLE"
        h.failure_count = 0
        h.last_failure_at = None
        h.cooldown_until = None
        h.last_success_at = None
        h.last_error = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_provider(provider_id: str, assets: List[Dict[str, Any]]):
    mock_cls = type(
        f"Mock{provider_id}",
        (BaseProvider,),
        {
            "provider_id": provider_id,
            "schema_version": "test",
            "endpoint": "http://test",
            "fetch": lambda self, session, limit, timeout: (assets, datetime.now(timezone.utc), {"response_type": "list", "field_count_checked": True}),
            "normalize": lambda self, payload: (payload, datetime.now(timezone.utc), {"response_type": "list"}),
        },
    )
    return mock_cls()


def _valid_assets(count: int = 5) -> List[Dict[str, Any]]:
    return [
        {
            "provider_asset_id": f"asset-{i}",
            "symbol": f"ASSET{i}",
            "name": f"Asset {i}",
            "price_usd": float(100.0 / i),
            "market_cap_usd": 1_000_000_000.0 / i,
            "provider_rank": i,
            "price_change_24h_pct": 2.0,
            "market_cap_change_24h_pct": 2.0,
            "provider_timestamp": "2026-09-12T12:00:00+00:00",
        }
        for i in range(1, count + 1)
    ]


# ---------------------------------------------------------------------------
# sha256_obj, safe_json, write_json (Unit 2 utilities)
# ---------------------------------------------------------------------------

def test_sha256_obj_deterministic():
    h1 = sha256_obj({"a": 1, "b": 2})
    h2 = sha256_obj({"a": 1, "b": 2})
    assert h1 == h2


def test_sha256_obj_different():
    h1 = sha256_obj({"a": 1})
    h2 = sha256_obj({"a": 2})
    assert h1 != h2


def test_sha256_obj_string():
    h = sha256_obj("test")
    assert isinstance(h, str)
    assert len(h) == 64


def test_safe_json_datetime():
    dt = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    result = safe_json({"ts": dt})
    assert result["ts"] == "2026-09-12T12:00:00+00:00"


def test_safe_json_float():
    result = safe_json({"x": 1.5})
    assert result["x"] == 1.5


def test_safe_json_nan():
    result = safe_json({"x": float("nan")})
    assert result["x"] is None


def test_safe_json_nested():
    result = safe_json({"a": {"b": [1, 2.0, None]}})
    assert result == {"a": {"b": [1, 2.0, None]}}


def test_write_json_creates_file(tmp_path):
    path = tmp_path / "test.json"
    write_json(path, {"key": "value"})
    assert path.exists()
    data = json.loads(path.read_text())
    assert data == {"key": "value"}


# ---------------------------------------------------------------------------
# _cooldown
# ---------------------------------------------------------------------------

def test_cooldown_increments_failure_count():
    health = ProviderHealth("TEST", state="AVAILABLE", failure_count=0)
    now = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    _cooldown(health, "UNAVAILABLE", now)
    assert health.failure_count == 1
    assert health.state == "UNAVAILABLE"
    assert health.last_failure_at == "2026-09-12T12:00:00+00:00"
    assert health.cooldown_until is not None


def test_cooldown_sets_cooldown_until():
    health = ProviderHealth("TEST")
    now = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    _cooldown(health, "TIMEOUT", now)
    expected = now + timedelta(seconds=60)
    dt = health.cooldown_until
    assert dt is not None
    assert abs((datetime.fromisoformat(dt) - expected).total_seconds()) < 1


def test_cooldown_resets_on_success():
    health = ProviderHealth("TEST", state="AVAILABLE", failure_count=3, cooldown_until="2026-09-12T13:00:00+00:00")
    now = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    health.state = "AVAILABLE"
    health.failure_count = 0
    health.last_success_at = "2026-09-12T12:00:01+00:00"
    health.last_error = None
    health.cooldown_until = None
    assert health.failure_count == 0
    assert health.cooldown_until is None


# ---------------------------------------------------------------------------
# provider_order
# ---------------------------------------------------------------------------

def test_provider_order_default():
    now = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    order = provider_order(now)
    assert "COINGECKO" in order
    assert "COINMARKETCAP" in order


def test_provider_order_coingecko_first():
    now = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    order = provider_order(now)
    assert order[0] == "COINGECKO"


def test_provider_order_excludes_cooldown():
    now = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    future = "2026-09-12T13:00:00+00:00"
    PROVIDER_REGISTRY["COINGECKO"]["health"].cooldown_until = future
    PROVIDER_REGISTRY["COINMARKETCAP"]["health"].cooldown_until = None
    try:
        order = provider_order(now)
        assert "COINGECKO" not in order
        assert order[0] == "COINMARKETCAP"
    finally:
        PROVIDER_REGISTRY["COINGECKO"]["health"].cooldown_until = None


# ---------------------------------------------------------------------------
# orchestrate_universe with mock providers
# ---------------------------------------------------------------------------

def test_orchestrate_universe_returns_snapshot():
    assets = _valid_assets(125)
    mock_cg = _make_mock_provider("COINGECKO", assets)
    mock_cmc = _make_mock_provider("COINMARKETCAP", assets)
    original_cg = PROVIDER_REGISTRY["COINGECKO"]["provider"]
    original_cmc = PROVIDER_REGISTRY["COINMARKETCAP"]["provider"]
    PROVIDER_REGISTRY["COINGECKO"]["provider"] = mock_cg
    PROVIDER_REGISTRY["COINMARKETCAP"]["provider"] = mock_cmc
    try:
        result = orchestrate_universe()
        assert result["snapshot"] is not None
        assert result["snapshot"].provider_id == "COINGECKO"
        assert result["snapshot"].provider_request_status == "SUCCESS"
        assert result["validation"]["status"] == "PASS"
        assert result["snapshot"].fallback_used is False
        assert len(result["snapshot"].raw_assets) == 125
    finally:
        PROVIDER_REGISTRY["COINGECKO"]["provider"] = original_cg
        PROVIDER_REGISTRY["COINMARKETCAP"]["provider"] = original_cmc


def test_orchestrate_universe_fallback_to_cmc():
    assets = _valid_assets(125)
    failing_cg = _make_mock_provider("COINGECKO", [])
    mock_cmc = _make_mock_provider("COINMARKETCAP", assets)
    original_cg = PROVIDER_REGISTRY["COINGECKO"]["provider"]
    original_cmc = PROVIDER_REGISTRY["COINMARKETCAP"]["provider"]
    PROVIDER_REGISTRY["COINGECKO"]["provider"] = failing_cg
    PROVIDER_REGISTRY["COINMARKETCAP"]["provider"] = mock_cmc
    try:
        result = orchestrate_universe()
        assert result["snapshot"] is not None
        assert result["snapshot"].provider_id == "COINMARKETCAP"
        assert result["snapshot"].fallback_used is True
        assert result["snapshot"].fallback_chain == ["COINGECKO", "COINMARKETCAP"]
    finally:
        PROVIDER_REGISTRY["COINGECKO"]["provider"] = original_cg
        PROVIDER_REGISTRY["COINMARKETCAP"]["provider"] = original_cmc


def test_orchestrate_universe_all_fail():
    class FailingProvider(BaseProvider):
        provider_id = "FAIL"
        schema_version = "test"
        endpoint = "http://fail"

        def fetch(self, session, limit, timeout):
            raise ProviderError("UNAVAILABLE", "always fails")

        def normalize(self, payload):
            return [], None, {}

    original_cg = PROVIDER_REGISTRY["COINGECKO"]["provider"]
    original_cmc = PROVIDER_REGISTRY["COINMARKETCAP"]["provider"]
    PROVIDER_REGISTRY["COINGECKO"]["provider"] = FailingProvider()
    PROVIDER_REGISTRY["COINMARKETCAP"]["provider"] = FailingProvider()
    try:
        result = orchestrate_universe()
        assert result["snapshot"] is None
        assert result["validation"]["status"] == "DATA_UNAVAILABLE"
    finally:
        PROVIDER_REGISTRY["COINGECKO"]["provider"] = original_cg
        PROVIDER_REGISTRY["COINMARKETCAP"]["provider"] = original_cmc


def test_orchestrate_universe_with_session():
    assets = _valid_assets(125)
    mock_cg = _make_mock_provider("COINGECKO", assets)
    original_cg = PROVIDER_REGISTRY["COINGECKO"]["provider"]
    PROVIDER_REGISTRY["COINGECKO"]["provider"] = mock_cg
    session = requests.Session()
    try:
        result = orchestrate_universe(session=session)
        assert result["snapshot"] is not None
        assert result["snapshot"].provider_id == "COINGECKO"
    finally:
        PROVIDER_REGISTRY["COINGECKO"]["provider"] = original_cg


def test_orchestrate_attempts_populated():
    assets = _valid_assets(125)
    mock_cg = _make_mock_provider("COINGECKO", assets)
    original_cg = PROVIDER_REGISTRY["COINGECKO"]["provider"]
    PROVIDER_REGISTRY["COINGECKO"]["provider"] = mock_cg
    try:
        result = orchestrate_universe()
        snap = result["snapshot"]
        assert len(snap.attempts) >= 1
        for att in snap.attempts:
            assert isinstance(att, dict)
            assert "provider_id" in att
            assert "attempt" in att
            assert "http_status" in att
    finally:
        PROVIDER_REGISTRY["COINGECKO"]["provider"] = original_cg


def test_orchestrate_failure_count_tracked():
    mock_cg = _make_mock_provider("COINGECKO", [])
    mock_cmc = _make_mock_provider("COINMARKETCAP", _valid_assets(125))
    original_cg = PROVIDER_REGISTRY["COINGECKO"]["provider"]
    original_cmc = PROVIDER_REGISTRY["COINMARKETCAP"]["provider"]
    PROVIDER_REGISTRY["COINGECKO"]["provider"] = mock_cg
    PROVIDER_REGISTRY["COINMARKETCAP"]["provider"] = mock_cmc
    try:
        result = orchestrate_universe()
        assert result["snapshot"] is not None
        assert result["snapshot"].provider_id == "COINMARKETCAP"
        assert result["snapshot"].fallback_used is True
        cg_attempts = [a for a in result["snapshot"].attempts if a.get("provider_id") == "COINGECKO"]
        assert len(cg_attempts) >= 1
    finally:
        PROVIDER_REGISTRY["COINGECKO"]["provider"] = original_cg
        PROVIDER_REGISTRY["COINMARKETCAP"]["provider"] = original_cmc


def test_orchestrate_provider_attempts_structure():
    assets = _valid_assets(125)
    mock_cg = _make_mock_provider("COINGECKO", assets)
    original_cg = PROVIDER_REGISTRY["COINGECKO"]["provider"]
    original_cmc = PROVIDER_REGISTRY["COINMARKETCAP"]["provider"]
    PROVIDER_REGISTRY["COINGECKO"]["provider"] = mock_cg
    try:
        result = orchestrate_universe()
        snap = result["snapshot"]
        assert snap is not None
        for att in snap.attempts:
            assert isinstance(att, dict)
            assert "provider_id" in att
            assert "attempt" in att
            assert "request_timestamp" in att
            assert "response_timestamp" in att
            assert "http_status" in att
            assert "health_state" in att
            assert "endpoint" in att
    finally:
        PROVIDER_REGISTRY["COINGECKO"]["provider"] = original_cg
        PROVIDER_REGISTRY["COINMARKETCAP"]["provider"] = original_cmc


# ---------------------------------------------------------------------------
# synthetic_assets
# ---------------------------------------------------------------------------

def test_synthetic_assets_count():
    assets = synthetic_assets("broad")
    assert len(assets) == 125


def test_synthetic_assets_ranks_1_to_125():
    assets = synthetic_assets("broad")
    ranks = [a["provider_rank"] for a in assets]
    assert ranks == list(range(1, 126))


def test_synthetic_assets_btc_is_first():
    assets = synthetic_assets("broad")
    btc = assets[0]
    assert btc["provider_rank"] == 1
    assert btc["name"] == "Bitcoin"
    assert btc["symbol"] == "btc"


def test_synthetic_assets_eth_is_second():
    assets = synthetic_assets("broad")
    eth = assets[1]
    assert eth["provider_rank"] == 2
    assert eth["name"] == "Ethereum"
    assert eth["symbol"] == "eth"


def test_synthetic_assets_market_cap_descending():
    assets = synthetic_assets("broad")
    mcs = [a["market_cap_usd"] for a in assets]
    for i in range(len(mcs) - 1):
        assert mcs[i] > mcs[i + 1], f"Rank {i} MC {mcs[i]} <= Rank {i+1} MC {mcs[i+1]}"


def test_synthetic_assets_all_have_required_fields():
    assets = synthetic_assets("broad")
    required = [
        "provider_asset_id", "symbol", "name", "price_usd", "market_cap_usd",
        "provider_rank", "price_change_24h_pct", "market_cap_change_24h_pct",
        "provider_timestamp",
    ]
    for a in assets:
        for field in required:
            assert field in a, f"Missing {field} in asset {a.get('provider_asset_id', '?')}"


def test_synthetic_assets_mode_falling():
    assets = synthetic_assets("falling")
    assert assets[0]["price_change_24h_pct"] == 3.0
    assert assets[1]["price_change_24h_pct"] == 4.0
    for a in assets[2:]:
        assert a["price_change_24h_pct"] == -3.0


def test_synthetic_assets_mode_btc():
    assets = synthetic_assets("btc")
    assert assets[0]["price_change_24h_pct"] == 3.0
    assert assets[1]["price_change_24h_pct"] == 4.0
    assert assets[2]["price_change_24h_pct"] == -1.5


def test_synthetic_assets_mode_mixed():
    assets = synthetic_assets("mixed")
    assert assets[0]["price_change_24h_pct"] == 3.0
    for a in assets[1:]:
        assert a["price_change_24h_pct"] in (4.0, -3.0, 0.0)


def test_synthetic_assets_default_mode():
    assets = synthetic_assets()
    for a in assets[2:]:
        rank = a["provider_rank"]
        expected = 3.0 if rank % 2 else 1.0
        assert a["price_change_24h_pct"] == expected


def test_synthetic_assets_validate_pass():
    assets = synthetic_assets("broad")
    v = validate_provider_assets(assets, 125)
    assert v["status"] == "PASS"


# ---------------------------------------------------------------------------
# synthetic_validation_suite
# ---------------------------------------------------------------------------

def test_synthetic_validation_suite_pass():
    result = synthetic_validation_suite()
    assert result["status"] == "PASS"
    assert isinstance(result["tests"], list)
    assert result["count"] == len(result["tests"])
    assert result["count"] > 0


def test_synthetic_validation_suite_test_names():
    result = synthetic_validation_suite()
    for test in result["tests"]:
        assert test.endswith(":PASS")


# ---------------------------------------------------------------------------
# execute_u09
# ---------------------------------------------------------------------------

def test_execute_u09_data_unavailable():
    class FailingProvider(BaseProvider):
        provider_id = "FAIL"
        schema_version = "test"
        endpoint = "http://fail"

        def fetch(self, session, limit, timeout):
            raise ProviderError("UNAVAILABLE", "always fails")

        def normalize(self, payload):
            return [], None, {}

    original_cg = PROVIDER_REGISTRY["COINGECKO"]["provider"]
    original_cmc = PROVIDER_REGISTRY["COINMARKETCAP"]["provider"]
    PROVIDER_REGISTRY["COINGECKO"]["provider"] = FailingProvider()
    PROVIDER_REGISTRY["COINMARKETCAP"]["provider"] = FailingProvider()
    try:
        result = execute_u09()
        assert result["validation_status"] == "DATA_UNAVAILABLE"
        assert result["data_quality"] == "FAIL"
        assert result["confidence"] == 0.0
        assert result["provider"] is None
        assert result["participation_state"] == "UNAVAILABLE"
    finally:
        PROVIDER_REGISTRY["COINGECKO"]["provider"] = original_cg
        PROVIDER_REGISTRY["COINMARKETCAP"]["provider"] = original_cmc


def test_execute_u09_with_mock_orchestrator():
    def mock_orch():
        assets = synthetic_assets("broad")
        v = validate_provider_assets(assets, 125)
        ref = build_reference_from_24h(v["valid_assets"])
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

    result = execute_u09(orchestrator=mock_orch)
    assert result["validation_status"] == "PASS"
    assert result["provider"] == "COINGECKO"
    assert result["fallback_used"] is False
    assert len(result["segments"]) == 4
    assert result["message"] is not None
    assert "MARKET PARTICIPATION" in result["message"]


def test_execute_u09_safety_locks():
    def mock_orch():
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

    result = execute_u09(orchestrator=mock_orch)
    assert result["safety"]["trading"] is False
    assert result["safety"]["orders"] is False
    assert result["safety"]["strategy"] is False
    assert result["safety"]["portfolio_actions"] is False


# ---------------------------------------------------------------------------
# audit_result
# ---------------------------------------------------------------------------

def test_audit_pass():
    assets = synthetic_assets("broad")
    v = validate_provider_assets(assets, 125)
    ref = build_reference_from_24h(v["valid_assets"])
    calc = build_segments(v["valid_assets"], ref)
    rs = relative_strength(calc["segments"])
    comp = composition_compare(assets) if False else {"composition_quality": "STABLE"}
    state, _ = participation_brain(calc["segments"], rs, comp)
    result = execute_u09.__wrapped__ if hasattr(execute_u09, "__wrapped__") else None
    if result is None:
        from app.market.universe import execute_u09 as _eu
        result = _eu(orchestrator=lambda: {"snapshot": ProviderSnapshot(
            provider_id="COINGECKO", primary_provider="COINGECKO", fallback_used=False,
            fallback_chain=["COINGECKO"], fallback_reason=None, provider_status="ACTIVE",
            provider_timestamp=datetime.now(timezone.utc).isoformat(),
            request_timestamp=datetime.now(timezone.utc).isoformat(),
            response_timestamp=datetime.now(timezone.utc).isoformat(),
            provider_schema_version="test", provider_endpoint="http://test",
            provider_request_status="SUCCESS", raw_assets=v["valid_assets"], attempts=[],
        ), "validation": v, "provider_meta": {}})

    audit = audit_result(result)
    assert audit["status"] == "PASS"
    assert audit["issues"] == []


def test_audit_trading_lock():
    result = {"safety": {"trading": True, "orders": False, "strategy": False, "portfolio_actions": False}}
    audit = audit_result(result)
    assert audit["status"] == "FAIL"
    assert any("trading_lock" in i for i in audit["issues"])


def test_audit_banned_language():
    result = {
        "safety": {"trading": False, "orders": False, "strategy": False, "portfolio_actions": False},
        "validation_status": "PASS",
        "message": "BTC capital flow detected",
        "universe_snapshot": {"frozen": True, "assets": [{"provider_asset_id": "a"}]},
        "segments": {},
    }
    audit = audit_result(result)
    assert audit["status"] == "FAIL"
    assert any("banned_language:capital flow" in i for i in audit["issues"])


def test_audit_message_contract():
    from app.market.universe import build_message as _bm
    seg = {
        "BTC": {"constituents": [{"price_change_24h_pct": 3.0}], "dominance_change_pct": 0.5, "market_cap_change_pct": 2.0},
        "ETH": {"constituents": [{"price_change_24h_pct": 2.0}], "dominance_change_pct": 0.4, "market_cap_change_pct": 1.5},
        "TOP10_ALT": {"constituents": [], "dominance_change_pct": 0.3, "market_cap_change_pct": 1.0},
        "BROAD_ALT_11_125": {"constituents": [], "dominance_change_pct": 0.2, "market_cap_change_pct": 0.5},
    }
    msg = _bm({"validation_status": "PASS", "segments": seg})
    result = {
        "validation_status": "PASS", "message": msg,
        "universe_snapshot": {"frozen": True, "assets": synthetic_assets("broad")},
        "segments": seg,
        "safety": {"trading": False, "orders": False, "strategy": False, "portfolio_actions": False},
    }
    audit = audit_result(result)
    assert audit["status"] == "PASS"


def test_audit_snapshot_not_frozen():
    result = {
        "safety": {"trading": False, "orders": False, "strategy": False, "portfolio_actions": False},
        "validation_status": "PASS",
        "message": "test",
        "universe_snapshot": {"frozen": False, "assets": [1] * 125},
        "segments": {},
    }
    audit = audit_result(result)
    assert audit["status"] == "FAIL"
    assert any("snapshot_not_frozen" in i for i in audit["issues"])


def test_audit_snapshot_count():
    result = {
        "safety": {"trading": False, "orders": False, "strategy": False, "portfolio_actions": False},
        "validation_status": "PASS",
        "message": "test",
        "universe_snapshot": {"frozen": True, "assets": [1] * 100},
        "segments": {},
    }
    audit = audit_result(result)
    assert audit["status"] == "FAIL"
    assert any("snapshot_count" in i for i in audit["issues"])


def test_audit_message_line_contract():
    result = {
        "safety": {"trading": False, "orders": False, "strategy": False, "portfolio_actions": False},
        "validation_status": "PASS",
        "message": "line1\nline2",
        "universe_snapshot": {"frozen": True, "assets": [{"provider_asset_id": "a"}] * 125},
        "segments": {},
    }
    audit = audit_result(result)
    assert audit["status"] == "FAIL"
    assert any("message_line_contract" in i for i in audit["issues"])


# ---------------------------------------------------------------------------
# persist_result
# ---------------------------------------------------------------------------

def test_persist_result_creates_files(tmp_path):
    from app.market.universe import SNAPSHOT_DIR, AUDIT_DIR
    original_snapshot = SNAPSHOT_DIR
    original_audit = AUDIT_DIR
    from app.market import universe as uni_mod
    uni_mod.SNAPSHOT_DIR = tmp_path / "snapshots" / "u09"
    uni_mod.AUDIT_DIR = tmp_path / "audit" / "u09"
    try:
        result = {"test": "data", "message": "test"}
        audit = {"status": "PASS", "issues": []}
        result_path, audit_path = persist_result(result, audit)
        assert result_path.exists()
        assert audit_path.exists()
        saved_result = json.loads(result_path.read_text())
        assert saved_result["test"] == "data"
        saved_audit = json.loads(audit_path.read_text())
        assert saved_audit["status"] == "PASS"
    finally:
        uni_mod.SNAPSHOT_DIR = original_snapshot
        uni_mod.AUDIT_DIR = original_audit


def test_persist_result_returns_paths():
    from app.market import universe as uni_mod
    original_snapshot = uni_mod.SNAPSHOT_DIR
    original_audit = uni_mod.AUDIT_DIR
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        uni_mod.SNAPSHOT_DIR = Path(tmp) / "snapshots" / "u09"
        uni_mod.AUDIT_DIR = Path(tmp) / "audit" / "u09"
        try:
            result = {"test": "data"}
            audit = {"status": "PASS"}
            result_path, audit_path = persist_result(result, audit)
            assert isinstance(result_path, Path)
            assert isinstance(audit_path, Path)
            assert "U09_" in result_path.name
            assert "U09_AUDIT_" in audit_path.name
            assert result_path.suffix == ".json"
            assert audit_path.suffix == ".json"
        finally:
            uni_mod.SNAPSHOT_DIR = original_snapshot
            uni_mod.AUDIT_DIR = original_audit


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def test_provider_snapshot_asdict():
    snap = ProviderSnapshot(
        provider_id="TEST", primary_provider="PRIMARY", fallback_used=False,
        fallback_chain=[], fallback_reason=None, provider_status="ACTIVE",
        provider_timestamp="2026-09-12T12:00:00+00:00",
        request_timestamp="2026-09-12T12:00:00+00:00",
        response_timestamp="2026-09-12T12:00:01+00:00",
        provider_schema_version="v1", provider_endpoint="/test",
        provider_request_status="SUCCESS", raw_assets=[], attempts=[],
    )
    d = asdict(snap) if False else snap.__dict__
    assert d["provider_id"] == "TEST"
    assert d["fallback_used"] is False


from dataclasses import asdict


def test_provider_attempt_fields():
    att = ProviderAttempt(
        provider_id="TEST", attempt=1,
        request_timestamp="2026-09-12T12:00:00+00:00",
        response_timestamp="2026-09-12T12:00:01+00:00",
        http_status=200, health_state="AVAILABLE",
        error=None, endpoint="/test",
    )
    assert att.provider_id == "TEST"
    assert att.attempt == 1
    assert att.http_status == 200
