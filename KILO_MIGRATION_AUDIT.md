# PART 1 — CORE ENGINE AUDIT

## U01 — Bootstrap + Architecture

### Exact Purpose
Creates the project directory structure, Python package boundaries, version metadata, configuration boundary, dependency manifest, environment template, and initial test harness. U01 is purely scaffolding; it does not implement any market data, scanner, or trading logic.

### Important Functions and Classes
- `get_settings()` — returns a frozen `Settings` dataclass instance.
- `Settings` — configuration boundary dataclass with `environment`, `timezone`, `log_level`.

### Important Constants and Schemas
- `PROJECT_NAME = "KITCHEN_ROBOT"`
- `PROJECT_VERSION = "2.7.0-dev"`
- `EXECUTION_UNIT = "U01"`
- Directory manifest: `app/`, `app/config/`, `app/core/`, `app/data/`, `app/market/`, `app/scanner/`, `app/trading/`, `app/journal/`, `app/orderbook/`, `app/api/`, `tests/`, `scripts/`, `config/`, `logs/`, `data/`, `backups/`, `ledgers/`

### Validation and Quality Gates
- pytest suite (`tests/test_u01.py`) verifying project metadata constants, configuration boundary, and required directories.
- U01 self-check verifying all artifact files exist.
- Final lock assertions verifying manifest, audit metadata, and ledger contain expected lock strings.

### Algorithms and Business Rules
- No market algorithms or business rules. Deterministic directory and file creation. SHA-256 inventory generation for all project files.

### Inputs and Outputs
- Inputs: None (bootstrap-only).
- Outputs: Directory tree, `app/core/version.py`, `app/config/settings.py`, `requirements.txt`, `config/.env.example`, `tests/test_u01.py`, `U01_AUDIT_METADATA.json`, `U01_MANIFEST.json`, `U01_SHA256.json`, `ledgers/U01_LEDGER.md`.

### Dependencies on Other Units
- None (first unit).

### Core Business Logic vs Colab/Build/Scaffolding Code
- Core business logic: None.
- Colab/build/scaffolding code: `pip install pytest`, `ROOT.mkdir`, package `__init__.py` generation, artifact inventory/manifest/SHA-256 generation, pytest execution via `subprocess.run`, Colab-specific print banners.

---

## U02 — Runtime Foundation + Flask/WSGI + Migration Readiness

### Exact Purpose
Establishes the WSGI runtime boundary using Flask, adds a timeframe/range validation guard, and verifies migration readiness. No scanner intelligence or market data is implemented.

### Important Functions and Classes
- `create_app()` — Flask application factory with `/health` and `/` endpoints.
- `validate_timeframe_guard(timeframe, custom_start, custom_end)` — technical validation boundary for timeframes and custom ranges.
- `_parse_custom_range(value)` — parses `DD-MM-YYYY HH:MM` format.

### Important Constants and Schemas
- `STANDARD_TIMEFRAMES = {"M1": 60, "M5": 300, "M15": 900, "H1": 3600, "H4": 14400, "D1": 86400, "D7": 604800}`
- `SUB_DAILY_WARNING` — warning string for sub-daily timeframes/ranges.
- Return schema: `{"valid", "warning", "reason", "is_sub_daily", "duration_seconds?"}`

### Validation and Quality Gates
- pytest (`tests/test_u02.py`) covering Flask app creation, endpoints, sub-daily warnings, custom range behavior, invalid inputs, WSGI entrypoint, and runtime file existence.
- Migration readiness self-check.
- Final lock assertions.

### Algorithms and Business Rules
- Timeframe normalization via regex.
- Sub-daily rule: recognized standard timeframe below D1 → VALID + SUB_DAILY_WARNING; D1 and higher → VALID without warning.
- Custom Range rule: `DD-MM-YYYY HH:MM`; below 24h → valid + warning; 24h+ → valid without warning; invalid format/order → invalid.
- No hardcoded list of low timeframes; duration comparison is used.

### Inputs and Outputs
- Inputs: `timeframe: str`, optional `custom_start: str`, `custom_end: str`.
- Outputs: Validation dict; Flask app; `app/api/app.py`, `wsgi.py`, `app/config/runtime.py`, `scripts/start_wsgi.sh`, `requirements.txt`, `tests/test_u02.py`, `U02_AUDIT_METADATA.json`, `U02_MANIFEST.json`, `U02_SHA256.json`, `ledgers/U02_LEDGER.md`.

### Dependencies on Other Units
- Requires U01 artifacts (manifest, audit, ledger) to be present and locked.

### Core Business Logic vs Colab/Build/Scaffolding Code
- Core business logic: `validate_timeframe_guard`, `_parse_custom_range`, `STANDARD_TIMEFRAMES`, `SUB_DAILY_WARNING`.
- Colab/build/scaffolding code: `pip install Flask gunicorn`, `subprocess.run` pytest execution, print banners, artifact inventory/manifest/SHA-256 generation, migration readiness checks.

---

## U03 — Data / Capture Foundation

### Exact Purpose
Creates the provider-independent data foundation: canonical Candle model, capture contract, validation layer, normalization layer, and JSONL storage foundation.

### Important Functions and Classes
- `Candle` — frozen dataclass with `symbol`, `timestamp`, `open`, `high`, `low`, `close`, `volume`. Includes `__post_init__` validation.
- `candle_to_dict(candle)` — serializes Candle to dict.
- `candle_from_dict(data)` — deserializes dict to Candle.
- `CandleCapture(ABC)` — abstract base class with `fetch(symbol, limit)`.
- `validate_candles(candles)` — validates collection is non-empty, all are Candle instances, strictly chronological.
- `normalize_candle(data)` — normalizes raw dict to Candle (symbol uppercased/stripped, numeric coercion).
- `write_candles(candles, path)` — writes JSONL storage.

### Important Constants and Schemas
- Candle schema: `symbol: str`, `timestamp: int (>0)`, `open/high/low/close: float (positive, high>=low, open/close within [low,high])`, `volume: float (>=0)`.

### Validation and Quality Gates
- pytest (`tests/data/test_u03.py`) covering Candle model, invalid OHLC rejection, chronological validation, normalization, and JSONL storage.
- Data foundation self-check.
- U02 prerequisite lock verification.
- Final lock assertions.

### Algorithms and Business Rules
- OHLC structural validation: `high >= low`, `low <= open <= high`, `low <= close <= high`, `volume >= 0`.
- Chronological validation: strictly increasing timestamps.
- Normalization: symbol → upper/strip; numeric fields → float/int coercion.

### Inputs and Outputs
- Inputs: Raw candle dicts or Candle instances.
- Outputs: Validated/normalized Candle instances; JSONL files; `app/data/models/candle.py`, `app/data/capture/base.py`, `app/data/validation/candles.py`, `app/data/validation/normalize.py`, `app/data/capture/storage.py`, `tests/data/test_u03.py`, `U03_AUDIT_METADATA.json`, `U03_MANIFEST.json`, `U03_SHA256.json`, `ledgers/U03_LEDGER.md`.

### Dependencies on Other Units
- Requires U02 to be validated and locked.

### Core Business Logic vs Colab/Build/Scaffolding Code
- Core business logic: `Candle` model, `validate_candles`, `normalize_candle`, `write_candles`, `CandleCapture` ABC.
- Colab/build/scaffolding code: directory creation, pytest execution, artifact inventory/manifest/SHA-256 generation, U02 prerequisite checks.

---

## U04 — Real Market Data Provider / Capture

### Exact Purpose
Connects to real public market data providers (Binance primary, Coinbase fallback) and captures live candle data. Validates import integrity, structural correctness, and live data quality.

### Important Functions and Classes
- `BinancePublicAdapter` — Binance Spot Public adapter with `_request()`, `symbol_available()`, `fetch()`.
- `CoinbasePublicAdapter` — Coinbase Exchange Public fallback adapter with `_product_id()`, `symbol_available()`, `fetch()`.
- `ProviderRouter` — routes requests Binance-first, Coinbase-fallback via `fetch()`.
- `BinanceProviderUnavailable`, `CoinbaseProviderUnavailable` — exception classes.

### Important Constants and Schemas
- `BinancePublicAdapter.BASE_URLS` — list of 5 Binance API base URLs.
- `BinancePublicAdapter.GRANULARITY_MAP` — interval mapping.
- `CoinbasePublicAdapter.BASE_URL` — single Coinbase API URL.
- `CoinbasePublicAdapter.GRANULARITY_MAP` — seconds mapping.
- Candle row schema (Binance): `[open_time, open, high, low, close, volume, close_time, quote_volume, ...]`
- Candle row schema (Coinbase): `[time, low, high, open, close, volume]`

### Validation and Quality Gates
- Structural tests (`tests/data/test_u04.py`) covering adapter existence, provider_name, limit validation, interval validation, router existence, and provider priority.
- Import integrity check (stale module removal + re-import).
- Live provider capture: 5 BTCUSDT 1m candles.
- Live data validation: count, chronological order, duplicate timestamps, symbol consistency, OHLC bounds, volume non-negativity.
- Final artifact check and lock assertions.

### Algorithms and Business Rules
- Provider priority: Binance always first; Coinbase only on Binance failure.
- Binance multi-URL fallback: iterates `BASE_URLS` until HTTP 200.
- Coinbase symbol normalization: `USDT` → `-USD`, `USD` → `-USD`.
- Candle mapping:
  - Binance: `timestamp=int(row[0])`, `open=float(row[1])`, `high=float(row[2])`, `low=float(row[3])`, `close=float(row[4])`, `volume=float(row[5])`.
  - Coinbase: `timestamp=int(row[0])*1000`, `open=float(row[3])`, `high=float(row[2])`, `low=float(row[1])`, `close=float(row[4])`, `volume=float(row[5])`.

### Inputs and Outputs
- Inputs: `symbol: str`, `interval: str`, `limit: int`.
- Outputs: `list[Candle]`; raw JSON and normalized JSONL capture files; `app/data/capture/binance.py`, `app/data/capture/coinbase.py`, `app/data/capture/router.py`, `tests/data/test_u04.py`, `U04_PROVIDER_MANIFEST.json`, `U04_CAPTURE_SHA256.json`, `U04_AUDIT_METADATA.json`, `ledgers/U04_LEDGER.md`.

### Dependencies on Other Units
- Requires U03 artifacts (manifest, audit, ledger, candle model, validation) to be present and locked.

### Core Business Logic vs Colab/Build/Scaffolding Code
- Core business logic: `BinancePublicAdapter`, `CoinbasePublicAdapter`, `ProviderRouter`, `_product_id`, candle row normalization, provider priority routing.
- Colab/build/scaffolding code: `pip install requests`, `subprocess.run` pytest execution, print banners, artifact generation, live capture orchestration, hash inventory.

---

## U05 — Real Market Data / Multi-Symbol Capture

### Exact Purpose
Captures 100 real observed candles per symbol for 5 assets (BTCUSDT, ETHUSDT, SOLUSDT, XRPUSDT, ADAUSDT) using Binance-primary/Coinbase-fallback routing. Computes rolling volume over `NOW - 60m -> NOW` based on actual timestamps. Enforces strict volume and trading safety rules.

### Important Functions and Classes
- `positive_decimal(value, field_name)` — converts to positive float via Decimal.
- `non_negative_decimal(value, field_name)` — converts to non-negative float via Decimal.
- `provider_symbol(provider_name, symbol)` — normalizes symbol per provider.
- `utc_now()`, `now_ms()`, `rolling_range()` — time helpers.
- `BinancePublicAdapter` — `_get()`, `fetch_recent()` returning dicts with `volume_base`, `volume_usd`, `volume_usd_exact`, `volume_usd_source`.
- `CoinbasePublicAdapter` — `fetch_batch()` with pagination.
- `fetch_coinbase_real_candles(adapter, symbol, interval, required_count)` — paginated backward-in-time collection.
- `fetch_from_provider(provider_name, symbol)` — single-provider fetch with elapsed timing.
- `capture_with_priority(symbol)` — iterates `PROVIDER_PRIORITY`, records attempts, raises if all fail.
- `build_record(candle, symbol, provider_name, provider_symbol_value)` — constructs canonical U05 record.
- `validate_records(records, expected_symbol)` — enforces count, chronological order, unique timestamps, symbol, OHLC, volume source/counting/double-counting rules.
- `calculate_rolling_volume(provider_name, symbol)` — computes rolling base and USD volume over `NOW - 60m -> NOW`.

### Important Constants and Schemas
- `SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT"]`
- `INTERVAL = "1m"`
- `CANDLES_PER_SYMBOL = 100`
- `REQUESTED_DURATION_MINUTES = 60`
- `REQUESTED_RANGE_MODE = "ROLLING_END_AT_NOW"`
- `PROVIDER_PRIORITY = ["BINANCE_SPOT_PUBLIC", "COINBASE_EXCHANGE_PUBLIC"]`
- `TRADING_ENABLED = False`, `ORDERS_ENABLED = False`, `STRATEGY_ENABLED = False`
- Record schema includes: `volume_base`, `volume_definition="TOTAL_TRADED_BASE_ASSET_VOLUME"`, `volume_source="PROVIDER_SUPPLIED"`, `volume_counting_rule="EACH_TRADE_COUNTED_ONCE"`, `volume_double_counting=False`, `buyer_seller_not_double_counted=True`, `total_series_included=False`, `trading_enabled=False`, `orders_enabled=False`, `strategy_enabled=False`.

### Validation and Quality Gates
- Per-symbol: count == 100, chronological, unique timestamps, symbol match, OHLC bounds, positive prices, non-negative volume.
- Volume contract: `volume_source == "PROVIDER_SUPPLIED"`, `volume_counting_rule == "EACH_TRADE_COUNTED_ONCE"`, `volume_double_counting is False`, `buyer_seller_not_double_counted is True`, `total_series_included is False`.
- Rolling volume: timestamp-range-based selection (not `records[-60:]`), exact provider quote volume when available.
- Provider priority enforcement and attempt logging.

### Algorithms and Business Rules
- Rolling volume: filter candles where `start_ms <= timestamp <= end_ms`; sum `volume_base`; sum `volume_usd` only when `volume_usd_exact` is True for all in-range candles.
- Coinbase pagination: backward-in-time pages of up to 300 minutes; never fabricates missing candles.
- Volume semantics: real traded base-asset volume; buyer+seller not double-counted; no `close * volume`; no market-cap derivation; no interpolation.

### Inputs and Outputs
- Inputs: Provider APIs (Binance, Coinbase).
- Outputs: `data/historical_u05/raw/{symbol}_1m.json`, `data/historical_u05/normalized/{symbol}_1m.jsonl`, per-symbol manifests and quality data; `U05_CAPTURE_MANIFEST.json`, `U05_SHA256.json`, `DATASET_INDEX.json`, `U05_DATA_QUALITY_REPORT.json`.

### Dependencies on Other Units
- Requires U03 data foundation (Candle model, validation, storage).
- Requires U04 provider adapters (conceptually; U05 defines its own adapters inline).

### Core Business Logic vs Colab/Build/Scaffolding Code
- Core business logic: provider adapters, `capture_with_priority`, `build_record`, `validate_records`, `calculate_rolling_volume`, `fetch_coinbase_real_candles`, volume contract enforcement.
- Colab/build/scaffolding code: `pip install requests`, print banners, file I/O orchestration, artifact generation, timestamp-based range calculations for dataset metadata.

---

## U06 — U05 Historical Data Quality Gate

### Exact Purpose
Validates the actual U05 dataset schema and records without modifying source data. Enforces SHA-256 integrity, record counts, chronological order, OHLC bounds, volume contract, and safety flags.

### Important Functions and Classes
- `ensure_drive()` — portable Colab/Drive/Jupyter root discovery.
- `sha256_file(path)` — SHA-256 hash helper.
- `numeric(value, field_name)` — Decimal-based numeric validation.
- `validate_ohlc(record)` — validates open/high/low/close/volume bounds and positivity.
- `load_jsonl(path)` — parses JSONL, returns records and parse errors.

