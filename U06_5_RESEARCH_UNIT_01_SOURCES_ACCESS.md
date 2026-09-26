# U06.5 Research — Unit 01: Sources Access Checkpoint

**Cell ID**: U06.5 | **Version**: 8.4.5 | **Schema**: U06_5_SCHEMA_V6_0
**Checkpoint Date**: 2026-09-26T14:09:00Z
**Type**: Evidence-based checkpoint (Unit 01: Source Access verification)
**Status**: CONSOLIDATED FROM EXISTING FINDINGS

---

## 1. Objective

Verify source-level access to all data providers consumed by U06.5 (Market Data Foundation). This checkpoint covers:
- 2 global providers: CoinMarketCap, CoinGecko
- 8 exchanges: Binance, OKX, Bybit, KuCoin, Coinbase, Gate, Upbit, Bitget

**Scope**: Acquisition endpoints, authentication modes, normalization, and validation rules only (Layer A). No ranking, reference price, or indices analysis.

**Evidence basis**: Source code, configuration constants, and test artifacts at `/workspaces/My-cloud-project-`. Live API responses NOT captured. All endpoints are as configured in code; actual availability depends on runtime network conditions and provider status.

---

## 2. Sources Summary

| # | Source | Type | Priority | Mode | Source File | Lines |
|---|--------|------|----------|------|-------------|-------|
| 1 | CoinMarketCap | Global Provider | 1 (primary) | Keyless PUBLIC / Optional AUTH | `app/market/global_providers.py` | 341 |
| 2 | CoinGecko | Global Provider | 2 (fallback) | PUBLIC (no key) | `app/market/global_providers.py` | 341 |
| 3 | Binance | Exchange | 1 (primary) | PUBLIC_SPOT | `app/market/exchange_evidence.py` | 527 |
| 4 | OKX | Exchange | 2 | PUBLIC_SPOT | `app/market/exchange_evidence.py` | 527 |
| 5 | Bybit | Exchange | 3 | PUBLIC_SPOT | `app/market/exchange_evidence.py` | 527 |
| 6 | KuCoin | Exchange | 4 | PUBLIC_SPOT | `app/market/exchange_evidence.py` | 527 |
| 7 | Coinbase | Exchange | 5 | PUBLIC_SPOT | `app/market/exchange_evidence.py` | 527 |
| 8 | Gate | Exchange | 6 | PUBLIC_SPOT | `app/market/exchange_evidence.py` | 527 |
| 9 | Upbit | Exchange | 7 | PUBLIC_SPOT | `app/market/exchange_evidence.py` | 527 |
| 10 | Bitget | Exchange | 8 (lowest) | PUBLIC_SPOT | `app/market/exchange_evidence.py` | 527 |

**Forbidden providers**: tradingview, tradingview_reference, tv (`app/config/exchanges.py:60-64`)

---

## 3. Global Provider Endpoints

### 3.1 CoinMarketCap

| Endpoint | URL | Params | Auth | Status |
|----------|-----|--------|------|--------|
| Listings | `{keyless}/v3/cryptocurrency/listings/latest` | start=1, limit=125, convert=USD | None (keyless) | LIVE — primary |
| Listings (auth) | `{auth}/v3/cryptocurrency/listings/latest` | start=1, limit=125, convert=USD | `X-CMC_PRO_API_KEY` | LIVE — if CMC_API_KEY configured |
| Quotes | `{keyless}/v3/cryptocurrency/quotes/latest` | id=1,1027,825, convert=USD | None (keyless) | LIVE — core assets |
| Global Metrics | `{keyless}/v1/global-metrics/quotes/latest` | convert=USD | None (keyless) | LIVE |
| Simple Price | `{keyless}/v1/simple/price` | id=1,1027,825, convert=USD | None (keyless) | LIVE — core assets |

**Keyless Base**: `https://pro-api.coinmarketcap.com/public-api` (`app/config/quality.py:25`)
**Authenticated Base**: `https://pro-api.coinmarketcap.com` (`app/config/quality.py:26`)
**Credential Discovery Order**: `CMC_API_KEY` → `KITCHEN_CMC_API_KEY` → `COINMARKETCAP_API_KEY` → `CMC_PRO_API_KEY` (`app/config/quality.py:74-88`)

