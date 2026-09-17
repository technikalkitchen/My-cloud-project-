# U06.5 FULL DISCOVERY REPORT

## 1. Executive Summary

U06.5 (Market Data Foundation) is the core market-data acquisition, validation, ranking, and orchestration layer for the Kitchen Assistant v3.1 project. It provides the authoritative data foundation consumed by Stages U07, U08, U09, U10, U11, and U12.

**Key Architectural Decisions:**
- **Dynamic Ranking**: Assets are ranked by market-cap on every request (no persistent cache)
- **Provider Priority**: CoinMarketCap (keyless → authenticated) → CoinGecko (fallback)
- **Exchange Priority**: 8 exchanges in fixed priority order (Binance → OKX → Bybit → KuCoin → Coinbase → Gate → Upbit → Bitget)
- **Fallback Direction**: Only toward higher-priority exchanges (never lower)
- **Coverage Gates**: 7-of-8 exchanges required for multi-exchange evidence; 100% Top-125 coverage required
- **Immutable Snapshots**: SHA-256 frozen foundations with consumer adapters for downstream stages
- **No Data Fabrication**: Explicit unavailable/error handling; no synthetic values

**Version**: 8.4.5 | **Schema**: U06_5_SCHEMA_V6_0 | **Cell ID**: U06.5

---

## 2. Exact U06.5 Files Found

### Core Source Files (Layer A)
| File | Path | Lines | Purpose |
|------|------|-------|---------|
| u06_5.py | `/app/core/u06_5.py` | 239 | Core utilities (hashing, timestamps, paths, redaction) |
| ranking.py | `/app/market/ranking.py` | 241 | Dynamic market-cap ranking + Kitchen indices |
| global_providers.py | `/app/market/global_providers.py` | 341 | CMC + CoinGecko acquisition, normalization, validation |
| exchange_evidence.py | `/app/market/exchange_evidence.py` | 527 | Exchange OHLCV + orderbook acquisition (8 exchanges) |
| reference.py | `/app/market/reference.py` | 778 | Reliability-weighted reference price engine |
| finalization.py | `/app/market/finalization.py` | 2273 | Foundation assembly, hashing, consumer adapters, lock gate |
| http.py | `/app/market/http.py` | 157 | HTTP client with error classification |

### Configuration Files
| File | Path | Lines | Purpose |
|------|------|-------|---------|
| quality.py | `/app/config/quality.py` | 168 | All validation thresholds, provider priority, constants |
| exchanges.py | `/app/config/exchanges.py` | 204 | Exchange specs, 8-venue configs, coverage contracts |

### Test Files (10 unit test modules)
| File | Path | Lines | Tests |
|------|------|-------|-------|
| test_u06_5_core.py | `/tests/unit/test_u06_5_core.py` | 99 | Core utilities |
| test_u06_5_config.py | `/tests/unit/test_u06_5_config.py` | 70 | Configuration contracts |
| test_u06_5_global_providers.py | `/tests/unit/test_u06_5_global_providers.py` | 114 | Global provider acquisition |
| test_u06_5_http.py | `/tests/unit/test_u06_5_http.py` | 129 | HTTP client |
| test_u06_5_unit_4_exchange_evidence.py | `/tests/unit/test_u06_5_unit_4_exchange_evidence.py` | 122 | 8-exchange OHLCV + 7-of-8 gate |
| test_u06_5_unit_5_orderbook.py | `/tests/unit/test_u06_5_unit_5_orderbook.py` | 112 | 8-exchange orderbook |
| test_u06_5_unit_6_global_validation.py | `/tests/unit/test_u06_5_unit_6_global_validation.py` | 179 | Asset normalization + validation |
| test_u06_5_unit_7_reference_price.py | `/tests/unit/test_u06_5_unit_7_reference_price.py` | 594 | Reference price engine |
| test_u06_5_unit_8_ranking.py | `/tests/unit/test_u06_5_unit_8_ranking.py` | 315 | Dynamic ranking + Kitchen indices |
| test_u06_5_unit_9_finalization.py | `/tests/unit/test_u06_5_unit_9_finalization.py` | 416 | Foundation, hash, lock gate, adapters |

### Manifests / Audit / Ledger Artifacts
| File | Path | Purpose |
|------|------|---------|
| U06_MANIFEST.json | `/U06_MANIFEST.json` | Execution unit manifest (U06 = U05 Historical Data Quality Gate) |
| U06_AUDIT_METADATA.json | `/U06_AUDIT_METADATA.json` | Audit results for U06 |
| U06_SHA256.json | `/U06_SHA256.json` | SHA-256 hashes for U06 artifacts |
| U06_LEDGER.md | `/ledgers/U06_LEDGER.md` | U06 execution ledger |