### Important Constants and Schemas
- `SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT"]`
- `INTERVAL = "1m"`
- `EXPECTED_RECORDS_PER_SYMBOL = 100`
- `EXPECTED_TOTAL_RECORDS = 500`
- `REQUIRED_FIELDS` — 22-field list including `volume_base` (not `volume`), `volume_source`, `volume_counting_rule`, `volume_double_counting`, `buyer_seller_not_double_counted`, `total_series_included`, `trading_enabled`, `orders_enabled`, `strategy_enabled`.

### Validation and Quality Gates
- U05 control artifact verification (`DATASET_INDEX.json`, `U05_SHA256.json`, `U05_CAPTURE_MANIFEST.json`, `U05_DATA_QUALITY_REPORT.json`).
- U05 index validation (execution_unit == "U05", symbols match).
- SHA-256 control verification for all raw and normalized files.
- Per-symbol inspection: record count == 100, required fields present, symbol/execution_unit/interval match, timestamps in milliseconds, chronological, unique, OHLC and volume bounds via `validate_ohlc`, volume contract flags, trading/orders/strategy/total_series flags == False.
- Timestamp gap diagnosis: Coinbase gaps tolerated as diagnostic; Binance gaps treated as integrity failures.
- Global validation: total records, symbol coverage, source unmodified.
- Safety validation: trading/orders/strategy/total_series all disabled; provider volume; double-counting disabled.
- Final quality report and summary written to disk.
- U06 locks only after every required gate passes.

### Algorithms and Business Rules
- Schema correction: U05 canonical volume field is `volume_base`; U06 explicitly validates `volume_base` and rejects records containing `volume`.
- Gap tolerance: Coinbase may omit no-trade intervals; Binance gaps are integrity failures.
- Hard problem counting: tolerated Coinbase-gap diagnostics are excluded from `hard_problem_count`.

### Inputs and Outputs
- Inputs: U05 dataset files (`data/historical_u05/raw/`, `data/historical_u05/normalized/`, control artifacts).
- Outputs: `U06_DATA_QUALITY_REPORT.json`, `U06_DATA_QUALITY_SUMMARY.txt`, `ledgers/U06_LEDGER.md`.

### Dependencies on Other Units
- Requires U05 artifacts and data files to be present and valid.
- Requires U04 provider concepts (for gap tolerance rules).

### Core Business Logic vs Colab/Build/Scaffolding Code
- Core business logic: `validate_ohlc`, `load_jsonl`, `numeric`, SHA-256 verification, per-record schema enforcement, gap tolerance logic, volume contract validation, safety flag validation.
- Colab/build/scaffolding code: `ensure_drive` (Colab-specific), print banners, artifact file writing, self-check dictionaries, ledger generation.

---

## U06.5 — Market Data Source & Validation Foundation

### Exact Purpose
Provides a portable, self-contained market data source and validation foundation. Acquires and normalizes data from CMC (keyless primary, authenticated optional), CoinGecko (fallback), and 8-exchange public spot venues. Builds dynamic reliability-weighted multi-exchange price foundation, order-book depth metrics, Top-125 dynamic ranking, Kitchen TOTAL/TOTAL2/TOTAL3/Others.D indices, and cross-source evidence. No TradingView. Historical 5m data is never fabricated.

### Important Functions and Classes
- `HTTPResult` — dataclass for HTTP responses.
- `classify_http_error(status, body)` — error classification.
- `http_json(url, params, headers)` — portable JSON HTTP client using `urllib`.
- CMC helpers: `cmc_status_ok`, `cmc_data`, `cmc_quote`, `cmc_asset_records`.
- `acquire_cmc(endpoint, params, authenticated)` — CMC acquisition.
- `acquire_cmc_top125()`, `acquire_cmc_quotes()`, `acquire_cmc_global()`, `acquire_cmc_simple_price()`.
- `acquire_coingecko_top125()`.
- `acquire_exchange_symbol_ohlcv(symbol)` — Binance-primary/Coinbase-fallback for U05 symbols.
- `_normalize_multi_exchange_rows(provider, payload)` — normalizes 8-exchange kline payloads.
- `acquire_multi_exchange_symbol(provider, limit)` — current 5m probe per exchange.
- `_normalize_orderbook(provider, payload, retrieved_at)` — normalizes order books.
- `acquire_multi_exchange_orderbook(provider)` — live order-book acquisition.
- `orderbook_quality_metrics(book)` — spread, depth bands, price impact.
- `acquire_multi_exchange_evidence()` — combined candle + orderbook evidence for all 8 exchanges.
- `acquire_exchange_historical_ohlcv(provider, start_ts, end_ts, max_pages)` — explicit historical 5m fetch with pagination.
- `acquire_exchange_evidence()` — U05-compatible exchange evidence.
- `canonical_asset_id(provider, provider_asset_id, symbol)` — identity mapping.
- `normalize_cmc_asset`, `normalize_coingecko_asset` — provider-specific normalization.
- `validate_identity`, `validate_numeric_market_fields`, `validate_timestamp_fields`, `freshness_status`, `validate_record` — per-record validation.
- `validate_ranked_universe(records, expected_count)` — Top-125 rank completeness validation.
- `validate_core_assets(records)` — BTC/ETH/USDT core asset presence.
- `persist_raw_artifact(...)` — raw artifact persistence with redaction.
- `build_provider_cross_source_evidence(cmc_records, cg_records)` — CMC vs CoinGecko price comparison.
- `make_market_observation(...)`, `normalize_quote_to_usd(...)`, `validate_market_observation(...)` — market observation pipeline.
- `median_abs_deviation(values)`, `outlier_filter_v1(observations)` — MAD-based outlier detection.
- `_build_reliability_scores(observations)` — dynamic reliability scoring (data integrity, freshness, volume, depth, spread, price impact, cross-exchange consistency).
- `build_live_reference_price_from_multi_exchange(multi_exchange)` — canonical BTC reference price.
- `price_aggregate_v1(observations)` — reliability-weighted price aggregation.
- `validate_circulating_supply(asset)`, `calculate_market_cap_v1(...)` — market-cap calculation.
- `dynamic_rank_assets(valid_assets)` — Top-125 dynamic ranking by market cap.
- `calculate_indices_from_top125(top125)` — Kitchen TOTAL/TOTAL2/TOTAL3/Others.D/BTC.D/ETH.D/USDT.D.
- `normalize_cmc_global_metrics(data)` — CMC global metrics normalization (evidence only).
- `acquire_market_index_time_series()` — external 5m historical market-index evidence.

### Important Constants and Schemas
- `CMC_BASE_KEYLESS`, `CMC_BASE_AUTH`, `COINGECKO_BASE`
- `TOP_N = 125`, `TIMEFRAME = "5m"`, `SUPPORTED_TIMEFRAMES = ("1m", "5m", "15m", "1h", "4h", "1d")`
- `TARGET_CANDIDATE_POOL = 1250`, `TARGET_EXCHANGE_COUNT = 8`, `MIN_VALIDATED_EXCHANGE_COUNT = 7`
- `MULTI_EXCHANGE_SPECS` — 8-exchange endpoint/symbol map.
- `QUALITY_CONFIG` — thresholds for max source age, price deviation, robust z-score, min volume, depth bands, spread soft limit, price impact notional, reliability component weights.
- `CORE_ASSETS = {1: "BTC", 1027: "ETH", 825: "USDT"}`
- `PROVIDER_PRIORITY = {"global": ["coinmarketcap", "coingecko"], "exchange": ["binance", "okx", "bybit", "kucoin", "coinbase", "gate", "upbit", "bitget"]}`
- `FORBIDDEN_RUNTIME_PROVIDERS = {"tradingview", "tradingview_reference", "tv"}`
- `AUTO_PERSIST_SNAPSHOT = False`

### Validation and Quality Gates
- Per-record: identity, numeric, timestamp, freshness, outlier filtering.
- Universe-level: rank completeness (1-125), duplicate IDs, missing ranks, coverage ratio.
- Core asset presence: BTC, ETH, USDT must be present.
- Cross-source evidence: CMC vs CoinGecko price agreement.
- Reliability scoring: dynamic weighted model with missing-feature exclusion.
- Exchange coverage: minimum 7 of 8 core exchanges validated.
- Historical index: 5m cadence validation, deduplication.

### Algorithms and Business Rules
- CMC keyless is primary current-data mode; authenticated optional.
- CoinGecko is fallback.
- TradingView is forbidden.
- Kitchen TOTAL is calculated from validated dynamic Top-125; CMC Global Metrics are evidence only.
- Exchange prices are reliability-weighted; no fixed exchange ranking.
- Missing features (orderbook depth, spread, etc.) are never fabricated; excluded from reliability denominator.
- Historical 5m data: never fabricated, never silently substituted, never resampled/interpolated.
- Outlier detection: MAD-based robust z-score with configurable thresholds.
- Market cap: `REFERENCE_PRICE_USD * VALIDATED_CIRCULATING_SUPPLY`; forbidden supply substitutions rejected.
- Dominance: `segment_mc / total_mc * 100`.

### Inputs and Outputs
- Inputs: Public APIs (CMC, CoinGecko, 8 exchanges).
- Outputs: Raw artifacts, normalized records, Top-125 ranked universe, Kitchen indices, cross-source evidence, provider health snapshots, reliability scores, reference price.

### Dependencies on Other Units
- Requires U03 data foundation.
- Requires U04 provider concepts (Binance/Coinbase).
- Requires U05 exchange symbol mapping.
- Provides foundation for U07, U08, U09.

### Core Business Logic vs Colab/Build/Scaffolding Code
- Core business logic: All provider acquisition, normalization, validation, ranking, index calculation, reliability scoring, outlier filtering, cross-source evidence, market-cap calculation.
- Colab/build/scaffolding code: `resolve_root()` (portable root discovery), print banners, raw artifact persistence, redaction utilities, canonical hashing.

---

## U07 — Market Structure Scenario Engine + Range Detection Engine

### Exact Purpose
Analyzes market structure for TOTAL and USDT.D series, classifies direction (INCREASE/DECREASE/RANGE), computes range confidence, maps to the canonical 9-scenario matrix, and selects approved Persian narratives.

### Important Functions and Classes
- `Direction(str, Enum)` — `INCREASE`, `DECREASE`, `RANGE`.
- `RangeType(str, Enum)` — `LOW_VOLATILITY_RANGE`, `HIGH_VOLATILITY_RANGE`, `NONE`.
- `RangeConfidence(str, Enum)` — `HIGH`, `MEDIUM`, `LOW`.
- `ScenarioType(str, Enum)` — `MIRROR`, `PARALLEL`, `RANGE_COMPATIBLE_STATE`, `NEUTRAL_FLAT`.
- `RangeConfig` — frozen dataclass with configurable thresholds.
- `validate_series(series, name)` — input validation.
- `validate_ohlc_structure(highs, lows, closes, name)` — OHLC consistency.
- `validate_user_range(analysis_range)` — authoritative user range validation.
- `parse_timeframe(timeframe)` — general timeframe parser with sub-daily warning.
- `pct_change(start, end)`, `range_amplitude_pct(series)`, `normalized_path_length(series)`, `direction_switch_count(series)`, `close_dispersion_pct(series)` — movement metrics.
- `calculate_dmi_adx(highs, lows, closes, period, adx_period)` — Wilder-style DMI/ADX.
- `analyze_range(values, highs, lows, closes, config)` — core range analysis engine.
- `run_u07(total_values, usdt_values, timeframe, analysis_range, ...)` — main engine entry point.
- `validate_scenario_matrix()` — matrix integrity check.
- `validate_timeframes()` — timeframe regression test.
- `run_u07_regression_tests()` — full regression suite.

### Important Constants and Schemas
- `DEFAULT_RANGE_CONFIG` — default configurable thresholds.
- `SCENARIO_MATRIX` — 9-scenario mapping of `(Direction, Direction)` pairs to scenario IDs and types.
- `NARRATIVES` — 9 scenarios × 3 patterns = 27 locked Persian narrative texts.

### Validation and Quality Gates
- `validate_scenario_matrix()` — ensures all 9 pairs exist with correct IDs.
- `validate_timeframes()` — regression across 14 timeframes.
- `run_u07_regression_tests()` — matrix, timeframe, zero-movement, internal structure, 9-scenario pairs, execution locks.
- Hard safety locks asserted at module load: `TRADING_ENABLED = False`, `ORDERS_ENABLED = False`, `STRATEGY_ENABLED = False`, `PORTFOLIO_ACTIONS_ENABLED = False`.

### Algorithms and Business Rules
- Range scoring components: net movement, direction switching, DMI balance, ADX, relative amplitude.
- Direction thresholds: `> direction_threshold_pct` = INCREASE; `< -direction_threshold_pct` = DECREASE; else RANGE.
- Zero-movement edge case: treated as RANGE with internal structure evaluated.
- Contradiction detection: directional movement + range-supporting structure + strong ADX = ambiguous.
- Confidence: HIGH if `score >= 0.78`, MEDIUM if `score >= 0.62`, else LOW.
- Range decision: `score >= range_score_threshold` OR `zero_net` OR `internal_chop`.
- Scenario mapping: exact 9×9 matrix; unmapped pairs raise RuntimeError.
- User range is authoritative and never silently replaced.
- Sub-daily timeframe rule: ANY valid timeframe below 1D = VALID + SUB_DAILY_WARNING.

### Inputs and Outputs
- Inputs: `total_values: List[float]`, `usdt_values: List[float]`, `timeframe: str`, `analysis_range: Any`, optional OHLC lists, `pattern_index: int`.
- Outputs: `ScenarioResult` dataclass with classifications, range types, confidence, scores, DMI/ADX, selected narrative, audit dict.

### Dependencies on Other Units
- Requires U06.5 for data foundation and indices.
- Provides analysis output consumed by U08.

### Core Business Logic vs Colab/Build/Scaffolding Code
- Core business logic: `analyze_range`, `calculate_dmi_adx`, `parse_timeframe`, `run_u07`, `SCENARIO_MATRIX`, `NARRATIVES`, all movement metrics, contradiction detection, confidence scoring.
- Colab/build/scaffolding code: `print` banners, `json.dumps` validation output, assertion blocks.

---

## U08 — BTC + BTC.D Context & Relative-Movement Engine

### Exact Purpose
Analyzes BTC and BTC.D directions, classifies market context (BULLISH/BEARISH/RANGE), resolves the canonical 9-scenario matrix, selects from 27 locked narrative patterns, ranks strong movers and relative movers, and produces top-10 asset lists.

### Important Functions and Classes
- `Direction(str, Enum)` — `INCREASE`, `DECREASE`, `RANGE`.
- `Context(str, Enum)` — `BULLISH`, `BEARISH`, `RANGE`.
- `RelativeDirection(str, Enum)` — `RELATIVE_STRENGTH`, `RELATIVE_WEAKNESS`, `RELATIVE_NEUTRAL`.
- `Cell08Config` — frozen dataclass with `top_n`, `strong_movers_n`, `relative_movers_n`, epsilon, volume requirements.
- `_normalize_direction(direction)` — alias-aware direction normalization.
- `classify_context(btc_direction, btc_d_direction)` — context classification.
- `resolve_scenario(btc_direction, btc_d_direction)` — scenario resolution.
- `select_pattern(scenario_id, pattern_index)` — narrative pattern selection.
- `calculate_relative_btc_performance(asset_change_pct, btc_change_pct)` — relative performance.
- `classify_relative_performance(...)` — relative direction classification.
- `normalize_asset(asset)` — asset field normalization.
- `enrich_relative_performance(assets, btc_change_pct)` — adds relative performance to assets.
- `rank_strong_movers(assets, market_context, n)` — absolute movement ranking.
- `rank_relative_movers(assets, market_context, n)` — BTC-relative ranking.
- `rank_top_assets(assets, market_context, n)` — top-N by change and volume.
- `is_opposite_direction(btc_direction, btc_d_direction)` — opposite direction detection.
- `build_altcoin_structure_context(...)` — altcoin structure context (enabled only when BTC and BTC.D are opposite).
- `build_scenario_ranking(assets, btc_direction, btc_d_direction)` — combined ranking.
- `run_cell_08(...)` — main engine entry point.
- `cell08_to_dict(result)`, `cell08_to_json(result)` — serialization.
- `run_cell08_regression_tests()` — regression suite.

