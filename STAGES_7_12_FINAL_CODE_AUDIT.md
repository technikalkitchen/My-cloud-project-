# STAGES 7-12 FINAL CODE AUDIT — Stage 13 Relevance

## 1. Runtime Path

### Entry Points
- **wsgi.py**: imports `app.api.app` -> `application = app` (Flask WSGI entry)
- **app/api/app.py**: `create_app()` creates Flask app; registered at module level as `app = create_app()`
- **Flask endpoints**: `/health`, `/`, `/bot/status`, `/bot/webhook` (POST)
- **app/bot/telegram.py**: `TelegramBot` class - Telegram polling/webhook handler
- **app/bot/runner.py**: `BotRunner` class - command handler, pipeline orchestrator

### Flask -> Telegram -> Stage Execution Path
1. HTTP request -> Flask `/bot/webhook` POST endpoint (app/api/app.py:231-253)
2. Webhook extracts `text` from JSON update, splits command
3. Calls `BotRunner.handle_command(command, args)` (app/bot/runner.py:39)
4. For `/top3`: `BotRunner._handle_top3()` (app/bot/runner.py:46)
5. `_handle_top3()` calls `run_top3()` (app/analysis/stage12_top3.py:534)
6. `run_top3()` -> `get_dynamic_top10()` (Stage 10) + `run_strong_movers()` (Stage 11) + `build_candidate_pool()` + `evaluate_candidate()` + `select_top3()` (Stage 12)
7. Returns `Top3Output` -> `format_top3_telegram()` (Stage 12 formatting)
8. For Telegram bot: `TelegramBot._cmd_top3()` (app/bot/telegram.py:45) -> `BotRunner.handle_command('/top3')` -> same pipeline
9. Response sent via `update.message.reply_text(response, parse_mode='HTML')`

### Dependency Chain
- Stage 12 depends on: Stage 10 (Dynamic Top 10), Stage 11 (Strong Movers), U06.5 ranking (dynamic_rank_assets)
- Stage 11 depends on: U06.5 ranking, Stage 10 contracts (Exchange, DISPLAY_FALLBACK_PRIORITY, ExchangeRouter)
- Stage 10 depends on: U06.5 ranking (dynamic_rank_assets)
- Stage 7 depends on: U06.5 adapter (validate_stage7_input), matrix, narratives, range engine
- Stage 8 depends on: U08 narratives, U08 scenario, U08 ranking, U08 context, U08 relative, U08 altcoin

## 2. Stage 7 Findings (U07 Scenario Engine)

### Runtime Entry/Function/Call Chain
- **Primary entry**: `run_u07()` (app/analysis/engine.py:54) — standalone engine entry
- **Integrated entry**: `run_stage7()` (app/analysis/engine.py:390) — full pipeline orchestrator
- **Dependencies**: `validate_stage7_input()` (input_contract.py), `calculate_stage7()` (calculations.py), `analyze_range()` (range_engine.py), `lookup_scenario()` (matrix.py), `select_narrative()` (narratives.py), `parse_timeframe()` (timeframe.py), `validate_user_range()` (validation.py), `validate_series()` (validation.py)

### Unit 7.1 — Input Contract
- **File**: `app/analysis/input_contract.py`
- **Function**: `validate_stage7_input(adapter, max_freshness_age_seconds=None)` -> `Stage7InputContract`
- **Validates**: 21 required adapter fields, SOURCE_CELL must be "U06.5", series must be non-empty/finite/positive, NO_DATA_FABRICATION must be True, HISTORY_STATUS must be VALIDATED or PARTIAL, FRESHNESS.status must be FRESH or UNAVAILABLE (STALE rejected), at least 2 history points
- **Runtime used**: Yes — called by `run_stage7()` at engine.py:408

### Unit 7.2 — Calculations
- **File**: `app/analysis/calculations.py`
- **Function**: `calculate_stage7(contract)` -> `Stage7Calculations`
- **Calculations**: total_net_change_pct, total_amplitude_pct, usdt_d_net_change_pct, usdt_d_net_change_pp (percentage-point vs percentage distinction), btc_d_net_change_pct, btc_d_net_change_pp, all extremes, all validations
- **Runtime used**: Yes — called by `run_stage7()` at engine.py:413 and `run_u07()` at engine.py:111-125

### Unit 7.3 — Scenario Matrix
- **File**: `app/analysis/matrix.py`
- **Constant**: `SCENARIO_MATRIX` — 9 entries keyed by (Direction, Direction) tuples
- **Mapping**: (INCREASE, DECREASE)->1 MIRROR, (DECREASE, INCREASE)->2 MIRROR, (INCREASE, INCREASE)->3 PARALLEL, (DECREASE, DECREASE)->4 PARALLEL, (INCREASE, RANGE)->5 RANGE-COMPATIBLE STATE, (DECREASE, RANGE)->6 RANGE-COMPATIBLE STATE, (RANGE, INCREASE)->7 RANGE-COMPATIBLE STATE, (RANGE, DECREASE)->8 RANGE-COMPATIBLE STATE, (RANGE, RANGE)->9 NEUTRAL_FLAT
- **Function**: `lookup_scenario(total_direction, usdt_direction)` — raises RuntimeError for unmapped pairs
- **Runtime used**: Yes — `run_u07()` at engine.py:156; `run_stage7()` at engine.py:451

### Unit 7.4 — Narratives
- **File**: `app/analysis/narratives.py`
- **Constant**: `NARRATIVES` — 9 scenarios x 3 patterns = 27 locked Persian narrative texts (exact text preserved)
- **Function**: `select_narrative(scenario_id, pattern_index)` — returns exact locked text, raises ValueError for invalid IDs
- **Pattern selection logic**: `pattern_index` must be 1, 2, or 3; `approved_patterns = NARRATIVES[scenario_id]`; `selected_pattern = approved_patterns[pattern_index - 1]`
- **Runtime used**: Yes — `run_u07()` at engine.py:180-186; `run_stage7()` at engine.py:456

### Unit 7.5 — Integrated Pipeline
- **Function**: `run_stage7(adapter, pattern_index, ...)` -> `ScenarioResult`
- **Pipeline**: validate_stage7_input -> calculate_stage7 -> derive OHLC -> analyze_range (x2) -> lookup_scenario -> select_narrative -> ScenarioResult
- **Runtime used**: Yes (definition exists; no evidence of direct invocation in runtime code outside tests)

### User-Facing Text (Stage 7)
- **NOT directly output to Telegram** — Stage 7 is an internal analysis engine, not directly wired to the Telegram bot pipeline. The `/top3` command path bypasses Stage 7 entirely (goes U06.5 -> Stage 10 -> Stage 11 -> Stage 12).
- **Scenario header labels**: `ScenarioType` enum values: "MIRROR", "PARALLEL", "RANGE-COMPATIBLE STATE", "NEUTRAL/FLAT" (app/analysis/enums.py:32-36)