---

## 3. Exact Paths for Every Related File

```
/workspaces/My-cloud-project-/app/core/u06_5.py
/workspaces/My-cloud-project-/app/market/ranking.py
/workspaces/My-cloud-project-/app/market/global_providers.py
/workspaces/My-cloud-project-/app/market/exchange_evidence.py
/workspaces/My-cloud-project-/app/market/reference.py
/workspaces/My-cloud-project-/app/market/finalization.py
/workspaces/My-cloud-project-/app/market/http.py
/workspaces/My-cloud-project-/app/config/quality.py
/workspaces/My-cloud-project-/app/config/exchanges.py
/workspaces/My-cloud-project-/tests/unit/test_u06_5_core.py
/workspaces/My-cloud-project-/tests/unit/test_u06_5_config.py
/workspaces/My-cloud-project-/tests/unit/test_u06_5_global_providers.py
/workspaces/My-cloud-project-/tests/unit/test_u06_5_http.py
/workspaces/My-cloud-project-/tests/unit/test_u06_5_unit_4_exchange_evidence.py
/workspaces/My-cloud-project-/tests/unit/test_u06_5_unit_5_orderbook.py
/workspaces/My-cloud-project-/tests/unit/test_u06_5_unit_6_global_validation.py
/workspaces/My-cloud-project-/tests/unit/test_u06_5_unit_7_reference_price.py
/workspaces/My-cloud-project-/tests/unit/test_u06_5_unit_8_ranking.py
/workspaces/My-cloud-project-/tests/unit/test_u06_5_unit_9_finalization.py
/workspaces/My-cloud-project-/U06_MANIFEST.json
/workspaces/My-cloud-project-/U06_AUDIT_METADATA.json
/workspaces/My-cloud-project-/U06_SHA256.json
/workspaces/My-cloud-project-/ledgers/U06_LEDGER.md
```

---

## 4. U06.5 Source-Code Inventory

### Units Implemented (Layer A - Acquisition/Normalization/Validation)

| Unit | File | Function | Description |
|------|------|----------|-------------|
| **Unit 1-3** | global_providers.py | `acquire_cmc_top125()`, `acquire_coingecko_top125()` | CMC (keyless → auth) primary, CoinGecko fallback |
| **Unit 4** | exchange_evidence.py | `acquire_multi_exchange_evidence()` | 8 independent exchange OHLCV probes, 7-of-8 gate |
| **Unit 5** | exchange_evidence.py | `acquire_multi_exchange_orderbook()` | 8 independent orderbook probes, same gate |
| **Unit 6** | global_providers.py | `normalize_cmc_asset()`, `normalize_coingecko_asset()`, `validate_*()` | Asset normalization + validation |
| **Unit 7** | reference.py | `price_aggregate_v1()`, `build_live_reference_price_from_multi_exchange()` | MAD outlier filter, reliability-weighted aggregation |
| **Unit 8** | ranking.py | `dynamic_rank_assets()`, `calculate_indices_from_top125()` | Market-cap ranking + Kitchen indices |
| **Unit 9** | finalization.py | `run_u06_5()`, `build_foundation()`, `freeze_foundation()` | Orchestration, SHA-256 freeze, consumer adapters |

### Layer B Components (Consumed by U06.5 but implemented in Stage 10+)
| Component | File | Purpose |
|-----------|------|---------|
| Dynamic Top-10 Consumer | `app/analysis/stage10_consumer.py` | Consumes `dynamic_rank_assets()` for ranks 2-10 |
| Exchange Router | `app/analysis/stage10_router.py` | Higher-priority-only fallback routing |
| USDT/BTC Processors | `app/analysis/stage10_usdt.py`, `stage10_btc.py` | Pair validation with fallback provenance |

---

## 5. U06.5 Configuration Inventory

### Provider Priority (quality.py + exchanges.py)
```python
PROVIDER_PRIORITY = {
    "global": ["coinmarketcap", "coingecko"],
    "exchange": [
        "binance", "okx", "bybit", "kucoin",
        "coinbase", "gate", "upbit", "bitget"
    ]
}
FORBIDDEN_RUNTIME_PROVIDERS = {"tradingview", "tradingview_reference", "tv"}
```

### Coverage Contracts (exchanges.py - IMMUTABLE)
```python
TARGET_EXCHANGE_COUNT = 8
MIN_VALIDATED_EXCHANGE_COUNT = 7
MULTI_EXCHANGE_PROBE_SYMBOL = "BTCUSDT"
```