### Important Constants and Schemas
- `SCENARIO_MATRIX` — 9-scenario mapping for BTC/DIR × BTC.D/DIR.
- `NARRATIVES` — 27 locked patterns (9 scenarios × 3 patterns) with `pattern`, `title`, `text` fields.
- `CELL08_CONFIG` — default config with `top_n=10`, `strong_movers_n=10`, `relative_movers_n=10`.

### Validation and Quality Gates
- `validate_narratives()` — asserts 9 scenarios, 3 patterns each, non-empty text.
- `run_cell08_regression_tests()` — 9 scenarios, 27 patterns, opposite-direction cases, absolute≠relative, no false bullish label, range does not imply all assets range.
- Hard safety locks asserted at module load.
- Snapshot smoke test runs `run_cell_08` with synthetic assets.

### Algorithms and Business Rules
- Context: BTC INCREASE → BULLISH; BTC DECREASE → BEARISH; else RANGE.
- Strong movers ranking: BULLISH → descending change; BEARISH → ascending change; RANGE → descending absolute change.
- Relative movers: BEARISH → ascending relative performance; otherwise descending.
- Top assets: BULLISH/BEARISH → change then volume; RANGE → absolute change then volume.
- Opposite direction: BTC↑/BTC.D↓ or BTC↓/BTC.D↑.
- Altcoin structure context enabled only when opposite direction; otherwise disabled with reason.
- BTC is always the benchmark; relative performance is complementary.

### Inputs and Outputs
- Inputs: `btc_direction`, `btc_d_direction`, `btc_change_pct`, `assets: List[Dict]`, `pattern_index`, optional `total2`, `total3`, `others_d`.
- Outputs: `Cell08Result` dataclass with scenario, context, opposite_direction, selected_pattern, top_10_assets, strong_movers, relative_movers, altcoin_structure, audit.

### Dependencies on Other Units
- Requires U07 for scenario/range analysis.
- Provides analysis output consumed by the U01→U08 snapshot.

### Core Business Logic vs Colab/Build/Scaffolding Code
- Core business logic: scenario matrix, narrative library, ranking engines, relative performance calculations, context classification, `run_cell_08`.
- Colab/build/scaffolding code: `print` banners, `json.dumps` serialization, snapshot discovery, regression test execution.

---

## U09 — Dynamic Market Universe / Market Participation Engine

### Exact Purpose
Builds a dynamic Rank 1-125 universe segmented as BTC / ETH / TOP10_ALT / BROAD_ALT_11_125. Acquires data from CoinGecko (primary) and CoinMarketCap (secondary). Computes dominance, breadth, relative strength, participation state, and a compact user-facing message. No trading, orders, portfolio actions, or advice.

### Important Functions and Classes
- `ProviderHealth`, `ProviderAttempt`, `ProviderSnapshot` — dataclasses for provider state.
- `ProviderError(RuntimeError)` — provider error with state and status code.
- `BaseProvider`, `CoinGeckoProvider`, `CoinMarketCapProvider` — provider classes with `fetch` and `normalize`.
- `validate_provider_assets(assets, limit)` — rank coverage, duplicate detection, numeric validation, rank consistency.
- `freshness_status(provider_ts, now)` — FRESH/STALE/UNAVAILABLE.
- `provider_order(now)` — cooldown-aware provider ordering.
- `orchestrate_universe()` — failover orchestration with retries and cooldown.
- `segment_for_rank(rank)` — rank-to-segment mapping.
- `build_reference_from_24h(assets)` — 24h reference market-cap reconstruction.
- `reference_timestamp_from_provider_24h(provider_timestamp)` — reference timestamp semantics.
- `build_segments(assets, reference_mc_by_id)` — segment metrics (MC, dominance, breadth, change).
- `relative_strength(segments)` — pairwise MC ratios.
- `composition_compare(current_assets)` — membership change detection vs previous snapshot.
- `participation_brain(seg, rs, composition)` — BROADENING/CONCENTRATED/WEAKENING/MIXED/UNAVAILABLE.
- `fmt_pct(v, min_decimals, max_decimals)` — percentage formatting without -0.0.
- `build_message(result)` — compact 5-line user-facing message.
- `synthetic_assets(mode)` — deterministic synthetic 125-asset factory.
- `synthetic_validation_suite()` — exhaustive synthetic tests.
- `execute_u09()` — main execution pipeline.
- `audit_result(result)` — audit checks for banned language, message contract, frozen snapshot.

### Important Constants and Schemas
- `CONFIG` — universe_limit=125, currency=usd, lookback=24h, breadth thresholds, dominance tolerance, retry/cooldown, cache settings, message contract (24h movements only, dominance relative %, no participation state in message).
- `SEGMENTS = {"BTC": 1, "ETH": 2, "TOP10_ALT": 3-10, "BROAD_ALT_11_125": 11-125}`
- `PROVIDER_REGISTRY` — CoinGecko priority 1, CoinMarketCap priority 2.
- Safety flags: `TRADING_ENABLED=False`, `ORDERS_ENABLED=False`, `STRATEGY_ENABLED=False`, `PORTFOLIO_ACTIONS_ENABLED=False`.

### Validation and Quality Gates
- Synthetic validation suite: rank identity/segmentation/aggregation/dominance, breadth exact 10/5/5, relative strength pairs, zero reference guard, duplicate ID/rank rejection, missing rank rejection, invalid numeric rejection, composition boundary, dominance semantics, freshness states, participation brain state set, message contract (5 lines, no Participation:/pp/-0.0%).
- Provider validation: rank coverage, duplicate IDs/ranks, numeric validity, freshness.
- Audit: banned language check, message line count, snapshot frozen, asset count = 125.
- Hard assertions on synthetic tests, audit status, and safety locks.

### Algorithms and Business Rules
- Provider failover: CoinGecko → CoinMarketCap; retries with fixed backoff; cooldown on failure; validation score decay.
- Reference timestamp: provider_timestamp minus 24h.
- Dominance: `segment_mc / total_mc * 100`.
- Breadth: rising/flat/falling counts based on `price_change_24h_pct` vs threshold; STRONG ≥70% rising, POSITIVE ≥55%, WEAK ≥70% falling, NEGATIVE ≥55% falling, else MIXED.
- Participation brain: BROADENING if TOP10+BROAD both support expansion; CONCENTRATED if core support + broad weak; WEAKENING if broad+top weak; else MIXED.
- Message contract: exactly 5 lines; 24h movements only; dominance relative % only; no participation state/scenario/pp.
- Composition quality: STABLE/MINOR_CHANGE/MATERIAL_CHANGE/UNRELIABLE based on membership changes.

### Inputs and Outputs
- Inputs: Public APIs (CoinGecko, CoinMarketCap).
- Outputs: `U09_RESULT` dict with universe snapshot, segments, dominance, breadth, relative strength, participation state, message, audit, provider health; persisted snapshots and audit files.

### Dependencies on Other Units
- Requires U06.5 for Top-125 validation, ranking, and index concepts.
- Requires U08 for scenario/context analysis.
- Provides market universe and participation analysis for downstream consumption.

### Core Business Logic vs Colab/Build/Scaffolding Code
- Core business logic: provider orchestration, asset validation, segmentation, dominance/breadth/relative-strength calculation, participation brain, message building, synthetic test suite, audit checks.
- Colab/build/scaffolding code: `print` banners, file persistence to `snapshots/` and `audit/` directories, hard assertions, console report generation.

---

# PART 2 — FINAL BOT REQUIREMENTS AUDIT

## Telegram Commands
**NOT SPECIFIED**
- No Telegram bot implementation exists in the notebook.
- No command handlers, command registry, or Telegram API integration are defined.
- The notebook is an analysis/build pipeline; it does not define a Telegram interface.

## User Inputs
**PARTIALLY SPECIFIED**
- Analysis engines accept structured inputs: `timeframe: str`, `analysis_range: dict/tuple/list`, `pattern_index: int`, symbol lists, and asset dictionaries.
- `validate_user_range()` enforces authoritative user range format.
- `parse_timeframe()` validates and normalizes timeframe strings.
- No Telegram message parsing, inline keyboard handling, or conversational state management is specified.

## Bot Outputs
**PARTIALLY SPECIFIED**
- `build_message()` in U09 produces a compact 5-line market participation message.
- U07 selects Persian narrative patterns; U08 selects 1 of 27 locked patterns.
- No Telegram-specific formatting (Markdown/HTML, inline buttons, media, etc.) is defined.
- Outputs are currently consumed as Python objects/dicts or printed to console.

## Analysis Requests
**SPECIFIED**
- U07: `run_u07(total_values, usdt_values, timeframe, analysis_range, ...)` — market structure scenario analysis.
- U08: `run_cell_08(btc_direction, btc_d_direction, btc_change_pct, assets, ...)` — BTC/BTC.D context and relative-movement analysis.
- U09: `execute_u09()` — dynamic market universe and participation engine.
- U06.5: `build_live_reference_price_from_multi_exchange()`, `calculate_indices_from_top125()`, `price_aggregate_v1()` — data foundation and price engines.
- Request/response contracts are fully defined for each engine.

## Market Reports
**SPECIFIED**
- U09 produces a market participation report with 5-line user-facing message covering BTC, ETH, TOP10 ALT, and BROAD 11–125.
- U06 produces `U06_DATA_QUALITY_REPORT.json` and `U06_DATA_QUALITY_SUMMARY.txt`.
- U04/U05 produce provider manifests, capture hashes, and raw/normalized JSONL datasets.
- No periodic/delivered report schedule is defined.

## Alerts and Notifications
**NOT SPECIFIED**
- No alert engine, threshold monitoring, or notification dispatch logic exists.
- U09 `participation_brain()` returns a state string, but it is not wired to alerts.
- No Telegram alert integration, webhook, or push notification mechanism.

## Scheduling and Periodic Jobs
**NOT SPECIFIED**
- No scheduler, cron, or periodic execution framework is defined.
- U09 and U06.5 are designed as on-demand engines; no auto-refresh or interval-based trigger is specified.

## Signal Generation
**NOT SPECIFIED**
- No buy/sell signals, entry/exit logic, or trade recommendations are defined.
- All safety locks explicitly disable trading, orders, and strategy.
- U07/U08 produce scenario classifications and narratives only; they do not generate actionable signals.

## Portfolio/Trading Functionality
**SPECIFIED AS DISABLED**
- Hard safety locks are asserted at module load in U07, U08, U09: `TRADING_ENABLED = False`, `ORDERS_ENABLED = False`, `STRATEGY_ENABLED = False`, `PORTFOLIO_ACTIONS_ENABLED = False`.
- U05, U06, U06.5 records explicitly set `trading_enabled: False`, `orders_enabled: False`.
- No portfolio mutation, order creation, or capital-flow logic exists.

## Risk Management
**NOT SPECIFIED**
- No position sizing, stop-loss, take-profit, or risk metric calculations are defined.
- U06.5 includes outlier filtering and reliability scoring for data quality, but this is not trading risk management.
- No drawdown, exposure, or capital-protection rules.

## Persistence and History
**PARTIALLY SPECIFIED**
- U05 writes raw JSON and normalized JSONL to `data/historical_u05/`.
- U06 writes quality reports and summaries to `data/historical_u05/quality/`.
- U06.5 persists raw artifacts to `data/raw/U06_5/`.
- U09 persists snapshots to `u09_dynamic_market_universe/snapshots/` and audit to `audit/`.
- U09 `composition_compare()` reads previous snapshots for membership change detection.
- No user session history, chat history, or persistent user preferences are specified.

## Configuration
**SPECIFIED**
- U01: `Settings` dataclass with `environment`, `timezone`, `log_level` from environment variables.
- U02: `app/config/runtime.py` with `HOST`, `PORT`, `DEBUG` from environment variables.
- U05: `SYMBOLS`, `INTERVAL`, `CANDLES_PER_SYMBOL`, `REQUESTED_DURATION_MINUTES`, `PROVIDER_PRIORITY`, safety flags.
- U06.5: `QUALITY_CONFIG` dict with explicit thresholds; `CMC_API_KEY`, `COINGECKO_API_KEY` discovery from env.
- U09: `CONFIG` dict with universe_limit, currency, lookback, breadth thresholds, retry/cooldown, cache settings, message contract.
- Environment templates (`.env.example`) are generated in U01.

## Admin Controls
**NOT SPECIFIED**
- No admin panel, admin commands, role-based access, or privileged operations are defined.
- No user management, ban/kick, or broadcast mechanisms.

## Authentication/Authorization
**NOT SPECIFIED**
- No user authentication, authorization, session management, or access control is defined for a bot.
- Provider API keys are discovered from environment variables but are not user-facing credentials.

## Error Handling
**PARTIALLY SPECIFIED**
- Provider-level error handling: `BinanceProviderUnavailable`, `CoinbaseProviderUnavailable`, `ProviderError`, HTTP error classification, retry/backoff, cooldown.
- Data validation errors: `validate_ohlc`, `validate_candles`, `validate_record` raise or return failure reasons.
- U06 quality gate distinguishes hard failures from tolerated diagnostics (Coinbase gaps).
- No bot-level error handling, user-friendly error messages, or fallback chat flows are specified.

## Logging
**PARTIALLY SPECIFIED**
- `print` statements are used extensively for console output in every unit.
- U01–U04 generate artifact files (manifest, ledger, SHA-256, audit metadata) that serve as audit logs.
- U06.5 persists raw artifacts with redacted request parameters.
- No structured logging framework, log levels, log rotation, or centralized logger is specified.

## User-Facing Messages
**SPECIFIED**
- U09: `build_message()` produces a strict 5-line message: header + 2 lines per market block (BTC, ETH, TOP10 ALT, BROAD 11–125).
- U07: 27 locked Persian narrative texts across 9 scenarios.
- U08: 27 locked Persian narrative patterns across 9 scenarios with titles.
- Message contracts enforce no participation state, no pp values, no signed zero, no banned language.
- All user-facing messages are currently in Persian (Farsi) with some English labels/emojis.

## Persian Language/Narratives
**SPECIFIED**
- U07 `NARRATIVES`: 9 scenarios × 3 patterns = 27 exact Persian narrative texts. Locked; do not rewrite.
- U08 `NARRATIVES`: 9 scenarios × 3 patterns = 27 exact Persian narrative texts with `pattern`, `title`, `text` fields. Locked; do not rewrite.
- U09 `build_message()` uses Persian labels: `📊 MARKET PARTICIPATION`, `₿ BTC Price`, `🔷 ETH Price`, `🔹 TOP10 ALT MC`, `◈ BROAD 11–125 MC`.
- No translation layer, i18n framework, or language selection is specified; Persian is the sole specified user language.

## Data Freshness and Timeframes
**SPECIFIED**
- U02: `validate_timeframe_guard()` enforces sub-daily warning for timeframes below D1; supports custom ranges.
- U05: `REQUESTED_RANGE_MODE = "ROLLING_END_AT_NOW"` with `REQUESTED_DURATION_MINUTES = 60`.
- U06.5: `FRESHNESS_THRESHOLD_SECONDS = 900` (15 min); `freshness_status()` returns FRESH/STALE/UNAVAILABLE; stale responses rejected for Top-125 snapshots.
- U06.5: `MAX_SOURCE_AGE_SECONDS` configurable; orderbook age limit 30s.
- U09: `max_current_age_seconds = 900`, `maximum_reference_age_seconds = 48h`, `lookback = 24h`.
- U06: timestamp unit detection (milliseconds vs seconds), chronological validation, duplicate detection.
- Historical 5m data must be genuine; no fabrication, resampling, or silent substitution.

---

## Summary

