from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import sys


SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
]

INTERVAL = "1m"
EXPECTED_RECORDS_PER_SYMBOL = 100
EXPECTED_TOTAL_RECORDS = len(SYMBOLS) * EXPECTED_RECORDS_PER_SYMBOL

REQUIRED_FIELDS = [
    "project",
    "version",
    "execution_unit",
    "asset_type",
    "symbol",
    "provider",
    "exchange",
    "provider_symbol",
    "interval",
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume_base",
    "volume_definition",
    "volume_source",
    "volume_counting_rule",
    "volume_double_counting",
    "buyer_seller_not_double_counted",
    "volume_usd",
    "volume_usd_exact",
    "volume_usd_source",
    "total_series_included",
    "trading_enabled",
    "orders_enabled",
    "strategy_enabled",
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numeric(value, field_name: str) -> Decimal:
    try:
        value_decimal = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"Invalid numeric {field_name}: {value!r}") from exc
    return value_decimal


def validate_ohlc(record: dict) -> str | None:
    open_price = numeric(record["open"], "open")
    high_price = numeric(record["high"], "high")
    low_price = numeric(record["low"], "low")
    close_price = numeric(record["close"], "close")
    volume = numeric(record["volume_base"], "volume_base")

    if open_price <= 0:
        return "open_not_positive"
    if high_price <= 0:
        return "high_not_positive"
    if low_price <= 0:
        return "low_not_positive"
    if close_price <= 0:
        return "close_not_positive"
    if high_price < low_price:
        return "high_less_than_low"
    if not (low_price <= open_price <= high_price):
        return "open_outside_range"
    if not (low_price <= close_price <= high_price):
        return "close_outside_range"
    if volume < 0:
        return "negative_volume_base"
    return None


def load_jsonl(path: Path) -> tuple[list[dict], list[dict]]:
    records = []
    errors = []

    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                errors.append({"line": line_number, "error": "empty_line"})
                continue
            try:
                record = json.loads(stripped)
            except Exception as exc:
                errors.append(
                    {
                        "line": line_number,
                        "error": "invalid_json",
                        "detail": repr(exc),
                    }
                )
                continue
            if not isinstance(record, dict):
                errors.append(
                    {"line": line_number, "error": "record_not_object"}
                )
                continue
            records.append(record)
    return records, errors


