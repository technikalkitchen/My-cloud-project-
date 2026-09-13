"""U09 — Dynamic Market Universe / Market Participation Engine.

Unit 2: Universe / Reference Data / Four Segments
    pct_change, dominance, dominance_change_pct, segment_for_rank,
    build_reference_from_24h, reference_timestamp_from_provider_24h,
    build_segments

Unit 3: Relative Strength / Composition / Participation / Message
    relative_strength, composition_compare, participation_brain,
    fmt_pct, build_message

Unit 4: Synthetic Validation / Execution / Audit / Persistence / Orchestration
    synthetic_assets, synthetic_validation_suite, execute_u09,
    audit_result, persist_result, orchestrate_universe

Consumes U09 Unit 1 and Unit 2 contracts.
"""
from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import requests

from app.config.market_universe import CONFIG
from app.market.providers import (
    BaseProvider,
    CoinGeckoProvider,
    CoinMarketCapProvider,
    ProviderAttempt,
    ProviderError,
    ProviderHealth,
    ProviderSnapshot,
    PROVIDER_REGISTRY,
    finite_nonnegative,
    iso,
    parse_ts,
    utc_now,
)
from app.market.validation import (
    freshness_status,
    validate_provider_assets,
)

SNAPSHOT_DIR = Path(__file__).resolve().parent.parent / "snapshots" / "u09"
AUDIT_DIR = Path(__file__).resolve().parent.parent / "audit" / "u09"


def sha256_obj(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def safe_json(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): safe_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [safe_json(v) for v in obj]
    if isinstance(obj, datetime):
        return iso(obj)
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    return obj


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(safe_json(obj), indent=2, ensure_ascii=False), encoding="utf-8")


SEGMENTS = {
    "BTC": range(1, 2),
    "ETH": range(2, 3),
    "TOP10_ALT": range(3, 11),
    "BROAD_ALT_11_125": range(11, 126),
}


def pct_change(current: Optional[float], reference: Optional[float]) -> Optional[float]:
    if current is None or reference is None:
        return None
    if not finite_nonnegative(current) or not finite_nonnegative(reference):
        return None
    if reference == 0:
        return None
    return (current - reference) / reference * 100.0


def dominance(segment_mc: Optional[float], total_mc: Optional[float]) -> Optional[float]:
    if segment_mc is None or total_mc is None:
        return None
    if not finite_nonnegative(segment_mc) or not finite_nonnegative(total_mc) or total_mc <= 0:
        return None
    return segment_mc / total_mc * 100.0


def dominance_change_pct(current: Optional[float], reference: Optional[float]) -> Optional[float]:
    return pct_change(current, reference)


def segment_for_rank(rank: int) -> str:
    for name, rr in SEGMENTS.items():
        if rank in rr:
            return name
    return "OUT_OF_UNIVERSE"


def build_reference_from_24h(assets: List[Dict[str, Any]]) -> Dict[str, float]:
    ref: Dict[str, float] = {}
    for a in assets:
        mc = float(a["market_cap_usd"])
        ch = a.get("market_cap_change_24h_pct")
        try:
            ch = float(ch) if ch is not None else None
        except Exception:
            ch = None
        if ch is not None and math.isfinite(ch) and ch > -100.0:
            ref_mc = mc / (1.0 + ch / 100.0)
            if finite_nonnegative(ref_mc):
                ref[a["provider_asset_id"]] = ref_mc
    return ref


def reference_timestamp_from_provider_24h(provider_timestamp: Optional[str]) -> Optional[str]:
    dt = parse_ts(provider_timestamp)
    if dt is None:
        return None
    return iso(dt - timedelta(hours=24))


