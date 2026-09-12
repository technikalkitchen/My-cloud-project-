"""Stage 8 (U08) Unit 0 — Cell 08 configuration."""
from __future__ import annotations

import pytest

from app.analysis.u08_config import Cell08Config, CELL08_CONFIG


def test_config_is_dataclass_instance():
    assert isinstance(CELL08_CONFIG, Cell08Config)


def test_default_config_values():
    assert CELL08_CONFIG.top_n == 10
    assert CELL08_CONFIG.strong_movers_n == 10
    assert CELL08_CONFIG.relative_movers_n == 10


def test_default_thresholds():
    assert CELL08_CONFIG.min_valid_price_change_pct == 0.0
    assert CELL08_CONFIG.relative_strength_epsilon_pct == 0.0


def test_default_flags():
    assert CELL08_CONFIG.require_finite_values is True
    assert CELL08_CONFIG.include_btc_in_top_assets is True
    assert CELL08_CONFIG.include_btc_in_strong_movers is True
    assert CELL08_CONFIG.volume_required is True


def test_config_is_frozen():
    with pytest.raises((AttributeError, TypeError)):
        CELL08_CONFIG.top_n = 99  # type: ignore[misc]


def test_custom_config_override():
    custom = Cell08Config(volume_required=False, strong_movers_n=3)
    assert custom.volume_required is False
    assert custom.strong_movers_n == 3
    # unmentioned fields keep their defaults
    assert custom.top_n == 10


def test_config_instances_are_independent():
    a = Cell08Config(top_n=5)
    b = CELL08_CONFIG
    assert a.top_n == 5