| Area | Status |
|------|--------|
| Telegram commands | NOT SPECIFIED |
| User inputs | PARTIALLY SPECIFIED |
| Bot outputs | PARTIALLY SPECIFIED |
| Analysis requests | SPECIFIED |
| Market reports | SPECIFIED |
| Alerts and notifications | NOT SPECIFIED |
| Scheduling and periodic jobs | NOT SPECIFIED |
| Signal generation | NOT SPECIFIED |
| Portfolio/trading functionality | SPECIFIED AS DISABLED |
| Risk management | NOT SPECIFIED |
| Persistence and history | PARTIALLY SPECIFIED |
| Configuration | SPECIFIED |
| Admin controls | NOT SPECIFIED |
| Authentication/authorization | NOT SPECIFIED |
| Error handling | PARTIALLY SPECIFIED |
| Logging | PARTIALLY SPECIFIED |
| User-facing messages | SPECIFIED |
| Persian language/narratives | SPECIFIED |
| Data freshness and timeframes | SPECIFIED |

---

# PART 3 — MIGRATION MAP AND SNAPSHOT AUDIT

## 1. U01 → U09 Migration Map

### What Should Become Permanent Python Source Code
- **U03**: `Candle` dataclass, `validate_candles`, `normalize_candle`, `write_candles`, `CandleCapture` ABC → `app/data/models/`, `app/data/validation/`, `app/data/capture/`.
- **U04**: `BinancePublicAdapter`, `CoinbasePublicAdapter`, `ProviderRouter` → `app/data/capture/`.
- **U05**: Provider adapters, `capture_with_priority`, `build_record`, `validate_records`, `calculate_rolling_volume`, `fetch_coinbase_real_candles` → `app/data/capture/`, `app/data/validation/`.
- **U06.5**: All provider acquisition, normalization, validation, ranking, index calculation, reliability scoring, outlier filtering, cross-source evidence, market-cap calculation → `app/market/` or `app/core/`.
- **U07**: `analyze_range`, `calculate_dmi_adx`, `parse_timeframe`, `run_u07`, `SCENARIO_MATRIX`, `NARRATIVES` → `app/analysis/` or `app/scanner/`.
- **U08**: `run_cell_08`, scenario matrix, narrative library, ranking engines, relative performance calculations → `app/analysis/` or `app/scanner/`.
- **U09**: `execute_u09`, provider orchestration, segmentation, dominance/breadth/relative-strength, participation brain, message building → `app/market/` or `app/analysis/`.

### What Should Become Configuration
- **U01**: `Settings` dataclass, `.env.example` → `app/config/settings.py`.
- **U02**: Runtime config (`HOST`, `PORT`, `DEBUG`) → `app/config/runtime.py`.
- **U05**: `SYMBOLS`, `INTERVAL`, `CANDLES_PER_SYMBOL`, `REQUESTED_DURATION_MINUTES`, `PROVIDER_PRIORITY` → `app/config/market_data.py`.
- **U06.5**: `QUALITY_CONFIG`, `TOP_N`, `TARGET_EXCHANGE_COUNT`, `MIN_VALIDATED_EXCHANGE_COUNT`, `MULTI_EXCHANGE_SPECS` → `app/config/quality.py`, `app/config/exchanges.py`.
- **U07**: `DEFAULT_RANGE_CONFIG` → `app/config/analysis.py`.
- **U08**: `CELL08_CONFIG` → `app/config/analysis.py`.
- **U09**: `CONFIG` dict → `app/config/market_universe.py`.
- Environment variables: `CMC_API_KEY`, `COINGECKO_API_KEY`, `KITCHEN_ROOT`, `KITCHEN_DATASET_MODE`, etc.

### What Should Become Tests
- **U01**: `tests/test_u01.py` → `tests/unit/test_bootstrap.py`.
- **U02**: `tests/test_u02.py` → `tests/unit/test_timeframe_guard.py`, `tests/unit/test_runtime.py`.
- **U03**: `tests/data/test_u03.py` → `tests/unit/test_candle_model.py`.
- **U04**: `tests/data/test_u04.py` → `tests/integration/test_providers.py`.
- **U05**: U05 validation logic → `tests/integration/test_multi_symbol_capture.py`.
- **U06**: U06 quality gate logic → `tests/integration/test_data_quality_gate.py`.
- **U06.5**: Synthetic validation suites, regression tests → `tests/unit/test_market_data_foundation.py`.
- **U07**: `run_u07_regression_tests()` → `tests/unit/test_scenario_engine.py`.
- **U08**: `run_cell08_regression_tests()` → `tests/unit/test_relative_movement.py`.
- **U09**: `synthetic_validation_suite()` → `tests/unit/test_market_universe.py`.

### What Should Be Discarded as Colab-Only Scaffolding
- `pip install` subprocess calls inside notebook cells.
- `ROOT.mkdir(parents=True, exist_ok=True)` directory scaffolding.
- Package `__init__.py` auto-generation.
- Colab-specific `print("=" * 60)` banners.
- `subprocess.run([sys.executable, "-m", "pytest", ...])` pytest execution from within cells.
- Artifact inventory/SHA-256/MANIFEST generation that assumes notebook execution order.
- `U01_AUDIT_METADATA.json`, `U02_MANIFEST.json`, etc., generated as side-effects of cell execution.
- Cell-by-cell lock assertions and audit metadata generation tied to notebook execution.
- `ensure_drive()` and `/content/drive/MyDrive/Colab Notebooks` path assumptions.
- `notebook_path` discovery and snapshot cells that rely on filesystem `.ipynb` location.

### Dependencies Between Modules
```
U01 (config/settings) → U02 (runtime config) → U03 (data models)
U03 → U04 (providers) → U05 (multi-symbol capture)
U05 → U06 (quality gate) → U06.5 (market foundation)
U06.5 → U07 (scenario engine) → U08 (relative movement)
U08 → U09 (market universe)
U07/U08/U09 → bot interface (future)
```
- All units depend on `app/config/*` for thresholds and safety flags.
- `TRADING_ENABLED=False` chain must be preserved across U05–U09.

---

## 2. U06.5 Migration in Special Detail

### Market-Data Architecture to Preserve
- **Provider priority**: CMC keyless primary, authenticated optional; CoinGecko fallback.
- **Exchange layer**: 8-core public spot venues (Binance, OKX, Bybit, KuCoin, Coinbase, Gate, Upbit, Bitget) with provider-specific normalization.
- **Validation pipeline**: identity → numeric → timestamp → freshness → outlier filtering → rank completeness.
- **Reliability model**: dynamic weighted scoring across 8 components; missing features excluded from denominator, never fabricated.
- **Price aggregation**: reliability-weighted multi-exchange reference price with outlier rejection.
- **Market-cap calculation**: `REFERENCE_PRICE_USD * VALIDATED_CIRCULATING_SUPPLY`; forbidden supply substitutions rejected.
- **Ranking**: dynamic Top-125 by market cap with deterministic tie-break.
- **Index engine**: Kitchen TOTAL/TOTAL2/TOTAL3/Others.D/BTC.D/ETH.D/USDT.D calculated from validated Top-125.
- **Cross-source evidence**: CMC vs CoinGecko price comparison with agreement status.

### Components That Must Survive Migration
- `http_json()` — portable HTTP client (must be extracted; currently uses `urllib`).
- `HTTPResult` dataclass and `classify_http_error()`.
- All provider classes: `CoinGeckoProvider`, `CoinMarketCapProvider`, and 8-exchange specs.
- `_normalize_multi_exchange_rows()` and `_normalize_orderbook()`.
- `validate_identity()`, `validate_numeric_market_fields()`, `validate_timestamp_fields()`, `validate_record()`.
- `validate_ranked_universe()`, `validate_core_assets()`.
- `outlier_filter_v1()` and `_build_reliability_scores()`.
- `price_aggregate_v1()` and `build_live_reference_price_from_multi_exchange()`.
- `calculate_market_cap_v1()` and `validate_circulating_supply()`.
- `dynamic_rank_assets()` and `calculate_indices_from_top125()`.
- `build_provider_cross_source_evidence()`.
- `QUALITY_CONFIG` and all explicit thresholds.
- `CORE_ASSETS`, `PROVIDER_PRIORITY`, `FORBIDDEN_RUNTIME_PROVIDERS`.
- `redact()` and credential-safe serialization.
- All normalization functions: `normalize_cmc_asset`, `normalize_coingecko_asset`, `canonical_asset_id`.

### Notebook/Build-Only Infrastructure to Remove
- `resolve_root()` — portable root discovery with notebook-host-specific exclusions.
- `AUTO_PERSIST_SNAPSHOT = False` and raw artifact persistence tied to notebook paths.
- `persist_raw_artifact()` as implemented (writes to `data/raw/U06_5/` with notebook-specific naming).
- `acquire_market_index_time_series()` historical 5m index acquisition that depends on external provider historical endpoints.
- Print banners and console progress output.
- Any `__main__`-style execution block at module bottom.

---

## 3. Snapshot Cells

### Snapshot-Related Cells/Artifacts
- **Cell 09** (`cell_09.py` / `Kitchen Assistant v3.1from 1 to 8.ipynb`): Canonical Master Portable Snapshot U01→U08.
  - `MASTER_SNAPSHOT_V4` schema.
  - Discovers notebook identity, function registry, runtime state, audit/ledger/artifact objects.
  - Runs regression tests and smoke test.
  - Produces `Kitchen_Assistant_V3.1_MASTER_SNAPSHOT_U01_U08.json`.
- **Cell 06.5** (`cell_06.py`): `U06_5_DATA_FOUNDATION` and raw artifact persistence.
- **U09**: `persist_result()` writes `U09_*.json` snapshots and `U09_AUDIT_*.json` to disk.
- **U05/U06**: Dataset manifests, SHA-256 inventories, quality reports.

### Temporary/Debug/Export Snapshots vs Permanent Business Logic
- **Temporary/export**:
  - Cell 09 snapshot is a notebook execution artifact; it embeds no source code and is tied to the IPYNB runtime.
  - U09 `persist_result()` snapshots are runtime exports; the underlying business logic (provider orchestration, segmentation, etc.) is permanent, but the JSON snapshot files are transient runtime outputs.
  - U06.5 `persist_raw_artifact()` produces debug/audit raw payloads; these are build artifacts, not business logic.
- **Permanent business logic**:
  - `build_segments()`, `relative_strength()`, `participation_brain()`, `build_message()` — these are core U09 logic and must survive.
  - `price_aggregate_v1()`, `dynamic_rank_assets()`, `calculate_indices_from_top125()` — core U06.5 logic.
  - `SCENARIO_MATRIX`, `NARRATIVES` — core U07/U08 logic.

### What Should Survive Migration
- All core engine functions, dataclasses, and config schemas listed in Section 1.
- Snapshot schema definitions (for future runtime state serialization if needed).
- Regression test suites and synthetic validation factories.
- Audit/ledger metadata structure as a serialization format (not as cell side-effects).

### What Should Not Survive Migration
- Notebook-path-dependent snapshot discovery (`notebook_path`, `NOTEBOOK_NAME`, `SNAPSHOT_ROOT_CANDIDATES` with `/content/...`).
- Cell 09's `_safe()` recursive serializer that introspects `globals()` for state objects.
- Function registry built from `MASTER_FUNCTIONS` list tied to Cell 08 globals.
- Snapshot files themselves (`Kitchen_Assistant_V3.1_MASTER_SNAPSHOT_U01_U08.json`, `U09_*.json`) — these are runtime outputs, not source code.

---

## 4. Colab-Specific Dependencies

### /content Paths
- U01: `ROOT = Path("/content/kitchen_robot_v27")`.
- U04: same `/content/kitchen_robot_v27` root.
- U05: `ROOT = Path("/content/drive/MyDrive/Colab Notebooks")`.
- U06: `ensure_drive()` searches `/content/drive/MyDrive/Colab Notebooks`.
- U06.5: `resolve_root()` explicitly excludes paths containing `"content"` and falls back to `/mnt/data` or `/tmp`.
- U09: `ROOT = Path("/content/drive/MyDrive/Colab Notebooks")`.
- **Migration action**: Replace with portable `Path.cwd()`, `Path(__file__).resolve().parent`, or configurable `KITCHEN_ROOT` env var. U06.5's `resolve_root()` already demonstrates the portable pattern.

### Google Drive
- U06: `ensure_drive()` attempts `from google.colab import drive; drive.mount("/content/drive")`.
- U09: assumes Drive mount for persistence.
- **Migration action**: Remove Drive mount dependency. Use local filesystem paths relative to project root or configurable data directories.

### pip Installation Inside Notebook
- U01: `subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pytest>=8,<9"])`.
- U02: `pip install Flask>=3,<4 gunicorn>=23,<24 pytest>=8,<9`.
- U04/U05: `pip install requests>=2,<3`.
- **Migration action**: Move to `requirements.txt`, `pyproject.toml`, or `setup.cfg`. Remove runtime `subprocess` pip calls.

### Notebook Execution Order
- Every cell assumes prior cells have executed and populated `globals()` or the filesystem.
- U02 verifies U01 artifacts; U03 verifies U02; U04 verifies U03; etc.
- **Migration action**: Replace with proper Python package imports and dependency management. Each module should be importable independently after its dependencies are installed.

### subprocess-Based pytest
- U01: `subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT)`.
- U02: `subprocess.run([sys.executable, "-m", "pytest", "-q", "tests/test_u02.py"], cwd=ROOT)`.
- U03/U04: similar patterns.
- **Migration action**: Use a proper test runner (pytest directly, tox, nox) outside the application code. Remove in-cell test execution.

### Other Colab-Only Assumptions
- `from google.colab import drive` (U06).
- `print("=" * 60)` console banners in every cell.
- Cell-level `raise RuntimeError("U01 VALIDATION FAILED")` used as flow control.
- Notebook-specific `sys.path.insert(0, str(ROOT))` manipulation.
- Cell-by-cell artifact generation (manifest, ledger, SHA-256) as side-effects.
- **Migration action**: Replace with structured exceptions, proper logging, and standard Python packaging.

---

## 5. Proposed Project Structure

```
kitchen-assistant/
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── README.md
├── LICENSE
│
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── runtime.py
│   │   ├── market_data.py
│   │   ├── quality.py
│   │   ├── exchanges.py
│   │   └── analysis.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── version.py
│   │   └── safety.py
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── candle.py
│   │   ├── capture/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── binance.py
│   │   │   ├── coinbase.py
│   │   │   ├── router.py
│   │   │   ├── storage.py
│   │   │   └── multi_exchange.py
│   │   └── validation/
│   │       ├── __init__.py
│   │       ├── candles.py
│   │       └── normalize.py
│   │
│   ├── market/
│   │   ├── __init__.py
│   │   ├── foundation.py
│   │   ├── indices.py
│   │   ├── universe.py
│   │   ├── participation.py
│   │   └── message.py
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── range_engine.py
│   │   ├── scenario.py
│   │   ├── narratives.py
│   │   ├── relative_movement.py
│   │   └── context.py
│   │
│   ├── trading/            # disabled / boundary only
│   │   ├── __init__.py
│   │   └── _disabled.py
│   │
│   ├── journal/            # future
│   │   └── __init__.py
│   │
│   ├── orderbook/          # future
│   │   └── __init__.py
│   │
│   └── api/
│       ├── __init__.py
│       └── app.py
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_bootstrap.py
│   │   ├── test_timeframe_guard.py
│   │   ├── test_candle_model.py
│   │   ├── test_scenario_engine.py
│   │   ├── test_relative_movement.py
│   │   └── test_market_universe.py
│   ├── integration/
│   │   ├── test_providers.py
│   │   ├── test_multi_symbol_capture.py
│   │   └── test_data_quality_gate.py
│   └── fixtures/
│       └── sample_data.json
│
├── data/
│   ├── raw/
│   │   └── U06_5/
│   ├── snapshots/
│   │   └── U06_5/
│   ├── historical_u05/
│   │   ├── raw/
│   │   ├── normalized/
│   │   ├── manifests/
│   │   └── quality/
│   └── audit/
│       └── U06_5/
│
├── logs/
├── scripts/
│   ├── start_wsgi.sh
│   └── run_u09.py
│
└── docs/
    ├── AUDIT.md
    └── MIGRATION.md
```

