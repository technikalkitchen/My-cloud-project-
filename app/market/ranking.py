"""U06.5 Unit 8 — Dynamic market-cap ranking + Kitchen index engine.

Deterministic market-cap ranking with a fixed tie-break rule, and the
Kitchen family of indices (KITCHEN_TOTAL_TOP125, TOTAL2, TOTAL3, Others.D,
BTC.D, ETH.D, USDT.D).

No market-cap, supply, price, or dominance data is fabricated. Rankings are
deterministic: market_cap descending, then canonical_asset_id ascending, then
symbol ascending.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.core.u06_5 import deep_copy, safe_float, safe_int
from app.config.quality import (
    CORE_ASSETS,
    TARGET_CANDIDATE_POOL,
    TOP_N,
)
from app.config.exchanges import (
    MIN_VALIDATED_EXCHANGE_COUNT,
)

INDEX_VERSION = "KITCHEN_INDEX_V1"
RANKING_VERSION = "KITCHEN_RANKING_V1"


def deterministic_sort_key(record: Dict[str, Any]) -> Tuple[float, str, str]:
    """Deterministic sort: market-cap desc, canonical_asset_id asc, symbol asc."""
    mc = safe_float(record.get("market_cap"))
    asset_id = record.get("canonical_asset_id") or record.get("provider_asset_id") or ""
    symbol = str(record.get("symbol") or "").upper()
    return (-(mc if mc is not None else -1.0), str(asset_id), symbol)


def dynamic_rank_assets(
    valid_assets: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    """Rank validated asset records by market cap with deterministic tie-break.

    Only records with a non-negative, finite market_cap are candidates. The
    tie-break is market_cap desc → canonical_asset_id asc → symbol asc.
    """
    candidates = [
        deep_copy(x)
        for x in valid_assets
        if safe_float(x.get("market_cap")) is not None
        and safe_float(x.get("market_cap")) >= 0
    ]

    candidates.sort(key=deterministic_sort_key)

    ranked: List[Dict[str, Any]] = []
    for rank, asset in enumerate(candidates, start=1):
        item = deep_copy(asset)
        item["calculated_rank"] = rank
        item["ranking_version"] = RANKING_VERSION
        ranked.append(item)

    top125 = ranked[:TOP_N]

    for item in top125:
        provider_rank = safe_int(item.get("provider_rank"))
        calculated_rank = safe_int(item.get("calculated_rank"))
        if provider_rank is None:
            consistency = "UNAVAILABLE"
        else:
            diff = abs(provider_rank - calculated_rank)
            consistency = (
                "MATCH" if diff == 0
                else "MINOR_DIFFERENCE" if diff <= 2
                else "WARNING"
            )
        item["rank_consistency"] = consistency

        r = item["calculated_rank"]
        item["segment"] = (
            "BTC" if r == 1
            else "ETH" if r == 2
            else "TOP10_ALT" if r <= 10
            else "BROAD_ALT_11_125"
        )

    return {
        "status": (
            "VALIDATED" if len(top125) == TOP_N
            else "DATA_PARTIAL"
        ),
        "candidate_requested": TARGET_CANDIDATE_POOL,
        "candidate_received": len(valid_assets),
        "candidate_valid": len(candidates),
        "candidate_invalid": max(0, len(valid_assets) - len(candidates)),
        "candidate_excluded": max(0, len(candidates) - TOP_N),
        "candidate_coverage_ratio": (
            len(candidates) / TARGET_CANDIDATE_POOL
            if TARGET_CANDIDATE_POOL else 0.0
        ),
        "ranking_version": RANKING_VERSION,
        "tie_break_rule": (
            "market_cap_desc, canonical_asset_id_asc, symbol_asc"
        ),
        "all_valid_ranked": ranked,
        "top125": top125,
    }


def calculate_indices_from_top125(
    top125: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    """Calculate Kitchen market-cap indices from the validated Top-125.

    KITCHEN_TOTAL_TOP125 = SUM(market_cap of ranks 1-125)
    KITCHEN_TOTAL2       = KITCHEN_TOTAL_TOP125 - BTC
    KITCHEN_TOTAL3       = KITCHEN_TOTAL_TOP125 - BTC - ETH
    KITCHEN_OTHERS       = SUM(market_cap of ranks 11-125)
    KITCHEN_BTC_D        = BTC / KITCHEN_TOTAL_TOP125 * 100
    KITCHEN_ETH_D        = ETH / KITCHEN_TOTAL_TOP125 * 100
    KITCHEN_USDT_D       = USDT / KITCHEN_TOTAL_TOP125 * 100
    KITCHEN_OTHERS_D     = KITCHEN_OTHERS / KITCHEN_TOTAL_TOP125 * 100
    """
    if len(top125) != TOP_N:
        return {
            "status": "DATA_PARTIAL",
            "reason": "TOP125_NOT_COMPLETE",
            "formula_version": INDEX_VERSION,
            "values": {},
        }

    by_symbol = {
        str(asset.get("symbol") or "").upper(): asset
        for asset in top125
    }

    if any(symbol not in by_symbol for symbol in CORE_ASSETS.values()):
        return {
            "status": "DATA_UNAVAILABLE",
            "reason": "CORE_ASSET_MISSING",
            "formula_version": INDEX_VERSION,
            "values": {},
        }

    if any(
        safe_float(asset.get("market_cap")) is None
        for asset in top125
    ):
        return {
            "status": "DATA_PARTIAL",
            "reason": "MARKET_CAP_INVALID",
            "formula_version": INDEX_VERSION,
            "values": {},
        }

    total = sum(float(asset["market_cap"]) for asset in top125)
    btc = float(by_symbol["BTC"]["market_cap"])
    eth = float(by_symbol["ETH"]["market_cap"])
    usdt = float(by_symbol["USDT"]["market_cap"])

    others = sum(
        float(asset["market_cap"])
        for asset in top125
        if safe_int(asset.get("calculated_rank")) is not None
        and asset["calculated_rank"] >= 11
    )

    def dominance(numerator: float, denominator: float) -> Optional[float]:
        return numerator / denominator * 100.0 if denominator > 0 else None

    values = {
        "KITCHEN_TOTAL_TOP125": total,
        "KITCHEN_TOTAL2": total - btc,
        "KITCHEN_TOTAL3": total - btc - eth,
        "KITCHEN_OTHERS": others,
        "KITCHEN_BTC_D": dominance(btc, total),
        "KITCHEN_ETH_D": dominance(eth, total),
        "KITCHEN_USDT_D": dominance(usdt, total),
        "KITCHEN_OTHERS_D": dominance(others, total),
    }

    manifests: Dict[str, Any] = {}
    for metric, formula in {
        "KITCHEN_TOTAL_TOP125": "SUM(MARKET_CAP of calculated ranks 1-125)",
        "KITCHEN_TOTAL2": "KITCHEN_TOTAL_TOP125 - BTC_MARKET_CAP",
        "KITCHEN_TOTAL3": (
            "KITCHEN_TOTAL_TOP125 - BTC_MARKET_CAP - ETH_MARKET_CAP"
        ),
        "KITCHEN_OTHERS": (
            "SUM(MARKET_CAP of calculated ranks 11-125)"
        ),
        "KITCHEN_BTC_D": (
            "BTC_MARKET_CAP / KITCHEN_TOTAL_TOP125 * 100"
        ),
        "KITCHEN_ETH_D": (
            "ETH_MARKET_CAP / KITCHEN_TOTAL_TOP125 * 100"
        ),
        "KITCHEN_USDT_D": (
            "USDT_MARKET_CAP / KITCHEN_TOTAL_TOP125 * 100"
        ),
        "KITCHEN_OTHERS_D": (
            "KITCHEN_OTHERS / KITCHEN_TOTAL_TOP125 * 100"
        ),
    }.items():
        output = values[metric]
        manifests[metric] = {
            "formula_id": f"{INDEX_VERSION}:{metric}",
            "formula": formula,
            "inputs": {
                "top125_members": [
                    {
                        "canonical_asset_id": x.get("canonical_asset_id"),
                        "rank": x.get("calculated_rank"),
                        "market_cap": x.get("market_cap"),
                    }
                    for x in top125
                ]
            },
            "input_timestamp": sorted({
                str(x.get("source_timestamp"))
                for x in top125
                if x.get("source_timestamp")
            }),
            "input_provenance": "U06.5_VALIDATED_TOP125",
            "calculation_version": INDEX_VERSION,
            "processor": "KITCHEN_U06_5",
            "output": output,
            "validation_status": (
                "VALID"
                if output is not None and math.isfinite(float(output))
                else "INVALID"
            ),
        }

    return {
        "status": "CALCULATED",
        "calculated_by": "KITCHEN",
        "formula_version": INDEX_VERSION,
        "values": values,
        "manifests": manifests,
        "tradingview_value_used": False,
    }