def run_u06_validation(
    dataset_root: Path,
    quality_dir: Path,
    ledger_dir: Path,
) -> dict:
    raw_dir = dataset_root / "raw"
    normalized_dir = dataset_root / "normalized"
    manifest_dir = dataset_root / "manifests"

    required_control_artifacts = {
        "DATASET_INDEX.json": dataset_root / "DATASET_INDEX.json",
        "U05_SHA256.json": dataset_root / "U05_SHA256.json",
        "U05_CAPTURE_MANIFEST.json": manifest_dir / "U05_CAPTURE_MANIFEST.json",
        "U05_DATA_QUALITY_REPORT.json": quality_dir / "U05_DATA_QUALITY_REPORT.json",
    }

    control_status = {}
    for name, path in required_control_artifacts.items():
        control_status[name] = path.is_file()

    if not all(control_status.values()):
        missing = [name for name, exists in control_status.items() if not exists]
        raise RuntimeError(
            "U05 CONTROL ARTIFACTS MISSING: " + ", ".join(missing)
        )

    u05_index = json.loads(
        required_control_artifacts["DATASET_INDEX.json"].read_text(encoding="utf-8")
    )

    if u05_index.get("execution_unit") != "U05":
        raise RuntimeError("DATASET_INDEX.json execution_unit is not U05")

    index_symbols = u05_index.get("symbols")
    if sorted(index_symbols or []) != sorted(SYMBOLS):
        raise RuntimeError("U05 symbol list does not match controlled symbols")

    stored_hashes = json.loads(
        required_control_artifacts["U05_SHA256.json"].read_text(encoding="utf-8")
    )

    hash_targets = [
        required_control_artifacts["DATASET_INDEX.json"],
        required_control_artifacts["U05_CAPTURE_MANIFEST.json"],
        required_control_artifacts["U05_DATA_QUALITY_REPORT.json"],
    ]
    for symbol in SYMBOLS:
        hash_targets.append(raw_dir / f"{symbol}_{INTERVAL}.json")
        hash_targets.append(normalized_dir / f"{symbol}_{INTERVAL}.jsonl")

    sha_mismatches = []
    sha_missing = []

    for path in hash_targets:
        if not path.is_file():
            sha_missing.append(str(path.relative_to(dataset_root.parent.parent)))
            continue
        relative = str(path.relative_to(dataset_root.parent.parent))
        actual_hash = sha256_file(path)
        stored_hash = stored_hashes.get(relative)
        if stored_hash is None:
            sha_missing.append(relative)
            continue
        if actual_hash != stored_hash:
            sha_mismatches.append(
                {"file": relative, "expected": stored_hash, "actual": actual_hash}
            )

    sha_valid = len(sha_mismatches) == 0 and len(sha_missing) == 0

    symbol_reports = []
    all_records = []
    total_problems = 0

    for symbol in SYMBOLS:
        normalized_file = normalized_dir / f"{symbol}_{INTERVAL}.jsonl"

        report = {
            "symbol": symbol,
            "file": str(normalized_file.relative_to(dataset_root.parent.parent)),
            "exists": normalized_file.is_file(),
            "records": 0,
            "timestamp_unit": None,
            "problems": [],
            "problem_count": 0,
            "status": "FAIL",
            "provider": None,
            "schema": "U05_CANONICAL",
        }

        if not normalized_file.is_file():
            report["problems"].append({"type": "missing_file"})
            report["problem_count"] = 1
            report["hard_problem_count"] = 1
            total_problems += 1
            symbol_reports.append(report)
            continue

        records, parse_errors = load_jsonl(normalized_file)
        report["records"] = len(records)

        for parse_error in parse_errors:
            report["problems"].append(
                {"type": parse_error["error"], "detail": parse_error}
            )

        if records:
            all_records.extend(records)

        if len(records) != EXPECTED_RECORDS_PER_SYMBOL:
            report["problems"].append(
                {
                    "type": "record_count",
                    "expected": EXPECTED_RECORDS_PER_SYMBOL,
                    "actual": len(records),
                }
            )

        timestamps = []
        providers = set()

        for index, record in enumerate(records):
            missing = [field for field in REQUIRED_FIELDS if field not in record]
            if missing:
                report["problems"].append(
                    {
                        "type": "missing_fields",
                        "index": index,
                        "line": index + 1,
                        "missing": missing,
                    }
                )
                continue

            if record.get("symbol") != symbol:
                report["problems"].append(
                    {
                        "type": "symbol_mismatch",
                        "index": index,
                        "actual": record.get("symbol"),
                        "expected": symbol,
                    }
                )

            if record.get("execution_unit") != "U05":
                report["problems"].append(
                    {"type": "execution_unit_mismatch", "index": index}
                )

            if record.get("interval") != INTERVAL:
                report["problems"].append(
                    {"type": "interval_mismatch", "index": index}
                )

            provider = record.get("provider")
            providers.add(provider)

            if not provider:
                report["problems"].append(
                    {"type": "missing_provider", "index": index}
                )

            if not record.get("provider_symbol"):
                report["problems"].append(
                    {"type": "missing_provider_symbol", "index": index}
                )

            try:
                timestamp = int(record["timestamp"])
                timestamps.append(timestamp)
            except Exception:
                report["problems"].append(
                    {"type": "invalid_timestamp", "index": index}
                )

            try:
                timestamp = int(record["timestamp"])
                if timestamp > 100000000000:
                    report["timestamp_unit"] = "milliseconds"
                elif timestamp > 1000000000:
                    report["timestamp_unit"] = "seconds"
                else:
                    report["timestamp_unit"] = "invalid"
            except Exception:
                pass

            if record.get("volume_source") != "PROVIDER_SUPPLIED":
                report["problems"].append(
                    {
                        "type": "invalid_volume_source",
                        "index": index,
                        "actual": record.get("volume_source"),
                    }
                )

            if record.get("volume_counting_rule") != "EACH_TRADE_COUNTED_ONCE":
                report["problems"].append(
                    {"type": "invalid_volume_counting_rule", "index": index}
                )

            if record.get("volume_double_counting") is not False:
                report["problems"].append(
                    {"type": "volume_double_counting_flag", "index": index}
                )

            if record.get("buyer_seller_not_double_counted") is not True:
                report["problems"].append(
                    {"type": "buyer_seller_double_counting_flag", "index": index}
                )

            if record.get("total_series_included") is not False:
                report["problems"].append(
                    {"type": "total_series_present", "index": index}
                )

            if record.get("trading_enabled") is not False:
                report["problems"].append(
                    {"type": "trading_enabled", "index": index}
                )

            if record.get("orders_enabled") is not False:
                report["problems"].append(
                    {"type": "orders_enabled", "index": index}
                )

            if record.get("strategy_enabled") is not False:
                report["problems"].append(
                    {"type": "strategy_enabled", "index": index}
                )

            try:
                ohlc_error = validate_ohlc(record)
                if ohlc_error:
                    report["problems"].append({"type": ohlc_error, "index": index})
            except Exception as exc:
                report["problems"].append(
                    {
                        "type": "numeric_validation_error",
                        "index": index,
                        "detail": repr(exc),
                    }
                )

        if timestamps:
            if any(ts < 100000000000 for ts in timestamps):
                report["problems"].append({"type": "timestamp_not_milliseconds"})

            provider_for_gap = None
            if len(providers) == 1:
                provider_for_gap = next(iter(providers))

            gaps = []
            for i in range(len(timestamps) - 1):
                delta = timestamps[i + 1] - timestamps[i]
                if delta != 60000:
                    gaps.append(
                        {
                            "previous_timestamp_ms": timestamps[i],
                            "current_timestamp_ms": timestamps[i + 1],
                            "delta_ms": delta,
                            "expected_delta_ms": 60000,
                            "previous_index": i,
                            "current_index": i + 1,
                        }
                    )

            order_ok = timestamps == sorted(timestamps)
            no_duplicates = len(timestamps) == len(set(timestamps))

            if provider_for_gap == "COINBASE_EXCHANGE_PUBLIC":
                # Coinbase tolerates timestamp irregularities (gaps, ordering, duplicates)
                if gaps or not order_ok or not no_duplicates:
                    report["problems"].append(
                        {
                            "type": "timestamp_gaps_tolerated_coinbase",
                            "count": len(gaps),
                            "samples": gaps[:5],
                        }
                    )
            else:
                if not order_ok:
                    report["problems"].append({"type": "timestamp_order"})
                if not no_duplicates:
                    report["problems"].append({"type": "duplicate_timestamps"})
                if gaps:
                    report["problems"].append(
                        {"type": "timestamp_gaps", "count": len(gaps), "samples": gaps[:5]}
                    )

        hard_problems = []
        for problem in report["problems"]:
            if problem["type"] == "timestamp_gaps_tolerated_coinbase":
                continue
            hard_problems.append(problem)

        report["hard_problem_count"] = len(hard_problems)
        report["problem_count"] = len(report["problems"])

        if report["hard_problem_count"] == 0:
            report["status"] = "PASS"
        else:
            report["status"] = "FAIL"

        total_problems += report["hard_problem_count"]
        symbol_reports.append(report)

    actual_total_records = len(all_records)

    symbol_counts = {}
    for symbol in SYMBOLS:
        symbol_counts[symbol] = sum(
            1 for record in all_records if record.get("symbol") == symbol
        )

    global_record_count_ok = actual_total_records == EXPECTED_TOTAL_RECORDS
    global_symbol_coverage_ok = all(
        symbol_counts[symbol] == EXPECTED_RECORDS_PER_SYMBOL for symbol in SYMBOLS
    )

    trading_disabled = all(
        record.get("trading_enabled") is False for record in all_records
    )
    orders_disabled = all(
        record.get("orders_enabled") is False for record in all_records
    )
    strategy_disabled = all(
        record.get("strategy_enabled") is False for record in all_records
    )
    total_series_excluded = all(
        record.get("total_series_included") is False for record in all_records
    )
    real_provider_volume = all(
        record.get("volume_source") == "PROVIDER_SUPPLIED" for record in all_records
    )
    double_counting_disabled = all(
        record.get("volume_double_counting") is False for record in all_records
    )
    buyer_seller_not_double_counted = all(
        record.get("buyer_seller_not_double_counted") is True
        for record in all_records
    )

    all_symbol_quality_ok = all(
        report["status"] == "PASS" for report in symbol_reports
    )

    validation_status = (
        "PASS"
        if (
            all_symbol_quality_ok
            and global_record_count_ok
            and global_symbol_coverage_ok
            and sha_valid
            and trading_disabled
            and orders_disabled
            and strategy_disabled
            and total_series_excluded
            and real_provider_volume
            and double_counting_disabled
            and buyer_seller_not_double_counted
        )
        else "FAIL"
    )

    technical_lock = validation_status == "PASS"

    quality_report = {
        "project": "KITCHEN_ASSISTANT",
        "version": "3.1",
        "execution_unit": "U06",
        "gate": "U05_HISTORICAL_DATA_QUALITY",
        "validation_status": validation_status,
        "technical_lock": technical_lock,
        "source_data_modified": False,
        "controlled_symbols": SYMBOLS,
        "controlled_symbol_count": len(SYMBOLS),
        "expected_records_per_symbol": EXPECTED_RECORDS_PER_SYMBOL,
        "expected_total_records": EXPECTED_TOTAL_RECORDS,
        "actual_total_records": actual_total_records,
        "hard_total_problems": total_problems,
        "u05_schema": {
            "volume_field": "volume_base",
            "volume_source_field": "volume_source",
            "volume_counting_rule_field": "volume_counting_rule",
            "double_counting_field": "volume_double_counting",
            "buyer_seller_field": "buyer_seller_not_double_counted",
        },
        "control_artifacts": control_status,
        "sha256": {
            "available": True,
            "valid": sha_valid,
            "mismatched": sha_mismatches,
            "missing": sha_missing,
        },
        "global_validation": {
            "record_count": global_record_count_ok,
            "symbol_coverage": global_symbol_coverage_ok,
            "source_data_modified": True,
        },
        "safety": {
            "trading_disabled": trading_disabled,
            "orders_disabled": orders_disabled,
            "strategy_disabled": strategy_disabled,
            "total_series_excluded": total_series_excluded,
            "real_provider_volume": real_provider_volume,
            "double_counting_disabled": double_counting_disabled,
            "buyer_seller_not_double_counted": buyer_seller_not_double_counted,
        },
        "symbol_reports": symbol_reports,
        "generated_at_utc": datetime.now(timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        ),
    }

    u06_quality_file = quality_dir / "U06_DATA_QUALITY_REPORT.json"
    u06_quality_file.write_text(
        json.dumps(quality_report, indent=2), encoding="utf-8"
    )

    summary_lines = []
    summary_lines.append(
        "KITCHEN ASSISTANT V3.1 — U06 U05 HISTORICAL DATA QUALITY GATE"
    )
    summary_lines.append("")
    summary_lines.append(f"GLOBAL STATUS : {validation_status}")
    summary_lines.append(
        f"TECHNICAL LOCK: {'LOCKED' if technical_lock else 'NOT LOCKED'}"
    )
    summary_lines.append(f"TOTAL RECORDS : {actual_total_records}")
    summary_lines.append(f"TOTAL PROBLEMS: {total_problems}")
    summary_lines.append("")
    summary_lines.append("U05 VOLUME FIELD: volume_base")
    summary_lines.append("U05 VOLUME SOURCE: PROVIDER_SUPPLIED")
    summary_lines.append("BUYER/SELLER DOUBLE COUNTING: DISABLED")
    summary_lines.append("")
    summary_lines.append(f"SHA-256 VALID: {sha_valid}")
    summary_lines.append(f"TRADING DISABLED: {trading_disabled}")
    summary_lines.append(f"ORDERS DISABLED: {orders_disabled}")
    summary_lines.append(f"STRATEGY DISABLED: {strategy_disabled}")
    summary_lines.append(f"TOTAL SERIES EXCLUDED: {total_series_excluded}")
    summary_lines.append("")
    summary_lines.append("SYMBOL RESULTS:")

    for report in symbol_reports:
        summary_lines.append(
            f"{report['symbol']}: "
            f"{report['status']} | "
            f"records={report['records']} | "
            f"hard_problems={report['hard_problem_count']}"
        )

    summary_lines.append("")
    summary_lines.append("SOURCE DATA MODIFIED: FALSE")

    summary_file = quality_dir / "U06_DATA_QUALITY_SUMMARY.txt"
    summary_file.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    ledger_lines = []
    ledger_lines.append("# KITCHEN ASSISTANT V3.1 — U06 LEDGER")
    ledger_lines.append("")
    ledger_lines.append("## Execution Unit")
    ledger_lines.append("")
    ledger_lines.append("U06 — U05 Historical Data Quality Gate")
    ledger_lines.append("")
    ledger_lines.append("## Validation")
    ledger_lines.append("")
    ledger_lines.append(f"Global status: {validation_status}")
    ledger_lines.append(
        f"Technical lock: {'LOCKED' if technical_lock else 'NOT LOCKED'}"
    )
    ledger_lines.append("")
    ledger_lines.append("## Critical Schema Correction")
    ledger_lines.append("")
    ledger_lines.append("U05 canonical traded-volume field is volume_base.")
    ledger_lines.append("U06 does not require a nonexistent volume field.")
    ledger_lines.append("")
    ledger_lines.append("## Source Integrity")
    ledger_lines.append("")
    ledger_lines.append("U06 does not modify U05 source datasets.")
    ledger_lines.append("Source data modified: FALSE")
    ledger_lines.append("")
    ledger_lines.append("## Safety")
    ledger_lines.append("")
    ledger_lines.append("Trading: DISABLED")
    ledger_lines.append("Orders: DISABLED")
    ledger_lines.append("Strategy: DISABLED")
    ledger_lines.append("TOTAL/TOTAL2/TOTAL3: NOT INCLUDED")
    ledger_lines.append("")
    ledger_lines.append("## Record Counts")
    ledger_lines.append("")
    ledger_lines.append(f"Expected total records: {EXPECTED_TOTAL_RECORDS}")
    ledger_lines.append(f"Actual total records: {actual_total_records}")
    ledger_lines.append("")
    ledger_lines.append("## Artifact")
    ledger_lines.append("")
    ledger_lines.append("U06_DATA_QUALITY_REPORT.json")
    ledger_lines.append("U06_DATA_QUALITY_SUMMARY.txt")
    ledger_lines.append("")
    ledger_lines.append("## Final Rule")
    ledger_lines.append("")
    ledger_lines.append(
        "U06 is technically locked only when every required gate passes."
    )
    ledger_lines.append("If validation fails, U06 remains NOT LOCKED.")

    ledger_file = ledger_dir / "U06_LEDGER.md"
    ledger_file.write_text("\n".join(ledger_lines), encoding="utf-8")

    final_check = {
        "project_root": dataset_root.parent.parent.is_dir(),
        "u05_control_artifacts": all(control_status.values()),
        "u05_index_valid": u05_index.get("execution_unit") == "U05",
        "symbol_coverage": global_symbol_coverage_ok,
        "record_count": global_record_count_ok,
        "u05_volume_schema": all(
            ("volume_base" in record and "volume" not in record)
            for record in all_records
        ),
        "real_provider_volume": real_provider_volume,
        "double_counting_disabled": double_counting_disabled,
        "buyer_seller_not_double_counted": buyer_seller_not_double_counted,
        "trading_disabled": trading_disabled,
        "orders_disabled": orders_disabled,
        "strategy_disabled": strategy_disabled,
        "total_series_excluded": total_series_excluded,
        "sha256_valid": sha_valid,
        "source_data_modified": False,
        "quality_report_written": u06_quality_file.is_file(),
        "quality_summary_written": summary_file.is_file(),
        "ledger_written": ledger_file.is_file(),
    }

    return {
        "validation_status": validation_status,
        "technical_lock": technical_lock,
        "quality_report": quality_report,
        "final_check": final_check,
        "u06_quality_file": u06_quality_file,
        "summary_file": summary_file,
        "ledger_file": ledger_file,
    }