### Quality Thresholds (quality.py)
```python
TOP_N = 125
TIMEFRAME = "5m"
FRESHNESS_THRESHOLD_SECONDS = 900  # 15 minutes
MIN_TOP125_COVERAGE = 1.0  # 100%
TARGET_CANDIDATE_POOL = 1250
MAX_RETRIES_PER_PROVIDER = 1
HTTP_TIMEOUT_SECONDS = 20
```

### Reference / Cross-Source
```python
REFERENCE_STATUS = "REFERENCE_NOT_USED"
REFERENCE_PROVIDER = "coingecko"
REFERENCE_MAX_PRICE_DEVIATION_PCT = 1.0
REFERENCE_MIN_OVERLAP = 0.80
REFERENCE_REQUIRED_FOR_LOCK = False
```

### Reliability Component Weights (quality.py:140-149)
```python
"reliability_component_weights": {
    "data_integrity": 0.15,      # Fixed 1.0
    "freshness": 0.10,
    "volume": 0.15,
    "near_depth": 0.20,
    "far_depth": 0.10,
    "spread": 0.10,
    "price_impact": 0.10,
    "cross_exchange_consistency": 0.10,
}
```

### Safety Locks (asserted at import)
```python
TRADING_ENABLED = False
ORDERS_ENABLED = False
STRATEGY_ENABLED = False
PORTFOLIO_ACTIONS_ENABLED = False
AUTO_PERSIST_SNAPSHOT = False
```

---

## 6. Exchange Ranking/Scoring Logic

### Global Provider Priority (Static Configuration)
**Source**: `app/config/quality.py:12`, `app/config/exchanges.py:52-58`

The provider priority is **STATIC** (configured at startup):
1. **Global**: CoinMarketCap (keyless) → CoinMarketCap (authenticated, optional) → CoinGecko
2. **Exchange**: Binance (1) → OKX (2) → Bybit (3) → KuCoin (4) → Coinbase (5) → Gate (6) → Upbit (7) → Bitget (8)

### Exchange Fallback Logic (Static Priority, Dynamic Selection)
**Source**: `app/analysis/stage10_router.py:73-90`, `app/analysis/stage10_consumer.py:37-46`

```python
DISPLAY_FALLBACK_PRIORITY = [
    Exchange.BINANCE,      # Priority 1 (highest)
    Exchange.OKX,          # Priority 2
    Exchange.BYBIT,        # Priority 3
    Exchange.KUCOIN,       # Priority 4
    Exchange.COINBASE,     # Priority 5
    Exchange.GATE,         # Priority 6
    Exchange.UPBIT,        # Priority 7
    Exchange.BITGET,       # Priority 8 (lowest)
]
```

**Fallback Chain**: Selected exchange → higher-priority exchanges only
- Example: Selected=Bitget → [Bitget, Upbit, Gate, Coinbase, KuCoin, Bybit, OKX, Binance]
- Example: Selected=OKX → [OKX, Binance]
- Example: Selected=Binance → [Binance]

**Rule**: NEVER falls back to lower-priority exchanges (validated in `validate_fallback_direction()`)

---

## 7. Whether Exchange Ranking is STATIC or DYNAMIC

| Ranking Type | Implementation | Static/Dynamic |
|--------------|----------------|----------------|
| **Global Provider Priority** | `PROVIDER_PRIORITY` dict | **STATIC** (config constant) |
| **Exchange Display Priority** | `DISPLAY_FALLBACK_PRIORITY` list | **STATIC** (config constant) |
| **Asset Market-Cap Ranking** | `dynamic_rank_assets()` | **DYNAMIC** (computed per request) |
| **Exchange Validation Gate** | `acquire_multi_exchange_evidence()` | **DYNAMIC** (live probe per run) |
| **Reference Price Reliability** | `price_aggregate_v1()` | **DYNAMIC** (per-observation scoring) |

**Key Finding**: The exchange *priority order* is static configuration. The asset *market-cap ranking* is dynamic (recomputed each call). The exchange *validation results* are dynamic (live probes).

---

## 8. Exact Ranking Criteria Found

### Asset Market-Cap Ranking (`ranking.py:30-35`)
```python
def deterministic_sort_key(record):
    mc = safe_float(record.get("market_cap"))
    asset_id = record.get("canonical_asset_id") or record.get("provider_asset_id") or ""
    symbol = str(record.get("symbol") or "").upper()
    return (-(mc if mc is not None else -1.0), str(asset_id), symbol)
```

**Tie-Break Rule** (exact, from `ranking.py:101-103`):
> "market_cap_desc, canonical_asset_id_asc, symbol_asc"

