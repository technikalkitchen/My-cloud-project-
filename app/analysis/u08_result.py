"""Stage 8 (U08) Cell 8 result dataclass and serialization.

Mirrors Kitchen Assistant v3.1.4.ipynb Cell 8 `Cell08Result` dataclass
and `cell08_to_dict` / `cell08_to_json` serialization helpers.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List
import json


@dataclass(frozen=True)
class Cell08Result:
    """Structured output of Cell 8 (BTC + BTC.D Context & Relative-Movement Engine).

    All fields are deterministic and analysis-only. No trading/order/strategy
    fields are included. Hard safety locks are reflected in the audit dict.
    """

    engine: str
    version: str
    timestamp_utc: str

    scenario_id: int
    scenario_type: str

    btc_direction: str
    btc_d_direction: str

    context: str

    opposite_direction: bool

    selected_pattern: Dict[str, str]

    top_10_assets: List[Dict[str, Any]]
    strong_movers: List[Dict[str, Any]]
    relative_movers: List[Dict[str, Any]]

    altcoin_structure: Dict[str, Any]

    audit: Dict[str, Any]


def cell08_to_dict(result: Cell08Result) -> Dict[str, Any]:
    """Serialize Cell08Result to a plain dict (dataclasses.asdict)."""
    return asdict(result)


def cell08_to_json(result: Cell08Result) -> str:
    """Serialize Cell08Result to JSON string (Persian-safe, indented)."""
    return json.dumps(
        cell08_to_dict(result),
        ensure_ascii=False,
        indent=2,
    )