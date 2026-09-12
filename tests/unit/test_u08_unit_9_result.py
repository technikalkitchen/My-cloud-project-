"""Stage 8 (U08) Unit 8.9 — Cell 8 Result Dataclass focused tests.

Covers ``Cell08Result``, ``cell08_to_dict``, ``cell08_to_json``
from ``app.analysis.u08_result``.
"""
from __future__ import annotations

import json

import pytest

from app.analysis.u08_result import Cell08Result, cell08_to_dict, cell08_to_json


def _minimal_result() -> Cell08Result:
    return Cell08Result(
        engine="CELL_08",
        version="V3.1",
        timestamp_utc="2026-01-01T00:00:00+00:00",
        scenario_id=1,
        scenario_type="BTC_UP_BTC_D_UP",
        btc_direction="INCREASE",
        btc_d_direction="INCREASE",
        context="BULLISH",
        opposite_direction=False,
        selected_pattern={
            "pattern": "Pattern 1",
            "title": "🟢 BTC Strength",
            "text": "Test narrative text.",
        },
        top_10_assets=[],
        strong_movers=[],
        relative_movers=[],
        altcoin_structure={"enabled": False, "reason": "test"},
        audit={"engine": "CELL_08", "trading_enabled": False},
    )


# ---- Cell08Result dataclass --------------------------------------------------

def test_cell08_result_all_fields_present():
    r = _minimal_result()
    assert r.engine == "CELL_08"
    assert r.version == "V3.1"
    assert r.timestamp_utc == "2026-01-01T00:00:00+00:00"
    assert r.scenario_id == 1
    assert r.scenario_type == "BTC_UP_BTC_D_UP"
    assert r.btc_direction == "INCREASE"
    assert r.btc_d_direction == "INCREASE"
    assert r.context == "BULLISH"
    assert r.opposite_direction is False
    assert r.selected_pattern["pattern"] == "Pattern 1"
    assert r.top_10_assets == []
    assert r.strong_movers == []
    assert r.relative_movers == []
    assert r.altcoin_structure["enabled"] is False
    assert r.audit["engine"] == "CELL_08"


def test_cell08_result_is_frozen():
    r = _minimal_result()
    with pytest.raises(Exception):
        r.engine = "OTHER"


def test_cell08_result_with_populated_lists():
    r = Cell08Result(
        engine="CELL_08",
        version="V3.1",
        timestamp_utc="2026-01-01T00:00:00+00:00",
        scenario_id=2,
        scenario_type="BTC_UP_BTC_D_DOWN",
        btc_direction="INCREASE",
        btc_d_direction="DECREASE",
        context="BULLISH",
        opposite_direction=True,
        selected_pattern={"pattern": "Pattern 1", "title": "Test", "text": "Text"},
        top_10_assets=[{"symbol": "ETHUSDT", "change_pct": 5.0}],
        strong_movers=[{"symbol": "SOLUSDT", "change_pct": 10.0}],
        relative_movers=[{"symbol": "XRPUSDT", "relative_btc_performance_pct": 2.0}],
        altcoin_structure={"enabled": True, "total2": {}, "total3": {}, "others_d": {}},
        audit={"engine": "CELL_08", "opposite_direction": True},
    )
    assert len(r.top_10_assets) == 1
    assert len(r.strong_movers) == 1
    assert len(r.relative_movers) == 1
    assert r.altcoin_structure["enabled"] is True


# ---- cell08_to_dict ----------------------------------------------------------

def test_cell08_to_dict_returns_plain_dict():
    r = _minimal_result()
    d = cell08_to_dict(r)
    assert isinstance(d, dict)
    assert d["engine"] == "CELL_08"
    assert d["scenario_id"] == 1
    assert d["selected_pattern"]["pattern"] == "Pattern 1"
    assert isinstance(d["top_10_assets"], list)
    assert isinstance(d["audit"], dict)


def test_cell08_to_dict_preserves_nested_structure():
    r = _minimal_result()
    d = cell08_to_dict(r)
    assert d["selected_pattern"]["title"] == "🟢 BTC Strength"
    assert d["altcoin_structure"]["reason"] == "test"


# ---- cell08_to_json ----------------------------------------------------------

def test_cell08_to_json_returns_string():
    r = _minimal_result()
    s = cell08_to_json(r)
    assert isinstance(s, str)


def test_cell08_to_json_parsable():
    r = _minimal_result()
    s = cell08_to_json(r)
    parsed = json.loads(s)
    assert parsed["engine"] == "CELL_08"
    assert parsed["scenario_id"] == 1


def test_cell08_to_json_persian_safe():
    r = Cell08Result(
        engine="CELL_08",
        version="V3.1",
        timestamp_utc="2026-01-01T00:00:00+00:00",
        scenario_id=1,
        scenario_type="BTC_UP_BTC_D_UP",
        btc_direction="INCREASE",
        btc_d_direction="INCREASE",
        context="BULLISH",
        opposite_direction=False,
        selected_pattern={
            "pattern": "Pattern 1",
            "title": "🟢 BTC Strength",
            "text": "رشد هم‌زمان BTC و BTC.D نشان می‌دهد",
        },
        top_10_assets=[],
        strong_movers=[],
        relative_movers=[],
        altcoin_structure={"enabled": False},
        audit={"engine": "CELL_08"},
    )
    s = cell08_to_json(r)
    assert "رشد هم‌زمان BTC و BTC.D" in s
    assert "🟢 BTC Strength" in s


def test_cell08_to_json_indented():
    r = _minimal_result()
    s = cell08_to_json(r)
    assert "\n" in s  # indented output has newlines


def test_cell08_to_json_roundtrip():
    r = _minimal_result()
    s = cell08_to_json(r)
    parsed = json.loads(s)
    assert parsed["engine"] == r.engine
    assert parsed["scenario_id"] == r.scenario_id
    assert parsed["selected_pattern"]["pattern"] == r.selected_pattern["pattern"]
    assert parsed["top_10_assets"] == r.top_10_assets