### Module Placement Rationale
- `app/config/` — all configurable thresholds, safety flags, provider lists, environment-derived settings.
- `app/data/` — U03/U04/U05 data foundation, capture adapters, validation, normalization, storage.
- `app/market/` — U06.5 market foundation, indices, universe, participation, message building.
- `app/analysis/` — U07 range/scenario engine, U08 relative-movement engine, locked narratives.
- `app/trading/` — boundary only; explicitly disabled. Contains `_disabled.py` asserting `TRADING_ENABLED = False`.
- `app/api/` — Flask/WSGI boundary from U02 (if retained for health/runtime).
- `tests/` — unit tests for pure logic; integration tests for provider capture and quality gates.
- `data/` — runtime data, snapshots, audit artifacts outside the package.

---

## 6. Migration Risks

### Business Rule Changes During Extraction
- **Timeframe warning logic**: U02 and U07 both implement sub-daily warnings. If extracted inconsistently, the threshold (`< 1440 minutes`) or warning string could diverge. **Risk**: divergent sub-daily behavior between runtime guard and analysis engine. **Mitigation**: centralize in `app/config/analysis.py` and import from both U02 and U07.
- **Volume field naming**: U05 uses `volume_base`; U04 uses `volume`. U06 explicitly corrected a previous bug where `volume` was validated instead of `volume_base`. **Risk**: reintroducing the `volume` vs `volume_base` mismatch during extraction. **Mitigation**: keep `volume_base` as the canonical field name in `app/data/models/candle.py` and enforce via type/model.
- **Scenario matrix drift**: U07 and U08 each define a `SCENARIO_MATRIX` with 9 scenarios. They are similar but not identical (U07 uses `ScenarioType` enum; U08 uses string `scenario_type`). **Risk**: extracting them separately could cause divergence. **Mitigation**: define the matrix once in `app/analysis/scenario.py` and import from U08.
- **Narrative lock**: 27 Persian narratives in U07 and 27 in U08 are locked. **Risk**: accidental rewrite or paraphrase during migration. **Mitigation**: copy verbatim into `app/analysis/narratives.py` with `# LOCKED — DO NOT REWRITE` markers and include in regression tests.
- **Provider priority**: U04, U05, and U06.5 each define Binance-first/Coinbase-fallback or CoinGecko-first/CoinMarketCap-fallback. **Risk**: priority inversion during extraction. **Mitigation**: define provider priority once in `app/config/exchanges.py` and `app/config/market_data.py`.
- **Safety flag propagation**: `TRADING_ENABLED=False` is asserted in U07, U08, U09 and set in U05 records. **Risk**: a migrated module forgets the flag. **Mitigation**: centralize in `app/core/safety.py` and assert at package init.
- **Timestamp units**: U06 explicitly handles millisecond vs second timestamps. U06.5 normalizes all timestamps to ISO UTC. **Risk**: mixed timestamp units in migrated storage layer. **Mitigation**: enforce UTC ISO 8601 in `app/data/models/candle.py` and all capture adapters.
- **Exchange coverage contract**: U06.5 requires minimum 7 of 8 validated exchanges. **Risk**: reducing the target during migration changes data quality. **Mitigation**: keep `TARGET_EXCHANGE_COUNT = 8` and `MIN_VALIDATED_EXCHANGE_COUNT = 7` as constants in `app/config/exchanges.py`.
- **Snapshot cell side-effects**: Cell 09 and U09 persistence rely on notebook execution state (`globals()`). **Risk**: extracting snapshot logic into a standalone module could break runtime object discovery. **Mitigation**: treat snapshots as explicit serialization of known state containers, not `globals()` introspection.
- **Test execution model**: Current pytest runs inside notebook cells via `subprocess.run`. **Risk**: migrated tests might rely on filesystem paths or environment state set by prior cells. **Mitigation**: use pytest fixtures and `conftest.py` for setup/teardown; ensure each test is independently runnable.

---

## Summary

| Area | Status |
|------|--------|
| U01 → U09 source code migration | MAPPED — core logic to `app/`, scaffolding discarded |
| U06.5 special preservation | 30+ components identified; architecture fully specified |
| Snapshot cells | Cell 09 and U09 persistence identified as temporary exports; core logic preserved |
| Colab dependencies | 6 categories identified; all replaceable with portable alternatives |
| Proposed structure | Complete Python package tree with module placement rationale |
| Migration risks | 9 concrete risks with mitigations |

---

# PART 4 — PORTABILITY AND DATA/API CONTRACT AUDIT

## 1. Runtime Portability

### Python Version Assumptions
- **FACT**: Notebook cells use syntax and libraries compatible with Python 3.9+ (e.g., `dict[str, Any]`, `list[Candle]`, `float("inf")`, `math.isfinite`, `statistics.median`, `dataclass(frozen=True)`).
- **FACT**: U01 prints `sys.version.split()[0]` but does not enforce a minimum version.
- **FACT**: U06.5 imports `from __future__ import annotations` and uses `list[Candle]`, `dict[str, Any]` type hints, requiring Python 3.9+.
- **RECOMMENDATION**: Declare `python_requires = ">=3.9"` in `pyproject.toml`.

### Filesystem/Path Assumptions
- **FACT**: U01–U05, U09 hardcode `/content/kitchen_robot_v27` or `/content/drive/MyDrive/Colab Notebooks`.
- **FACT**: U06 `ensure_drive()` searches `/content/drive/MyDrive/Colab Notebooks` and falls back to `/content`, `Path.cwd()`.
- **FACT**: U06.5 `resolve_root()` explicitly excludes paths containing `"content"` and falls back to `/mnt/data` or `/tmp`.
- **FACT**: U09 writes to `U09_ROOT = ROOT / "u09_dynamic_market_universe"` with subdirs `snapshots/`, `audit/`, `cache/`.
- **FACT**: U05 writes to `DATASET_ROOT = ROOT / "data" / "historical_u05"` with `raw/`, `normalized/`, `manifests/`, `quality/`.
- **FACT**: U06.5 writes to `RAW_DIR = DATA_DIR / "raw" / "U06_5"`, `SNAPSHOT_DIR`, `AUDIT_DIR`, `HISTORY_DIR`.
- **RECOMMENDATION**: Use `Path(__file__).resolve().parent` or configurable `KITCHEN_ROOT` environment variable. Ensure all data directories are created at runtime with `mkdir(parents=True, exist_ok=True)`.

### Environment Variables
- **FACT**: U01: `APP_ENV`, `APP_TIMEZONE`, `LOG_LEVEL`.
- **FACT**: U02: `APP_HOST`, `APP_PORT`, `APP_DEBUG`.
- **FACT**: U05: No env vars; all config is inline constants.
- **FACT**: U06.5: `KITCHEN_ROOT`, `KITCHEN_DATASET_MODE` (`SNAPSHOT` or `HISTORICAL`), `KITCHEN_TARGET_CANDIDATE_POOL` (default 1250), `KITCHEN_EXCHANGE_KLINE_LIMIT` (default 2), `KITCHEN_HISTORICAL_PAGE_LIMIT` (default 300), `KITCHEN_TIME_SERIES_LOOKBACK_DAYS` (default 1), `CMC_API_KEY`, `KITCHEN_CMC_API_KEY`, `COINMARKETCAP_API_KEY`, `CMC_PRO_API_KEY`, `COINGECKO_API_KEY`, `KITCHEN_COINGECKO_API_KEY`.
- **FACT**: U09: `COINGECKO_API_KEY`, `COINMARKETCAP_API_KEY`.
- **FACT**: `.env.example` is generated in U01 with `APP_ENV=development`, `APP_TIMEZONE=UTC`, `LOG_LEVEL=INFO`.
- **RECOMMENDATION**: Centralize all env var discovery in `app/config/settings.py` using `pydantic.BaseSettings` or `dataclass` with `os.getenv` defaults.

### Package/Dependency Requirements
- **FACT**: U01 installs `pytest>=8,<9`.
- **FACT**: U02 installs `Flask>=3,<4`, `gunicorn>=23,<24`, `pytest>=8,<9`.
- **FACT**: U04/U05 install `requests>=2,<3`.
- **FACT**: U09 imports `requests`.
- **FACT**: U06.5 uses only Python standard library.
- **RECOMMENDATION**: Create `requirements.txt` with `requests>=2,<3`, `flask>=3,<4`, `gunicorn>=23,<24`, `pytest>=8,<9`. Consider `pyproject.toml` with optional extras for dev/test.

### Network Requirements
- **FACT**: U04 connects to `https://api.binance.com`, `https://api1.binance.com`–`api4`, `https://api.exchange.coinbase.com`.
- **FACT**: U05 connects to Binance and Coinbase public APIs.
- **FACT**: U06.5 connects to `https://pro-api.coinmarketcap.com/public-api`, `https://pro-api.coinmarketcap.com`, `https://api.coingecko.com/api/v3`, and 8 exchange endpoints.
- **FACT**: U09 connects to `https://api.coingecko.com/api/v3/coins/markets` and CMC listings endpoints.
- **FACT**: HTTP timeout defaults: U06.5 uses 20s; U09 uses 12s.
- **RECOMMENDATION**: Document outbound ports (443 HTTPS). Consider proxy support for restricted environments.

### Timezone/Date-Time Assumptions
- **FACT**: All engines use `datetime.now(timezone.utc)` or `.isoformat()`.
- **FACT**: U05 `rolling_range()` computes `start_dt = end_dt - timedelta(minutes=REQUESTED_DURATION_MINUTES)`.
- **FACT**: U06.5 `parse_timestamp()` converts strings to UTC-aware datetimes; naive datetimes are replaced with `timezone.utc`.
- **FACT**: U06.5 `timestamp_age_seconds()` computes `max(0.0, (retrieved_at - source_timestamp).total_seconds())`.
- **FACT**: U09 `reference_timestamp_from_provider_24h()` returns `provider_timestamp - timedelta(hours=24)`.
- **RECOMMENDATION**: Enforce UTC-only policy in `app/core/datetime.py` with helper functions.

---

## 2. External Data Providers

### Binance Spot Public
- **Purpose**: Primary provider for U05 symbols; 8-exchange core spot venue.
- **Endpoints/Adapter Role**:
  - U04/U05: `https://api.binance.com/api/v3/klines` (single-symbol, interval, limit).
  - U06.5: `https://api.binance.com/api/v3/klines` (current 5m probe) and historical pagination with `startTime`/`endTime`.
  - U06.5 order book: `https://api.binance.com/api/v3/depth`.
- **Input Requirements**: `symbol` (e.g., `BTCUSDT`), `interval` (e.g., `1m`, `5m`), `limit` (≤1000).
- **Output/Schema**:
  - U04/U05 kline: `[open_time, open, high, low, close, volume, close_time, quote_volume, ...]` → `Candle(symbol, timestamp, open, high, low, close, volume)`.
  - U06.5 normalized: `{exchange, market_id, timestamp (ISO UTC), open, high, low, close, volume, quote_volume, volume_source, timeframe, provider_timestamp_ms}`.
- **Fallback Relationship**: Primary in U04/U05; first-choice in U06.5 multi-exchange.
- **Retry/Failure Behavior**:
  - U04: Iterates 5 base URLs (`api.binance.com`, `api1`–`api4`).
  - U06.5: Single request per call; failure recorded in `attempts` list.
- **Rate-Limit Considerations**: U04/U05 do not implement explicit rate-limit handling; U06.5 records HTTP 429 as `RATE_LIMIT` in `HTTPResult.error_class`.
- **Validation Rules**: U04 validates `limit > 0`, `limit ≤ 1000`, `interval` in `GRANULARITY_MAP`. U06.5 `_valid_binance_kline_row()` requires `len(row) >= 7`, finite numeric values, `volume > 0`, `close >= 0`.

### Coinbase Exchange Public
- **Purpose**: Fallback provider for U05 symbols; 8-exchange core spot venue.
- **Endpoints/Adapter Role**:
  - U04/U05: `https://api.exchange.coinbase.com/products/{product_id}/candles` with `granularity` in seconds.
  - U06.5: `https://api.exchange.coinbase.com/products/BTC-USDT/candles` (current 5m probe) and historical with `start`/`end` ISO timestamps.
  - U06.5 order book: `https://api.exchange.coinbase.com/products/BTC-USDT/book`.
- **Input Requirements**: `product_id` (e.g., `BTC-USDT`), `granularity` (300 for 5m), `start`/`end` for historical.
- **Output/Schema**:
  - U04/U05: `[time, low, high, open, close, volume]` → `Candle` with `timestamp = int(row[0]) * 1000`.
  - U06.5 normalized: same structure as Binance but `quote_volume = None`, `volume_usd_exact = False`.
- **Fallback Relationship**: Fallback in U04/U05 when Binance fails; secondary in U06.5 multi-exchange.
- **Retry/Failure Behavior**: U05 `fetch_coinbase_real_candles()` paginates backward in time up to 20 pages; raises `CoinbaseProviderUnavailable` if insufficient candles.
- **Rate-Limit Considerations**: No explicit rate-limit handling; HTTP 429 not specially treated in U04/U05.
- **Validation Rules**: U04 validates `limit > 0`, `limit ≤ 300`, `interval` in `GRANULARITY_MAP`. U06.5 `_valid_coinbase_candle_row()` requires `len(row) >= 6`, finite numeric values, `high > 0`, `volume >= 0`.

### CoinGecko
- **Purpose**: Primary global market data provider for U09; fallback for U06.5 global metrics.
- **Endpoints/Adapter Role**:
  - U06.5: `https://api.coingecko.com/api/v3/coins/markets` (Top-125 by market cap).
  - U09: `https://api.coingecko.com/api/v3/coins/markets` (universe limit 125).
- **Input Requirements**: `vs_currency=usd`, `order=market_cap_desc`, `per_page=125`, `page=1`, `sparkline=false`, `price_change_percentage=24h`. Optional `x-cg-demo-api-key` header.
- **Output/Schema**:
  - U06.5 normalized: `{provider_asset_id, symbol, name, price, market_cap, provider_rank, price_change_24h_pct, market_cap_change_24h_pct, provider_timestamp, retrieved_at, identity_status, identity_mapping_provenance}`.
  - U09 normalized: `{provider_asset_id, symbol, name, price_usd, market_cap_usd, provider_rank, price_change_24h_pct, market_cap_change_24h_pct, provider_timestamp}`.
- **Fallback Relationship**: Primary in U09; fallback in U06.5 global metrics.
- **Retry/Failure Behavior**: U06.5 single request; U09 retries up to `max_retries_per_provider + 1` (default 2) with fixed 1s backoff for `TIMEOUT`, `RATE_LIMITED`, `UNAVAILABLE`.
- **Rate-Limit Considerations**: U06.5 classifies HTTP 429 as `RATE_LIMITED`. U09 treats 429 as retryable `ProviderError("RATE_LIMITED")`.
- **Validation Rules**: U06.5 validates `id`, `symbol`, `market_cap_rank`, `current_price`, `market_cap`, `price_change_percentage_24h`. U09 validates rank 1–125, duplicate IDs, numeric price/market_cap.

### CoinMarketCap (CMC)
- **Purpose**: Secondary global provider for U09; primary global metrics for U06.5; optional authenticated mode.
- **Endpoints/Adapter Role**:
  - U06.5 keyless: `https://pro-api.coinmarketcap.com/public-api/v3/cryptocurrency/listings/latest`.
  - U06.5 authenticated: `https://pro-api.coinmarketcap.com/v3/cryptocurrency/listings/latest`.
  - U06.5 quotes: `/v3/cryptocurrency/quotes/latest` (core assets).
  - U06.5 global: `/v1/global-metrics/quotes/latest`.
  - U06.5 simple price: `/v1/simple/price`.
  - U09: keyless or keyed listings/latest endpoint.