**UNKNOWN**: Whether `CMC_API_KEY` is configured at runtime (`app/config/quality.py:74-88` — code exists, env value NOT VERIFIED)

### 3.2 CoinGecko

| Endpoint | URL | Params | Auth | Status |
|----------|-----|--------|------|--------|
| Markets | `https://api.coingecko.com/api/v3/coins/markets` | vs_currency=usd, order=market_cap_desc, per_page=125, page=1, sparkline=false | None | LIVE — fallback when CMC fails |

**Base URL**: `https://api.coingecko.com/api/v3` (`app/config/quality.py:27`)
**Auth**: PUBLIC — no API key sent in request despite `CG_API_KEY` env var being read (`app/config/quality.py:90-94`)
**Role**: REFERENCE_STATUS="REFERENCE_NOT_USED", REFERENCE_PROVIDER="coingecko" (`app/config/quality.py:108-109`)

**UNKNOWN**: Whether `CG_API_KEY` is configured at runtime (`app/config/quality.py:90-94` — read but not used)

---

## 4. Exchange Endpoints (OHLCV + Orderbook)

### Configuration Constants (`app/config/exchanges.py`)

| Constant | Value | Source |
|----------|-------|--------|
| TARGET_EXCHANGE_COUNT | 8 | `exchanges.py:18` |
| MIN_VALIDATED_EXCHANGE_COUNT | 7 | `exchanges.py:19` |
| MULTI_EXCHANGE_PROBE_SYMBOL | "BTCUSDT" | `exchanges.py:23` |
| EXCHANGE_KLINE_INTERVAL | "5m" | `exchanges.py:41` |
| EXCHANGE_KLINE_LIMIT | 2 (env: KITCHEN_EXCHANGE_KLINE_LIMIT) | `exchanges.py:42,78` |
| EXCHANGE_ORDERBOOK_LIMIT | 100 | `exchanges.py:78,160,167,172,...` |

### Per-Exchange Endpoints

| Exchange | OHLCV URL | OHLCV Symbol | OHLCV Params | Orderbook URL | Orderbook Params |
|----------|-----------|-------------|-------------|---------------|-----------------|
| **Binance** | `https://api.binance.com/api/v3/klines` | BTCUSDT | symbol=BTCUSDT, interval=5m, limit=N | `https://api.binance.com/api/v3/depth` | symbol=BTCUSDT, limit=100 |
| **OKX** | `https://www.okx.com/api/v5/market/history-candles` | BTC-USDT | instId=BTC-USDT, bar=5m, limit=N | `https://www.okx.com/api/v5/market/books` | instId=BTC-USDT, sz=100 |
| **Bybit** | `https://api.bybit.com/v5/market/kline` | BTCUSDT | category=spot, symbol=BTCUSDT, interval=5(int), limit=N | `https://api.bybit.com/v5/market/orderbook` | category=spot, symbol=BTCUSDT, limit=100 |
| **KuCoin** | `https://api.kucoin.com/api/v1/market/candles` | BTC-USDT | symbol=BTC-USDT, type=5min, limit=N | `https://api.kucoin.com/api/v1/market/orderbook/level2_100` | symbol=BTC-USDT |
| **Coinbase** | `https://api.exchange.coinbase.com/products/BTC-USDT/candles` | BTC-USDT | granularity=300(sec) | `https://api.exchange.coinbase.com/products/BTC-USDT/book` | limit=100 |
| **Gate** | `https://api.gateio.ws/api/v4/spot/candlesticks` | BTC_USDT | currency_pair_id=BTC_USDT, interval=5m, limit=N | `https://api.gateio.ws/api/v4/spot/order_book` | currency_pair_id=BTC_USDT, limit=100 |
| **Upbit** | `https://api.upbit.com/v1/candles/minutes/5` | USDT-BTC | market=USDT-BTC, count=N | `https://api.upbit.com/v1/orderbook` | markets=USDT-BTC |
| **Bitget** | `https://api.bitget.com/api/v2/spot/market/history-candles` | BTCUSDT | symbol=BTCUSDT, period=5min, limit=N | `https://api.bitget.com/api/v2/spot/market/orderbook` | symbol=BTCUSDT, limit=100 |