### Key Constants
- `DEFAULT_RANGE_CONFIG` (config.py:50): direction_threshold_pct=0.50, flat_threshold_pct=0.10, low_volatility_pct=2.00, range_score_threshold=0.60, high_volatility_pct=5.00, dmi_period=14, adx_period=14, high_confidence_score=0.78, medium_confidence_score=0.62
- **Timeframe**: `parse_timeframe()` (timeframe.py:27) — validates format, assigns SUB_DAILY_WARNING for <1D

### Safety/No-Signal
- `audit["execution_locks"]` in `run_u07()`: trading=False, orders=False, strategy=False, portfolio_actions=False (engine.py:322-331)
- `validate_series()`: requires positive values only, rejects zero/negative

## 3. Stage 8 Findings (U08 Cell 8)

### Runtime Entry/Function/Call Chain
- **Primary entry**: `run_cell_08()` (app/analysis/u08_engine.py:26)
- **Dependencies**: `resolve_scenario()` (u08_scenario.py), `add_absolute_direction()` (u08_ranking.py), `enrich_relative_performance()` (u08_relative.py), `build_scenario_ranking()` (u08_altcoin.py), `get_narrative()` (u08_narratives.py), `classify_context()` (u08_context.py), `_normalize_direction()` (u08_normalize.py)

### Unit 8.1 — Scenario Resolution
- **File**: `app/analysis/u08_scenario.py`
- **Constant**: `SCENARIO_MATRIX` — 9 entries with different scenario_type strings than Stage 7 (e.g., "BTC_UP_BTC_D_UP", "BTC_UP_BTC_D_DOWN", etc.)
- **Function**: `lookup_scenario(btc_direction, btc_d_direction)` — raises RuntimeError for unmapped pairs
- **Function**: `resolve_scenario(btc_direction, btc_d_direction)` — normalizes aliases then looks up
- **Runtime used**: Yes — `run_cell_08()` at u08_engine.py:74

### Unit 8.2 — Context Classification
- **File**: `app/analysis/u08_context.py`
- **Function**: `classify_context(btc_direction, btc_d_direction)` -> `Context` enum
- **Logic**: BTC.INCREASE -> BULLISH, BTC.DECREASE -> BEARISH, else RANGE. BTC.D direction does NOT affect context.
- **Runtime used**: Yes — `build_scenario_ranking()` at u08_altcoin.py:121

### Unit 8.3 — Ranking
- **File**: `app/analysis/u08_ranking.py`
- **Functions**: `rank_top_assets()` (context-aware: BULLISH sorts by change desc then volume desc; BEARISH sorts ascending; RANGE sorts by abs(change) desc then volume desc), `rank_strong_movers()`, `rank_relative_movers()`, `add_absolute_direction()`, `is_opposite_direction()`
- **Runtime used**: Yes — via `build_scenario_ranking()` at u08_altcoin.py

### Unit 8.4 — Relative Performance
- **File**: `app/analysis/u08_relative.py`
- **Functions**: `calculate_relative_btc_performance()` (asset_change - btc_change), `classify_relative_performance()` (RELATIVE_STRENGTH/WEAKNESS/NEUTRAL with epsilon=0.0), `enrich_relative_performance()`
- **Runtime used**: Yes — `run_cell_08()` at u08_engine.py:84

### Unit 8.5 — Altcoin Structure
- **File**: `app/analysis/u08_altcoin.py`
- **Function**: `build_altcoin_structure_context()` — only enabled when BTC and BTC.D are in OPPOSITE directions; otherwise returns enabled=False
- **Functions**: `build_strong_movers()`, `build_relative_movers()`, `build_scenario_ranking()`, `volume_record()`, `ensure_volume_fields()`
- **Runtime used**: Yes — `run_cell_08()` at u08_engine.py:101

### Unit 8.6 — Narratives
- **File**: `app/analysis/u08_narratives.py`
- **Constant**: `NARRATIVES` — 9 scenarios x 3 patterns = 27 locked narratives, each as dict with "pattern", "title", "text" keys (different structure from Stage 7 narratives which are plain strings)
- **Function**: `get_narrative(scenario_id, pattern_index)` -> dict with pattern/title/text
- **Runtime used**: Yes — `run_cell_08()` at u08_engine.py:113

### User-Facing Text (Stage 8)
- **NOT directly output to Telegram** via the `/top3` command path. Stage 8 is used for Cell 8 analysis, not directly wired to the Telegram bot pipeline shown in runner.py.
- **Narrative titles**: Include emoji markers like "🟢 BTC Strength", "🔴 Altcoin Weakness", "🟡 BTC Weakness / Alt Relative Strength", "🟢 Broad Market Strength", etc.

### Safety Locks
- `audit` in `run_cell_08()`: trading_enabled=False, orders_enabled=False, strategy_enabled=False, portfolio_actions_enabled=False, scenarios_locked=True, narratives_locked=True, narrative_pattern_count=27, btc_is_benchmark=True (u08_engine.py:129-147)

### Key Data Structures
- `Cell08Result` (u08_result.py): frozen dataclass with engine, version, timestamp_utc, scenario_id, scenario_type, btc_direction, btc_d_direction, context, opposite_direction, selected_pattern (dict with pattern/title/text), top_10_assets, strong_movers, relative_movers, altcoin_structure, audit
- `CELL08_CONFIG` (u08_config.py): top_n=10, strong_movers_n=10, relative_movers_n=10, min_valid_price_change_pct=0.0, relative_strength_epsilon_pct=0.0, require_finite_values=True, include_btc_in_top_assets=True, include_btc_in_strong_movers=True, volume_required=True

## 4. Stage 10 Findings (Dynamic Top 10 + Pairs)

### Runtime Entry/Function/Call Chain
- **Primary entry**: `get_dynamic_top10()` (app/analysis/stage10_consumer.py:118)
- **Pair processing**: `UsdtPairProcessor.process()` (stage10_usdt.py:74), `BtcPairProcessor.process()` (stage10_btc.py:73)
- **Telegram formatting**: `format_top10_telegram()` (stage10_telegram.py:168) — NOT called in `/top3` path but available
- **Exchange routing**: `ExchangeRouter` (stage10_router.py:40)
- **Runtime used by /top3**: Indirectly via `run_top3()` at stage12_top3.py:561 which calls `get_dynamic_top10()`

### Unit 10.1 — Exchange + Fallback Priority
- **File**: `app/analysis/stage10_consumer.py`
- **Exchange enum** (lines 26-34): BINANCE="Binance", OKX="OKX", BYBIT="Bybit", KUCOIN="KuCoin", COINBASE="Coinbase", GATE="Gate", UPUB="Upbit", BITGET="Bitget"
- **DISPLAY_FALLBACK_PRIORITY** (lines 37-46): [BINANCE, OKX, BYBIT, KUCOIN, COINBASE, GATE, UPBIT, BITGET] — 8 exchanges in priority order
- **View enum**: KITCHEN, EXCHANGE
- **Runtime used**: Yes — all stages consume this