- **Input Requirements**: `start=1`, `limit=125` (U06.5) or `limit=200` (U09), `convert=USD`. Authenticated mode requires `X-CMC-PRO-API-KEY` header.
- **Output/Schema**:
  - U06.5 normalized: `{provider_asset_id, symbol, name, price, market_cap, volume_24h, provider_rank, price_change_24h, market_cap_change_24h, source_timestamp, retrieved_at, identity_status, identity_mapping_provenance}`.
  - U09 normalized: `{provider_asset_id, symbol, name, price_usd, market_cap_usd, provider_rank, price_change_24h_pct, market_cap_change_24h_pct, provider_timestamp}`.
- **Fallback Relationship**: Secondary in U09 (after CoinGecko); primary in U06.5 (keyless).
- **Retry/Failure Behavior**: Same retry/backoff as CoinGecko in U09. U06.5 single request.
- **Rate-Limit Considerations**: HTTP 429 classified as `RATE_LIMITED` in U06.5. U09 treats 429 as retryable.
- **Validation Rules**: U06.5 checks `status.error_code == 0` or `None`; validates `cmc_rank`, `quote.USD.price`, `quote.USD.market_cap`. U09 validates rank 1–125, duplicate IDs, numeric validity.

### 8-Exchange Public Spot Venues (U06.5 only)
- **Purpose**: Provide multi-exchange OHLCV and order-book evidence for BTC reliability-weighted reference price and historical coverage.
- **Exchanges and Endpoints**:
  - **Binance**: `https://api.binance.com/api/v3/klines` (current), `startTime`/`endTime` (historical), `https://api.binance.com/api/v3/depth` (order book).
  - **OKX**: `https://www.okx.com/api/v5/market/history-candles` (current), `https://www.okx.com/api/v5/market/books` (order book).
  - **Bybit**: `https://api.bybit.com/v5/market/kline` (current), `https://api.bybit.com/v5/market/orderbook` (order book).
  - **KuCoin**: `https://api.kucoin.com/api/v1/market/candles` (current), `https://api.kucoin.com/api/v1/market/orderbook/level2_100` (order book).
  - **Coinbase**: `https://api.exchange.coinbase.com/products/BTC-USDT/candles` (current), `start`/`end` ISO (historical), `https://api.exchange.coinbase.com/products/BTC-USDT/book` (order book).
  - **Gate**: `https://api.gateio.ws/api/v4/spot/candlesticks` (current), `https://api.gateio.ws/api/v4/spot/order_book` (order book).
  - **Upbit**: `https://api.upbit.com/v1/candles/minutes/5` (current), `https://api.upbit.com/v1/orderbook` (order book).
  - **Bitget**: `https://api.bitget.com/api/v2/spot/market/history-candles` (current), `https://api.bitget.com/api/v2/spot/market/orderbook` (order book).
- **Input Requirements**: Symbol per exchange convention (e.g., `BTCUSDT`, `BTC-USDT`, `BTC_USDT`, `USDT-BTC`), interval `5m`, limit per exchange max.
- **Output/Schema**: Normalized to `{exchange, market_id, timestamp (ISO UTC), open, high, low, close, volume, quote_volume, volume_source, timeframe}`.
- **Fallback Relationship**: Independent parallel probes; no failover between exchanges. Minimum 7 of 8 validated required.
- **Retry/Failure Behavior**: Single request per exchange per call; failures recorded in `per_exchange` dict with `error_class` and `error_message`.
- **Rate-Limit Considerations**: No explicit rate-limit handling; HTTP 429 recorded as `RATE_LIMITED` in `HTTPResult`.
- **Validation Rules**: `_valid_binance_kline_row()` and `_valid_coinbase_candle_row()` for OHLCV validity; `_valid_ohlcv_record()` for normalized rows.

### CMC Global Metrics (Evidence Only)
- **Purpose**: External market-cap dominance evidence; NOT used as Kitchen TOTAL.
- **Endpoint**: `https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest`.
- **Output/Schema**: `normalize_cmc_global_metrics()` returns `{status, provider, provider_mode, total_market_cap, btc_dominance, eth_dominance, active_cryptocurrencies, source_timestamp}`.
- **Fallback Relationship**: Optional cross-source evidence only.
- **Validation Rules**: Schema validation; numeric non-negative checks.

### TradingView
- **FACT**: Explicitly forbidden. `FORBIDDEN_RUNTIME_PROVIDERS = {"tradingview", "tradingview_reference", "tv"}`.
- **FACT**: `tradingview_value_used: False` in `calculate_indices_from_top125()` output.

---

## 3. Internal Data Contracts

### Candles
- **Schema** (U03 `Candle` dataclass):
  - `symbol: str` — non-empty, uppercased/stripped on normalization.
  - `timestamp: int` — positive, strictly increasing in collections.
  - `open: float` — positive, `low <= open <= high`.
  - `high: float` — positive, `high >= low`.
  - `low: float` — positive.
  - `close: float` — positive, `low <= close <= high`.
  - `volume: float` — non-negative.
- **Serialization**: `candle_to_dict()` → `{"symbol", "timestamp", "open", "high", "low", "close", "volume"}`. `candle_from_dict()` reverses with type coercion.
- **Storage**: JSONL (one JSON object per line) via `write_candles()`.

### Market Data (U06.5 normalized record)
- **Schema**:
  - `exchange: str`
  - `market_id: str`
  - `timestamp: str` — ISO 8601 UTC.
  - `open, high, low, close: float`
  - `volume: float` — base-asset traded volume.
  - `quote_volume: float | None`
  - `volume_source: str` — `"PROVIDER_SUPPLIED_TRADED_BASE_VOLUME"`.
  - `timeframe: str` — e.g., `"5m"`.
  - `provider_timestamp_ms | provider_timestamp_seconds: int | None`
  - `retrieved_at: str` — ISO 8601 UTC.
- **Validation**: `validate_market_observation()` checks `market_type == "SPOT"`, positive price, optional volume threshold, freshness age, `asset` and `market_id` presence.

### Volume
- **U05 canonical field**: `volume_base` (not `volume`).
- **Volume contract fields**:
  - `volume_base: float` — provider-supplied traded base-asset volume.
  - `volume_definition: str` — `"TOTAL_TRADED_BASE_ASSET_VOLUME"`.
  - `volume_source: str` — `"PROVIDER_SUPPLIED"`.
  - `volume_counting_rule: str` — `"EACH_TRADE_COUNTED_ONCE"`.
  - `volume_double_counting: bool` — `False`.
  - `buyer_seller_not_double_counted: bool` — `True`.
  - `volume_usd: float | None` — exact quote volume when provider supplies it.
  - `volume_usd_exact: bool` — `True` only when provider quote volume is used directly.
  - `volume_usd_source: str | None` — e.g., `"BINANCE_KLINE_QUOTE_VOLUME"`.
- **Business rule**: No `close * volume` fabrication. No buyer+seller double-counting. No market-cap derivation from volume.

### Market Universe (U09)
- **Asset record schema**:
  - `provider_asset_id: Any` — provider-specific ID (CMC int, CoinGecko string).
  - `canonical_asset_id: str` — `"{provider}:{provider_asset_id}"` or `"{provider}:symbol:{SYMBOL}"`.
  - `symbol: str` — uppercased.
  - `name: str`
  - `provider: str` — `"coingecko"` or `"coinmarketcap"`.
  - `provider_rank: int` — 1 to 125.
  - `price_usd: float | None`
  - `market_cap_usd: float | None`
  - `provider_timestamp: str | None`
  - `retrieved_at: str` — ISO 8601 UTC.
  - `price_change_24h_pct: float | None`
  - `market_cap_change_24h_pct: float | None`
  - `calculated_rank: int`
  - `rank_consistency: str` — `"MATCH"`, `"MINOR_DIFFERENCE"`, `"WARNING"`, `"UNAVAILABLE"`.
  - `segment: str` — `"BTC"`, `"ETH"`, `"TOP10_ALT"`, `"BROAD_ALT_11_125"`.
- **Universe snapshot schema**:
  - `snapshot_id: str`
  - `frozen: bool` — must be `True`.
  - `provider: str`
  - `provider_timestamp: str | None`
  - `created_at: str`
  - `universe_limit: int` — 125.
  - `assets: List[Dict]`
  - `snapshot_hash: str` — SHA-256 of canonical asset JSON.

### Dominance
- **Formula**: `segment_mc / total_mc * 100`.
- **Segments**:
  - `BTC`: rank 1.
  - `ETH`: rank 2.
  - `TOP10_ALT`: ranks 3–10.
  - `BROAD_ALT_11_125`: ranks 11–125.
- **Kitchen indices** (U06.5):
  - `KITCHEN_TOTAL_TOP125 = SUM(market_cap of ranks 1–125)`.
  - `KITCHEN_TOTAL2 = KITCHEN_TOTAL_TOP125 - BTC_MARKET_CAP`.
  - `KITCHEN_TOTAL3 = KITCHEN_TOTAL_TOP125 - BTC_MARKET_CAP - ETH_MARKET_CAP`.
  - `KITCHEN_OTHERS = SUM(market_cap of ranks 11–125)`.
  - `KITCHEN_BTC_D = BTC_MARKET_CAP / KITCHEN_TOTAL_TOP125 * 100`.
  - `KITCHEN_ETH_D = ETH_MARKET_CAP / KITCHEN_TOTAL_TOP125 * 100`.
  - `KITCHEN_USDT_D = USDT_MARKET_CAP / KITCHEN_TOTAL_TOP125 * 100`.
  - `KITCHEN_OTHERS_D = KITCHEN_OTHERS / KITCHEN_TOTAL_TOP125 * 100`.
- **U09 dominance**:
  - `dominance_pct`: current segment dominance.
  - `reference_dominance_pct`: dominance at reference timestamp (24h ago).
  - `dominance_change_pct`: relative percent change.
  - `dominance_change_pp`: absolute percentage-point change (internal/audit only; not displayed).

### Breadth
- **Thresholds** (U09 `CONFIG`):
  - `breadth_threshold_pct = 0.25` — rising if `price_change_24h_pct > 0.25`, falling if `< -0.25`, else flat.
  - `breadth_flat_band_pct = 0.25` — same as threshold (flat band symmetric).
- **Breadth states**:
  - `STRONG`: rising ≥ 70%.
  - `POSITIVE`: rising ≥ 55%.
  - `WEAK`: falling ≥ 70%.
  - `NEGATIVE`: falling ≥ 55%.
  - `MIXED`: otherwise.
- **Schema**: `{rising_count, flat_count, falling_count, rising_pct, flat_pct, falling_pct, breadth_state, price_change_threshold_pct}`.

### Participation
- **States** (U09 `participation_brain()`):
  - `BROADENING`: TOP10 and BROAD both support expansion (`rising_pct >= 55` and `market_cap_change_pct > 0`).
  - `CONCENTRATED`: core support (`BTC_MC > 0` or `ETH_MC > 0`) and broad+top weak (`rising_pct < 45` and `market_cap_change_pct < 0`).
  - `WEAKENING`: broad weak and top weak.
  - `MIXED`: otherwise.
  - `UNAVAILABLE`: if any segment count == 0 or composition quality unreliable.
- **Business rule**: Participation state is internal only; never emitted in user-facing messages.

### Snapshots
- **Cell 09 schema** (`MASTER_PORTABLE_SNAPSHOT_V4`):
  - `snapshot`: engine, version, schema, timestamp_utc, status, source_code_embedded, notebook identity.
  - `source_of_truth`: code=IPYNB, state=MASTER_SNAPSHOT, history=MASTER_SNAPSHOT, audit=MASTER_SNAPSHOT, ledger=MASTER_SNAPSHOT, artifacts=MASTER_SNAPSHOT.
  - `architecture`: coverage U01_U08, unit evidence, notebook name.
  - `execution`: trading/orders/strategy/portfolio flags, execution_mode=ANALYSIS_ONLY.
  - `configuration`: cell08_config.
  - `contracts`: scenario_matrix_locked, narratives_locked, btc_is_benchmark, analysis_only, trading_authorization=False.
  - `scenarios`: count, scenario_ids.
  - `narratives`: scenario_count, total_patterns.
  - `functions`: registry of 26 callables.
  - `runtime_state`, `audit`, `ledger`, `artifacts`, `history`: discovered objects.
  - `regression`: test result.
  - `smoke_test`: run_cell_08 smoke result.
  - `continuity`: current_state=U08_VALIDATED.
  - `integrity`: boolean pass/fail fields.
  - `known_issues`, `pending_work`, `decisions`.
  - `handoff`: ready flag, instructions.
- **U09 snapshot schema**:
  - `snapshot_id`, `frozen`, `provider`, `provider_timestamp`, `created_at`, `universe_limit=125`, `assets`, `snapshot_hash`.
- **Business rule**: Snapshots are frozen at creation; composition changes are detected but never retroactively mutate old snapshots.

### Audit/Quality Records
- **U06 quality report** (`U06_DATA_QUALITY_REPORT.json`):
  - `project`, `version`, `execution_unit`, `gate`, `validation_status`, `technical_lock`, `source_data_modified`, `controlled_symbols`, `expected_records_per_symbol`, `expected_total_records`, `actual_total_records`, `hard_total_problems`, `u05_schema`, `control_artifacts`, `sha256`, `global_validation`, `safety`, `symbol_reports`, `generated_at_utc`.
- **U06 quality summary** (`U06_DATA_QUALITY_SUMMARY.txt`): Plain-text summary with global status, technical lock, total records, problems, symbol results.
- **U09 audit** (`U09_AUDIT_*.json`):
  - `status`: `"PASS"` or `"FAIL"`.
  - `issues`: list of strings (trading_lock, orders_lock, strategy_lock, portfolio_lock, banned_language, message_participation_state_should_be_internal, message_pp_should_be_internal, message_signed_zero, message_line_contract, snapshot_not_frozen, snapshot_count).
- **U09 result** (`U09_*.json`):
  - `engine`, `version`, `validation_status`, `data_quality`, `confidence`, `provider`, `primary_provider`, `fallback_used`, `fallback_chain`, `fallback_reason`, `current_timestamp`, `reference_timestamp`, `universe_snapshot`, `btc_metrics`, `eth_metrics`, `top10_metrics`, `broad_metrics`, `segments`, `total_125_mc`, `reference_total_125_mc`, `dominance_metrics`, `breadth_metrics`, `relative_strength_metrics`, `composition_status`, `participation_state`, `participation_explanation`, `synthetic_tests`, `validation`, `provider_health`, `internal_diagnostics`, `safety`, `message`, `audit`, `technical_lock_candidate`, `execution_seconds`.

---

## 4. Timeframe and Timestamp Rules

### Supported Timeframes
- **U02**: `M1`, `M5`, `M15`, `H1`, `H4`, `D1`, `D7`. Custom range via `validate_timeframe_guard()`.
- **U04**: `1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `8h`, `12h`, `1d` (Binance `GRANULARITY_MAP`).
- **U05**: `1m` only (hardcoded `INTERVAL = "1m"`).
- **U06.5**: `1m`, `5m`, `15m`, `1h`, `4h`, `1d` (`SUPPORTED_TIMEFRAMES`). Exchange probes use `5m`.
- **U07**: `1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `8h`, `12h`, `1D`, `1W`, `1M` via `parse_timeframe()`.
- **U09**: 24h lookback only (`lookback = "24h"`, `message_window_label = "24H"`).

### Timestamp Normalization
- **FACT**: U06.5 normalizes all timestamps to ISO 8601 UTC strings with `+00:00` or `Z` suffix.
- **FACT**: U06.5 `parse_timestamp()` accepts `int`, `float`, `str` (ISO 8601 with optional `Z`), and `datetime` objects. Naive datetimes are assumed UTC.
- **FACT**: U04 Binance uses millisecond timestamps (`int(row[0])`). U04 Coinbase uses second timestamps multiplied by 1000.
- **FACT**: U05 uses `timestamp: int` in milliseconds for rolling range calculations.
- **FACT**: U06 detects timestamp unit: `> 100_000_000_000` → milliseconds; `> 1_000_000_000` → seconds; else invalid.
- **FACT**: U09 `reference_timestamp_from_provider_24h()` returns `provider_timestamp - timedelta(hours=24)`.
- **RECOMMENDATION**: Enforce UTC ISO 8601 everywhere; never mix milliseconds and seconds in the same record type.

