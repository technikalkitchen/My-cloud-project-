from pathlib import Path
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import json
import tempfile
import shutil
import pytest

from app.data.validation.u06_quality_gate import (
    SYMBOLS,
    INTERVAL,
    EXPECTED_RECORDS_PER_SYMBOL,
    EXPECTED_TOTAL_RECORDS,
    REQUIRED_FIELDS,
    sha256_file,
    numeric,
    validate_ohlc,
    load_jsonl,
    run_u06_validation,
)


def _make_valid_record(
    timestamp: int,
    symbol: str = "BTCUSDT",
    provider: str = "BINANCE_SPOT_PUBLIC",
) -> dict:
    return {
        "project": "KITCHEN_ASSISTANT",
        "version": "3.1",
        "execution_unit": "U05",
        "asset_type": "ASSET",
        "symbol": symbol,
        "provider": provider,
        "exchange": provider,
        "provider_symbol": symbol,
        "interval": "1m",
        "timestamp": timestamp,
        "open": 50000.0,
        "high": 50100.0,
        "low": 49900.0,
        "close": 50050.0,
        "volume_base": 100.0,
        "volume_definition": "TOTAL_TRADED_BASE_ASSET_VOLUME",
        "volume_source": "PROVIDER_SUPPLIED",
        "volume_counting_rule": "EACH_TRADE_COUNTED_ONCE",
        "volume_double_counting": False,
        "buyer_seller_not_double_counted": True,
        "volume_usd": 5000000.0,
        "volume_usd_exact": True,
        "volume_usd_source": "BINANCE_KLINE_QUOTE_VOLUME",
        "total_series_included": False,
        "trading_enabled": False,
        "orders_enabled": False,
        "strategy_enabled": False,
    }