**Symbol format divergence**: Binance/Bybit/Bitget use BTCUSDT; OKX/KuCoin/Coinbase use BTC-USDT; Gate uses BTC_USDT; Upbit uses USDT-BTC (reversed).

**Interval format divergence**: Binance/Gate use "5m" string; KuCoin/Bitget use "5min" string; OKX uses bar=5m; Bybit uses interval=5 (integer); Coinbase uses granularity=300 (seconds); Upbit uses path-based `/minutes/5`.

### 4.1 Normalization Contracts

All 8 exchanges normalized through shared functions:
- OHLCV: `_normalize_exchange_payload(exchange, spec, result)` → `app/market/exchange_evidence.py:244-333`
- Orderbook: `_normalize_orderbook(exchange, spec, result)` → `app/market/exchange_evidence.py:407-476`
- Kline validation: `_valid_kline_row(row, min_len=7)` → `app/market/exchange_evidence.py:230-241`
- Binance-specific validation: `_valid_binance_kline_row(row)` → stricter, requires volume>0 → `app/market/exchange_evidence.py:33-45`
- Orderbook validation: `_valid_orderbook_payload(payload)` → `app/market/exchange_evidence.py:390-404`

**Normalized OHLCV fields**: exchange, market_id, timestamp, open, high, low, close, volume, quote_volume, volume_source, timeframe, provider_timestamp_ms

**Normalized Orderbook fields**: bids [{price, size}], asks [{price, size}]

### 4.2 Validation Gate

| Gate | Required | Target | Gate Function | Source |
|------|----------|--------|---------------|--------|
| Exchange OHLCV Coverage | 7 | 8 | `validated_count >= MIN_VALIDATED_EXCHANGE_COUNT` | `exchange_evidence.py:356-357` |
| Exchange Orderbook Coverage | 7 | 8 | Same threshold | `exchange_evidence.py:498-500` |
| GATE NAME (OHLCV) | — | — | `U06_5_UNIT_4_EXCHANGE_COVERAGE` | `exchange_evidence.py:371` |
| GATE NAME (Orderbook) | — | — | `U06_5_UNIT_5_ORDERBOOK_COVERAGE` | `exchange_evidence.py:510-519` |

**Gate behavior**: Independent parallel probes (no failover between exchanges). Passes if ≥7 of 8 validate. Bitget failure → 7 remain → PASSED. Two failures → 6 remain → FAILED.

**NOT VERIFIED**: Whether live probes against all 8 exchanges pass the 7-of-8 gate. Tests use synthetic mock rows (`tests/unit/test_u06_5_unit_4_exchange_evidence.py:22-32`).

---

## 5. Global Provider Normalization & Validation

### CMC Normalization (`normalize_cmc_asset`, `app/market/global_providers.py:182-200`)

| Field | Extraction |
|-------|-----------|
| provider | "coinmarketcap" (literal) |
| provider_mode | "KEYLESS_PUBLIC" (literal) |
| canonical_asset_id | `safe_int(asset.get("id"))` or `safe_int(asset.get("slug"))` |
| provider_asset_id | `str(asset.get("slug") or asset.get("id"))` |
| symbol | `str(asset.get("symbol")).strip().upper()` |
| name | `str(asset.get("name")).strip()` |
| price | `safe_float(quote.get("price"))` |
| market_cap | `safe_float(quote.get("market_cap"))` |
| volume_24h | `safe_float(quote.get("volume_24h"))` |
| percent_change_1h | `safe_float(quote.get("percent_change_1h"))` |
| percent_change_24h | `safe_float(quote.get("percent_change_24h"))` |
| rank | `safe_int(asset.get("rank"))` or `safe_int(quote.get("rank"))` |
| last_updated | `str(asset.get("last_updated") or quote.get("last_updated"))` |

