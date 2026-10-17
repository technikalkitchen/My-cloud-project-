"""Simple TEST001 runner: discover listed pairs and their first/last candles."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import uuid
from typing import Any, Iterable

from .config import EXCHANGES, QUOTE_ASSETS, TIMEFRAMES
from .adapters import AdapterError, make_adapter

DEFAULT_UNIVERSE = Path("data/test001/universe.json")
DEFAULT_OUTPUT = Path("data/test001/results.json")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_universe(
    path: str | Path = DEFAULT_UNIVERSE,
) -> list[dict[str, str | None]]:
    """Load assets from a JSON list or an object containing an assets list."""
    source = Path(path)

    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"Cannot read universe JSON at {source}: {exc}"
        ) from exc

    assets = payload.get("assets") if isinstance(payload, dict) else payload

    if not isinstance(assets, list):
        raise ValueError(
            "Universe must be a list or an object containing an 'assets' list"
        )

    result: list[dict[str, str | None]] = []
    seen: set[str] = set()

    for item in assets:
        if not isinstance(item, dict):
            raise ValueError("Each universe item must be an object")

        symbol = str(item.get("symbol", "")).strip().upper()

        if not symbol:
            raise ValueError("Each asset needs a non-empty 'symbol'")

        raw_coin_id = item.get("coingecko_id")
        coin_id = (
            str(raw_coin_id).strip() or None
            if raw_coin_id is not None
            else None
        )

        if symbol in seen:
            raise ValueError(
                f"Duplicate asset symbol in universe: {symbol}"
            )

        seen.add(symbol)
        result.append({
            "symbol": symbol,
            "coingecko_id": coin_id,
        })

    if not result:
        raise ValueError("Universe is empty")

    return result


def _market_id(adapter: Any, base: str, quote: str) -> str:
    builder = getattr(adapter, "market_id", None)

    if callable(builder):
        return builder(base, quote)

    return base + quote


def _quotes_for(symbol: str) -> tuple[str, ...]:
    # BTC/BTC is not canonical. All other assets use USDT and BTC.
    return ("USDT",) if symbol == "BTC" else QUOTE_ASSETS


def run_test001(
    universe_path: str | Path = DEFAULT_UNIVERSE,
    output_path: str | Path = DEFAULT_OUTPUT,
    exchanges: Iterable[str] = EXCHANGES,
    timeframes: Iterable[str] = TIMEFRAMES.keys(),
    limit_assets: int | None = None,
    stop_on_exchange_error: bool = False,
) -> dict[str, Any]:
    """Run TEST001 over the selected universe."""
    assets = load_universe(universe_path)

    if limit_assets is not None:
        if limit_assets < 1:
            raise ValueError("limit_assets must be >= 1")
        assets = assets[:limit_assets]

    exchange_names = tuple(exchanges)
    tf_names = tuple(timeframes)

    unknown_exchanges = set(exchange_names) - set(EXCHANGES)
    unknown_timeframes = set(tf_names) - set(TIMEFRAMES)

    if unknown_exchanges:
        raise ValueError(
            f"Unknown exchanges: {', '.join(sorted(unknown_exchanges))}"
        )

    if unknown_timeframes:
        raise ValueError(
            f"Unknown timeframes: {', '.join(sorted(unknown_timeframes))}"
        )

    if not exchange_names or not tf_names:
        raise ValueError(
            "At least one exchange and timeframe are required"
        )

    report: dict[str, Any] = {
        "run_id": str(uuid.uuid4()),
        "generated_at_utc": utc_now(),
        "status": "RUNNING",
        "assets_requested": len(assets),
        "exchanges_requested": list(exchange_names),
        "timeframes_checked": list(tf_names),
        "assets": [],
        "errors": [],
    }

    adapters: dict[str, Any] = {}
    listed_markets: dict[str, set[str] | None] = {}

    for name in exchange_names:
        try:
            adapter = make_adapter(name)
            adapters[name] = adapter
            listed_markets[name] = adapter.markets()

        except (AdapterError, ValueError, KeyError) as exc:
            adapters[name] = None
            listed_markets[name] = None

            report["errors"].append({
                "exchange": name,
                "stage": "markets",
                "error": str(exc)[:300],
            })

            if stop_on_exchange_error:
                report["status"] = "FAILED"
                report["finished_at_utc"] = utc_now()
                _write_json(report, output_path)
                return report

    for asset in assets:
        symbol = asset["symbol"]

        asset_result: dict[str, Any] = {
            "symbol": symbol,
            "coingecko_id": asset["coingecko_id"],
            "exchanges": {},
        }

        for name in exchange_names:
            adapter = adapters[name]
            market_set = listed_markets[name]

            exchange_result: dict[str, Any] = {
                "status": (
                    "ERROR"
                    if adapter is None or market_set is None
                    else "OK"
                ),
                "pairs": {},
                "timeframes_checked": list(tf_names),
            }

            for quote in _quotes_for(symbol):
                market = (
                    _market_id(adapter, symbol, quote)
                    if adapter is not None
                    else None
                )

                if adapter is None or market_set is None:
                    pair_result = {
                        "symbol": market,
                        "status": "ERROR",
                        "timeframes": {},
                    }

                elif market not in market_set:
                    pair_result = {
                        "symbol": market,
                        "status": "NOT_LISTED",
                        "timeframes": {},
                    }

                else:
                    pair_result = {
                        "symbol": market,
                        "status": "LISTED",
                        "timeframes": {},
                    }

                    for timeframe in tf_names:
                        try:
                            candle_result = adapter.inspect_market(
                                market,
                                timeframe,
                            )

                        except Exception as exc:
                            candle_result = {
                                "status": "ERROR",
                                "first": None,
                                "last": None,
                                "error": str(exc)[:300],
                            }

                        pair_result["timeframes"][timeframe] = candle_result

                        if candle_result["status"] == "ERROR":
                            report["errors"].append({
                                "symbol": symbol,
                                "exchange": name,
                                "pair": market,
                                "timeframe": timeframe,
                                "error": candle_result.get(
                                    "error",
                                    "unknown error",
                                ),
                            })

                exchange_result["pairs"][quote.lower()] = pair_result

            if any(
                pair.get("status") == "ERROR"
                for pair in exchange_result["pairs"].values()
            ):
                exchange_result["status"] = "ERROR"

            asset_result["exchanges"][name] = exchange_result

        report["assets"].append(asset_result)

    statuses = [
        timeframe_result.get("status")
        for asset in report["assets"]
        for exchange in asset["exchanges"].values()
        for pair in exchange["pairs"].values()
        for timeframe_result in pair.get("timeframes", {}).values()
    ]

    if report["errors"] or any(
        status == "ERROR" for status in statuses
    ):
        report["status"] = "PARTIAL"

    elif any(
        status in ("NO_DATA", "PARTIAL")
        for status in statuses
    ):
        report["status"] = "PARTIAL"

    else:
        report["status"] = "COMPLETED"

    report["finished_at_utc"] = utc_now()
    _write_json(report, output_path)

    return report


def _write_json(
    payload: dict[str, Any],
    path: str | Path,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    temporary = destination.with_suffix(
        destination.suffix + ".tmp"
    )

    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    temporary.replace(destination)
