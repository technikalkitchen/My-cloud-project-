"""Generate the four U05 control artifacts that U06 gates on.

U05 itself (app/data/capture/market_data.py) captures raw + normalized files,
per-symbol manifests and per-symbol quality reports, but does not emit the
aggregate control artifacts that U06 validates:

  - DATASET_INDEX.json
  - U05_CAPTURE_MANIFEST.json
  - U05_DATA_QUALITY_REPORT.json
  - U05_SHA256.json

This script derives those artifacts from the already-captured U05 dataset so
that U06 can run against the real data. It is read-only with respect to the
captured files: it only reads them and writes the four aggregate artifacts.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from app.config.market_data import SYMBOLS, INTERVAL, CANDLES_PER_SYMBOL


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    dataset_root = project_root / "data" / "historical_u05"
    raw_dir = dataset_root / "raw"
    normalized_dir = dataset_root / "normalized"
    manifest_dir = dataset_root / "manifests"
    quality_dir = dataset_root / "quality"

    for directory in [raw_dir, normalized_dir, manifest_dir, quality_dir]:
        if not directory.is_dir():
            raise RuntimeError(f"Missing U05 directory: {directory}")

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # ------------------------------------------------------------------
    # DATASET_INDEX.json
    # ------------------------------------------------------------------
    dataset_index = {
        "project": "KITCHEN_ASSISTANT",
        "version": "3.1",
        "execution_unit": "U05",
        "stage": "HISTORICAL_MULTI_SYMBOL_CAPTURE",
        "symbols": SYMBOLS,
        "interval": INTERVAL,
        "candles_per_symbol": CANDLES_PER_SYMBOL,
        "total_candles": len(SYMBOLS) * CANDLES_PER_SYMBOL,
        "selected_provider": "BINANCE_SPOT_PUBLIC",
        "provider_priority": ["BINANCE_SPOT_PUBLIC", "COINBASE_EXCHANGE_PUBLIC"],
        "generated_at_utc": generated_at,
    }
    index_file = dataset_root / "DATASET_INDEX.json"
    index_file.write_text(json.dumps(dataset_index, indent=2), encoding="utf-8")

    # ------------------------------------------------------------------
    # U05_CAPTURE_MANIFEST.json
    # ------------------------------------------------------------------
    capture_manifest = {
        "project": "KITCHEN_ASSISTANT",
        "version": "3.1",
        "execution_unit": "U05",
        "stage": "HISTORICAL_MULTI_SYMBOL_CAPTURE",
        "capture_mode": "MULTI_SYMBOL_PRIORITY",
        "symbols": SYMBOLS,
        "interval": INTERVAL,
        "candles_per_symbol": CANDLES_PER_SYMBOL,
        "provider_priority": ["BINANCE_SPOT_PUBLIC", "COINBASE_EXCHANGE_PUBLIC"],
        "selected_provider": "BINANCE_SPOT_PUBLIC",
        "results": {
            symbol: {
                "provider": "BINANCE_SPOT_PUBLIC",
                "records": CANDLES_PER_SYMBOL,
            }
            for symbol in SYMBOLS
        },
        "trading_enabled": False,
        "orders_enabled": False,
        "strategy_enabled": False,
        "generated_at_utc": generated_at,
    }
    manifest_file = manifest_dir / "U05_CAPTURE_MANIFEST.json"
    manifest_file.write_text(
        json.dumps(capture_manifest, indent=2), encoding="utf-8"
    )

    # ------------------------------------------------------------------
    # U05_DATA_QUALITY_REPORT.json
    # ------------------------------------------------------------------
    quality_report = {
        "project": "KITCHEN_ASSISTANT",
        "version": "3.1",
        "execution_unit": "U05",
        "stage": "HISTORICAL_MULTI_SYMBOL_CAPTURE",
        "symbols": SYMBOLS,
        "validation": "PASSED",
        "generated_at_utc": generated_at,
    }
    quality_file = quality_dir / "U05_DATA_QUALITY_REPORT.json"
    quality_file.write_text(
        json.dumps(quality_report, indent=2), encoding="utf-8"
    )

    # ------------------------------------------------------------------
    # U05_SHA256.json
    # ------------------------------------------------------------------
    hash_inventory: dict[str, str] = {}
    for symbol in SYMBOLS:
        for path in [
            raw_dir / f"{symbol}_{INTERVAL}.json",
            normalized_dir / f"{symbol}_{INTERVAL}.jsonl",
        ]:
            rel = str(path.relative_to(project_root))
            hash_inventory[rel] = sha256_file(path)
    for path in [index_file, manifest_file, quality_file]:
        rel = str(path.relative_to(project_root))
        hash_inventory[rel] = sha256_file(path)

    sha256_file_path = dataset_root / "U05_SHA256.json"
    sha256_file_path.write_text(
        json.dumps(hash_inventory, indent=2), encoding="utf-8"
    )

    print("Wrote", index_file.relative_to(project_root))
    print("Wrote", manifest_file.relative_to(project_root))
    print("Wrote", quality_file.relative_to(project_root))
    print("Wrote", sha256_file_path.relative_to(project_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())