### 24h Calculations
- **U09**: `build_reference_from_24h()` reconstructs 24h-ago market cap: `reference_mc = mc / (1.0 + ch / 100.0)` where `ch` is `market_cap_change_24h_pct`.
- **U09**: `dominance_change_pct(current, reference)` computes `(current - reference) / reference * 100.0`.
- **U09**: `reference_timestamp` = provider timestamp minus exactly 24 hours.
- **Business rule**: 24h movement is relative percent change; percentage-point change is `(current_pct - reference_pct)` and remains internal/audit only.

### 5m Honesty Rules
- **FACT**: U06.5 explicitly states: "Historical 5m data is never fabricated or silently substituted."
- **FACT**: `acquire_exchange_historical_ohlcv()` documentation: "Missing periods remain missing; no resampling/backfilling is performed."
- **FACT**: Coinbase may omit no-trade intervals; U06 tolerates Coinbase gaps as diagnostics but treats Binance gaps as integrity failures.
- **FACT**: U05 never creates zero-volume synthetic candles for missing intervals.
- **Business rule**: No interpolation, resampling, or silent substitution of historical 5m data.

### Timezone Handling
- **FACT**: All engines use UTC. `datetime.now(timezone.utc)` is the canonical current-time call.
- **FACT**: U06.5 `parse_timestamp()` replaces naive `tzinfo=None` with `timezone.utc`.
- **FACT**: U05 `rolling_range()` returns `start_utc` and `end_utc` as formatted strings with `" UTC"` suffix.
- **RECOMMENDATION**: Enforce UTC-only policy; never accept local time without explicit conversion.

### M vs m Distinction
- **FACT**: U07 `parse_timeframe()` intentionally preserves uppercase `M` as MONTH (`43200` minutes). Lowercase `m` is minutes.
- **FACT**: Regex: `^\s*(\d+(?:\.\d+)?)\s*([mMhHdDwW])\s*$`.
- **Business rule**: Uppercase `M` must NEVER be lowercased before interpretation. `1M` = 1 month (30 days, 43200 minutes); `1m` = 1 minute.

---

## 5. Reliability and Failure Behavior

### Provider Failover
- **U04/U05**: Binance → Coinbase. Binance is always first choice; Coinbase used only when Binance cannot provide requested data.
- **U06.5**: Multi-exchange parallel probes. No failover between exchanges; each is independent. Minimum 7 of 8 validated required.
- **U09**: CoinGecko → CoinMarketCap. Primary = CoinGecko; fallback = CoinMarketCap. `provider_order()` respects cooldown and validation score.

### Retries
- **U06.5**: `MAX_RETRIES_PER_PROVIDER = 1` (default). Retries for `TIMEOUT`, `RATE_LIMITED`, `UNAVAILABLE` with fixed backoff (not implemented in U06.5 global providers; implemented in U09).
- **U09**: `max_retries_per_provider = 1` (default). Fixed `retry_backoff_seconds = 1.0`. Retries only for `TIMEOUT`, `RATE_LIMITED`, `UNAVAILABLE`.

### Cooldowns
- **U09**: `provider_cooldown_seconds = 60`. On failure, provider health state is set to error class and cooldown until `now + 60s`. `provider_order()` skips providers in cooldown. Validation score decays by 0.2 on each failure.

### Validation Scoring
- **U06.5 outlier filter**: MAD-based robust z-score. `max_price_deviation_pct_from_median = 5.0`, `max_robust_z = 6.0`.
- **U06.5 reliability model**: 8 components with configurable weights: data_integrity (0.15), freshness (0.10), volume (0.15), near_depth (0.20), far_depth (0.10), spread (0.10), price_impact (0.10), cross_exchange_consistency (0.10). Missing components excluded from denominator.
- **U09 provider validation**: rank coverage, duplicate ID/rank detection, numeric validity, freshness. `validation_score` decays on failure.

### Quality Gates
- **U06**: Lock only when every required gate passes: SHA-256 valid, record count exact, symbol coverage exact, OHLC valid, volume contract valid, safety flags all False, source unmodified.
- **U06.5**: Top-125 completeness (exactly 125 valid records), core assets present, duplicate IDs/ranks rejected, rank gaps detected.
- **U09**: Synthetic validation suite must PASS; audit must PASS; `validation_status == "PASS"`; safety locks asserted.

### Technical Lock Conditions
- **U01–U06**: Lock requires pytest PASSED, artifact self-check PASSED, lock assertions PASSED, audit metadata written.
- **U06**: `technical_lock = (validation_status == "PASS")`. Locks only when `hard_problem_count == 0` for all symbols and all global checks pass.
- **U07**: Assert `U07_VALIDATION["status"] == "PASS"` at module load.
- **U08**: Snapshot `core_pass` requires all integrity fields True.
- **U09**: `technical_lock_candidate = synthetic_tests PASS and audit PASS and validation_status PASS`. Hard assertions enforce this.

### Unavailable/Invalid Data Behavior
- **U04**: `BinanceProviderUnavailable` / `CoinbaseProviderUnavailable` raised when provider fails.
- **U05**: `capture_with_priority()` raises `RuntimeError("ALL PROVIDERS FAILED")` with attempt JSON if all providers fail.
- **U06.5**: `HTTPResult` returned for all HTTP outcomes (ok or error). `acquire_multi_exchange_symbol()` returns `status: "NOT_AVAILABLE"` on failure. `price_aggregate_v1()` returns `status: "DATA_UNAVAILABLE"` if no valid markets. `calculate_indices_from_top125()` returns `status: "DATA_PARTIAL"` if Top-125 incomplete.
- **U09**: `orchestrate_universe()` returns `{"snapshot": None, "validation": {"status": "DATA_UNAVAILABLE", ...}}` when all providers fail. `execute_u09()` handles `DATA_UNAVAILABLE` gracefully and still persists result + audit.
- **Business rule**: No fabricated values. No silent reuse of stale data. Explicit `DATA_UNAVAILABLE` returned when validation fails.

---

## 6. Telegram Integration Readiness

### What Data the Future Telegram Layer Can Consume
- **U09 message**: `build_message()` returns a strict 5-line string:
  ```
  📊 MARKET PARTICIPATION | 24H
  ₿ BTC Price {24h_pct} | BTC.D {dom_change_pct}
  🔷 ETH Price {24h_pct} | ETH.D {dom_change_pct}
  🔹 TOP10 ALT MC {24h_pct} | TOP10.D {dom_change_pct}
  ◈ BROAD 11–125 MC {24h_pct} | BROAD.D {dom_change_pct}
  ```
- **U07/U08 narratives**: 27 Persian narrative patterns per engine, each with `pattern`, `title`, `text`. Selectable by `pattern_index` (1–3).
- **U08 result**: `Cell08Result` dataclass with `scenario_id`, `scenario_type`, `context`, `opposite_direction`, `selected_pattern`, `top_10_assets`, `strong_movers`, `relative_movers`, `altcoin_structure`, `audit`.
- **U07 result**: `ScenarioResult` dataclass with `scenario_id`, `scenario_type`, `total_classification`, `usdt_d_classification`, `total_range_type`, `total_range_confidence`, `total_range_score`, `usdt_range_*`, `timeframe`, `analysis_range`, `audit`.
- **U06 quality report**: `U06_DATA_QUALITY_REPORT.json` with per-symbol status, problems, hard_problem_count.
- **U09 full result**: `U09_RESULT` dict containing segments, dominance, breadth, relative strength, participation state, provider health, synthetic tests, validation, audit.

### Interfaces/Adapters Missing
- **Telegram bot framework**: No `python-telegram-bot`, `aiogram`, or raw `requests` to Telegram Bot API.
- **Command handlers**: No `/start`, `/help`, `/report`, `/universe`, `/scenario`, `/btc` commands defined.
- **Message dispatcher**: No routing from Telegram update to engine call.
- **Session/state management**: No user session, chat state, or conversation handler.
- **Inline keyboards**: No button layouts for timeframe selection, pattern selection, or asset navigation.
- **Callback query handlers**: No handling of inline button presses.
- **Media/formatting**: No Markdown/HTML formatting, no chart images, no file attachments.
- **Webhook/polling**: No long-polling or webhook server.
- **Error-to-user mapping**: Engine exceptions are not mapped to user-friendly Telegram error messages.

### Contracts to Create Between Engine and Telegram Bot
- **FACT**: Engine outputs are pure Python dicts/dataclasses; they do not depend on Telegram.
- **RECOMMENDATION**: Define a `BotOutput` protocol/interface:
  - `format_market_report(u09_result: dict) -> str` — wraps `build_message()`.
  - `format_narrative(scenario_result: dict, pattern_index: int) -> str` — wraps U07/U08 narrative selection.
  - `format_quality_gate(quality_report: dict) -> str` — wraps U06 summary.
  - `validate_user_input(timeframe: str, analysis_range: Any) -> dict` — wraps `parse_timeframe()` and `validate_user_range()`.
- **RECOMMENDATION**: Define a `BotEngine` interface with methods:
  - `get_market_universe() -> dict`
  - `run_scenario_analysis(total_values, usdt_values, timeframe, analysis_range) -> dict`
  - `run_relative_movement(btc_direction, btc_d_direction, btc_change_pct, assets) -> dict`
- **RECOMMENDATION**: Engine should raise domain-specific exceptions (`ProviderUnavailable`, `ValidationFailed`, `DataUnavailable`) that the bot layer catches and translates to Persian/English user messages.
- **FACT**: Current user-facing messages are in Persian (Farsi) with some English labels/emojis. No translation layer or language selection is specified.

---

# PART 5 — TESTING, GAPS, RISKS AND FINAL RECOMMENDATION

## 1. Testing Audit

### Existing Tests
- **U01**: `tests/test_u01.py` — validates project metadata (`PROJECT_NAME`, `PROJECT_VERSION`, `EXECUTION_UNIT`), configuration boundary (`get_settings()`), and required directory existence.
- **U02**: `tests/test_u02.py` — validates Flask app creation, `/health` and `/` endpoints, sub-daily standard timeframe warnings, daily/weekly no-warning behavior, custom range below/above daily warnings, invalid custom range format/order, unsupported timeframe, WSGI entrypoint existence, and runtime file existence.
- **U03**: `tests/data/test_u03.py` — validates Candle model construction, invalid OHLC rejection, chronological validation, non-chronological rejection, normalization, and JSONL storage count/line count.
- **U04**: `tests/data/test_u04.py` — validates adapter existence, `provider_name`, Binance limit validation (0, 1001, invalid interval), Coinbase adapter existence, router existence, and provider priority.
- **U06**: No standalone pytest file; validation is performed inline in the cell via loops over JSONL files and artifact files.
- **U06.5**: `synthetic_validation_suite()` embedded in cell; `run_u07_regression_tests()` in U07; `run_cell08_regression_tests()` in U08.
- **U07**: `run_u07_regression_tests()` — validates scenario matrix, timeframe regression, zero-movement edge case, internal structure, 9-scenario pairs, and execution locks.
- **U08**: `run_cell08_regression_tests()` — validates 9 scenarios, 27 patterns, opposite-direction cases, absolute≠relative, no false bullish label, range does not imply all assets range.
- **U09**: `synthetic_validation_suite()` — validates rank identity/segmentation/aggregation/dominance, breadth exact 10/5/5, relative strength pairs, zero reference guard, duplicate ID/rank rejection, missing rank rejection, invalid numeric rejection, composition boundary, dominance semantics, freshness states, participation brain state set, message contract.

### What Each Test Validates
- **Unit-level**: U01–U04, U07, U08 tests validate pure functions, dataclasses, and Flask endpoints without network I/O.
- **Integration-level**: U04 live capture test, U05 multi-symbol capture, U06 quality gate, U06.5 multi-exchange evidence, U09 `orchestrate_universe()` — these require live network access.
- **Regression-level**: U07, U08, U09 include embedded regression suites that assert matrix completeness, narrative counts, and edge cases.
- **Quality gates**: U06 enforces SHA-256, record counts, OHLC bounds, volume contract, safety flags. U06.5 enforces Top-125 completeness, core assets, outlier filtering. U09 enforces synthetic tests, audit, and safety locks.

### Test Coverage by U01–U09
- **U01**: Metadata, config, directories — covered.
- **U02**: Timeframe guard, Flask runtime — covered.
- **U03**: Candle model, validation, normalization, JSONL storage — covered.
- **U04**: Provider adapters, router, live capture — partially covered (structural tests exist; live capture is manual/inline).
- **U05**: Multi-symbol capture, rolling volume, volume contract — no standalone pytest file; validated inline.
- **U06**: Quality gate, SHA-256, schema enforcement — no standalone pytest file; validated inline.
- **U06.5**: Synthetic suite covers ranking, segmentation, dominance, breadth, reliability, outlier filtering, message contract — covered but embedded in cell.
- **U07**: Scenario matrix, range engine, DMI/ADX, timeframe regression — covered via `run_u07_regression_tests()`.
- **U08**: Scenario resolution, narrative library, ranking, relative performance — covered via `run_cell08_regression_tests()`.
- **U09**: Provider orchestration, universe building, segmentation, participation brain, message contract — covered via `synthetic_validation_suite()`.

### Live-Network Tests vs Deterministic Tests
- **Live-network**: U04 live capture (5 BTCUSDT 1m candles), U05 multi-symbol capture (100 candles × 5 symbols), U06.5 `acquire_multi_exchange_evidence()` (8 exchanges), U09 `orchestrate_universe()` (CoinGecko/CMC). These depend on external API availability and rate limits.
- **Deterministic**: U01–U03, U07, U08, U09 synthetic suite — fully deterministic, no network I/O.
- **Mixed**: U06.5 `price_aggregate_v1()` can run on synthetic observations; `build_live_reference_price_from_multi_exchange()` requires live exchange probes.

### Missing Tests
- **U04**: No tests for actual HTTP failure modes (timeout, 429, 500), multi-URL fallback behavior, or Coinbase pagination.
- **U05**: No pytest file for `capture_with_priority`, `build_record`, `validate_records`, `calculate_rolling_volume`. Rolling volume edge cases (empty range, exact 24h boundary) are not explicitly tested.
- **U06**: No pytest file for `validate_ohlc`, `load_jsonl`, SHA-256 verification, gap tolerance logic, or safety flag validation.
- **U06.5**: No pytest file for `http_json`, `HTTPResult`, `classify_http_error`, `acquire_cmc`, `acquire_coingecko_top125`, `_normalize_multi_exchange_rows`, `_normalize_orderbook`, `orderbook_quality_metrics`, `outlier_filter_v1`, `_build_reliability_scores`, `price_aggregate_v1`, `calculate_market_cap_v1`, `dynamic_rank_assets`, `calculate_indices_from_top125`, `build_provider_cross_source_evidence`. Synthetic suite covers some but not all.
- **U09**: No pytest file for `provider_order`, `_cooldown`, `freshness_status`, `segment_for_rank`, `build_reference_from_24h`, `reference_timestamp_from_provider_24h`, `build_segments`, `relative_strength`, `composition_compare`, `participation_brain`, `fmt_pct`, `build_message`, `audit_result`, `persist_result`.
- **Cross-cutting**: No tests for environment variable discovery, config loading, or error-to-user mapping.