### Unit 10.2 — Exchange Router
- **File**: `app/analysis/stage10_router.py`
- **Class**: `ExchangeRouter` — routes through Display Fallback Priority chain
- **Key methods**: `get_fallback_chain()` (selected -> highest priority only, NEVER lower), `is_higher_priority()`, `validate_fallback_direction()`, `route()`, `route_with_provenance()`
- **Validation**: Selected exchange MUST be in DISPLAY_FALLBACK_PRIORITY; raises ValueError otherwise
- **Runtime used**: Yes — UsdtPairProcessor, BtcPairProcessor, Stage 11/12 exchange validation

### Unit 10.3 — USDT Pair + Volume
- **File**: `app/analysis/stage10_usdt.py`
- **Class**: `UsdtPairProcessor`
- **Method**: `process(data)` -> `UsdtPairResult`
- **Validation**: symbol must end with "USDT", change_pct must be finite, volume must be non-negative finite (VALID_VOLUME_SOURCE = "PROVIDER_SUPPLIED_TRADED_BASE_VOLUME"), timestamp freshness (FRESHNESS_THRESHOLD_SECONDS = 15*60 = 900s), timeframe match
- **Source/Fallback labels**: `_source_label(requested, actual)` -> "Source: {requested}" or "Fallback from: {actual}"
- **Provenance**: Per-field provenance dict tracking which exchange validated each field
- **Freshness check**: `_is_fresh(timestamp)` — age <= FRESHNESS_THRESHOLD_SECONDS
- **Runtime used**: Yes — `run_top3()` at stage12_top3.py:586-608; also called in BotRunner._collect_pair_data() at runner.py:117

### Unit 10.4 — BTC Pair + Fallback Cohesion
- **File**: `app/analysis/stage10_btc.py`
- **Class**: `BtcPairProcessor`
- **Method**: `process(btc_data, usdt_result, allow_kitchen_calculation, kitchen_btc_value)` -> `BtcPairResult`
- **Fake-pair prevention**: `_is_valid_btc_pair(symbol)` — must end with "BTC", prefix non-empty, not "BTC" alone, alphabetic only (blocks "FAKEBTC", "BTCBTC", "BTC")
- **Fallback cohesion**: Prefers USDT fallback exchange when valid (usdt_fallback_exchange from USDT result)
- **Kitchen BTC calculation**: Only when `allow_kitchen_calculation=True` and `kitchen_btc_value` provided and all USDT errors present
- **Unavailable state**: `_unavailable_result(reason)` — explicit unavailable when no data
- **Runtime used**: Yes — `run_top3()` at stage12_top3.py:590-624; BotRunner._collect_pair_data() at runner.py:127

### Unit 10.5 — Telegram Output
- **File**: `app/analysis/stage10_telegram.py`
- **Class**: `TelegramFormatter` with `format_top10()`
- **Display order**: Asset -> USDT pair + movement -> USDT volume -> Source/Fallback -> BTC pair + movement -> Source/Fallback
- **Volume**: Only for USDT pair, NEVER for BTC
- **Labels**: TOP10_HEADER = "🏆 TOP 10 MARKET CAP", VOLUME_LABEL = "Volume:", SOURCE_LABEL = "Source", FALLBACK_LABEL = "Fallback from"
- **RTL protection**: `RTL_PROTECT_START = "‏"`, `RTL_PROTECT_END = "‏"` (defined but `check_rtl_safety()` always returns True — non-functional check)
- **Runtime used**: NOT in /top3 path; available but not called by runner.py or telegram.py

### User-Facing Text (Stage 10)
- `TOP10_HEADER`: "🏆 TOP 10 MARKET CAP" (stage10_telegram.py:30)
- `VOLUME_LABEL`: "Volume:" (stage10_telegram.py:31)
- `SOURCE_LABEL`: "Source" (stage10_telegram.py:32)
- `FALLBACK_LABEL`: "Fallback from" (stage10_telegram.py:33)

## 5. Stage 11 Findings (Strong Movers)

### Runtime Entry/Function/Call Chain
- **Primary entry**: `run_strong_movers()` (app/analysis/stage11_strong_movers.py:534)
- **Called by**: `run_top3()` at stage12_top3.py:569
- **Dependencies**: dynamic_rank_assets (ranking.py), Exchange, DISPLAY_FALLBACK_PRIORITY, ExchangeRouter (stage10_consumer.py/stage10_router.py), UsdtPairResult (stage10_usdt.py), BtcPairResult (stage10_btc.py)

### Unit 11.1 — Candidate Universe
- **Function**: `build_candidate_universe(valid_assets)` -> list of assets in ranks 11-125, excluding BTC rank 1
- **Logic**: Uses `dynamic_rank_assets()` on every call (no caching); filters 11 <= rank <= 125
- **Runtime used**: Yes — `run_strong_movers()` at stage11_strong_movers.py:557-566

### Unit 11.2 — Movement + Reliability Evaluation
- **Functions**: `_movement_score(change_pct, volume)` — abs(change) * (0.5 + 0.5 * min(volume/100M, 1.0)); `_reliability_score()` — usdt_valid: +4 or +1, btc_available+btc_valid: +2 or +0.5, volume tiers: >=1B +2, >=100M +1.5, >=10M +1, >=1M +0.5, change_pct present: +1
- **Function**: `evaluate_candidate(kitchen_rank, symbol, usdt_result, btc_result)` -> `StrongMoverCandidate`
- **Function**: `select_strong_movers(candidates, top_n=5)` — selects by total_score where valid = usdt_valid or btc_available
- **Runtime used**: Yes — `run_strong_movers()` at stage11_strong_movers.py:597-607

### Unit 11.3 — Exchange Selection + Fallback
- **Functions**: `get_fallback_chain(selected_exchange)` -> list, `is_higher_priority(a, b)`, `validate_fallback_direction(requested, actual)`, `route_exchange(selected_exchange, validator_fn)`
- **All reuse Stage 10 ExchangeRouter** — no duplicated logic
- **Runtime used**: Yes

### Unit 11.4 — Five Strong Movers Output
- **Function**: `build_strong_mover_result(candidate, timeframe)` -> `StrongMoverResult`
- **Function**: `format_strong_movers_telegram(output)` -> str
- **Volume label**: `_format_volume(volume)` — T/B/M/K USDT formatting (same logic as stage10_telegram.py and stage12_top3.py)
- **Source label**: `_format_source_label(actual_exchange, fallback_used, fallback_exchange)` -> "Source: {exchange}" / "Fallback from: {exchange}" / "Source"
- **Runtime used**: Available; NOT called in /top3 path (Stage 12 uses its own format_top3_telegram)