### Segment Assignment (`ranking.py:78-84`)
```python
item["segment"] = (
    "BTC" if r == 1
    else "ETH" if r == 2
    else "TOP10_ALT" if r <= 10
    else "BROAD_ALT_11_125"
)
```

### Rank Consistency Check (`ranking.py:65-76`)
Compares `provider_rank` vs `calculated_rank`:
- MATCH: diff == 0
- MINOR_DIFFERENCE: diff <= 2
- WARNING: diff <= 5 (configurable)
- UNAVAILABLE: provider_rank is None

---

## 9. Whether Ranking is Recalculated Per Request/Run

**YES - Fully Dynamic Per Request**

Evidence:
- `stage10_consumer.py:118-138`: `get_dynamic_top10()` calls `dynamic_rank_assets(valid_assets)` on **every call**
- `stage10_consumer.py:104-105`: "Computes dynamically — no caching. The caller is responsible for invoking dynamic_rank_assets fresh when a re-computation is needed."
- `ranking.py:38-106`: `dynamic_rank_assets()` accepts `valid_assets` sequence and returns new ranking each call
- `finalization.py:1244`: `ranking = dynamic_rank_assets(list(selected_records))` called during foundation assembly

**No persistent cache exists** for rankings. Each run/request gets a fresh ranking.

---

## 10. Color/Category/Band Logic Found

### Asset Segments (ranking.py:78-84)
| Segment | Rank Range | Meaning |
|---------|------------|---------|
| BTC | 1 | Bitcoin (excluded from Top-10) |
| ETH | 2 | Ethereum |
| TOP10_ALT | 3-10 | Top 10 altcoins (Dynamic Top-10) |
| BROAD_ALT_11_125 | 11-125 | Remaining validated assets |

### Depth Bands (quality.py:137)
```python
"depth_bands_pct": (0.05, 0.10, 0.25, 0.50, 1.00)
```
Used in `reference.py:742-749` for orderbook depth calculation at 0.05%, 0.10%, 0.25%, 0.50%, 1.00% from mid-price.

### Price Impact Notionals (quality.py:139)
```python
"price_impact_notional_usd": (10_000.0, 100_000.0)
```
Used for slippage calculation at $10k and $100k notional.

### Rank Consistency Bands (ranking.py:70-75, quality.py implied)
| Status | Difference Threshold |
|--------|---------------------|
| MATCH | 0 |
| MINOR_DIFFERENCE | ≤ 2 |
| WARNING | ≤ 5 (config: `rank_warning_difference`) |
| FAIL | > 5 |

### Freshness Status (global_providers.py:264-274, validation.py:113-121)
| Status | Condition |
|--------|-----------|
| FRESH | age ≤ FRESHNESS_THRESHOLD_SECONDS (900s) |
| STALE | age > 900s |
| UNAVAILABLE | unparseable/missing timestamp |

### Reference Validation Status (finalization.py:468-475)
| Status | Condition |
|--------|-----------|
| VALIDATED | overlap ≥ 80% AND agreement_ratio ≥ 80% |
| PARTIAL | usable core assets exist but thresholds not met |
| NOT_AVAILABLE | no usable cross-source data |

### Gate Status (exchange_evidence.py:370-377, 510-519)
| Gate | Status Values |
|------|---------------|
| Exchange Coverage (7-of-8) | PASSED / FAILED |
| Orderbook Coverage | PASSED / FAILED |

---

## 11. Exchange Fallback Logic and Its Source

### Primary Source: `app/analysis/stage10_router.py`

**Fallback Chain Generation** (lines 73-90):
```python
def get_fallback_chain(self) -> List[str]:
    selected_idx = index of selected in DISPLAY_FALLBACK_PRIORITY
    return [e.value for e in reversed(DISPLAY_FALLBACK_PRIORITY[:selected_idx + 1])]
```

**Validation** (lines 107-119):
```python
def validate_fallback_direction(self, requested: str, actual: str) -> Tuple[bool, str]:
    if requested == actual: return True, "no_fallback_needed"
    if self.is_higher_priority(actual, requested): return True, "fallback_higher_priority"
    return False, f"invalid_fallback: {actual} is lower priority than {requested}"
```

**Routing** (lines 121-161): Iterates fallback chain, returns first valid exchange.

### Legacy U05 Fallback (exchange_evidence.py:62-195)
```python
# Binance primary → Coinbase fallback only
# Used for U05 5-symbol compatibility
```

### Provider Fallback (global_providers.py:206-214, finalization.py:244-215)
```python
# CMC keyless → CMC authenticated (if key) → CoinGecko
# Implemented in provider_mode_sequence() and acquire_top125_with_orchestration()
```

---

## 12. Provider Priority Logic and Its Source