### CoinGecko Normalization (`normalize_coingecko_asset`, `app/market/global_providers.py:203-209`)

| Field | Extraction |
|-------|-----------|
| provider | "coingecko" (literal) |
| provider_mode | "PUBLIC" (literal) |
| canonical_asset_id | `safe_int(asset.get("id"))` or `safe_int(asset.get("market_cap_rank"))` |
| provider_asset_id | `str(asset.get("id"))` |
| symbol | `str(asset.get("symbol")).strip().upper()` |
| name | `str(asset.get("name")).strip()` |
| price | `safe_float(asset.get("current_price"))` |
| market_cap | `safe_float(asset.get("market_cap"))` |
| volume_24h | `safe_float(asset.get("total_volume"))` |
| percent_change_1h | `safe_float(asset.get("price_change_percentage_1h_in_currency"))` |
| percent_change_24h | `safe_float(asset.get("price_change_percentage_24h_in_currency"))` |
| rank | `safe_int(asset.get("market_cap_rank"))` |
| last_updated | `str(asset.get("last_updated"))` |

### Validation Rules (both providers, applied identically)

| Rule | Function | Source |
|------|----------|--------|
| Identity validation | `validate_identity()` — provider, symbol, canonical_asset_id required | `global_providers.py:223-232` |
| Numeric validation | `validate_numeric_market_fields()` — price, market_cap, volume_24h, pct_change_1h, pct_change_24h required | `global_providers.py:235-242` |
| Timestamp validation | `validate_timestamp_fields()` — last_updated present, parseable, fresh | `global_providers.py:245-261` |
| Ranked universe | `validate_ranked_universe(records, 125)` — ≥125 records, valid ranks, no duplicates, coverage ≥1.0 | `global_providers.py:277-306` |
| Core assets | `validate_core_assets(records)` — BTC(1), ETH(1027), USDT(825) must be present | `global_providers.py:309-322` |
| Per-record | `validate_record(record, retrieved_at)` — identity, numeric, timestamp checks | `global_providers.py:325-340` |
| Freshness | `freshness_status()` — FRESH ≤900s, STALE >900s, UNAVAILABLE | `global_providers.py:264-274` |

### Configuration Constants (`app/config/quality.py`)

| Constant | Value | Source |
|----------|-------|--------|
| TOP_N | 125 | `quality.py:32` |
| MIN_TOP125_COVERAGE | 1.0 | `quality.py:33` |
| FRESHNESS_THRESHOLD_SECONDS | 900 | `quality.py:44` |
| HTTP_TIMEOUT_SECONDS | 20 | `quality.py:43` |
| MAX_RETRIES_PER_PROVIDER | 1 | `quality.py:42` |
| CORE_ASSETS | {1: "BTC", 1027: "ETH", 825: "USDT"} | `quality.py:99-103` |
| TRADING_ENABLED | False | `quality.py:160` |
| ORDERS_ENABLED | False | `quality.py:161` |
| STRATEGY_ENABLED | False | `quality.py:162` |
| PORTFOLIO_ACTIONS_ENABLED | False | `quality.py:163` |
| AUTO_PERSIST_SNAPSHOT | False | `quality.py:155` |

---

## 6. Provider Mode Sequence (Runtime Fallback)

Source: `acquire_top125_with_orchestration()` → `app/market/finalization.py:239-352`

```
1. CMC keyless → acquire_cmc_top125(authenticated=False)
2. If FAIL → CMC authenticated → acquire_cmc_top125(authenticated=True) [if CMC_API_KEY]
3. If FAIL → CoinGecko → acquire_coingecko_top125()
4. Stops on first VALIDATED result
```

Each provider retried up to `MAX_RETRIES_PER_PROVIDER` (1) on: TIMEOUT, RATE_LIMIT, UNAVAILABLE, TECHNICAL_ERROR, PROVIDER_ERROR.

`fallback_used` and `fallback_reason` tracked in result (`finalization.py:288-333`).