### User-Facing Text (Stage 11)
- `STRONG_MOVERS_HEADER`: "🏆 5 STRONG MOVERS" (stage11_strong_movers.py:46)
- `SCANNER_WARNING`: Full Persian warning text (stage11_strong_movers.py:36-43):
  "⚠️ توجه: اطلاعات و انتخاب‌های ارائه‌شده توسط Scanner به‌هیچ‌وجه سیگنال ورود یا خروج از معامله نیستند و نباید به‌تنهایی مبنای تصمیم معاملاتی قرار گیرند. هدف Scanner، صرفه‌جویی در زمان و مشخص‌کردن دارایی‌های برتر، جریان حرکت سرمایه و جهت کلی بازار است تا بتوانید روی گزینه‌هایی که ارزش بررسی بیشتری دارند تمرکز کنید. تصمیم نهایی برای معامله، از جمله تشخیص Setup، Entry و Trigger، بر عهده خود شماست."

### Data Structures
- `StrongMoverCandidate`, `StrongMoverResult`, `StrongMoversOutput`, `StrongMoversConfig` (stage11_strong_movers.py)

## 6. Stage 12 Findings (Top 3 Reliable Movers)

### Runtime Entry/Function/Call Chain
- **Primary entry**: `run_top3(valid_assets, config, usdt_results, btc_results)` (app/analysis/stage12_top3.py:534)
- **Called by**: `BotRunner._handle_top3()` (app/bot/runner.py:49) — THE ONLY runtime invocation path
- **Telegram**: `format_top3_telegram(output)` (stage12_top3.py:482) — formats for Telegram output
- **Dependencies**: stage10_consumer (get_dynamic_top10, Exchange, DISPLAY_FALLBACK_PRIORITY), stage10_router (ExchangeRouter), stage10_usdt (UsdtPairResult), stage10_btc (BtcPairResult), stage11_strong_movers (run_strong_movers, StrongMoversConfig, SCANNER_WARNING), ranking (dynamic_rank_assets)

### Unit 12.1 — Candidate Pool
- **Function**: `build_candidate_pool(top10_assets, strong_movers, valid_assets)` -> list of `Top3Candidate`
- **Deduplication**: By canonical_asset_id; Top10 entries take priority over Strong Movers
- **Initial state**: All fields null/empty, valid=False; scored later by evaluate_candidate
- **Runtime used**: Yes — `run_top3()` at stage12_top3.py:576

### Unit 12.2 — Movement + Reliability Evaluation
- **Functions**: `_top3_movement_score(change_pct, volume)`, `_top3_reliability_score(usdt_valid, btc_available, btc_valid, usdt_volume, change_pct)`, `evaluate_candidate(candidate)` -> `Top3Candidate`, `select_top3(candidates, top_n=3)` -> list
- **Scoring**: Same formulas as Stage 11 (reused). Movement: abs(change) * (0.5 + 0.5 * min(vol/100M, 1.0)). Reliability: usdt_valid +4/+1, btc_available+btc_valid +2/+0.5, volume tiers, change_pct +1
- **Validity**: Top3Candidate.valid = usdt_valid or btc_available (vs Stage 11: usdt_valid or btc_available)
- **Runtime used**: Yes — `run_top3()` at stage12_top3.py:660-665

### Unit 12.3 — Exchange Continuity
- **Function**: `validate_exchange_continuity(selected_exchange, candidate_exchange)` -> (bool, str)
- **Logic**: Same exchange as selected OR higher-priority fallback allowed; reuses ExchangeRouter.validate_fallback_direction
- **Runtime used**: DEFINED but NOT called in any runtime code path found. Listed in code but no evidence of invocation.

### Unit 12.4 — Telegram Output
- **Function**: `format_top3_telegram(output)` -> str
- **Header**: `TOP3_HEADER = "🏆 TOP 3 RELIABLE MOVERS"` (stage12_top3.py:142)
- **Scanner warning**: `TOP3_SCANNER_WARNING = SCANNER_WARNING` (reuses Stage 11 warning, stage12_top3.py:143)
- **Format per result**:
  ```
  {position}. {symbol}
  
      {sign}{change:.2f}%
      {usdt_pair}
      Volume: {formatted_volume}  (if volume available)
      {usdt_source}
  
      {sign}{btc_change:.2f}%  (if btc_available)
      {btc_pair}
      {btc_source}  (if btc_available)
  ```
- **Volume formatting**: `_format_volume_top3(volume)` — T/B/M/K USDT (same as Stage 11)
- **BTC source label**: `_btc_source_label(actual_exchange, fallback_used, fallback_exchange)` -> "Fallback from: {ex}" / "Source: {ex}" / ""
- **Runtime used**: YES — called by BotRunner._handle_top3() at runner.py:55

### Unit 12.5 — Full Integration Orchestrator
- **Function**: `run_top3(valid_assets, config, usdt_results, btc_results)` -> `Top3Output`
- **Pipeline**:
  1. `dynamic_rank_assets(valid_assets)` -> ranking, ranking_version
  2. `get_dynamic_top10(valid_assets)` -> top10_assets (Stage 10)
  3. `run_strong_movers(valid_assets, config=StrongMoversConfig(top_n=5), usdt_results, btc_results)` -> strong_output (Stage 11)
  4. `build_candidate_pool(top10_assets, strong_movers, valid_assets)` -> candidate pool
  5. For each candidate: merge usdt_result, btc_result -> evaluate_candidate -> scored
  6. `select_top3(evaluated, top_n=3)` -> selected
  7. `build_top3_result(candidate, position, timeframe)` -> Top3Result for each
  8. `Top3Output(selected_exchange, display_fallback_priority, timeframe, ranking_version, top3, candidate_count, selected_count, scanner_warning, valid, errors)`
- **Exchange names**: `[e.value for e in DISPLAY_FALLBACK_PRIORITY]` = ["Binance", "OKX", "Bybit", "KuCoin", "Coinbase", "Gate", "Upbit", "Bitget"]
- **Runtime used**: YES — the main entry for /top3 command

### User-Facing Text (Stage 12)
- `TOP3_HEADER`: "🏆 TOP 3 RELIABLE MOVERS" (stage12_top3.py:142)
- `TOP3_SCANNER_WARNING`: Same as Stage 11 SCANNER_WARNING (full Persian text)
- Warning text exact: "⚠️ توجه: اطلاعات و انتخاب‌های ارائه‌شده توسط Scanner به‌هیچ‌وجه سیگنال ورود یا خروج از معامله نیستند و نباید به‌تنهایی مبنای تصمیم معاملاتی قرار گیرند. هدف Scanner، صرفه‌جویی در زمان و مشخص‌کردن دارایی‌های برتر، جریان حرکت سرمایه و جهت کلی بازار است تا بتوانید روی گزینه‌هایی که ارزش بررسی بیشتری دارند تمرکز کنید. تصمیم نهایی برای معامله، از جمله تشخیص Setup، Entry و Trigger، بر عهده خود شماست."

### Key Constants
- `STAGE12_HEADER`: "TOP 3 RELIABLE MOVERS" (stage12_top3.py:44)
- `DEFAULT_TIMEFRAME`: "5m" (stage12_top3.py:45)
- `TOP_N`: 3 (stage12_top3.py:46)
- `Top3Config`: selected_exchange=None, timeframe="5m", top_n=3 (stage12_top3.py:130-136)

## 7. Cross-Stage Findings