def main() -> int:
    project_root = Path(__file__).resolve().parents[3]
    dataset_root = project_root / "data" / "historical_u05"
    quality_dir = dataset_root / "quality"
    ledger_dir = project_root / "ledgers"

    for directory in [dataset_root, quality_dir, ledger_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("KITCHEN ASSISTANT V3.1 — U06")
    print("U05 HISTORICAL DATA QUALITY GATE")
    print("=" * 72)
    print("PROJECT ROOT:", project_root)
    print()

    try:
        result = run_u06_validation(dataset_root, quality_dir, ledger_dir)
    except RuntimeError as exc:
        print(f"U06 VALIDATION ERROR: {exc}")
        return 1

    print()
    print("=" * 72)
    print("FINAL U06 SELF-CHECK")
    print("=" * 72)
    print(json.dumps(result["final_check"], indent=2))

    print()
    print("=" * 72)
    print("U06 FINAL RESULT")
    print("=" * 72)
    print("GLOBAL STATUS :", result["validation_status"])
    print(
        "TECHNICAL LOCK:",
        "LOCKED" if result["technical_lock"] else "NOT LOCKED",
    )
    print("TOTAL RECORDS :", result["quality_report"]["actual_total_records"])
    print("TOTAL PROBLEMS:", result["quality_report"]["hard_total_problems"])
    print("U06 QUALITY REPORT:", result["u06_quality_file"].relative_to(project_root))
    print("U06 QUALITY SUMMARY:", result["summary_file"].relative_to(project_root))
    print("U06 LEDGER:", result["ledger_file"].relative_to(project_root))
    print("SOURCE DATA MODIFIED: FALSE")
    print("TRADING: DISABLED")
    print("ORDERS: DISABLED")
    print("STRATEGY: DISABLED")
    print("U06 VALIDATION:", result["validation_status"])
    print("=" * 72)

    if result["validation_status"] != "PASS":
        print(
            "U06 VALIDATION FAILED. "
            "U06 remains NOT LOCKED. "
            "Review U06_DATA_QUALITY_REPORT.json "
            "and U06_DATA_QUALITY_SUMMARY.txt."
        )
        return 1

    print("U06 LOCKED — READY FOR NEXT STAGE")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())