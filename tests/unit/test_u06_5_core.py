from datetime import datetime, timezone

import pytest

from app.core.u06_5 import (
    canonical_bytes,
    deep_copy,
    parse_timestamp,
    redact,
    resolve_root,
    safe_float,
    safe_int,
    safe_json,
    safe_name,
    sha256_bytes,
    sha256_obj,
    timestamp_age_seconds,
    utc_now,
)


def test_utc_timestamp_helpers():
    value = utc_now()
    parsed = parse_timestamp(value)

    assert parsed is not None
    assert parsed.tzinfo == timezone.utc
    assert parse_timestamp(None) is None
    assert parse_timestamp("") is None
    assert parse_timestamp("not-a-time") is None


def test_timestamp_normalization_and_age():
    source = parse_timestamp("2026-09-10T20:00:00Z")
    retrieved = parse_timestamp("2026-09-10T20:05:00+00:00")

    assert source is not None
    assert retrieved is not None
    assert source.tzinfo == timezone.utc
    assert timestamp_age_seconds(source, retrieved) == 300.0
    assert timestamp_age_seconds(retrieved, source) == 0.0
    assert timestamp_age_seconds("bad", retrieved) is None


def test_safe_numeric_helpers():
    assert safe_float("1.25") == 1.25
    assert safe_float("NaN") is None
    assert safe_float("inf") is None
    assert safe_float(object()) is None
    assert safe_int("12") == 12
    assert safe_int(True) is None
    assert safe_int("bad") is None


def test_safe_json_and_canonical_hash():
    value = {
        "b": [float("nan"), datetime(2026, 9, 10, 20, 0, tzinfo=timezone.utc)],
        "a": 2,
    }

    safe = safe_json(value)
    left = canonical_bytes({"a": 1, "b": 2})
    right = canonical_bytes({"b": 2, "a": 1})

    assert safe["b"][0] is None
    assert safe["b"][1] == "2026-09-10T20:00:00+00:00"
    assert left == right
    assert sha256_obj({"a": 1}) == sha256_bytes(canonical_bytes({"a": 1}))


def test_redaction_name_and_copy_helpers():
    value = {
        "api_key": "secret",
        "nested": {"token": "secret", "visible": [1, 2]},
    }
    copied = deep_copy(value)
    copied["nested"]["visible"].append(3)

    assert redact(value) == {
        "api_key": "[REDACTED]",
        "nested": {"token": "[REDACTED]", "visible": [1, 2]},
    }
    assert value["nested"]["visible"] == [1, 2]
    assert safe_name("BTC/USDT: market") == "BTC_USDT_market"


def test_explicit_portable_root(monkeypatch, tmp_path):
    monkeypatch.setenv("KITCHEN_ROOT", str(tmp_path))

    assert resolve_root() == tmp_path.resolve()


def test_content_paths_are_not_selected(monkeypatch, tmp_path):
    content_root = tmp_path / "content" / "project"
    content_root.mkdir(parents=True)
    monkeypatch.delenv("KITCHEN_ROOT", raising=False)
    monkeypatch.chdir(content_root)

    assert resolve_root() != content_root.resolve()