### CI/CD Readiness
- **Current state**: Tests are embedded in notebook cells and executed via `subprocess.run` inside Colab. Not suitable for CI/CD.
- **Gaps**: No `pytest.ini`, `tox.ini`, `noxfile.py`, or GitHub Actions/GitLab CI configuration. No test fixtures or `conftest.py`. No separation of unit vs integration tests.
- **RECOMMENDATION**: Extract all tests to `tests/` directory. Use `pytest` with markers `@pytest.mark.unit` and `@pytest.mark.integration`. Skip live-network tests in CI unless explicitly enabled via env var. Add `pytest-cov` for coverage reporting.

### Recommended Test Strategy After Migration
- **Unit tests**: Pure logic (U01–U04, U07, U08, U06.5 validation/ranking/indices) — run on every commit.
- **Integration tests**: Provider capture, quality gates, U06.5 multi-exchange — run on PR merge to main, with network access.
- **Deterministic synthetic tests**: U09 synthetic suite, U07/U08 regression — run on every commit.
- **Live-network tests**: U04/U05 capture, U09 `orchestrate_universe()` — run nightly or on-demand, not in CI.
- **Coverage target**: 90%+ for core logic; 70%+ for integration paths.

---

## 2. Gaps

### Already Implemented
- **Data foundation**: Candle model, validation, normalization, JSONL storage (U03).
- **Provider adapters**: Binance and Coinbase public adapters with priority routing (U04, U05).
- **Multi-symbol capture**: 100 real candles per symbol for 5 assets with rolling volume (U05).
- **Quality gate**: SHA-256 integrity, record count, OHLC bounds, volume contract, safety flags (U06).
- **Market data foundation**: CMC/CoinGecko global data, 8-exchange OHLCV/orderbook, reliability-weighted price aggregation, Top-125 ranking, Kitchen indices, cross-source evidence (U06.5).
- **Scenario engine**: Range detection, DMI/ADX, 9-scenario matrix, 27 Persian narratives, timeframe validation (U07).
- **Relative movement**: BTC/BTC.D context, 9-scenario matrix, 27 Persian patterns, strong/relative movers ranking (U08).
- **Market universe**: Dynamic Rank 1-125, segmentation, dominance, breadth, relative strength, participation brain, compact 5-line Persian message (U09).
- **Safety locks**: `TRADING_ENABLED=False`, `ORDERS_ENABLED=False`, `STRATEGY_ENABLED=False`, `PORTFOLIO_ACTIONS_ENABLED=False` asserted in U07, U08, U09 and set in U05 records.
- **Configuration**: Environment-derived settings, runtime config, market data config, quality thresholds, analysis config.
- **Artifact generation**: Manifests, ledgers, SHA-256 inventories, audit metadata, quality reports.

### Partially Implemented
- **Telegram interface**: No bot framework, command handlers, or message dispatcher. Engine outputs are ready for consumption but no delivery layer exists.
- **Persistence**: U05/U06/U06.5/U09 write data and audit files, but no user session history, chat history, or persistent user preferences.
- **Error handling**: Provider-level errors and data validation errors are handled. No bot-level error handling, user-friendly error messages, or fallback chat flows.
- **Logging**: `print` statements and artifact files exist. No structured logging framework, log levels, or rotation.
- **Scheduling**: No periodic job scheduler. Engines are on-demand only.
- **Alerts**: No threshold monitoring, alert dispatch, or notification logic.
- **Risk management**: U06.5 includes data-quality outlier filtering and reliability scoring. No trading risk management (position sizing, stop-loss, drawdown).

### Completely Missing
- **Telegram bot implementation**: Framework choice, command handlers, inline keyboards, callback queries, webhook/polling server.
- **User management**: Authentication, authorization, session state, user preferences, rate limiting per user.
- **Admin controls**: Admin commands, broadcast, user ban/kick, configuration overrides.
- **Signal generation**: No buy/sell signals, entry/exit logic, or trade recommendations (intentionally disabled).
- **Portfolio/trading**: No portfolio tracking, order management, execution, or capital flow (intentionally disabled).
- **Charting/media**: No chart images, Kline diagrams, or file attachments.
- **Localization**: No translation layer; Persian is hardcoded in narratives and labels. No English fallback or language selection.
- **API server**: No REST/GraphQL API for external consumption. Flask app in U02 is minimal (`/health`, `/`).
- **Database**: No relational or document database. All persistence is JSON/JSONL files.
- **Background tasks**: No Celery, RQ, or async task queue for long-running analysis.
- **Caching layer**: No Redis/Memcached. U09 has in-memory `cache_enabled` config but no persistent cache implementation.
- **Observability**: No metrics, tracing, or APM integration.

---

## 3. Risks

### Accidental Changes to U06.5
- **Risk**: U06.5 is the most complex unit (~2700 lines). During extraction, normalization rules, reliability weights, or outlier thresholds could be altered.
- **Mitigation**: Copy U06.5 verbatim into `app/market/foundation.py` with `# LOCKED — DO NOT MODIFY` markers. Include `synthetic_validation_suite()` as a pytest module. Run it in CI.

### Provider Behavior
- **Risk**: Provider APIs change without notice. Endpoints, parameter names, response schemas, rate limits, and error codes can break adapters silently.
- **Mitigation**: Pin provider behavior in adapter tests with recorded HTTP interactions (e.g., `pytest-recording`). Add contract tests that validate response schemas against provider documentation. Monitor provider changelogs.

### Data Schemas
- **Risk**: U05 `volume_base` vs U04 `volume` mismatch could reappear if adapters are extracted separately.
- **Mitigation**: Define canonical `Candle` model in `app/data/models/candle.py`. All adapters must return canonical models, not raw dicts.
- **Risk**: U06.5 normalized record schema is large (~20 fields). Missing or renamed fields during migration break downstream engines.
- **Mitigation**: Use `dataclass` or `pydantic.BaseModel` for normalized records. Include schema validation in tests.

### Timestamps/Timeframes
- **Risk**: Mixing milliseconds and seconds, or naive datetimes, causes silent data corruption.
- **Mitigation**: Enforce UTC ISO 8601 in `app/core/datetime.py`. Add tests that reject naive datetimes and mixed timestamp units.
- **Risk**: U07 and U02 both implement sub-daily warnings. Divergent thresholds break user experience.
- **Mitigation**: Centralize `SUB_DAILY_WARNING` and threshold in `app/config/analysis.py`.

### Live API Dependency
- **Risk**: Engines fail entirely when providers are unreachable. U09 handles `DATA_UNAVAILABLE`, but U04/U05 raise exceptions.
- **Mitigation**: Wrap live capture in graceful degradation. Return `DATA_UNAVAILABLE` with diagnostic metadata instead of raising. Cache last-known-good snapshots for analysis.

### Reliability/Quality Gates
- **Risk**: Lowering `MIN_VALIDATED_EXCHANGE_COUNT` or `TARGET_EXCHANGE_COUNT` weakens data quality silently.
- **Mitigation**: Keep these as immutable constants in `app/config/exchanges.py`. Include them in synthetic tests.
- **Risk**: Outlier thresholds (`max_price_deviation_pct_from_median`, `max_robust_z`) are configurable but could be changed inadvertently.
- **Mitigation**: Document that changes to `QUALITY_CONFIG` require explicit review and regression test updates.

### Persian Narrative Rules
- **Risk**: 27 narratives in U07 and 27 in U08 are locked. Accidental rewrite, paraphrase, or encoding corruption changes user-facing text.
- **Mitigation**: Store narratives in a separate `app/analysis/narratives.py` with explicit `# LOCKED — DO NOT REWRITE` comments. Include `validate_narratives()` in pytest. Store narratives as UTF-8 with BOM or ensure `encoding="utf-8"` everywhere.

### Portability
- **Risk**: `/content` paths, `google.colab` imports, and notebook execution order assumptions leak into migrated code.
- **Mitigation**: Remove all `google.colab` imports. Replace `/content` paths with `Path(__file__).resolve().parent` or `KITCHEN_ROOT` env var. Use standard Python packaging (`pyproject.toml`).

### Persistence
- **Risk**: Snapshot logic tied to `globals()` introspection breaks in standalone modules.
- **Mitigation**: Replace Cell 09 snapshot with explicit state serialization. Define `SnapshotState` dataclass with known fields. Serialize with `dataclasses.asdict()`.

### Security
- **Risk**: Provider API keys discovered via environment variables could be logged or serialized accidentally.
- **Mitigation**: Use `redact()` utility already present in U06.5. Never log or serialize `CMC_API_KEY`, `COINGECKO_API_KEY`, or any `*_API_KEY` value. Audit all `json.dumps`, `print`, and logging calls for credential leakage.

---

## 4. Migration Priorities

### P0 — Must Preserve/Fix Before Migration
1. **U06.5 architecture preservation**: Extract all 30+ components verbatim. Do not alter normalization, reliability weights, outlier thresholds, or ranking logic.
2. **Volume field canonicalization**: Enforce `volume_base` everywhere. Remove `volume` from U05+ schemas.
3. **Safety flag propagation**: Centralize `TRADING_ENABLED=False` chain in `app/core/safety.py`. Assert at package init.
4. **Timestamp normalization**: Enforce UTC ISO 8601 in all models and adapters. Reject naive datetimes.
5. **Scenario matrix unification**: Define `SCENARIO_MATRIX` once in `app/analysis/scenario.py`. Import from U07 and U08.
6. **Narrative lock**: Copy 27+27 Persian narratives verbatim. Add regression tests that assert exact text.

### P1 — Required for a Usable Standalone Engine
1. **Portable project structure**: Implement `pyproject.toml`, `requirements.txt`, `app/` package layout.
2. **Configuration centralization**: `app/config/settings.py`, `market_data.py`, `quality.py`, `exchanges.py`, `analysis.py`.
3. **Test extraction**: Move all inline tests to `tests/unit/` and `tests/integration/`. Add `conftest.py`.
4. **Logging framework**: Replace `print` with `logging`. Add levels, formatting, and file handlers.
5. **Error handling**: Define domain exceptions (`ProviderUnavailable`, `ValidationFailed`, `DataUnavailable`). Wrap engine entry points.
6. **Persistence layer**: Replace notebook-path-dependent file I/O with `app/core/paths.py` using `KITCHEN_ROOT`.

### P2 — Required for Telegram Integration
1. **Bot framework selection**: Choose `python-telegram-bot` or `aiogram`. Implement command handlers.
2. **Command interface**: `/start`, `/help`, `/report` (U09 message), `/scenario` (U07), `/btc` (U08), `/quality` (U06).
3. **Message formatting**: Wrap `build_message()`, narrative selection, quality summaries in `BotOutput` interface.
4. **Session/state management**: User preferences, timeframe selection, pattern index memory.
5. **Inline keyboards**: Timeframe selection, pattern navigation, asset drill-down.
6. **Error-to-user mapping**: Translate engine exceptions to Persian/English user messages.

### P3 — Later Improvements
1. **Database**: PostgreSQL/MongoDB for user sessions, chat history, persistent preferences.
2. **Background tasks**: Celery/RQ for periodic U09 updates and U06.5 refresh.
3. **Caching**: Redis for provider responses, universe snapshots, index calculations.
4. **Charting**: Kline charts, dominance pie charts, breadth bar charts.
5. **Localization**: English/Persian toggle, translation framework.
6. **API server**: Expand Flask app to REST API for external consumption.
7. **Admin panel**: Web UI for configuration, user management, broadcast.
8. **Advanced risk**: Portfolio tracking, position sizing, stop-loss logic (if trading ever enabled).

---

## 5. Final Verdict

### What We Already Have
- A complete, deterministic analysis engine covering data capture (U03–U06), market foundation (U06.5), scenario analysis (U07), relative movement (U08), and dynamic market universe (U09).
- Locked business rules: 27 Persian narratives per engine, 9-scenario matrices, volume contract, sub-daily warnings, 5m honesty, no fabrication.
- Safety locks asserted across all analysis units. Trading, orders, strategy, and portfolio actions are explicitly disabled.
- Provider-agnostic data foundation with Binance/Coinbase for historical data and CMC/CoinGecko/8-exchange for current data.
- Comprehensive inline validation, quality gates, and synthetic test suites.

### What the Notebook Does NOT Specify
- Telegram bot implementation (framework, commands, handlers, keyboards).
- User authentication, authorization, session management.
- Admin controls, broadcast, or user management.
- Scheduling, periodic jobs, or background tasks.
- Alert/notification thresholds and dispatch logic.
- Signal generation, portfolio tracking, or trading execution.
- Risk management (position sizing, stop-loss, drawdown).
- Persistence beyond JSON/JSONL files (no database).
- Structured logging, CI/CD pipeline, or deployment configuration.
- English language support or i18n framework.
- Charting, media, or rich formatting.

### What Must Be Built Around the Existing Engine
- Telegram bot framework and command handlers.
- Session/state management for user preferences and conversation flow.
- Error-to-user message mapping and Persian/English localization.
- Scheduling/periodic refresh for U09 and U06.5.
- Alert/threshold monitoring and notification dispatch.
- Structured logging, metrics, and observability.
- CI/CD pipeline with unit/integration test separation.
- Database or persistent cache for user data and snapshots.
- Deployment configuration (Docker, process manager, environment secrets).

### What Must NOT Be Rewritten Unnecessarily
- U06.5 market-data architecture: provider priority, normalization, validation, reliability scoring, outlier filtering, ranking, indices.
- U07/U08 scenario matrices and 27+27 Persian narratives.
- U05 volume contract (`volume_base`, `PROVIDER_SUPPLIED`, `EACH_TRADE_COUNTED_ONCE`).
- Sub-daily warning logic and timeframe validation rules.
- Safety flag chain (`TRADING_ENABLED=False` etc.).
- Timestamp normalization to UTC ISO 8601.
- 5m honesty rules: no fabrication, no interpolation, no silent substitution.

### Whether the Project Is Better Described as an Analysis Engine/Framework
- **Yes**. The notebook specifies a professional, auditable, deterministic crypto market-analysis engine with strict data-quality gates, multi-provider reliability models, and locked narrative outputs.
- It is **not** a finished Telegram bot. The bot layer, user interface, scheduling, persistence, and operational infrastructure are entirely unspecified.
- The correct description is: **"a portable, provider-agnostic crypto market-analysis engine with scenario classification, relative-movement ranking, dynamic universe construction, and Persian narrative generation — analysis-only, trading-disabled, and designed to serve as the backend for a future Telegram bot."**

---

## 6. Final Three Sections

### WHAT WE ALREADY HAVE
- **U01–U09**: Complete analysis engine with data foundation, market data acquisition, quality gates, scenario analysis, relative movement, dynamic universe, and Persian narrative generation.
- **U06.5**: Robust multi-provider, multi-exchange market-data foundation with reliability-weighted pricing, outlier filtering, Top-125 ranking, and Kitchen indices.
- **Safety**: Hard-coded trading/order/strategy/portfolio locks across all units.
- **Validation**: Inline and synthetic tests covering core logic, edge cases, and data contracts.
- **Narratives**: 27 locked Persian scenarios in U07 and 27 in U08.
- **Message contract**: Strict 5-line U09 market participation message with 24h movements only.

### WHAT THE NOTEBOOK DOES NOT SPECIFY
- Telegram bot framework, commands, handlers, keyboards, or webhook/polling.
- User authentication, sessions, preferences, or admin controls.
- Scheduling, background jobs, or periodic refresh.
- Alerts, notifications, or signal generation.
- Portfolio tracking, trading execution, or risk management.
- Database, caching, structured logging, CI/CD, or deployment.
- Localization beyond hardcoded Persian.

### RECOMMENDED MIGRATION PLAN
1. **Phase 0 (P0)**: Extract U01–U09 core logic into `app/` package. Preserve U06.5 verbatim. Centralize safety flags, timestamps, scenario matrix, and narratives. Add pytest infrastructure.
2. **Phase 1 (P1)**: Replace Colab scaffolding with portable paths, config, logging, and error handling. Extract tests to `tests/`. Add CI/CD.
3. **Phase 2 (P2)**: Build Telegram bot layer with command handlers, message formatting, session management, and error-to-user mapping.
4. **Phase 3 (P3)**: Add database, caching, scheduling, alerts, charting, admin panel, and optional English localization.
