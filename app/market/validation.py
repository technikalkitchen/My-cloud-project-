"""U09 — Provider asset validation and freshness.

validate_provider_assets: rank coverage, duplicate detection, numeric
validation, rank consistency, coverage enforcement.

freshness_status: FRESH / STALE / UNAVAILABLE with age in seconds.

Layer A only. Layer B (segmentation, dominance, relative strength) is NOT here.
"""
from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.config.market_universe import CONFIG


def validate_provider_assets(assets: List[Dict[str, Any]], limit: int) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []
    ids: List[str] = []
    ranks: List[int] = []
    symbols: Dict[str, List[str]] = {}
    valid: List[Dict[str, Any]] = []

    for i, a in enumerate(assets):
        aid = a.get("provider_asset_id")
        rank = a.get("provider_rank")
        sym = str(a.get("symbol") or "").upper()
        if not aid:
            errors.append(f"missing_id_at_{i}")
            continue
        if not isinstance(rank, int) or isinstance(rank, bool):
            try:
                rank = int(rank)
            except Exception:
                errors.append(f"invalid_rank_{aid}")
                continue
        if rank < 1 or rank > limit:
            errors.append(f"rank_out_of_range_{aid}:{rank}")
            continue
        if not finite_nonnegative(a.get("price_usd")):
            errors.append(f"invalid_price_{aid}")
            continue
        if not finite_nonnegative(a.get("market_cap_usd")):
            errors.append(f"invalid_market_cap_{aid}")
            continue
        if aid in ids:
            errors.append(f"duplicate_id_{aid}")
            continue
        ids.append(aid)
        if rank in ranks:
            errors.append(f"duplicate_rank_{rank}")
        ranks.append(rank)
        if sym:
            symbols.setdefault(sym, []).append(aid)
        b = dict(a)
        b["provider_rank"] = rank
        valid.append(b)

    for sym, aids in symbols.items():
        if len(aids) > 1:
            warnings.append(f"symbol_collision_{sym}:{len(aids)}")

    rank_set = set(ranks)
    missing = [r for r in range(1, limit + 1) if r not in rank_set]
    if missing:
        errors.append("rank_gaps:" + ",".join(map(str, missing[:20])))

    valid.sort(key=lambda x: x["provider_rank"])
    calculated = sorted(valid, key=lambda x: (-float(x["market_cap_usd"]), str(x["provider_asset_id"])))
    calc_rank = {a["provider_asset_id"]: i + 1 for i, a in enumerate(calculated)}
    for a in valid:
        cr = calc_rank.get(a["provider_asset_id"])
        a["calculated_rank"] = cr
        diff = abs(int(a["provider_rank"]) - int(cr)) if cr is not None else 999
        a["rank_difference"] = diff
        if diff == 0:
            a["rank_consistency_status"] = "MATCH"
        elif diff <= CONFIG["rank_minor_difference"]:
            a["rank_consistency_status"] = "MINOR_DIFFERENCE"
        elif diff <= CONFIG["rank_warning_difference"]:
            a["rank_consistency_status"] = "WARNING"
            warnings.append(f"rank_warning_{a['provider_asset_id']}:{diff}")
        else:
            a["rank_consistency_status"] = "FAIL"
            errors.append(f"rank_fail_{a['provider_asset_id']}:{diff}")

    coverage = len(set(ranks)) / float(limit)
    if len(valid) != limit:
        errors.append(f"coverage_count_{len(valid)}_expected_{limit}")

    status = "PASS" if not errors else "FAIL"
    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "valid_assets": valid,
        "coverage_ratio": coverage,
        "calculated_rank_count": len(calc_rank),
    }


def finite_nonnegative(value: Any) -> bool:
    try:
        x = float(value)
        return math.isfinite(x) and x >= 0.0
    except Exception:
        return False


def freshness_status(
    provider_ts: Optional[datetime],
    now: datetime,
) -> Tuple[str, Optional[float]]:
    if not provider_ts:
        return "UNAVAILABLE", None
    age = max(0.0, (now - provider_ts).total_seconds())
    if age <= CONFIG["max_current_age_seconds"]:
        return "FRESH", age
    return "STALE", age
