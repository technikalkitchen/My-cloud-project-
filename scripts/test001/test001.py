#!/usr/bin/env python3
"""CLI entry point for the TEST001 market-history MVP."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.market.test001.config import EXCHANGES, TIMEFRAMES
from app.market.test001.runner import DEFAULT_OUTPUT, DEFAULT_UNIVERSE, run_test001


def _csv_values(raw: str, allowed: tuple[str, ...] | list[str], label: str) -> list[str]:
    values = [part.strip().lower() for part in raw.split(",") if part.strip()]
    if not values:
        raise argparse.ArgumentTypeError(f"{label} cannot be empty")
    unknown = sorted(set(values) - set(allowed))
    if unknown:
        raise argparse.ArgumentTypeError(f"Unknown {label}: {', '.join(unknown)}")
    if len(values) != len(set(values)):
        raise argparse.ArgumentTypeError(f"Duplicate {label} values are not allowed")
    return values


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check exchange pair availability and first/last candles.")
    parser.add_argument("--universe", default=str(DEFAULT_UNIVERSE), help="Path to universe JSON")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Path for result JSON")
    parser.add_argument("--exchanges", default=",".join(EXCHANGES), help="Comma-separated exchange names")
    parser.add_argument("--timeframes", default=",".join(TIMEFRAMES), help="Comma-separated timeframes")
    parser.add_argument("--limit-assets", type=int, default=None, help="Optional maximum assets for a small test run")
    parser.add_argument("--stop-on-exchange-error", action="store_true", help="Stop if an exchange market-list request fails")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        exchanges = _csv_values(args.exchanges, EXCHANGES, "exchange")
        timeframes = _csv_values(args.timeframes, list(TIMEFRAMES), "timeframe")
        if args.limit_assets is not None and args.limit_assets < 1:
            parser.error("--limit-assets must be >= 1")
        report = run_test001(
            universe_path=args.universe,
            output_path=args.output,
            exchanges=exchanges,
            timeframes=timeframes,
            limit_assets=args.limit_assets,
            stop_on_exchange_error=args.stop_on_exchange_error,
        )
    except (ValueError, OSError) as exc:
        print(f"TEST001 failed: {exc}", file=sys.stderr)
        return 2

    print(json.dumps({
        "status": report["status"],
        "assets_requested": report["assets_requested"],
        "exchanges_requested": report["exchanges_requested"],
        "timeframes_checked": report["timeframes_checked"],
        "output": str(Path(args.output)),
        "errors": len(report["errors"]),
    }, indent=2))
    return 0 if report["status"] == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