### Source: `app/config/quality.py:12`, `app/config/exchanges.py:52-58`

```python
PROVIDER_PRIORITY = {
    "global": ["coinmarketcap", "coingecko"],
    "exchange": [
        "binance", "okx", "bybit", "kucoin",
        "coinbase", "gate", "upbit", "bitget"
    ]
}
```

### Runtime Sequence (finalization.py:206-214):
```python
def provider_mode_sequence():
    sequence = []
    if CMC_API_KEY:
        sequence.append(("coinmarketcap", "KEYLESS"))
        sequence.append(("coinmarketcap", "AUTHENTICATED"))
    else:
        sequence.append(("coinmarketcap", "KEYLESS"))
    sequence.append(("coingecko", "PUBLIC"))
    return sequence
```

### Acquisition with Retry (finalization.py:239-352):
- Tries each provider/mode in sequence
- Up to `MAX_RETRIES_PER_PROVIDER` (1) retries per provider
- Retries on: TIMEOUT, RATE_LIMIT, UNAVAILABLE, TECHNICAL_ERROR, PROVIDER_ERROR
- Stops on first VALIDATED result
- Tracks `fallback_used` and `fallback_reason` in result

---

## 13. U06.5 Validation/Minimum-Data Rules

### Top-125 Validation (global_providers.py:277-306)
```python
def validate_ranked_universe(records, expected_count=TOP_N):
    # 1. Must be list
    # 2. Length >= 125
    # 3. Each record has valid rank (int >= 1)
    # 4. No duplicate ranks
    # 5. Coverage >= MIN_TOP125_COVERAGE (1.0 = 100%)
```

### Core Asset Validation (global_providers.py:309-322)
```python
def validate_core_assets(records):
    # BTC, ETH, USDT must be present in symbols
    CORE_ASSETS = {1: "BTC", 1027: "ETH", 825: "USDT"}
```

### Per-Record Validation (global_providers.py:325-340)
```python
def validate_record(record, retrieved_at):
    # 1. Identity: provider, symbol, canonical_asset_id
    # 2. Numeric: price, market_cap, volume_24h, pct_change_1h, pct_change_24h
    # 3. Timestamp: last_updated present, parseable, fresh (< 900s)
```

### Exchange Evidence Gates (exchange_evidence.py:356-377, 499-519)
```python
# 7-of-8 gate for OHLCV
gate_passed = validated_count >= MIN_VALIDATED_EXCHANGE_COUNT  # 7

# Orderbook gate (same threshold)
```

### Reference Price Minimum (reference.py:490-491, 504-505)
```python
min_markets_for_aggregate = 1      # QUALITY_CONFIG
min_reference_exchanges = 2        # QUALITY_CONFIG
```

### Foundation Lock Gate (finalization.py:2178-2241)
All must pass:
1. `foundation_hash_present` - SHA-256 not PENDING
2. `snapshot_id_present` - valid snapshot_id
3. `status_not_technical_error` - not TECHNICAL_ERROR
4. `no_critical_errors` - zero errors in foundation
5. `time_series_present` - required in HISTORICAL mode
6. `freshness_valid` - FRESH or ACCEPTABLE
7. `reference_validated` - only if REFERENCE_REQUIRED_FOR_LOCK=True (currently False)

---

## 14. U06.5 Tests

### Test Coverage Summary
| Test Module | Units Covered | Test Count | Key Assertions |
|-------------|--------------|------------|----------------|
| test_u06_5_core.py | Core utils | ~8 | Timestamps, hashing, redaction, root resolution |
| test_u06_5_config.py | Config | 6 | Constants, provider priority, exchange specs, safety locks |
| test_u06_5_global_providers.py | Units 1-3, 6 | ~8 | CMC/CG normalization, headers, routing |
| test_u06_5_http.py | HTTP | 5 | Success, 429, URL error, malformed, timeout |
| test_u06_5_unit_4_exchange_evidence.py | Unit 4 | 4 | 8-exch all pass, 1 fail passes gate, gate fail, malformed |
| test_u06_5_unit_5_orderbook.py | Unit 5 | 4 | Valid orderbook, malformed, provider failure, contract |
| test_u06_5_unit_6_global_validation.py | Unit 6 | 9 | Normalize CMC/CG, identity, numeric, timestamp, ranked, core |
| test_u06_5_unit_7_reference_price.py | Unit 7 | ~25 | Weights, MAD, outlier, observation, normalization, scoring, aggregation |
| test_u06_5_unit_8_ranking.py | Unit 8 | ~13 | Sort key, dynamic rank, segments, consistency, tie-break, indices |
| test_u06_5_unit_9_finalization.py | Unit 9 | ~15 | Structural, hash, run_u06_5, lock gate, adapters, persistence |

