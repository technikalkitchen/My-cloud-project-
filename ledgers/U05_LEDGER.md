# KITCHEN ASSISTANT V3.1 — U05 LEDGER

## Execution Unit

U05 — Historical Dataset / Multi-Symbol Capture

## Purpose

Extend U04 (single-symbol real capture) to multi-symbol
historical capture with rolling 60-minute volume analysis
across five trading pairs.

## Prerequisite

U04 — VALIDATED + LOCKED

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

## Symbols Captured

- BTCUSDT
- ETHUSDT
- SOLUSDT
- XRPUSDT
- ADAUSDT

## Capture

Interval: 1m
Requested candles per symbol: 100
Received candles per symbol: 100
Total candles captured: 500
Provider: BINANCE_SPOT_PUBLIC (all symbols)

## Rolling Volume

Mode: ROLLING_END_AT_NOW
Duration: 60 minutes
Candles in time range: 60 per symbol

| Symbol    | Rolling Volume (base) | Rolling Volume (USD) | Exact Quote |
|-----------|-----------------------|----------------------|-------------|
| BTCUSDT   | 1488.1048             | 114587415.362        | True        |
| ETHUSDT   | 62711.1313            | 152093522.926        | True        |
| SOLUSDT   | 166027.848            | 16510484.449         | True        |
| XRPUSDT   | 9187055.5             | 12486005.071         | True        |
| ADAUSDT   | 7448650.6             | 1562994.553          | True        |

## Volume Contract

Definition: TOTAL_TRADED_BASE_ASSET_VOLUME
Each trade counted once: YES
Buyer and seller not double counted: YES
Provider supplied: YES
Fabricated: NO
Interpolation: NO
Market cap derived: NO
Close times volume: NO
Last completed candle substitution: NO
Last N rows substitution: NO

## Authentication

No API key required.
No secret stored.

## Validation

- Import integrity
- Structural tests (32 tests)
- Multi-symbol capture validation
- Per-symbol chronological validation
- Per-symbol duplicate timestamp validation
- Per-symbol OHLC bounds validation
- Per-symbol volume contract validation
- Per-symbol safety locks verification
- Rolling volume calculation
- Exact USD quote volume verification
- No fabricated data verification
- TOTAL/TOTAL2/TOTAL3 exclusion verification

## Storage

- Raw capture (per symbol):
  data/historical_u05/raw/{SYMBOL}_1m.json
- Normalized JSONL capture (per symbol):
  data/historical_u05/normalized/{SYMBOL}_1m.jsonl
- Per-symbol manifests:
  data/historical_u05/manifests/{SYMBOL}_MANIFEST.json
- Per-symbol quality reports:
  data/historical_u05/quality/{SYMBOL}_QUALITY.json

## Trading

Trading logic: NOT CONNECTED
Order execution: NOT CONNECTED
Strategy: NOT CONNECTED

## Safety Locks

TRADING_ENABLED: False
ORDERS_ENABLED: False
STRATEGY_ENABLED: False

All safety locks asserted False at import time in
app/config/market_data.py.

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

U06 — Quality Gate over U05 artifacts