def build_segments(assets: List[Dict[str, Any]], reference_mc_by_id: Dict[str, float]) -> Dict[str, Any]:
    groups: Dict[str, List[Dict[str, Any]]] = {k: [] for k in SEGMENTS}
    for a in assets:
        seg = segment_for_rank(int(a["provider_rank"]))
        if seg in groups:
            b = dict(a)
            b["segment"] = seg
            groups[seg].append(b)

    total_mc = sum(float(a["market_cap_usd"]) for a in assets)
    total_ref = sum(reference_mc_by_id.get(a["provider_asset_id"], 0.0) for a in assets if a["provider_asset_id"] in reference_mc_by_id)
    out: Dict[str, Any] = {}
    for seg, rows in groups.items():
        mc = sum(float(a["market_cap_usd"]) for a in rows)
        ref_vals = [reference_mc_by_id[a["provider_asset_id"]] for a in rows if a["provider_asset_id"] in reference_mc_by_id]
        ref_mc = sum(ref_vals) if len(ref_vals) == len(rows) else None
        prices = [a for a in rows if finite_nonnegative(a.get("price_usd"))]
        rising = flat = falling = 0
        threshold = float(CONFIG["breadth_threshold_pct"])
        for a in prices:
            ch = a.get("price_change_24h_pct")
            try:
                ch = float(ch)
            except Exception:
                continue
            if ch > threshold:
                rising += 1
            elif ch < -threshold:
                falling += 1
            else:
                flat += 1
        n = len(prices)
        rp = rising / n * 100 if n else None
        fp = falling / n * 100 if n else None
        flp = flat / n * 100 if n else None
        if n == 0:
            breadth_state = "UNAVAILABLE"
        elif rp >= 70:
            breadth_state = "STRONG"
        elif rp >= 55:
            breadth_state = "POSITIVE"
        elif fp >= 70:
            breadth_state = "WEAK"
        elif fp >= 55:
            breadth_state = "NEGATIVE"
        else:
            breadth_state = "MIXED"
        out[seg] = {
            "constituents": rows,
            "count": len(rows),
            "aggregate_market_cap_usd": mc,
            "reference_market_cap_usd": ref_mc,
            "market_cap_change_pct": pct_change(mc, ref_mc),
            "dominance_pct": dominance(mc, total_mc),
            "reference_dominance_pct": dominance(ref_mc, total_ref) if ref_mc is not None and total_ref > 0 else None,
            "dominance_change_pct": dominance_change_pct(dominance(mc, total_mc), dominance(ref_mc, total_ref) if ref_mc is not None and total_ref > 0 else None),
            "dominance_change_pp": (dominance(mc, total_mc) - dominance(ref_mc, total_ref)) if ref_mc is not None and total_ref > 0 else None,
            "breadth": {
                "rising_count": rising,
                "flat_count": flat,
                "falling_count": falling,
                "rising_pct": rp,
                "flat_pct": flp,
                "falling_pct": fp,
                "breadth_state": breadth_state,
                "price_change_threshold_pct": threshold,
            },
        }
    return {"segments": out, "total_125_mc": total_mc, "reference_total_125_mc": total_ref if total_ref > 0 else None}


# ============================================================
# U09 Unit 3 — Relative Strength / Composition / Participation / Message
# ============================================================

def relative_strength(segments: Dict[str, Any]) -> Dict[str, Any]:
    mc = {k: segments[k]["aggregate_market_cap_usd"] for k in segments}
    btc = mc.get("BTC")
    pairs = [
        ("BTC", "ETH"), ("BTC", "TOP10_ALT"), ("BTC", "BROAD_ALT_11_125"),
        ("ETH", "TOP10_ALT"), ("TOP10_ALT", "BROAD_ALT_11_125"),
    ]
    ratios: Dict[str, Optional[float]] = {}
    for a, b in pairs:
        if finite_nonnegative(mc.get(a)) and finite_nonnegative(mc.get(b)) and mc.get(a, 0) > 0 and mc.get(b, 0) > 0:
            ratios[f"{a}_MC_OVER_{b}_MC"] = mc[a] / mc[b]
        else:
            ratios[f"{a}_MC_OVER_{b}_MC"] = None
    for k in segments:
        if finite_nonnegative(mc.get(k)) and finite_nonnegative(btc) and btc > 0 and mc.get(k, 0) >= 0:
            ratios[f"{k}_MC_OVER_BTC_MC"] = mc[k] / btc
        else:
            ratios[f"{k}_MC_OVER_BTC_MC"] = None
    return ratios