### Shared Logic (Reused, Not Duplicated)
1. **ExchangeRouter** (`stage10_router.py`): Used by Stage 10, Stage 11 (via import), Stage 12 (via import). Single implementation.
2. **DISPLAY_FALLBACK_PRIORITY** (`stage10_consumer.py`): Imported by Stage 11, Stage 12. Single definition.
3. **Exchange enum** (`stage10_consumer.py`): Imported by Stage 11, Stage 12.
4. **dynamic_rank_assets** (`ranking.py`): Used by Stage 10, Stage 11, Stage 12, and U06.5 finalization.
5. **Movement/reliability scoring formulas**: Stage 11 and Stage 12 use IDENTICAL formulas (`_movement_score` = `_top3_movement_score`, `_reliability_score` = `_top3_reliability_score`) — implemented separately in each module but with identical logic (not DRY, but not duplicated in a way that causes inconsistency).
6. **SCANNER_WARNING**: Stage 11 defines it; Stage 12 imports it (`TOP3_SCANNER_WARNING = SCANNER_WARNING` at stage12_top3.py:143).
7. **Volume formatting**: Stage 10 (`TelegramFormatter._format_volume`), Stage 11 (`_format_volume`), Stage 12 (`_format_volume_top3`) — all use identical T/B/M/K logic but implemented separately.
8. **Source/Fallback labeling pattern**: `Source: {exchange}` / `Fallback from: {exchange}` pattern used in Stage 10, Stage 11, Stage 12.
9. **Safety locks**: All stages have trading=False, orders=False, strategy=False, portfolio_actions=False in audit/execution locks.
10. **FRESHNESS_THRESHOLD_SECONDS = 900** (quality.py:43): Used by Stage 10 USDT freshness check, Stage 10 BTC freshness check, U06.5 global providers.

### Dependencies Between Stages
- Stage 12 -> Stage 11 (imports run_strong_movers, StrongMoversConfig, SCANNER_WARNING)
- Stage 12 -> Stage 10 (imports get_dynamic_top10, Exchange, DISPLAY_FALLBACK_PRIORITY, UsdtPairResult, BtcPairResult)
- Stage 11 -> Stage 10 (imports Exchange, DISPLAY_FALLBACK_PRIORITY, ExchangeRouter, UsdtPairResult, BtcPairResult)
- Stage 10 -> U06.5 ranking (imports dynamic_rank_assets from market.ranking)
- Stage 7 -> U06.5 (imports validate_stage7_input from input_contract; depends on U06.5 adapter)
- Stage 8 -> U08 components (internal to Stage 8, no external stage dependency)

### NOT in Telegram Bot Pipeline
- Stage 7 (U07) — NOT reachable via /top3 command; is a separate analysis engine
- Stage 8 (U08) — NOT reachable via /top3 command; is a separate analysis engine
- Stage 10 Telegram formatter (format_top10_telegram) — available but NOT called by /top3 path
- Stage 11 Telegram formatter (format_strong_movers_telegram) — available but NOT called by /top3 path

### Flask → Telegram → Stage Flow for /top3
Flask webhook (app/api/app.py:231-253) OR Telegram Bot (app/bot/telegram.py:45)
  -> BotRunner.handle_command("/top3") (app/bot/runner.py:40-41)
    -> BotRunner._handle_top3() (app/bot/runner.py:46)
      -> _collect_ranking_data() (CoinGecko API, runner.py:57) — fetches top 125 coins
      -> _collect_pair_data() (runner.py:94) — processes USDT/BTC pairs from local candle data
      -> run_top3(assets, config, usdt_results, btc_results) (stage12_top3.py:534)
        -> dynamic_rank_assets(valid_assets) (ranking.py)
        -> get_dynamic_top10(valid_assets) (stage10_consumer.py)
        -> run_strong_movers(valid_assets, config, usdt_results, btc_results) (stage11_strong_movers.py)
        -> build_candidate_pool() (stage12_top3.py)
        -> evaluate_candidate() x N (stage12_top3.py)
        -> select_top3() (stage12_top3.py)
        -> build_top3_result() x N (stage12_top3.py)
        -> Top3Output (stage12_top3.py)
      -> format_top3_telegram(output) (stage12_top3.py)
    -> Returns string to Telegram

## 8. Exact User-Facing Text Inventory

### HELP Text (Bot config)
- **Location**: `app/bot/config.py:11-18` and `app/bot/runner.py:21-28` (duplicate constant)
- **Text**: "KITCHEN ROBOT — Scanner Bot

Commands:
/top3 — Run Scanner: U06.5 → Top 10 → Strong Movers → Top 3
/help — Show this help message

⚠️ توجه: اطلاعات و انتخاب‌های ارائه‌شده توسط Scanner به‌هیچ‌وجه سیگنال ورود یا خروج از معامله نیستند."
- **WARNING**: "⚠️ توجه: اطلاعات و انتخاب‌های ارائه‌شده توسط Scanner به‌هیچ‌وجه سیگنال ورود یا خروج از معامله نیستند."

### Stage 12 Telegram Output
- Header: "🏆 TOP 3 RELIABLE MOVERS" (stage12_top3.py:142)
- Scanner warning: Full Persian text (same as HELP warning but longer, stage11_strong_movers.py:36-43)
- Per result: "{position}. {symbol}", "{sign}{change:.2f}%", "{usdt_pair}", "Volume: {formatted}", "{usdt_source}", BTC section only if btc_available
- Unknown command: "Unknown command: {command}
Use /help for available commands." (runner.py:44)

### Stage 10 Telegram Output (not in /top3 path)
- Header: "🏆 TOP 10 MARKET CAP" (stage10_telegram.py:30)
- Labels: "Volume:" (stage10_telegram.py:31), "Source" (stage10_telegram.py:32), "Fallback from" (stage10_telegram.py:33)

### Stage 11 Telegram Output (not in /top3 path)
- Header: "🏆 5 STRONG MOVERS" (stage11_strong_movers.py:46)
- Scanner warning: Same as Stage 12 warning

### Sub-Daily Warning (API)
- **Location**: `app/api/app.py:27-32` — SUB_DAILY_WARNING constant
- **Text**: "⚠️ WARNING: The selected timeframe/range is below daily (D1). Sub-daily data may contain higher noise and lower structural reliability. Structural market interpretation should be treated with caution and confirmed with daily (D1) or higher data."

### Error/Validation Text (API)
- "no text" (app.py:240), "INVALID_TIMEFRAME_TYPE", "SUB_DAILY_TIMEFRAME", "DAILY_OR_HIGHER", "CUSTOM_RANGE_ENDPOINTS_REQUIRED", "INVALID_CUSTOM_RANGE_FORMAT", "INVALID_CUSTOM_RANGE_ORDER", "SUB_DAILY_CUSTOM_RANGE", "DAILY_OR_HIGHER_CUSTOM_RANGE", "UNSUPPORTED_TIMEFRAME"


## 9. Commands/Buttons/Callbacks/Navigation Inventory