---

## 7. Data NOT Retrieved (Gaps)

### A. NO historical data retrieval implemented
- CMC historical listings (`/v3/cryptocurrency/listings/historical`): NOT implemented
- CMC historical quotes: NOT implemented
- CoinGecko historical market data: NOT implemented
- Exchange historical klines: NOT called (only 2 candles via `EXCHANGE_KLINE_LIMIT=2`)
- Orderbook history: Snapshot-only (REST, no WebSocket streams)

### B. NO trade data retrieved
- No exchange trade endpoints called (all 8 exchanges have trade APIs but U06.5 does not use them)
- No CMC trade data
- No CoinGecko trade data

### C. NO real-time streams
- All acquisition is REST HTTP GET — no WebSocket connections
- No real-time orderbook delta updates
- No ticker/price tick streams

### D. NO CMC authenticated data at runtime
- `acquire_market_index_time_series()` exists (`finalization.py:604-787`) but NOT called in current runtime path
- Requires CMC_API_KEY + CMC plan with intraday historical access

### E. NO persistence
- `AUTO_PERSIST_SNAPSHOT=False` — no foundation snapshots persisted
- `load_kitchen_index_history()` exists (`finalization.py:817-948`) but history directory is empty
- No raw artifact or audit artifact persistence for U06.5

### F. Exchange coverage is BTCUSDT-only
- All 8 exchanges probe only BTCUSDT (or equivalent: BTC-USDT, BTC_USDT, USDT-BTC)
- No per-asset OHLCV or orderbook for the other 124 assets in the Top-125

---

## 8. UNKNOWN Items (Cannot verify from code alone)

| # | Item | Evidence Location | Why Unknown |
|---|------|-------------------|-------------|
| 1 | CMC_API_KEY configured at runtime | `app/config/quality.py:74-88` | Env var; code discovery logic exists but value NOT inspected |
| 2 | CG_API_KEY configured at runtime | `app/config/quality.py:90-94` | Env var read but not used in request; runtime value NOT inspected |
| 3 | All 8 exchange endpoints return valid data | `app/market/exchange_evidence.py:198-383` | Tests use synthetic mock rows; no live probes captured |
| 4 | 7-of-8 gate passes with real exchange data | `app/market/exchange_evidence.py:356-357` | Gate logic is sound but empirical pass/fail rate NOT verified |
| 5 | CMC keyless rate limits behavior | `app/config/quality.py:25` | Rate limits not documented in config; depend on CMC free tier |
| 6 | CoinGecko free-tier rate limits | `app/config/quality.py:27` | Rate limits not documented in config; depend on CG free tier |
| 7 | Total latency of full multi-exchange run | `app/market/exchange_evidence.py:198-383` | No runtime timing data captured |
| 8 | Empirical basis for MIN_VALIDATED_EXCHANGE_COUNT=7 | `app/config/exchanges.py:19` | No documented rationale for threshold |
| 9 | Exchange response schema deviations | `_valid_kline_row()` at `exchange_evidence.py:230-241` | Tests use expected format; real-world deviations NOT tested |
| 10 | U06 vs U06.5 naming resolution | `U06_MANIFEST.json` vs code | Manifest says U06/stage=U05_HISTORICAL_DATA_QUALITY_GATE; code is U06.5 |

---

## 9. Test Evidence for Source Access

| Test Module | Tests | Coverage | Source |
|-------------|-------|----------|--------|
| `test_u06_5_global_providers.py` | ~8 | CMC/CG normalization, headers, routing | `/tests/unit/` |
| `test_u06_5_unit_4_exchange_evidence.py` | 4 | 8-exch all pass, 1 fail passes gate, gate fail, malformed | `tests/unit/test_u06_5_unit_4_exchange_evidence.py` |
| `test_u06_5_unit_5_orderbook.py` | 4 | Valid orderbook, malformed, provider failure, contract | `tests/unit/test_u06_5_unit_5_orderbook.py` |
| `test_u06_5_unit_6_global_validation.py` | 9 | Normalize CMC/CG, identity, numeric, timestamp, ranked, core | `tests/unit/test_u06_5_unit_6_global_validation.py` |
| `test_u06_5_http.py` | 5 | Success, 429, URL error, malformed, timeout | `tests/unit/test_u06_5_http.py` |