def _create_test_dataset(tmp_path: Path, provider: str = "BINANCE_SPOT_PUBLIC") -> Path:
    dataset_root = tmp_path / "data" / "historical_u05"
    raw_dir = dataset_root / "raw"
    normalized_dir = dataset_root / "normalized"
    manifest_dir = dataset_root / "manifests"
    quality_dir = dataset_root / "quality"
    ledger_dir = tmp_path / "ledgers"

    for d in [raw_dir, normalized_dir, manifest_dir, quality_dir, ledger_dir]:
        d.mkdir(parents=True, exist_ok=True)

    base_ts = 1700000000000
    all_records = []

    for symbol in SYMBOLS:
        records = [
            _make_valid_record(base_ts + i * 60000, symbol, provider)
            for i in range(EXPECTED_RECORDS_PER_SYMBOL)
        ]
        all_records.extend(records)

        raw_file = raw_dir / f"{symbol}_{INTERVAL}.json"
        raw_file.write_text(json.dumps(records), encoding="utf-8")

        normalized_file = normalized_dir / f"{symbol}_{INTERVAL}.jsonl"
        with normalized_file.open("w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")

    dataset_index = {
        "project": "KITCHEN_ASSISTANT",
        "version": "3.1",
        "execution_unit": "U05",
        "symbols": SYMBOLS,
        "interval": INTERVAL,
        "candles_per_symbol": EXPECTED_RECORDS_PER_SYMBOL,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
    index_file = dataset_root / "DATASET_INDEX.json"
    index_file.write_text(json.dumps(dataset_index, indent=2), encoding="utf-8")

    capture_manifest = {
        "project": "KITCHEN_ASSISTANT",
        "version": "3.1",
        "execution_unit": "U05",
        "capture_mode": "MULTI_SYMBOL_PRIORITY",
        "symbols": SYMBOLS,
        "interval": INTERVAL,
        "candles_per_symbol": EXPECTED_RECORDS_PER_SYMBOL,
        "provider_priority": ["BINANCE_SPOT_PUBLIC", "COINBASE_EXCHANGE_PUBLIC"],
        "results": {s: {"provider": provider, "records": EXPECTED_RECORDS_PER_SYMBOL} for s in SYMBOLS},
        "trading_enabled": False,
        "orders_enabled": False,
        "strategy_enabled": False,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
    manifest_file = manifest_dir / "U05_CAPTURE_MANIFEST.json"
    manifest_file.write_text(json.dumps(capture_manifest, indent=2), encoding="utf-8")

    quality_report = {
        "project": "KITCHEN_ASSISTANT",
        "version": "3.1",
        "execution_unit": "U05",
        "symbols": SYMBOLS,
        "validation": "PASSED",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
    quality_file = quality_dir / "U05_DATA_QUALITY_REPORT.json"
    quality_file.write_text(json.dumps(quality_report, indent=2), encoding="utf-8")

    hash_inventory = {}
    for symbol in SYMBOLS:
        for path in [raw_dir / f"{symbol}_{INTERVAL}.json", normalized_dir / f"{symbol}_{INTERVAL}.jsonl"]:
            rel = path.relative_to(tmp_path)
            hash_inventory[str(rel)] = sha256_file(path)
    for path in [index_file, manifest_file, quality_file]:
        rel = path.relative_to(tmp_path)
        hash_inventory[str(rel)] = sha256_file(path)

    sha256_file_path = dataset_root / "U05_SHA256.json"
    sha256_file_path.write_text(json.dumps(hash_inventory, indent=2), encoding="utf-8")

    return dataset_root, quality_dir, ledger_dir


def test_sha256_file(tmp_path: Path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world", encoding="utf-8")
    expected = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    assert sha256_file(test_file) == expected


def test_numeric_valid():
    assert numeric("100", "test") == Decimal("100")
    assert numeric(50.5, "test") == Decimal("50.5")
    assert numeric(0.001, "test") == Decimal("0.001")


def test_numeric_invalid():
    with pytest.raises(ValueError):
        numeric("abc", "test")


def test_validate_ohlc_valid():
    record = {
        "open": "50000",
        "high": "50100",
        "low": "49900",
        "close": "50050",
        "volume_base": "100",
    }
    assert validate_ohlc(record) is None


def test_validate_ohlc_invalid_open():
    record = {"open": "0", "high": "50100", "low": "49900", "close": "50050", "volume_base": "100"}
    assert validate_ohlc(record) == "open_not_positive"


def test_validate_ohlc_high_less_than_low():
    record = {"open": "50000", "high": "49000", "low": "50000", "close": "50050", "volume_base": "100"}
    assert validate_ohlc(record) == "high_less_than_low"


def test_validate_ohlc_open_outside_range():
    record = {"open": "51000", "high": "50100", "low": "49900", "close": "50050", "volume_base": "100"}
    assert validate_ohlc(record) == "open_outside_range"


def test_validate_ohlc_negative_volume():
    record = {"open": "50000", "high": "50100", "low": "49900", "close": "50050", "volume_base": "-10"}
    assert validate_ohlc(record) == "negative_volume_base"


def test_load_jsonl_valid(tmp_path: Path):
    file = tmp_path / "test.jsonl"
    records = [{"a": 1}, {"b": 2}]
    file.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    loaded, errors = load_jsonl(file)
    assert len(loaded) == 2
    assert len(errors) == 0


def test_load_jsonl_invalid_json(tmp_path: Path):
    file = tmp_path / "test.jsonl"
    file.write_text('{"a": 1}\ninvalid\n{"b": 2}\n', encoding="utf-8")
    loaded, errors = load_jsonl(file)
    assert len(loaded) == 2
    assert len(errors) == 1
    assert errors[0]["error"] == "invalid_json"


def test_run_u06_validation_pass(tmp_path: Path):
    dataset_root, quality_dir, ledger_dir = _create_test_dataset(tmp_path)

    result = run_u06_validation(dataset_root, quality_dir, ledger_dir)

    assert result["validation_status"] == "PASS"
    assert result["technical_lock"] is True
    assert result["final_check"]["u05_control_artifacts"] is True
    assert result["final_check"]["record_count"] is True
    assert result["final_check"]["symbol_coverage"] is True


def test_run_u06_validation_missing_control_artifacts(tmp_path: Path):
    dataset_root = tmp_path / "data" / "historical_u05"
    quality_dir = dataset_root / "quality"
    ledger_dir = tmp_path / "ledgers"
    dataset_root.mkdir(parents=True)
    quality_dir.mkdir(parents=True)
    ledger_dir.mkdir(parents=True)

    with pytest.raises(RuntimeError, match="U05 CONTROL ARTIFACTS MISSING"):
        run_u06_validation(dataset_root, quality_dir, ledger_dir)


def test_run_u06_validation_invalid_index(tmp_path: Path):
    dataset_root, quality_dir, ledger_dir = _create_test_dataset(tmp_path)

    index_file = dataset_root / "DATASET_INDEX.json"
    bad_index = {"execution_unit": "U04", "symbols": SYMBOLS}
    index_file.write_text(json.dumps(bad_index), encoding="utf-8")

    with pytest.raises(RuntimeError, match="execution_unit is not U05"):
        run_u06_validation(dataset_root, quality_dir, ledger_dir)


def test_run_u06_validation_symbol_mismatch(tmp_path: Path):
    dataset_root, quality_dir, ledger_dir = _create_test_dataset(tmp_path)

    index_file = dataset_root / "DATASET_INDEX.json"
    bad_index = {"execution_unit": "U05", "symbols": ["BTCUSDT", "ETHUSDT"]}
    index_file.write_text(json.dumps(bad_index), encoding="utf-8")

    with pytest.raises(RuntimeError, match="symbol list does not match"):
        run_u06_validation(dataset_root, quality_dir, ledger_dir)


def test_run_u06_validation_record_count_mismatch(tmp_path: Path):
    dataset_root, quality_dir, ledger_dir = _create_test_dataset(tmp_path)

    symbol = "BTCUSDT"
    normalized_file = dataset_root / "normalized" / f"{symbol}_{INTERVAL}.jsonl"
    records = [_make_valid_record(1700000000000 + i * 60000, symbol) for i in range(50)]
    with normalized_file.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    result = run_u06_validation(dataset_root, quality_dir, ledger_dir)

    assert result["validation_status"] == "FAIL"
    assert result["technical_lock"] is False


def test_run_u06_validation_missing_volume_base(tmp_path: Path):
    dataset_root, quality_dir, ledger_dir = _create_test_dataset(tmp_path)

    symbol = "BTCUSDT"
    normalized_file = dataset_root / "normalized" / f"{symbol}_{INTERVAL}.jsonl"
    records = [
        _make_valid_record(1700000000000 + i * 60000, symbol) for i in range(EXPECTED_RECORDS_PER_SYMBOL)
    ]
    records[0].pop("volume_base")
    with normalized_file.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    result = run_u06_validation(dataset_root, quality_dir, ledger_dir)

    assert result["validation_status"] == "FAIL"
    btc_report = next(r for r in result["quality_report"]["symbol_reports"] if r["symbol"] == "BTCUSDT")
    assert any(p["type"] == "missing_fields" for p in btc_report["problems"])


def test_run_u06_validation_wrong_volume_source(tmp_path: Path):
    dataset_root, quality_dir, ledger_dir = _create_test_dataset(tmp_path)

    symbol = "BTCUSDT"
    normalized_file = dataset_root / "normalized" / f"{symbol}_{INTERVAL}.jsonl"
    records = [
        _make_valid_record(1700000000000 + i * 60000, symbol) for i in range(EXPECTED_RECORDS_PER_SYMBOL)
    ]
    records[0]["volume_source"] = "ESTIMATED"
    with normalized_file.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    result = run_u06_validation(dataset_root, quality_dir, ledger_dir)

    assert result["validation_status"] == "FAIL"
    btc_report = next(r for r in result["quality_report"]["symbol_reports"] if r["symbol"] == "BTCUSDT")
    assert any(p["type"] == "invalid_volume_source" for p in btc_report["problems"])


def test_run_u06_validation_trading_enabled(tmp_path: Path):
    dataset_root, quality_dir, ledger_dir = _create_test_dataset(tmp_path)

    symbol = "BTCUSDT"
    normalized_file = dataset_root / "normalized" / f"{symbol}_{INTERVAL}.jsonl"
    records = [
        _make_valid_record(1700000000000 + i * 60000, symbol) for i in range(EXPECTED_RECORDS_PER_SYMBOL)
    ]
    records[0]["trading_enabled"] = True
    with normalized_file.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    result = run_u06_validation(dataset_root, quality_dir, ledger_dir)

    assert result["validation_status"] == "FAIL"
    assert result["quality_report"]["safety"]["trading_disabled"] is False


def test_run_u06_validation_sha_mismatch(tmp_path: Path):
    dataset_root, quality_dir, ledger_dir = _create_test_dataset(tmp_path)

    sha256_file_path = dataset_root / "U05_SHA256.json"
    hash_inventory = json.loads(sha256_file_path.read_text(encoding="utf-8"))
    hash_inventory["data/historical_u05/raw/BTCUSDT_1m.json"] = "deadbeef"
    sha256_file_path.write_text(json.dumps(hash_inventory, indent=2), encoding="utf-8")

    result = run_u06_validation(dataset_root, quality_dir, ledger_dir)

    assert result["validation_status"] == "FAIL"
    assert result["quality_report"]["sha256"]["valid"] is False


def test_run_u06_validation_coinbase_gaps_tolerated(tmp_path: Path):
    dataset_root, quality_dir, ledger_dir = _create_test_dataset(tmp_path, "COINBASE_EXCHANGE_PUBLIC")

    symbol = "BTCUSDT"
    normalized_file = dataset_root / "normalized" / f"{symbol}_{INTERVAL}.jsonl"
    records = [
        _make_valid_record(1700000000000 + i * 60000, symbol, "COINBASE_EXCHANGE_PUBLIC")
        for i in range(EXPECTED_RECORDS_PER_SYMBOL)
    ]
    records[50]["timestamp"] = records[50]["timestamp"] + 120000
    with normalized_file.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    result = run_u06_validation(dataset_root, quality_dir, ledger_dir)

    btc_report = next(r for r in result["quality_report"]["symbol_reports"] if r["symbol"] == "BTCUSDT")
    gap_problems = [p for p in btc_report["problems"] if p["type"] == "timestamp_gaps_tolerated_coinbase"]
    assert len(gap_problems) == 1
    assert btc_report["hard_problem_count"] == 0
    assert btc_report["status"] == "PASS"


def test_constants():
    assert SYMBOLS == ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT"]
    assert INTERVAL == "1m"
    assert EXPECTED_RECORDS_PER_SYMBOL == 100
    assert EXPECTED_TOTAL_RECORDS == 500
    assert len(REQUIRED_FIELDS) == 27
    assert "volume_base" in REQUIRED_FIELDS
    assert "volume" not in REQUIRED_FIELDS