### Commands
| Command | Handler | File | Line |
|---------|---------|------|------|
| /top3 | BotRunner._handle_top3() | app/bot/runner.py | 46 |
| /help | BotRunner._handle_help() (returns HELP_TEXT) | app/bot/runner.py | 44 |
| /top3 | TelegramBot._cmd_top3() | app/bot/telegram.py | 45 |
| /help | TelegramBot._cmd_help() | app/bot/telegram.py | 51 |

### Telegram Bot
- **CommandHandler registrations**: `CommandHandler("top3", self._cmd_top3)`, `CommandHandler("help", self._cmd_help)` (telegram.py:41-42)
- **No inline keyboard buttons** found anywhere in the runtime code
- **No callback_query handlers** found
- **No navigation** (no Start/Back/reset buttons)
- **run_polling()**: app.run_polling() (telegram.py:58)
- **run_once()**: Initialize -> Start -> StartPolling -> Sleep(1) -> Stop -> Shutdown (telegram.py:60-67)

### Flask Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /health | GET | Health check (status, project, version, execution_unit) |
| / | GET | Root (service, version, status) |
| /bot/status | GET | Bot config status (configured, status) |
| /bot/webhook | POST | Telegram webhook → BotRunner.handle_command() |

### Webhook Flow
- POST /bot/webhook extracts JSON update, reads message.text, chat_id
- Routes to BotRunner.handle_command(command, args)
- Returns JSON: {"ok": True, "chat_id": chat_id, "response": response}

## 10. Errors/Validation/Retry Inventory

### Stage 7 Errors
- `TECHNICAL_VALIDATION_ERROR`: Unsupported or malformed timeframe (engine.py:88-91)
- `MISSING_REQUIRED_FIELD`: Input contract field missing (input_contract.py:112)
- `SOURCE_CELL must be U06.5`: Wrong source (input_contract.py:143)
- `TOTAL_SERIES must be a non-empty list of finite positive values.` and similar for other series
- `HISTORY_POINTS must contain at least 2 observations.` (input_contract.py:190)
- `NO_DATA_FABRICATION must be True.` (input_contract.py:195)
- `HISTORY_STATUS must be VALIDATED or PARTIAL` (input_contract.py:200)
- `FRESHNESS.status must be FRESH or UNAVAILABLE` (input_contract.py:210)
- `CALCULATION_VALIDATION_FAILED`: Series validation errors (calculations.py:147)
- `No canonical U07 scenario mapping exists for this pair.` (engine.py:158)
- `pattern_index must be 1, 2, or 3.` (engine.py:176)

### Stage 10 Errors
- USDT: Invalid symbol, missing/invalid change_pct, missing/invalid/negative volume, wrong volume_source, stale timestamp, missing timeframe, invalid fallback direction, zero volume (stage10_usdt.py:127-182)
- BTC: Invalid pair symbol (fake-pair prevention), missing/invalid change_pct, missing/stale timestamp, missing timeframe, invalid fallback direction (stage10_btc.py:146-173)

### Stage 11 Errors
- "No candidate assets from U06.5 Dynamic Top-125" (stage11_strong_movers.py:579)

### Stage 12 Errors
- errors list in Top3Output (default empty, never populated in run_top3)

### Retry Behavior
- **No retry logic** in BotRunner — single attempt only
- **No retry logic** in format_top3_telegram — pure formatting
- API app.py: no retry on /bot/webhook — single attempt
- FRESHNESS_THRESHOLD_SECONDS = 900 (15 minutes) — staleness threshold, not retry
- HTTP_TIMEOUT_SECONDS = 20 (quality.py:43) — for CoinGecko in runner.py

### Validation Rules Summary
- All series must be non-empty, finite, positive (Stage 7)
- All exchange names must be in DISPLAY_FALLBACK_PRIORITY
- Fallback must go toward HIGHER priority only
- Volume must be PROVIDER_SUPPLIED_TRADED_BASE_VOLUME
- Timestamps must be within 15 minutes of now
- BTC pair must end with "BTC" and have valid prefix
- NO_DATA_FABRICATION must be True

## 11. Scenario/Matrix/Pattern/Narrative Inventory

### Stage 7 Matrix
- **File**: `app/analysis/matrix.py`
- **9 scenarios**: (INCREASE,DECREASE)->1 MIRROR, (DECREASE,INCREASE)->2 MIRROR, (INCREASE,INCREASE)->3 PARALLEL, (DECREASE,DECREASE)->4 PARALLEL, (INCREASE,RANGE)->5, (DECREASE,RANGE)->6, (RANGE,INCREASE)->7, (RANGE,DECREASE)->8, (RANGE,RANGE)->9 NEUTRAL_FLAT
- **Runtime used**: Yes, by run_u07() and run_stage7()

### Stage 7 Narratives
- **File**: `app/analysis/narratives.py`
- **27 patterns**: 9 scenarios x 3 patterns, exact Persian text (locked)
- **Selection**: `select_narrative(scenario_id, pattern_index)` — pattern_index must be 1, 2, or 3; `selected_pattern = approved_patterns[pattern_index - 1]`
- **Runtime used**: Yes, by run_u07() and run_stage7()

### Stage 8 Matrix
- **File**: `app/analysis/u08_scenario.py`
- **9 scenarios**: Different IDs than Stage 7 for same pairs (both map 1-9 but scenario_type strings differ)
- **Runtime used**: Yes, by run_cell_08()

### Stage 8 Narratives
- **File**: `app/analysis/u08_narratives.py`
- **27 patterns**: 9 scenarios x 3 patterns, each with pattern/title/text dict keys
- **Runtime used**: Yes, by run_cell_08()

### Pattern Selection Logic
- Stage 7: pattern_index in (1,2,3) validated; RuntimeError for invalid; select_narrative returns NARRATIVES[scenario_id][pattern_index - 1]
- Stage 8: Same pattern_index validation; get_narrative returns dict {pattern, title, text}

## 12. Memory/History/Anti-Repetition

### No Persistent Memory
- **No conversation memory** in BotRunner — stateless, no session tracking
- **No anti-repetition** mechanism — each /top3 call runs full pipeline independently
- **No caching** in Stage 12 — run_top3() recomputes everything on each call
- **No caching** in Stage 10 — get_dynamic_top10() calls dynamic_rank_assets() on every call (explicitly documented: "No persistent cache")
- **No caching** in Stage 11 — run_strong_movers() rebuilds on every call

### Snapshot/Historical Data
- **AUTO_PERSIST_SNAPSHOT = False** (quality.py:155) — no automatic persistence
- **Historical candle data**: BotRunner reads from `data/historical_u05/raw/*_1m.json` (runner.py:99-104)
- **No history of previous /top3 outputs** stored or referenced

### Safety Features
- No signal language (anywhere in output)
- No entry/exit/long/short/trading language (Stage 7-12 all have execution_locks)
- No fabrication (NO_DATA_FABRICATION=True enforced in Stage 7 input contract)
- No fake BTC pairs (stage10_btc.py:225-242 validation)
- No BTC volume in outputs (Cell 8 volume law: USDT pair only)
- No fallback to lower-priority exchanges (ExchangeRouter)

