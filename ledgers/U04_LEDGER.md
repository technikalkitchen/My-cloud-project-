# KITCHEN ASSISTANT V2.8 — U04 LEDGER

## Execution Unit

U04 — Real Market Data Provider / Capture

## Provider Priority

1. BINANCE_SPOT_PUBLIC
2. COINBASE_EXCHANGE_PUBLIC

## Provider Selection Rule

Priority: BINANCE_FIRST

Binance is always the first-choice provider.

Coinbase is used only when Binance cannot provide
the requested market data.

## Selected Provider

BINANCE_SPOT_PUBLIC

## Capture

Symbol: BTCUSDT
Interval: 1m
Requested candles: 5
Received candles: 5

## Authentication

No API key required.
No secret stored.

## Validation

- Import integrity
- Structural tests
- Provider response validation
- Candle model validation
- OHLC validation
- Volume validation
- Chronological validation
- Duplicate timestamp validation

## Storage

- Raw capture: data/raw/BTCUSDT_1m_u04.json
- Normalized JSONL capture: data/normalized/BTCUSDT_1m_u04.jsonl

## Trading

Trading logic: NOT CONNECTED
Order execution: NOT CONNECTED

## Technical Lock

LOCKED

## Audit

PASSED

## Cell Integrity Rule

No execution-error cell is accepted into the
working notebook.

A failed cell must be removed/replaced,
rerun successfully, and verified before
the Unit is locked.

## Next

U05 — Historical Dataset / Multi-Symbol Capture