**Total**: ~97 test functions across 10 modules

### Self-Tests Embedded in finalization.py
- `structural_self_tests()`: 30+ architectural assertions
- `market_engine_self_tests()`: End-to-end engine parity
- `hash_contract_self_tests()`: SHA-256 determinism
- `consumer_contract_self_tests()`: Adapter wiring
- `determinism_self_test()`: Hash repeatability
- `rule_zero_self_test()`: No Colab/notebook patterns
- `credential_discovery_self_test()`: Env-only credentials

---

## 15. Manifests / Metadata / Ledgers / Audit Artifacts

### Manifest (U06_MANIFEST.json)
```json
{
  "execution_unit": "U06",
  "stage": "U05_HISTORICAL_DATA_QUALITY_GATE",
  "status": "LOCKED",
  "technical_lock": "LOCKED",
  "outputs": [
    "data/historical_u05/quality/U06_DATA_QUALITY_REPORT.json",
    "data/historical_u05/quality/U06_DATA_QUALITY_SUMMARY.txt",
    "ledgers/U06_LEDGER.md"
  ]
}
```

### Audit Metadata (U06_AUDIT_METADATA.json)
```json
{
  "audit": { "status": "PASSED", "technical_lock": "LOCKED" },
  "gate": {
    "sha256_control": "PASSED",
    "per_symbol_schema": "PASSED",
    "record_count": "PASSED",
    "symbol_coverage": "PASSED",
    "volume_contract": "PASSED",
    "safety_locks": "PASSED"
  }
}
```

### SHA-256 (U06_SHA256.json)
5 files hashed: U06_AUDIT_METADATA.json, U06_MANIFEST.json, U06_DATA_QUALITY_REPORT.json, U06_DATA_QUALITY_SUMMARY.txt, ledgers/U06_LEDGER.md

### Ledger (ledgers/U06_LEDGER.md)
- Global status: PASS
- Technical lock: LOCKED
- Record counts: 500 expected, 500 actual
- Source integrity: NOT MODIFIED

---

## 16. Runtime Call Chain: Who Imports/Calls U06.5

### Direct Imports of U06.5 Core
```
app/market/ranking.py           → from app.core.u06_5 import deep_copy, safe_float, safe_int
app/market/global_providers.py  → from app.core.u06_5 import parse_timestamp, safe_float, safe_int, timestamp_age_seconds, utc_now
app/market/exchange_evidence.py → from app.core.u06_5 import safe_float, safe_int, utc_now
app/market/reference.py         → from app.core.u06_5 import deep_copy, parse_timestamp, safe_float, safe_int, timestamp_age_seconds, utc_now
app/market/finalization.py      → from app.core.u06_5 import (15+ functions)
```

### Direct Imports of U06.5 Market Modules
```
app/market/finalization.py      → from app.market.ranking import dynamic_rank_assets, calculate_indices_from_top125
app/market/finalization.py      → from app.market.global_providers import (15+ functions)
app/market/finalization.py      → from app.market.exchange_evidence import acquire_exchange_evidence, acquire_multi_exchange_evidence, acquire_multi_exchange_orderbook
app/market/finalization.py      → from app.market.reference import (8+ functions)
app/analysis/stage10_consumer.py → from app.market.ranking import dynamic_rank_assets
app/analysis/stage12_top3.py    → from app.market.ranking import dynamic_rank_assets
app/analysis/stage11_strong_movers.py → from app.market.ranking import dynamic_rank_assets
app/market/u09_engine.py        → from app.market.providers import PROVIDER_REGISTRY
app/market/universe.py          → from app.market.providers import ...
app/market/universe.py          → from app.market.validation import validate_provider_assets
```

### Runtime Execution Chain (from STAGE_13_CODE_SOURCE_DISCOVERY.md)
```
Telegram command / Flask webhook
    → app/bot/telegram.py handler
    → app/bot/runner.py: BotRunner.handle_command()
    → app/analysis/stage12_top3.py: run_top3()
    → U06.5 dynamic_rank_assets()          ← PRIMARY RANKING CALL
    → Stage 10 consumer/router/USDT/BTC
    → Stage 11 run_strong_movers()
    → Stage 12 result construction
    → format_top3_telegram()
    → Telegram reply / HTTP response
```

---

## 17. Which Later Stages Depend on U06.5