## 13. Stage 13 Relevant Facts

### What Stage 13 Would Need from Stages 7-12
1. **Stage 12 output format**: Top3Output with Top3Result list — fully implemented and RUNTIME USED via /top3 command
2. **Stage 12 scoring**: Movement + Reliability scoring — fully implemented
3. **Stage 12 exchange continuity**: `validate_exchange_continuity()` — IMPLEMENTED but RUNTIME USE NOT CONFIRMED (defined in stage12_top3.py:407 but never called)
4. **Stage 11 output**: StrongMoversOutput with StrongMoverResult — fully implemented and RUNTIME USED via run_top3()
5. **Stage 10 pairs**: UsdtPairResult, BtcPairResult — fully implemented and RUNTIME USED
6. **Stage 7-8 analysis engines**: Fully implemented but NOT connected to Telegram bot pipeline

### Critical Findings for Stage 13
- **Only /top3 command is wired** to the Telegram bot. No other stage commands exist.
- **Stage 12 is the final stage** in the /top3 pipeline — it IS the operational output stage.
- **No buttons/keyboards** exist in the bot — only command-based interaction.
- **No state management** — every /top3 is independent.
- **No persistence** of results — AUTO_PERSIST_SNAPSHOT=False, no output storage.
- **Single exchange hardcoded** in runner.py: `selected_exchange="Binance"` in _handle_top3() line 51.
- **BotRunner._collect_ranking_data()** uses CoinGecko public API directly (not U06.5 providers).
- **BotRunner._collect_pair_data()** reads from local `data/historical_u05/raw/` candle files, NOT from exchange API.
- **USDT and BTC pair processors** are called per-candle-symbol in BotRunner (lines 106-134).

## 14. NOT FOUND IN FINAL CODE

### Telegram Bot Infrastructure
- **No inline keyboard buttons** (ReplyKeyboardMarkup, InlineKeyboardMarkup) in any runtime code
- **No ConversationHandler or callback_query handlers** — bot is purely command-based
- **No /start command handler** — only /top3 and /help exist
- **No message handler** for non-command text (text without /) except webhook in Flask which routes to handle_command
- **No callback_data pattern** anywhere in runtime code
- **No Back/Start/reset navigation** — no states, no conversation tracking
- **No button-based navigation** at all

### Stage 7 (U07) Bot Integration
- **No /u07 or /scenario command** in BotRunner
- **No direct Stage 7 output to Telegram** — Stage 7 is not wired to the bot
- **No run_u07() call** found in runner.py, telegram.py, or app.py
- **No run_stage7() call** found in runner.py, telegram.py, or app.py
- **Stage 7 ScenarioResult/Dataclass** not referenced outside analysis module

### Stage 8 (U08) Bot Integration
- **No /cell8 or /u08 command** in BotRunner
- **No direct Cell 8 output to Telegram** — Stage 8 not wired to the bot
- **No run_cell_08() call** found in runner.py, telegram.py, or app.py

### Exchange Data Fetching
- **ExchangeRouter.route()** with live exchange probing — NOT in runtime; only validate_fallback_direction is called
- **Multi-exchange evidence acquisition** (exchange_evidence.py) — NOT called in /top3 path
- **BotRunner does NOT use** app.market.providers or app.market.exchange_evidence for data collection
- **BotRunner uses CoinGecko API directly** (runner.py:58) not the U06.5 provider stack

### Data Sources
- **No CMC (CoinMarketCap) API usage** in BotRunner (uses CoinGecko)
- **No U06.5 foundation** build in BotRunner path — uses raw CoinGecko data + local candle files
- **No dynamic_rank_assets** call in BotRunner (uses CoinGecko market_cap_rank directly)
- **No exchange_evidence.py** usage in /top3 path

### Persistence
- **No snapshot persistence** — AUTO_PERSIST_SNAPSHOT=False, no /top3 output saved
- **No database** — no SQLAlchemy, no ORM, no persistent storage of any kind
- **No result history** — each /top3 call is independent

### Retry/Resilience
- **No retry mechanism** in BotRunner._handle_top3() — single attempt
- **No timeout handling** in BotRunner — requests.get(timeout=20) is the only protection
- **No circuit breaker** in BotRunner
- **No fallback exchange selection** in BotRunner — always uses Binance
- **No error recovery** — if CoinGecko API fails, the command errors out

### Stage 12 Specific
- **validate_exchange_continuity()** — defined at stage12_top3.py:407 but NEVER called anywhere in runtime code
- **Top3Config.selected_exchange** — always "Binance" in runner.py; config is not user-selectable
- **prepare_for_top3()** from Stage 11 (stage11_strong_movers.py:486) — DEFINED but NOT called by Stage 12; Stage 12 has its own integration logic
- **format_strong_movers_telegram()** (stage11_strong_movers.py:441) — DEFINED but NOT called in /top3 path
- **format_top10_telegram()** (stage10_telegram.py:168) — DEFINED but NOT called in /top3 path
- **TelegramFormatter.check_rtl_safety()** — ALWAYS returns True (non-functional check at stage10_telegram.py:158-165)
- **Stage 10/11 Telegram formatters** — NOT wired to /top3 output

### Stage 8/9 Specific
- **No u08_regression gate** invoked in runtime (only test code)
- **No u09 engine** invoked in /top3 path (market/universe.py is separate)

## 15. Files Reviewed

