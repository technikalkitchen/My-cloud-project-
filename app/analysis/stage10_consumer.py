"""Stage 10 — Dynamic Top-10 Market-Cap View.

Unit 10.1 — Stage Contract + Dynamic Top-10 Consumer.

Consumes existing U06.5 ranking (dynamic_rank_assets) to select
current Kitchen Dynamic Top-125 ranks 2-10, excluding BTC rank 1.

No independent exchange/CMC ranking is introduced. The Top-10
is computed fresh on every request — no persistent cache.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from app.market.ranking import dynamic_rank_assets
from app.config.quality import TOP_N


class View(Enum):
    KITCHEN = "KITCHEN"
    EXCHANGE = "EXCHANGE"


class Exchange(Enum):
    BINANCE = "Binance"
    OKX = "OKX"
    BYBIT = "Bybit"
    KUCOIN = "KuCoin"
    COINBASE = "Coinbase"
    GATE = "Gate"
    UPBIT = "Upbit"
    BITGET = "Bitget"


DISPLAY_FALLBACK_PRIORITY: List[Exchange] = [
    Exchange.BINANCE,
    Exchange.OKX,
    Exchange.BYBIT,
    Exchange.KUCOIN,
    Exchange.COINBASE,
    Exchange.GATE,
    Exchange.UPBIT,
    Exchange.BITGET,
]


@dataclass
class Stage10Config:
    view: View = View.KITCHEN
    selected_exchange: Optional[Exchange] = None
    timeframe: str = "5m"
    min_ranks: int = 2
    max_ranks: int = 10


@dataclass
class RankedAsset:
    kitchen_rank: int
    symbol: str
    market_cap: float
    canonical_asset_id: str
    segment: str
    provider_rank: Optional[int]
    rank_consistency: str
    calculated_rank: int
    ranking_version: str


@dataclass
class Stage10Result:
    view: str
    selected_exchange: Optional[str]
    display_fallback_priority: List[str]
    timeframe: str
    ranking_version: str
    assets: List[Dict[str, Any]] = field(default_factory=list)
    raw_ranking_status: str = ""
    total_ranked: int = 0


def _asset_to_dict(asset: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "kitchen_rank": int(asset.get("calculated_rank", 0)),
        "symbol": str(asset.get("symbol", "")),
        "market_cap": float(asset.get("market_cap", 0.0)),
        "canonical_asset_id": str(asset.get("canonical_asset_id", "")),
        "segment": str(asset.get("segment", "")),
        "provider_rank": asset.get("provider_rank"),
        "rank_consistency": str(asset.get("rank_consistency", "UNAVAILABLE")),
        "calculated_rank": int(asset.get("calculated_rank", 0)),
        "ranking_version": str(asset.get("ranking_version", "")),
    }


def select_ranks(
    ranked_assets: List[Dict[str, Any]],
    min_rank: int = 2,
    max_rank: int = 10,
) -> List[Dict[str, Any]]:
    """Select assets within a rank range from a pre-computed ranking.

    Computes dynamically — no caching. The caller is responsible for
    invoking dynamic_rank_assets fresh when a re-computation is needed.
    """
    result: List[Dict[str, Any]] = []
    for asset in ranked_assets:
        rank = asset.get("calculated_rank")
        if rank is None:
            continue
        r: int = int(rank)
        if min_rank <= r <= max_rank:
            result.append(_asset_to_dict(asset))
    return result


def get_dynamic_top10(
    valid_assets: List[Dict[str, Any]],
    view: str = "KITCHEN",
    selected_exchange: Optional[str] = None,
    timeframe: str = "5m",
) -> Stage10Result:
    """Compute Stage 10 Dynamic Top-10 from valid assets.

    Consumes U06.5 dynamic_rank_assets on every call — no stale cache.
    Selects ranks 2-10, excluding BTC rank 1.

    Args:
        valid_assets: List of asset dicts with market_cap.
        view: "KITCHEN" or "EXCHANGE".
        selected_exchange: Optional preferred exchange for Exchange view.
        timeframe: Timeframe for data window.

    Returns:
        Stage10Result with ranks 2-10 assets.
    """
    ranking = dynamic_rank_assets(valid_assets)

    assets: List[Dict[str, Any]] = []
    for asset in ranking.get("top125", []):
        rank = asset.get("calculated_rank")
        if rank is None:
            continue
        r: int = int(rank)
        if 2 <= r <= 10:
            assets.append(_asset_to_dict(asset))

    exchange_names: List[str] = [e.value for e in DISPLAY_FALLBACK_PRIORITY]

    return Stage10Result(
        view=view,
        selected_exchange=selected_exchange,
        display_fallback_priority=exchange_names,
        timeframe=timeframe,
        ranking_version=ranking.get("ranking_version", ""),
        assets=assets,
        raw_ranking_status=ranking.get("status", ""),
        total_ranked=len(ranking.get("top125", [])),
    )