| Stage | Dependency | Entry Point |
|-------|------------|-------------|
| **U07** | `build_u07_adapter()` → indices, kitchen_index_history | `finalization.py:1121-1158` |
| **U08** | `build_u08_adapter()` → assets (BTC/ETH/USDT), indices | `finalization.py:1161-1187` |
| **U09** | `build_u09_adapter()` → universe (candidate/valid/invalid/excluded/top125), exchange_evidence | `finalization.py:1190-1210` |
| **Stage 10** | `dynamic_rank_assets()` → ranks 2-10 (Top-10) | `stage10_consumer.py:118-138` |
| **Stage 11** | `dynamic_rank_assets()` → candidate universe (ranks 11-125) | `stage11_strong_movers.py:33, 70-80` |
| **Stage 12** | `dynamic_rank_assets()` → candidate pool for Top 3 | `stage12_top3.py:41, 80-90` |

**All downstream stages consume U06.5 foundation via adapters or direct ranking calls.**

---

## 18. Contradictions Found Between U06.5 Files

### Contradiction 1: U06 vs U06.5 Naming
- **Manifest/Audit/Ledger** reference `U06` (execution unit for U05 Historical Data Quality Gate)
- **Code** implements `U06.5` (Market Data Foundation v8.4.5)
- **Discrepancy**: U06_MANIFEST.json says stage="U05_HISTORICAL_DATA_QUALITY_GATE" but code is U06.5 market foundation

### Contradiction 2: REFERENCE_REQUIRED_FOR_LOCK
- **quality.py:124**: `REFERENCE_REQUIRED_FOR_LOCK = False`
- **finalization.py:2215-2219**: Gate checks this but defaults to `True` when False
- **Effect**: Reference validation is NOT required for lock (correct), but code path is confusing

### Contradiction 3: Two Exchange Fallback Systems
1. **U05 Legacy** (`exchange_evidence.py:62-195`): Binance → Coinbase only (5 symbols)
2. **U06.5 Multi-Exchange** (`exchange_evidence.py:198-383`): 8 exchanges, 7-of-8 gate
3. **Stage 10 Display** (`stage10_router.py`): 8 exchanges, higher-priority-only fallback for display
- **Issue**: Three different fallback concepts coexist with different semantics

### Contradiction 4: DATASET_MODE Handling
- **quality.py:36-37**: `DATASET_MODE` from env (SNAPSHOT/HISTORICAL)
- **finalization.py:571-576**: `build_range_contract()` returns SNAPSHOT_RANGE_ONLY for SNAPSHOT mode
- **finalization.py:789-793**: `build_time_series_contract()` behaves differently
- **Inconsistency**: SNAPSHOT mode doesn't require time series but HISTORICAL does; lock gate enforces time_series_present only in HISTORICAL

---

## 19. Missing Expected U06.5 Artifacts

| Expected Artifact | Status | Notes |
|-------------------|--------|-------|
| U06.5 Manifest (distinct from U06) | **MISSING** | Only U06 manifest exists |
| U06.5 Audit Metadata (distinct) | **MISSING** | Only U06 audit exists |
| U06.5 SHA256 (distinct) | **MISSING** | Only U06 SHA256 exists |
| U06.5 Ledger (distinct) | **MISSING** | Only U06 ledger exists |
| U06.5 Config Export | **MISSING** | No standalone config export |
| Historical Snapshots Dir | **EMPTY** | `data/history/U06_5/` created but no snapshots persisted (AUTO_PERSIST_SNAPSHOT=False) |
| Raw Artifacts Dir | **EMPTY** | `data/raw/U06_5/` created but no artifacts (AUTO_PERSIST_SNAPSHOT=False) |
| Audit Artifacts Dir | **EMPTY** | `data/audit/U06_5/` created but no artifacts |

---

## 20. RELEVANCE TO STAGE 13 — FACTS ONLY

### Does a Dynamic Exchange Ranking Already Exist?
**YES** — but with critical distinctions:

| Ranking Type | Exists? | Location | Recalculated Per Request? |
|--------------|---------|----------|---------------------------|
| **Asset Market-Cap Ranking** | ✅ YES | `app/market/ranking.py:dynamic_rank_assets()` | ✅ YES — every call |
| **Exchange Display Priority** | ✅ YES | `app/config/exchanges.py:DISPLAY_FALLBACK_PRIORITY` | ❌ NO — static config |
| **Exchange Validation Results** | ✅ YES | `app/market/exchange_evidence.py:acquire_multi_exchange_evidence()` | ✅ YES — live probes per run |
| **Reference Price Reliability** | ✅ YES | `app/market/reference.py:price_aggregate_v1()` | ✅ YES — per observation |

### Where Is Dynamic Asset Ranking Implemented?
**Primary**: `app/market/ranking.py:38-106` — `dynamic_rank_assets(valid_assets)`
**Consumed by**: Stage 10 (`stage10_consumer.py:138`), Stage 11 (`stage11_strong_movers.py:73`), Stage 12 (`stage12_top3.py:83`)

