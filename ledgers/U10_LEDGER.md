# KITCHEN ASSISTANT V3.1 — U10 LEDGER

## Execution Unit

U10 — Dynamic Top-10 Market-Cap View

## Validation

Global status: PASS
Technical lock: LOCKED

## Stage 10 Integration Summary

### Unit 10.1 — Stage Contract + Dynamic Top-10 Consumer
- Stage 10 configuration (view, exchange, timeframe, ranks)
- Dynamic Top-125 via U06.5 dynamic_rank_assets
- Ranks 2-10 selected, BTC rank 1 excluded
- No caching, fresh on every request
- Status: PASSED

### Unit 10.2 — Exchange Selection + Fallback Router
- 8 exchange choices in Display Fallback Priority
- Selected exchange as Preferred Source
- Higher-priority-only fallback
- No lower-priority fallback
- Per-field provenance tracking
- Status: PASSED

### Unit 10.3 — USDT Pair + Volume
- USDT pair validation (symbol, price, volume, timestamp, timeframe)
- Provider-supplied volume only
- Volume USDT-only (not BTC)
- Source/Fallback presentation
- No fabricated volume, no 24h substitution
- Status: PASSED

### Unit 10.4 — BTC Pair + Fallback Cohesion
- BTC pair independent validation
- Fallback cohesion with USDT exchange
- Fake-pair prevention (BTC, BTCBTC, empty rejected)
- Approved Kitchen BTC calculation only where permitted
- Explicit unavailable state
- Status: PASSED

### Unit 10.5 — Telegram Output + RTL/LTR
- Telegram-ready Top-10 formatting
- Source/Fallback labeling
- Volume USDT-only
- RTL/LTR safety for Persian context
- Kitchen/Exchange view support
- Informational-only (no trading signals)
- Status: PASSED

## Cross-Unit Integration

- Dynamic current Top-10 comes from U06.5
- BTC rank 1 excluded from display
- Ranks 2-10 consumed dynamically
- Selected Exchange view works
- Kitchen view works
- Exchange fallback routing works
- USDT pair uses requested timeframe
- BTC pair independently validated
- Fallback cohesion verified
- Provenance preserved across all units
- Telegram output has required structure

## Real-Data Smoke Test

- Live CoinGecko data fetched (130 coins)
- U06.5 ranking: VALIDATED, 125 assets
- Unit 10.1: 9 assets (ranks 2-10), BTC excluded
- Unit 10.2: Fallback chain verified
- Unit 10.3: USDT pairs validated, Source labeled
- Unit 10.4: BTC pairs validated, cohesion verified
- Unit 10.5: Telegram output generated correctly
- Status: PASSED

## Source Integrity

U06.5, U07, U08, U09 units: UNMODIFIED
Units 10.1-10.5: NEW (not modifications)
Source data modified: FALSE

## Safety

Trading: DISABLED
Orders: DISABLED
Strategy: DISABLED
Portfolio Actions: DISABLED
No trading, orders, entries, exits, long/short, setup, trigger, or recommendations.

## Final Rule

U10 is technically locked only when every gate passes.
If validation fails, U10 remains NOT LOCKED.
