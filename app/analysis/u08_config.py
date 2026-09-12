"""Stage 8 (U08) configuration — Cell 8 (BTC + BTC.D).

Configurable engineering parameters. These are NOT presented as universal
market truths. Mirrors the locked Cell 08 configuration from
Kitchen Assistant v3.1.4.ipynb (Cell 8 / Stage 8).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Cell08Config:
    """Cell 8 tunable parameters.

    Frozen: Cell 8 runs in analysis-only mode and its parameter surface
    is locked, mirroring the notebook's locked-state banner
    (scenarios_locked / narratives_locked / trading disabled).
    """

    top_n: int = 10
    strong_movers_n: int = 10
    relative_movers_n: int = 10

    min_valid_price_change_pct: float = 0.0

    relative_strength_epsilon_pct: float = 0.0

    require_finite_values: bool = True

    include_btc_in_top_assets: bool = True
    include_btc_in_strong_movers: bool = True

    volume_required: bool = True


CELL08_CONFIG = Cell08Config()