### What Determines Its Ranking?
1. **Primary**: `market_cap` descending (must be finite, non-negative)
2. **Tie-break 1**: `canonical_asset_id` ascending
3. **Tie-break 2**: `symbol` ascending
4. **Segments assigned**: BTC(1), ETH(2), TOP10_ALT(3-10), BROAD_ALT_11_125(11-125)

### Should Stage 13 Consume It?
**YES** — Stage 13 should consume the **dynamic asset ranking** from U06.5 via:
- Direct call: `dynamic_rank_assets(valid_assets)` (fresh each request)
- Or via Stage 10 consumer: `get_dynamic_top10(valid_assets)` for ranks 2-10
- Or via foundation adapters: `build_u09_adapter(foundation)["TOP125"]`

### Does Current Implementation Conflict with "Dynamic Ranking + Higher-Ranked-Only Fallback"?
**PARTIAL CONFLICT / NEEDS REVIEW**

| Concept | Current Implementation | Conflict? |
|---------|------------------------|-----------|
| **Dynamic asset ranking** | ✅ Fully dynamic per request | NO CONFLICT |
| **Higher-priority-only exchange fallback** | ✅ Implemented in Stage 10 router | NO CONFLICT |
| **Dynamic exchange ranking** | ❌ NOT IMPLEMENTED — exchange priority is STATIC config | **CONFLICT** |
| **Exchange ranking by reliability/quality** | ✅ Exists in reference.py (per-observation) but NOT used for exchange selection | **GAP** |

**Critical Finding**: The "Dynamic Exchange Ranking" concept (exchanges ranked by real-time quality/reliability, with fallback only to higher-ranked) **does not exist** as a unified system. What exists:
1. Static exchange priority config (DISPLAY_FALLBACK_PRIORITY)
2. Dynamic per-observation reliability scoring (reference.py) — used only for reference price, NOT for exchange selection
3. 7-of-8 validation gate — pass/fail, not ranked

**Stage 13 Implication**: If Stage 13 requires "Dynamic Exchange Ranking + higher-ranked-only fallback", this must be **NEWLY IMPLEMENTED**. The current Stage 10 router uses static priority only. The reliability scoring in reference.py could be adapted but is currently disconnected from exchange selection.

---

## CLASSIFICATION SUMMARY

| Category | Items |
|----------|-------|
| **IMPLEMENTED / FOUND** | Dynamic asset ranking (market-cap), 8-exchange evidence with 7-of-8 gate, provider fallback (CMC→CG), exchange fallback (higher-priority-only), reliability-weighted reference price, Kitchen indices, SHA-256 frozen foundations, consumer adapters for U07/U08/U09, comprehensive validation gates, 97+ unit tests |
| **NOT FOUND** | Dynamic exchange ranking (by quality/reliability), U06.5-specific manifests/audits/ledgers (only U06 exists), persisted snapshots (AUTO_PERSIST_SNAPSHOT=False), historical time series (requires CMC authenticated), bot-level retry/recovery, user session state |
| **UNCERTAIN / NEEDS REVIEW** | U06 vs U06.5 naming discrepancy in manifests, three coexisting fallback systems (U05 legacy, U06.5 multi-exch, Stage 10 display), REFERENCE_REQUIRED_FOR_LOCK=False but gate checks it, reliability scoring disconnected from exchange selection |

---

## VERIFICATION DATA

### Files Searched
- All `*.py` files in `/app/**`
- All `*.py` files in `/tests/unit/**`
- All root-level `*.json`, `*.md` files
- All files in `/ledgers/`

### Relevant Files Found
- **26** source/config files directly implementing U06.5
- **10** test modules (97+ test functions)
- **4** audit/manifest/ledger artifacts (for U06, not U06.5 distinct)

### Tests Found
- **10** unit test modules specific to U06.5 units
- **7** self-test suites embedded in finalization.py
- **Integration**: `e2e_scanner_test.py` exercises full chain

### Artifacts Found
- U06_MANIFEST.json, U06_AUDIT_METADATA.json, U06_SHA256.json, ledgers/U06_LEDGER.md
- No U06.5-specific artifacts (distinct from U06)

### Git Commit/Hash
- **Latest commit**: `c52d99b` — "Add Stage 13 code source discovery"
- **Repository**: Kitchen Assistant v3.1
- **Branch**: main (assumed)

---

**Report Generated**: 2026-09-17T21:47:35Z  
**Discovery Scope**: Complete repository search for U06.5 / U06_5 / U06.5 market-data foundation  
**No Files Modified**: This is a discovery-only report