### Core Runtime (Definitive)
| File | Stage | Role |
|------|-------|------|
| wsgi.py | All | WSGI entry point |
| app/__init__.py | All | Empty |
| app/api/app.py | All | Flask app, /bot/webhook endpoint |
| app/api/__init__.py | All | Empty |
| app/bot/telegram.py | All | Telegram bot, command handlers |
| app/bot/runner.py | 10-12 | BotRunner, /top3 pipeline |
| app/bot/__init__.py | All | Empty |
| app/bot/config.py | All | BOT_TOKEN, HELP_TEXT, command constants |
| app/analysis/__init__.py | 7 | Module docstring |
| app/analysis/engine.py | 7 | run_u07, run_stage7 |
| app/analysis/stage12_top3.py | 12 | run_top3, format_top3_telegram |
| app/analysis/stage11_strong_movers.py | 11 | run_strong_movers, format_strong_movers_telegram |
| app/analysis/stage10_consumer.py | 10 | get_dynamic_top10, Exchange, DISPLAY_FALLBACK_PRIORITY |
| app/analysis/stage10_router.py | 10 | ExchangeRouter |
| app/analysis/stage10_usdt.py | 10 | UsdtPairProcessor, UsdtPairResult |
| app/analysis/stage10_btc.py | 10 | BtcPairProcessor, BtcPairResult |
| app/analysis/stage10_telegram.py | 10 | format_top10_telegram (not in /top3 path) |
| app/analysis/matrix.py | 7 | SCENARIO_MATRIX |
| app/analysis/narratives.py | 7 | NARRATIVES, select_narrative |
| app/analysis/input_contract.py | 7 | validate_stage7_input |
| app/analysis/calculations.py | 7 | calculate_stage7 |
| app/analysis/range_engine.py | 7 | analyze_range |
| app/analysis/validation.py | 7 | validate_series, validate_user_range |
| app/analysis/config.py | 7 | RangeConfig, DEFAULT_RANGE_CONFIG |
| app/analysis/enums.py | 7-8 | Direction, RangeType, RangeConfidence, ScenarioType, Context, RelativeDirection |
| app/analysis/metrics.py | 7 | _is_finite_number, pct_change, etc. |
| app/analysis/range_analysis.py | 7 | RangeAnalysis dataclass |
| app/analysis/dmi.py | 7 | calculate_dmi_adx |
| app/analysis/validation_helpers.py | 7 | validate_scenario_matrix, validate_timeframes |
| app/analysis/timeframe.py | 7 | parse_timeframe |
| app/analysis/u08_engine.py | 8 | run_cell_08 |
| app/analysis/u08_result.py | 8 | Cell08Result, cell08_to_dict, cell08_to_json |
| app/analysis/u08_context.py | 8 | classify_context |
| app/analysis/u08_config.py | 8 | Cell08Config, CELL08_CONFIG |
| app/analysis/u08_normalize.py | 8 | _safe_float, _normalize_direction, normalize_asset |
| app/analysis/u08_scenario.py | 8 | SCENARIO_MATRIX, resolve_scenario |
| app/analysis/u08_ranking.py | 8 | rank functions |
| app/analysis/u08_relative.py | 8 | relative performance |
| app/analysis/u08_altcoin.py | 8 | altcoin structure |
| app/analysis/u08_narratives.py | 8 | NARRATIVES (dict format), get_narrative |
| app/analysis/u08_regression.py | 8 | run_cell08_regression_gate (test only) |
| app/analysis/regression.py | 7 | run_u07_regression_tests (test only) |
| app/market/ranking.py | 10 | dynamic_rank_assets |
| app/market/__init__.py | All | Empty |
| app/market/http.py | All | http_json, HTTPResult |
| app/core/u06_5.py | All | Core utilities |
| app/core/__init__.py | All | Empty |
| app/config/quality.py | All | Constants (TOP_N, FRESHNESS_THRESHOLD_SECONDS, etc.) |
| app/config/exchanges.py | All | Exchange configs |
| app/config/market_universe.py | All | U09 config |
| app/config/market_data.py | All | Market data config |
| app/config/runtime.py | All | Flask host/port |
| app/config/settings.py | All | App settings |
| app/config/__init__.py | All | Empty |
| app/analysis/u08_scenario.py | 8 | BTC scenario matrix |

### Supporting (Reviewed for Context)
| File | Role |
|------|------|
| app/market/validation.py | U09 provider validation |
| app/market/universe.py | U09 orchestration |
| app/market/reference.py | U06.5 reference price engine |
| app/market/exchange_evidence.py | U06.5 exchange evidence |
| app/market/global_providers.py | CMC + CG providers |
| app/market/finalization.py | U06.5 finalization |
| app/analysis/stage10_router.py | ExchangeRouter |
| app/analysis/stage10_consumer.py | Stage 10 consumer |
| app/analysis/stage10_usdt.py | USDT pair |
| app/analysis/stage10_btc.py | BTC pair |
| app/analysis/stage10_telegram.py | Stage 10 telegram |
| app/analysis/matrix.py | Scenario matrix |
| app/analysis/narratives.py | Narratives |
| e2e_scanner_test.py | E2E test |

### NOT Reviewed (Not runtime code for Stages 7-12)
- app/orderbook/ — empty directory
- app/scanner/ — empty directory
- app/trading/ — empty directory
- app/journal/ — empty directory
- app/data/models/ — not in /top3 path
- app/data/validation/ — not in /top3 path
- app/data/capture/ — not in /top3 path
- app/analysis/u08_*.py (except those listed above) — not in /top3 path
- Backups/alternate versions — NOT runtime
- Documentation files (.md) — not code
- Notebook files — not runtime code

## 16. Classification Summary

### IMPLEMENTED + RUNTIME USED (Key items)
- /top3 command → BotRunner → run_top3() → format_top3_telegram() — FULL PIPELINE
- Stage 12 scoring (movement + reliability) — used in run_top3
- Stage 10 get_dynamic_top10() — called by run_top3
- Stage 11 run_strong_movers() — called by run_top3
- ExchangeRouter.validate_fallback_direction() — used in USDT/BTC processors
- dynamic_rank_assets() — called in run_top3
- SCENARIO_MATRIX (Stage 7) — used in run_u07/run_stage7
- NARRATIVES (Stage 7) — used in run_u07/run_stage7
- NARRATIVES (Stage 8) — used in run_cell_08
- SCANNER_WARNING — imported and used in Stage 12 output
- All exchange/validation/fallback logic in USDT/BTC processors
- Help text and warning text — used in bot responses
- Flask /bot/webhook endpoint — active endpoint
- Telegram /top3 and /help handlers — active handlers

### IMPLEMENTED + RUNTIME USE NOT CONFIRMED
- validate_exchange_continuity() (stage12_top3.py:407) — defined but never called
- prepare_for_top3() (stage11_strong_movers.py:486) — defined but not called by Stage 12
- format_strong_movers_telegram() (stage11_strong_movers.py:441) — defined but not in /top3 path
- format_top10_telegram() (stage10_telegram.py:168) — defined but not in /top3 path
- check_rtl_safety() (stage10_telegram.py:158) — always returns True
- run_u07() (engine.py:54) — exists but not called in bot path
- run_stage7() (engine.py:390) — exists but not called in bot path
- run_cell_08() (u08_engine.py:26) — exists but not called in bot path
- ExchangeRouter.route() — defined but not used in /top3 path
- ExchangeRouter.route_with_provenance() — defined but not used
- get_fallback_chain() — defined in Stage 11 but not used in /top3 path
- is_higher_priority() — defined but not called in /top3 path directly
- validate_fallback_direction() (standalone, stage11_strong_movers.py:349) — used only via router
- prepare_for_top3() — Stage 11 integration contract, not consumed by Stage 12
- BotRunner._collect_ranking_data() — called by /top3 but uses direct CoinGecko API (not U06.5)

### NOT FOUND IN FINAL CODE
- Inline keyboard buttons / callbacks
- /start, /cancel, or other bot commands
- Conversation/state management
- Retry/resilience logic
- Result persistence/storage
- Stage 7/8 bot command integration
- Multi-exchange routing in /top3 path (always Binance)
- CMC API in BotRunner (uses CoinGecko directly)
- U06.5 provider stack in /top3 path
- validate_exchange_continuity() invocations
- prepare_for_top3() invocations
- Database/ORM usage
- Anti-repetition/memory mechanisms
- Session tracking
- Trading/order/strategy execution code (locks exist but no actual trading code)