**Test row used for Binance validation** (synthetic):
```python
[1_700_000_000_000, "100.0", "110.0", "90.0", "105.0", "10.0", 1000, "1050.0"]
# [timestamp, open, high, low, close, volume, close_time, quote_volume]
```
Source: `tests/unit/test_u06_5_unit_4_exchange_evidence.py:22-32`

**Total**: ~97 test functions across 10 modules (`U06_5_FULL_DISCOVERY_REPORT.md:456-469`)

---

## 10. Summary Classification (Source Access)

### VERIFIED (Code/config evidence present)

| Capability | Status | Source |
|------------|--------|--------|
| CMC keyless Top-125 acquisition (4 endpoints) | VERIFIED | `global_providers.py:106-147`, `quality.py:25-26` |
| CoinGecko Top-125 fallback | VERIFIED | `global_providers.py:150-159`, `quality.py:27` |
| CMC authenticated mode (optional) | VERIFIED in code | `global_providers.py:82-90` |
| 8-exchange OHLCV acquisition (BTCUSDT, 5m, 2 candles) | VERIFIED | `exchange_evidence.py:198-383`, `exchanges.py:70-149` |
| 8-exchange orderbook acquisition (100 levels) | VERIFIED | `exchange_evidence.py:479-527` |
| 7-of-8 gate logic (OHLCV + orderbook) | VERIFIED | `exchange_evidence.py:356-357`, `498-500` |
| Independent parallel exchange probes | VERIFIED | `exchange_evidence.py:339-340` |
| Normalization (CMC/CG + all 8 exchanges) | VERIFIED | `global_providers.py:182-209`, `exchange_evidence.py:244-333,407-476` |
| Validation rules (identity, numeric, timestamp, universe, core, freshness) | VERIFIED | `global_providers.py:223-340`, `exchange_evidence.py:230-241,390-404` |
| HTTP timeout (20s), max retries (1) | VERIFIED | `quality.py:42-43` |
| Safety locks (all False) | VERIFIED | `quality.py:160-163` |
| Provider mode sequence with fallback | VERIFIED | `finalization.py:239-352` |
| 97+ unit tests covering all acquisition | VERIFIED | 10 test modules |

### NOT VERIFIED (No runtime evidence)

| Capability | Status | Reason |
|------------|--------|--------|
| CMC_API_KEY configured | NOT VERIFIED | Env var; code exists but runtime value unknown |
| CG_API_KEY configured | NOT VERIFIED | Env var read but not used; value unknown |
| Live exchange endpoint responses | NOT VERIFIED | Tests are synthetic/mocked |
| Live 7-of-8 gate pass rate | NOT VERIFIED | No runtime probe results |
| CMC keyless rate limit behavior | NOT VERIFIED | Not in config; provider-dependent |
| CoinGecko rate limit behavior | NOT VERIFIED | Not in config; provider-dependent |
| End-to-end pipeline execution | NOT VERIFIED | `e2e_scanner_test.py` exists but results NOT captured |

### NOT IMPLEMENTED / NOT AVAILABLE

| Capability | Status | Evidence |
|------------|--------|----------|
| Historical OHLCV beyond 2 candles | NOT AVAILABLE | `EXCHANGE_KLINE_LIMIT=2` (`exchanges.py:42`) |
| Historical global provider data | NOT AVAILABLE | No historical endpoints in `global_providers.py` |
| Trade data (any exchange) | NOT AVAILABLE | No trade endpoints called |
| Orderbook streams | NOT AVAILABLE | REST only, no WebSocket |
| Exchange API key authentication | NOT AVAILABLE | All 8 are PUBLIC_SPOT |
| Per-asset exchange data (non-BTCUSDT) | NOT AVAILABLE | All probes use BTCUSDT only |
| Snapshot persistence | NOT AVAILABLE | `AUTO_PERSIST_SNAPSHOT=False` (`quality.py:155`) |
| Foundation lock gate (runtime) | NOT VERIFIED | `technical_lock_gate()` exists (`finalization.py:2178-2241`) but no runtime execution evidence |