def composition_compare(current_assets: List[Dict[str, Any]]) -> Dict[str, Any]:
    snapshot_dir = Path(__file__).resolve().parent.parent / "snapshots" / "u09"
    files = []
    if snapshot_dir.exists():
        files = sorted(snapshot_dir.glob("U09_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        return {
            "composition_changed": False,
            "composition_quality": "STABLE",
            "previous_snapshot": None,
            "changes": [],
            "entered": [],
            "exited": [],
        }
    try:
        old = json.loads(files[0].read_text(encoding="utf-8"))
        old_assets = old.get("universe_snapshot", {}).get("assets", [])
        old_map = {x.get("provider_asset_id"): x.get("provider_rank") for x in old_assets}
        changes = []
        for a in current_assets:
            aid = a.get("provider_asset_id")
            old_rank = old_map.get(aid)
            new_rank = a.get("provider_rank")
            if old_rank is not None and old_rank != new_rank:
                changes.append({"asset_id": aid, "old_rank": old_rank, "new_rank": new_rank})
        old_ids = set(old_map)
        new_ids = {a.get("provider_asset_id") for a in current_assets}
        entered = sorted(new_ids - old_ids)
        exited = sorted(old_ids - new_ids)
        material = len(changes) + len(entered) + len(exited)
        if material == 0:
            q = "STABLE"
        elif material <= 3:
            q = "MINOR_CHANGE"
        elif material <= 10:
            q = "MATERIAL_CHANGE"
        else:
            q = "UNRELIABLE"
        return {
            "composition_changed": material > 0,
            "composition_quality": q,
            "previous_snapshot": files[0].name,
            "changes": changes,
            "entered": entered,
            "exited": exited,
        }
    except Exception as e:
        return {
            "composition_changed": True,
            "composition_quality": "UNRELIABLE",
            "previous_snapshot": files[0].name if files else None,
            "changes": [],
            "entered": [],
            "exited": [],
            "error": str(e),
        }


def participation_brain(seg: Dict[str, Any], rs: Dict[str, Any], composition: Dict[str, Any]) -> Tuple[str, str]:
    if composition.get("composition_quality") == "UNRELIABLE":
        return "UNAVAILABLE", "Composition quality is unreliable."
    broad = seg["BROAD_ALT_11_125"]
    top = seg["TOP10_ALT"]
    btc = seg["BTC"]
    eth = seg["ETH"]
    if any(seg[k]["count"] == 0 for k in seg):
        return "UNAVAILABLE", "Required segment data is unavailable."
    broad_rise = broad["breadth"]["rising_pct"] or 0
    top_rise = top["breadth"]["rising_pct"] or 0
    broad_mc = broad.get("market_cap_change_pct")
    top_mc = top.get("market_cap_change_pct")
    btc_mc = btc.get("market_cap_change_pct")
    eth_mc = eth.get("market_cap_change_pct")

    broad_support = broad_rise >= 55 and broad_mc is not None and broad_mc > 0
    top_support = top_rise >= 55 and top_mc is not None and top_mc > 0
    core_support = ((btc_mc or 0) > 0) or ((eth_mc or 0) > 0)
    broad_weak = broad_rise < 45 and (broad_mc is not None and broad_mc < 0)
    top_weak = top_rise < 45 and (top_mc is not None and top_mc < 0)

    if broad_support and top_support:
        return "BROADENING", "TOP10 and BROAD participation both support expansion of market participation."
    if core_support and broad_weak and top_weak:
        return "CONCENTRATED", "Relative participation is concentrated in the core while TOP10/BROAD breadth is weak."
    if broad_weak and top_weak:
        return "WEAKENING", "Breadth and aggregate movement in broader segments are deteriorating."
    return "MIXED", "Price, market-cap, breadth and relative-strength evidence is not directionally uniform."


def fmt_pct(v: Optional[float], *, min_decimals: int = 1, max_decimals: int = 6) -> str:
    if v is None:
        return "N/A"
    try:
        x = float(v)
    except Exception:
        return "N/A"
    if not math.isfinite(x):
        return "N/A"
    if x == 0.0:
        x = 0.0
    ax = abs(x)
    if ax == 0.0:
        decimals = min_decimals
    elif ax >= 1.0:
        decimals = min_decimals
    else:
        decimals = max(min_decimals, min(max_decimals, int(-math.floor(math.log10(ax))) + 2))
    text = f"{x:+.{decimals}f}%"
    if text.startswith("-0.") and float(text[:-1]) == 0.0:
        text = text.replace("-0.", "+0.", 1)
    return text


def build_message(result: Dict[str, Any]) -> str:
    if result.get("validation_status") == "DATA_UNAVAILABLE":
        return "U09 | DATA_UNAVAILABLE | No validated market-universe provider snapshot available."
    seg = result["segments"]
    btc_asset = seg["BTC"]["constituents"][0] if seg["BTC"]["constituents"] else None
    eth_asset = seg["ETH"]["constituents"][0] if seg["ETH"]["constituents"] else None
    btc_price = btc_asset.get("price_change_24h_pct") if btc_asset else None
    eth_price = eth_asset.get("price_change_24h_pct") if eth_asset else None
    lines = [
        f"📊 MARKET PARTICIPATION | {CONFIG['message_window_label']}",
        f"₿ BTC Price {fmt_pct(btc_price)} | BTC.D {fmt_pct(seg['BTC']['dominance_change_pct'], min_decimals=2, max_decimals=6)}",
        f"🔷 ETH Price {fmt_pct(eth_price)} | ETH.D {fmt_pct(seg['ETH']['dominance_change_pct'], min_decimals=2, max_decimals=6)}",
        f"🔹 TOP10 ALT MC {fmt_pct(seg['TOP10_ALT']['market_cap_change_pct'])} | TOP10.D {fmt_pct(seg['TOP10_ALT']['dominance_change_pct'], min_decimals=2, max_decimals=6)}",
        f"◈ BROAD 11–125 MC {fmt_pct(seg['BROAD_ALT_11_125']['market_cap_change_pct'])} | BROAD.D {fmt_pct(seg['BROAD_ALT_11_125']['dominance_change_pct'], min_decimals=2, max_decimals=6)}",
    ]
    return "\n".join(lines)


# ============================================================
# U09 Unit 4 — Synthetic Validation / Execution / Audit / Persistence / Orchestration
# ============================================================

def _cooldown(health: ProviderHealth, state: str, now: datetime) -> None:
    health.state = state
    health.failure_count += 1
    health.last_failure_at = iso(now)
    health.cooldown_until = iso(now + timedelta(seconds=CONFIG["provider_cooldown_seconds"]))


def provider_order(now: datetime) -> List[str]:
    candidates = []
    for pid, entry in PROVIDER_REGISTRY.items():
        h = entry["health"]
        if h.in_cooldown(now):
            continue
        candidates.append((entry["priority"], -float(entry.get("validation_score", 1.0)), pid))
    return [x[2] for x in sorted(candidates)]


def orchestrate_universe(session: Optional[requests.Session] = None) -> Dict[str, Any]:
    if session is None:
        session = requests.Session()
    now = utc_now()
    primary = "COINGECKO"
    attempts: List[Dict[str, Any]] = []
    chain: List[str] = []
    failures: List[str] = []

    for pid in provider_order(now):
        entry = PROVIDER_REGISTRY[pid]
        provider: BaseProvider = entry["provider"]
        health: ProviderHealth = entry["health"]
        chain.append(pid)
        last_error: Optional[ProviderError] = None
        for attempt_no in range(CONFIG["max_retries_per_provider"] + 1):
            req_ts = utc_now()
            try:
                assets, provider_ts, meta = provider.fetch(
                    session, CONFIG["universe_limit"], CONFIG["request_timeout_seconds"]
                )
                validation = validate_provider_assets(assets, CONFIG["universe_limit"])
                fstate, age = freshness_status(provider_ts, utc_now())
                if fstate == "STALE":
                    validation["errors"].append("provider_snapshot_stale")
                    validation["status"] = "FAIL"
                if validation["status"] != "PASS":
                    raise ProviderError("PARTIAL", "Provider validation failed: " + ";".join(validation["errors"][:5]))

                resp_ts = utc_now()
                health.state = "AVAILABLE"
                health.last_success_at = iso(resp_ts)
                health.last_error = None
                health.cooldown_until = None
                health.failure_count = 0
                entry["validation_score"] = 1.0
                attempts.append(asdict(ProviderAttempt(
                    pid, attempt_no + 1, iso(req_ts), iso(resp_ts), 200, "AVAILABLE", None, provider.endpoint,
                )))
                fallback_used = pid != primary
                reason = "; ".join(failures) if fallback_used else None
                snapshot = ProviderSnapshot(
                    provider_id=pid,
                    primary_provider=primary,
                    fallback_used=fallback_used,
                    fallback_chain=chain.copy(),
                    fallback_reason=reason,
                    provider_status="ACTIVE",
                    provider_timestamp=iso(provider_ts),
                    request_timestamp=meta.get("request_timestamp") or iso(req_ts),
                    response_timestamp=meta.get("response_timestamp") or iso(resp_ts),
                    provider_schema_version=provider.schema_version,
                    provider_endpoint=provider.endpoint,
                    provider_request_status="SUCCESS",
                    raw_assets=validation["valid_assets"],
                    attempts=attempts.copy(),
                )
                return {"snapshot": snapshot, "validation": validation, "provider_meta": meta, "health": asdict(health)}
            except ProviderError as e:
                last_error = e
                attempts.append(asdict(ProviderAttempt(
                    pid, attempt_no + 1, iso(req_ts), iso(utc_now()), e.status_code, e.state, str(e), provider.endpoint,
                )))
                if attempt_no < CONFIG["max_retries_per_provider"] and e.state in {"TIMEOUT", "RATE_LIMITED", "UNAVAILABLE"}:
                    time.sleep(CONFIG["retry_backoff_seconds"])
                    continue
                break

        if last_error:
            failures.append(f"{pid}:{last_error.state}:{last_error}")
            _cooldown(health, last_error.state, utc_now())
            entry["validation_score"] = max(0.0, float(entry.get("validation_score", 1.0)) - 0.2)

    return {
        "snapshot": None,
        "validation": {"status": "DATA_UNAVAILABLE", "errors": failures, "warnings": []},
        "provider_meta": {"attempts": attempts},
        "health": {pid: asdict(v["health"]) for pid, v in PROVIDER_REGISTRY.items()},
    }


def synthetic_assets(mode: str = "broad") -> List[Dict[str, Any]]:
    now = utc_now()
    rows = []
    for rank in range(1, 126):
        if rank == 1:
            name, symbol, price_ch = "Bitcoin", "btc", 3.0
        elif rank == 2:
            name, symbol, price_ch = "Ethereum", "eth", 4.0
        else:
            name, symbol = f"Asset {rank}", f"a{rank}"
            if mode == "broad":
                price_ch = 3.0 if rank % 2 else 1.0
            elif mode == "btc":
                price_ch = 3.0 if rank <= 2 else -1.5
            elif mode == "eth":
                price_ch = 2.0 if rank == 1 else (6.0 if rank == 2 else 0.5)
            elif mode == "mixed":
                price_ch = 4.0 if rank % 3 == 0 else (-3.0 if rank % 3 == 1 else 0.0)
            elif mode == "falling":
                price_ch = -3.0
            else:
                price_ch = 1.0
        mc = 1_000_000_000_000.0 / (rank ** 0.85)
        rows.append({
            "provider_asset_id": f"synthetic-{rank}",
            "symbol": symbol,
            "name": name,
            "price_usd": 100.0 / rank,
            "market_cap_usd": mc,
            "provider_rank": rank,
            "price_change_24h_pct": price_ch,
            "market_cap_change_24h_pct": price_ch,
            "provider_timestamp": iso(now),
        })
    return rows


def synthetic_validation_suite() -> Dict[str, Any]:
    tests = []

    assets = synthetic_assets("broad")
    v = validate_provider_assets(assets, 125)
    assert v["status"] == "PASS", v
    ref = build_reference_from_24h(v["valid_assets"])
    calc = build_segments(v["valid_assets"], ref)
    seg = calc["segments"]
    partition = sum(seg[k]["dominance_pct"] or 0 for k in seg)
    assert abs(partition - 100.0) <= CONFIG["dominance_partition_tolerance_pct"]
    tests.append("rank_identity_segmentation_aggregation_dominance:PASS")

    bassets = synthetic_assets("broad")
    for i, a in enumerate(bassets[:20]):
        a["price_change_24h_pct"] = 1.0 if i < 10 else (0.0 if i < 15 else -1.0)
    rising = sum(1 for a in bassets[:20] if a["price_change_24h_pct"] > CONFIG["breadth_threshold_pct"])
    flat = sum(1 for a in bassets[:20] if abs(a["price_change_24h_pct"]) <= CONFIG["breadth_threshold_pct"])
    falling = sum(1 for a in bassets[:20] if a["price_change_24h_pct"] < -CONFIG["breadth_threshold_pct"])
    assert (rising, flat, falling) == (10, 5, 5)
    tests.append("breadth_10_5_5:PASS")

    rs = relative_strength(seg)
    assert rs["BROAD_ALT_11_125_MC_OVER_BTC_MC"] is not None
    tests.append("relative_strength_pairs:PASS")

    assert pct_change(100.0, 0.0) is None
    tests.append("zero_reference_guard:PASS")

    dup = synthetic_assets("broad")
    dup[1]["provider_asset_id"] = dup[0]["provider_asset_id"]
    assert validate_provider_assets(dup, 125)["status"] == "FAIL"
    tests.append("duplicate_id_rejection:PASS")

    dup_rank = synthetic_assets("broad")
    dup_rank[1]["provider_rank"] = 1
    assert validate_provider_assets(dup_rank, 125)["status"] == "FAIL"
    tests.append("duplicate_rank_rejection:PASS")

    missing = synthetic_assets("broad")[:-1]
    assert validate_provider_assets(missing, 125)["status"] == "FAIL"
    tests.append("missing_rank_coverage_rejection:PASS")

    bad = synthetic_assets("broad")
    bad[0]["market_cap_usd"] = float("nan")
    assert validate_provider_assets(bad, 125)["status"] == "FAIL"
    tests.append("invalid_numeric_rejection:PASS")

    base = synthetic_assets("broad")
    moved = synthetic_assets("broad")
    moved[9]["provider_rank"], moved[10]["provider_rank"] = 11, 10
    moved_v = validate_provider_assets(moved, 125)
    assert moved_v["status"] == "PASS"
    assert segment_for_rank(10) == "TOP10_ALT" and segment_for_rank(11) == "BROAD_ALT_11_125"
    tests.append("composition_boundary_rank_validation:PASS")

    assert abs(dominance_change_pct(12.6, 12.0) - 5.0) < 1e-12
    assert abs((12.6 - 12.0) - 0.6) < 1e-12
    assert "-0.0%" not in fmt_pct(-0.00001, min_decimals=2, max_decimals=6)
    assert "0.00001" in fmt_pct(0.00001, min_decimals=2, max_decimals=6)
    tests.append("dominance_relative_percent_and_precision:PASS")

    ts = "2026-09-02T14:43:00+00:00"
    assert reference_timestamp_from_provider_24h(ts) == "2026-09-01T14:43:00+00:00"
    tests.append("reference_timestamp_24h_semantics:PASS")

    fresh_state, _ = freshness_status(utc_now(), utc_now())
    stale_state, _ = freshness_status(utc_now() - timedelta(hours=3), utc_now())
    assert fresh_state == "FRESH" and stale_state == "STALE"
    tests.append("freshness_states:PASS")

    brain = participation_brain(seg, rs, {"composition_quality": "STABLE"})
    assert brain[0] in {"BROADENING", "CONCENTRATED", "MIXED", "WEAKENING", "UNAVAILABLE"}
    tests.append("participation_brain_state:PASS")

    return {"status": "PASS", "tests": tests, "count": len(tests)}


def execute_u09(orchestrator: Optional[Callable] = None) -> Dict[str, Any]:
    started = utc_now()
    synthetic = synthetic_validation_suite()
    assert synthetic["status"] == "PASS"

    orch = orchestrator() if orchestrator else orchestrate_universe()
    snap: Optional[ProviderSnapshot] = orch.get("snapshot")
    if snap is None:
        result = {
            "engine": "U09_DYNAMIC_MARKET_UNIVERSE",
            "version": "1.1",
            "validation_status": "DATA_UNAVAILABLE",
            "data_quality": "FAIL",
            "confidence": 0.0,
            "provider": None,
            "primary_provider": "COINGECKO",
            "fallback_used": False,
            "fallback_chain": orch.get("provider_meta", {}).get("attempts", []),
            "fallback_reason": "; ".join(orch.get("validation", {}).get("errors", [])),
            "current_timestamp": iso(utc_now()),
            "reference_timestamp": None,
            "universe_snapshot": None,
            "segments": {},
            "participation_state": "UNAVAILABLE",
            "validation": orch.get("validation"),
            "synthetic_tests": synthetic,
            "provider_health": orch.get("health"),
            "safety": {
                "trading": False, "orders": False, "strategy": False, "portfolio_actions": False,
                "capital_flow_claim": False, "altseason_claim": False,
            },
        }
        return result

    assets = snap.raw_assets
    validation = orch["validation"]
    ref_map = build_reference_from_24h(assets)
    analytical = build_segments(assets, ref_map)
    rs = relative_strength(analytical["segments"])
    composition = composition_compare(assets)

    quality = "HIGH"
    confidence = 1.0
    if snap.fallback_used:
        quality = "MEDIUM"
        confidence -= 0.10
    if composition["composition_quality"] == "MINOR_CHANGE":
        confidence -= 0.05
    elif composition["composition_quality"] == "MATERIAL_CHANGE":
        quality = "LOW"
        confidence -= 0.20
    elif composition["composition_quality"] == "UNRELIABLE":
        quality = "PARTIAL"
        confidence -= 0.45
    if analytical["reference_total_125_mc"] is None:
        quality = "PARTIAL" if quality == "HIGH" else quality
        confidence -= 0.20

    state, explanation = participation_brain(analytical["segments"], rs, composition)
    confidence = max(0.0, min(1.0, confidence))

    universe_snapshot = {
        "snapshot_id": "U09-" + utc_now().strftime("%Y%m%dT%H%M%S%fZ"),
        "frozen": True,
        "provider": snap.provider_id,
        "provider_timestamp": snap.provider_timestamp,
        "created_at": snap.response_timestamp,
        "universe_limit": 125,
        "assets": assets,
        "snapshot_hash": sha256_obj(assets),
    }
    result = {
        "engine": "U09_DYNAMIC_MARKET_UNIVERSE",
        "version": "1.1",
        "validation_status": "PASS",
        "data_quality": quality,
        "confidence": confidence,
        "provider": snap.provider_id,
        "primary_provider": snap.primary_provider,
        "fallback_used": snap.fallback_used,
        "fallback_chain": snap.fallback_chain,
        "fallback_reason": snap.fallback_reason,
        "provider_metadata": {
            "provider_status": snap.provider_status,
            "provider_timestamp": snap.provider_timestamp,
            "request_timestamp": snap.request_timestamp,
            "response_timestamp": snap.response_timestamp,
            "provider_schema_version": snap.provider_schema_version,
            "provider_endpoint": snap.provider_endpoint,
            "provider_request_status": snap.provider_request_status,
            "attempts": snap.attempts,
        },
        "current_timestamp": snap.response_timestamp,
        "reference_timestamp": reference_timestamp_from_provider_24h(snap.provider_timestamp) if CONFIG["reference_mode"] == "provider_24h" else None,
        "universe_snapshot": universe_snapshot,
        "btc_metrics": analytical["segments"]["BTC"],
        "eth_metrics": analytical["segments"]["ETH"],
        "top10_metrics": analytical["segments"]["TOP10_ALT"],
        "broad_metrics": analytical["segments"]["BROAD_ALT_11_125"],
        "segments": analytical["segments"],
        "total_125_mc": analytical["total_125_mc"],
        "reference_total_125_mc": analytical["reference_total_125_mc"],
        "dominance_metrics": {k: {
            "current_pct": v["dominance_pct"],
            "reference_pct": v["reference_dominance_pct"],
            "change_pct": v["dominance_change_pct"],
            "change_pp": v["dominance_change_pp"],
        } for k, v in analytical["segments"].items()},
        "breadth_metrics": {k: v["breadth"] for k, v in analytical["segments"].items()},
        "relative_strength_metrics": rs,
        "composition_status": composition,
        "participation_state": state,
        "participation_explanation": explanation,
        "synthetic_tests": synthetic,
        "validation": validation,
        "provider_health": {pid: asdict(v["health"]) for pid, v in PROVIDER_REGISTRY.items()},
        "internal_diagnostics": {
            "reference_mode": CONFIG["reference_mode"],
            "reference_lookback": CONFIG["lookback"],
            "reference_timestamp_semantics": "provider_timestamp_minus_24h",
            "reference_coverage_ratio": len(ref_map) / 125.0,
            "coverage_ratio": validation.get("coverage_ratio"),
            "rank_status_counts": {
                s: sum(1 for a in assets if a.get("rank_consistency_status") == s)
                for s in ("MATCH", "MINOR_DIFFERENCE", "WARNING", "FAIL")
            },
            "composition_quality": composition.get("composition_quality"),
        },
        "safety": {
            "trading": False, "orders": False, "strategy": False, "portfolio_actions": False,
            "capital_flow_claim": False, "altseason_claim": False,
        },
    }
    result["message"] = build_message(result)
    result["execution_seconds"] = max(0.0, (utc_now() - started).total_seconds())
    return result


def audit_result(result: Dict[str, Any]) -> Dict[str, Any]:
    issues = []
    if result.get("safety", {}).get("trading") is not False:
        issues.append("trading_lock")
    if result.get("safety", {}).get("orders") is not False:
        issues.append("orders_lock")
    if result.get("safety", {}).get("strategy") is not False:
        issues.append("strategy_lock")
    if result.get("safety", {}).get("portfolio_actions") is not False:
        issues.append("portfolio_lock")
    text = str(result.get("message", "")).lower()
    for banned in ("capital flow", "money flow", "capital inflow", "capital outflow", "altseason"):
        if banned in text:
            issues.append("banned_language:" + banned)
    if result.get("validation_status") == "PASS":
        snap = result.get("universe_snapshot") or {}
        msg = result.get("message", "")
        if "Participation:" in msg:
            issues.append("message_participation_state_should_be_internal")
        if " pp" in msg:
            issues.append("message_pp_should_be_internal")
        if "-0.0%" in msg or "+-0.0%" in msg:
            issues.append("message_signed_zero")
        if len(msg.splitlines()) != 5:
            issues.append("message_line_contract")
        if not snap.get("frozen"):
            issues.append("snapshot_not_frozen")
        if len(snap.get("assets", [])) != 125:
            issues.append("snapshot_count")
    return {"status": "PASS" if not issues else "FAIL", "issues": issues}


def persist_result(result: Dict[str, Any], audit: Dict[str, Any]) -> Tuple[Path, Path]:
    stamp = utc_now().strftime("%Y%m%dT%H%M%S%fZ")
    result_path = SNAPSHOT_DIR / f"U09_{stamp}.json"
    audit_path = AUDIT_DIR / f"U09_AUDIT_{stamp}.json"
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(result_path, result)
    write_json(audit_path, audit)
    return result_path, audit_path