---

## 11. Key Findings (Unit 01: Source Access)

1. **All 10 source endpoints are fully configured in code** (2 global providers + 8 exchanges). Each has documented URLs, parameters, symbol formats, and normalization logic.

2. **No data fabrication mechanisms exist** — explicit unavailable/error handling throughout (`exchange_evidence.py:1-10`); no synthetic volume, no interpolation, no silent resampling.

3. **The 7-of-8 gate is implemented but not empirically verified** — gate logic is sound (independent parallel probes, ≥7 validation required), but tests use synthetic mock data, not live exchange responses.

4. **CMC authenticated mode is optional and conditional on environment** — code exists for header injection (`global_providers.py:82-90`), but `CMC_API_KEY` runtime status is UNKNOWN.

5. **Historical data access is entirely absent** — no historical endpoints implemented for any provider; exchange kline limit defaults to 2 candles; `AUTO_PERSIST_SNAPSHOT=False`.

6. **Exchange coverage is BTCUSDT-only** — all 8 exchanges are probed with the same trading pair; per-asset OHLCV/orderbook for the other 124 Top-125 assets is NOT retrieved.

7. **No exchange uses authenticated API keys** — all 8 are configured as PUBLIC_SPOT mode; WebSocket streams are not used (REST only).

8. **Three distinct fallback systems coexist** — U05 legacy (Binance→Coinbase, 5 symbols), U06.5 multi-exchange (8 venues, 7-of-8 gate), Stage 10 display routing (higher-priority-only).

---

## 12. Open Questions Requiring Live Verification

| Priority | Question | Evidence Need |
|----------|----------|---------------|
| HIGH | Is `CMC_API_KEY` configured? | Env var inspection + authenticated endpoint test |
| HIGH | Do all 8 exchange endpoints resolve and return valid OHLCV? | Live HTTP probe of each URL |
| HIGH | Does the 7-of-8 gate pass in practice? | Live `acquire_multi_exchange_evidence()` execution |
| HIGH | What are actual rate limits for CMC keyless and CoinGecko? | API response headers / documented limits |
| MEDIUM | Is exchange response schema consistent with validation expectations? | Live response field comparison |
| MEDIUM | What is total runtime latency for the full multi-exchange probe? | Timing instrumentation |
| LOW | Does CoinGecko accept and use CG_API_KEY if provided? | Code shows key read but not sent in request |

---

## 13. Evidence Sources Consumed

This checkpoint consolidates findings from:

| File | Commit | Purpose |
|------|--------|---------|
| `U06_5_FULL_DISCOVERY_REPORT.md` | `a7368dd` | Complete source inventory, call chain, downstream stage dependencies |
| `U06_5_SOURCE_HISTORICAL_EVIDENCE_AUDIT.md` | `19ece08` | Per-source audit of all 10 providers with endpoints, normalization, validation |
| `U06_5_RUNTIME_SOURCE_MAP.md` | (untracked, working dir) | Complete data-trace audit across 20 categories × A/B/C/D classifications |

**No new source code was written or modified. No web searches were performed. No live API calls were made.**

---

## 14. Checkpoint Metadata

| Field | Value |
|-------|-------|
| Checkpoint File | `U06_5_RESEARCH_UNIT_01_SOURCES_ACCESS.md` |
| Cell ID | U06.5 |
| Version | 8.4.5 |
| Schema | U06_5_SCHEMA_V6_0 |
| Checkpoint Date | 2026-09-26T14:09:00Z |
| Evidence Sources | 3 existing audit/report files (commits a7368dd, 19ece08; untracked working file) |
| Production Code Modified | NO |
| Live API Calls Made | NO |
| Web Searches Performed | NO |
| Status | CONSOLIDATED — no gaps to fill; marks UNKNOWN where evidence is absent |
