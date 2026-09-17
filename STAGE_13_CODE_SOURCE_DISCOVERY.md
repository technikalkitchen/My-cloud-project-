# Stage 13 Code-Source Discovery

## Scope and evidence boundary

This report records only the code-source findings already collected for the future Telegram Bot / Scanner interface. It does not introduce a Stage 13 design, roadmap, implementation decision, or new requirement.

- Existing Python runtime source, tests, configuration, and integration code were considered.
- Roadmaps, notebooks/IPYNB files, audit documents, migration documents, planning documents, Git history, backups, and alternate versions were not used as implementation evidence for this report.
- No existing source file was modified while creating this report.

## 1. Executive inventory

| Area | Existing source | Runtime status | Reuse potential |
|---|---|---|---|
| Telegram application | `app/bot/telegram.py`, `app/bot/config.py`, `app/bot/runner.py`, `app/bot/__init__.py` | Implemented and reachable through command handlers and Flask webhook | Direct base for a future interface |
| Flask integration | `app/api/app.py` | Implemented and smoke-tested through `/bot/status` and `/bot/webhook` | Existing HTTP entry point |
| Scanner orchestration | `app/analysis/stage12_top3.py` | Implemented and currently used by the bot path | Final operational Scanner entry point |
| Stage 11 | `app/analysis/stage11_strong_movers.py` | Implemented and called by Stage 12 | Reuses exchange, pair, scoring, and warning contracts |
| Stage 10 | `stage10_consumer.py`, `stage10_router.py`, `stage10_usdt.py`, `stage10_btc.py`, `stage10_telegram.py` | Data/path components are used indirectly by Stage 12; the Stage 10 formatter is not used by the current bot | Reusable data and formatting contracts |
| Stage 9 | `app/market/u09_engine.py` and market universe modules | Implemented but not connected to Telegram | Reusable market-universe/provider path |
| Stage 8 | `app/analysis/u08_*.py` | Implemented but not connected to Telegram | Reusable scenario, context, ranking, narrative, and result components |
| Stage 7 | `app/analysis/engine.py`, `input_contract.py`, `calculations.py`, `matrix.py`, `narratives.py`, and related modules | Implemented but not connected to Telegram | Reusable validated market-structure and narrative components |
| U06.5/data foundation | `app/core/u06_5.py`, `app/market/ranking.py`, provider/exchange/validation modules | Used by the current bot path through Stage 12 | Primary ranking, freshness, provenance, and fallback foundation |
| User interaction state | No source implementation found | Not found | Nothing currently reusable for per-user state |

The current operational chain is:

```text
Telegram command or Flask webhook request
    -> app/bot/telegram.py handler
    -> app/bot/runner.py: BotRunner.handle_command()
    -> app/analysis/stage12_top3.py: run_top3()
    -> U06.5 dynamic ranking
    -> Stage 10 consumer/router/USDT/BTC components
    -> Stage 11 run_strong_movers()
    -> Stage 12 result construction
    -> format_top3_telegram()
    -> Telegram reply or Flask HTTP response
```

A real integration run produced a Telegram-compatible Top 3 message using live CoinGecko market-cap data and historical candles. The run observed 30 ranked assets, selected ranks 2–10 for the Top 10 path, selected one Strong Mover in that run, and produced three Top 3 results. The message contained the mandatory Persian warning, USDT/BTC pair information, volume and source labels, and no trading-signal language. No message was delivered to a Telegram user because `BOT_TOKEN` was not set in the environment.

## 2. Telegram and bot source inventory

### 2.1 Bot configuration

**File:** `app/bot/config.py`

| Symbol | Finding | Classification |
|---|---|---|
| `BOT_TOKEN` environment configuration | Reads the Telegram token from the environment | Implemented + runtime configuration |
| `HELP_TEXT` | Existing help text used by the bot | Implemented + runtime used by `/help` |
| Command configuration | Existing command definitions include `/top3` and `/help` | Implemented + runtime used |

No hard-coded token or chat identifier was found in the collected source findings.

### 2.2 Bot runner

**File:** `app/bot/runner.py`

| Symbol | What it does | Classification |
|---|---|---|
| `BotRunner` | Coordinates a bot command and the existing Scanner pipeline | Implemented + runtime used |
| `BotRunner.handle_command()` | Dispatches the command to the real-data Scanner path and returns a Telegram-compatible result | Implemented + runtime used |
| `/top3` handling | Calls the Stage 12 Top 3 path | Implemented + runtime used |
| `/help` handling | Returns the configured help text | Implemented + runtime used |

The runner is deliberately thin: it does not replace U06.5, Stage 10, Stage 11, or Stage 12 logic.

### 2.3 Telegram application

**File:** `app/bot/telegram.py`

| Symbol | What it does | Classification |
|---|---|---|
| `TelegramBot` | Owns the `python-telegram-bot` application and handler registration | Implemented + runtime used |
| `python-telegram-bot` v22 `Application` | Provides the Telegram command application | Implemented + runtime used |
| Command handlers | Register `/top3` and `/help` | Implemented + runtime used |
| Polling support | A polling entry path exists | Implemented + not exercised in the recorded HTTP integration run |
| Message sending | Uses the runner result as the reply payload | Implemented + runtime used when a token is configured |

No callback-query handler, inline keyboard, reply keyboard, `callback_data`, message-edit/delete flow, or conversation handler was found.

### 2.4 Flask/API integration

**File:** `app/api/app.py`

| Endpoint | What it does | Classification |
|---|---|---|
| `GET /bot/status` | Reports bot/runtime status | Implemented + runtime used in smoke tests |
| `POST /bot/webhook` | Accepts a Telegram-style command request, invokes the runner, and returns the generated message | Implemented + runtime used |

The existing Flask application remains the HTTP host for the bot integration. `wsgi.py` exposes the Flask application through `wsgi:application`, and `scripts/start_wsgi.sh` starts it with gunicorn.

### 2.5 Dependency

**File:** `requirements.txt`

- `python-telegram-bot>=22,<23` is present.
- The existing Flask, gunicorn, pytest, and requests dependencies remain present.

## 3. Commands, navigation, and interaction inventory

### Implemented and reachable

| Command/path | Source | Behavior |
|---|---|---|
| `/top3` | `app/bot/config.py`, `app/bot/telegram.py`, `app/bot/runner.py` | Runs the current U06.5 → Stage 10 → Stage 11 → Stage 12 path and returns a Top 3 message |
| `/help` | `app/bot/config.py`, `app/bot/telegram.py` | Returns `HELP_TEXT` |
| `/bot/status` | `app/api/app.py` | Returns bot/runtime status |
| `/bot/webhook` | `app/api/app.py` | Runs a command through the bot runner and returns the generated message |

### Not found in source

- `/start`
- Any other Scanner command
- Back, Start, reset, cancel, or navigation commands
- Buttons or keyboards
- Callback queries or `callback_data`
- Per-user menus
- Conversation/state handlers
- Message editing or deletion
- Chat-specific session handling

## 4. Stage 7 source inventory

### 4.1 Entry points and contracts

**Files:** `app/analysis/input_contract.py`, `app/analysis/engine.py`

| Symbol | What it does | Runtime status |
|---|---|---|
| `Stage7InputContract` | Validates the Stage 7 input adapter consumed from U06.5 | Implemented + test-used; not reachable from Telegram |
| `run_stage7(adapter, pattern_index)` | Wires the Stage 7 input contract, calculations, scenario lookup, and narrative selection | Implemented + not reachable from Telegram |
| `run_u07` | Existing legacy/raw-value Stage 7 entry point | Implemented + not used by the current bot path |

The Stage 7 contract requires U06.5 source identity, finite positive series, sufficient history, no data fabrication, and accepted freshness states. Stale data is rejected rather than silently reused.

### 4.2 Calculations and validation

**Files:** `app/analysis/calculations.py`, `range_engine.py`, `metrics.py`, `dmi.py`, `range_analysis.py`, `validation.py`, `validation_helpers.py`, `timeframe.py`

Existing components calculate and validate:

- Total-market values and movements.
- USDT.D values and movements.
- The distinction between percentage movement and dominance percentage-point movement.
- Range, DMI, metric, timeframe, finiteness, positivity, and series-length checks.
- Deterministic handling of missing, invalid, stale, and edge-case data.

These components are implemented and test-covered, but none is called by the current Telegram path.

### 4.3 Scenario and narrative components

**Files:** `app/analysis/matrix.py`, `app/analysis/narratives.py`, `app/analysis/enums.py`, `app/analysis/config.py`

- `matrix.py` contains a nine-scenario Stage 7 matrix and a consumable scenario lookup.
- `narratives.py` contains 27 Persian narrative patterns and a narrative selection helper.
- `select_narrative()` and `lookup_scenario()` are implemented.
- The narratives are informational and contain no trading-signal contract.

No Stage 7 Telegram formatter or Stage 7 command exists.

### 4.4 Stage 7 output and reachability

`run_stage7()` returns a Stage 7 result object after scenario and narrative selection. The result is usable as a pure Python/JSON analysis result, but there is no source path from Telegram to Stage 7 and no Stage 7-specific user-facing formatter.

## 5. Stage 8 source inventory

### 5.1 Engine and result

**Files:** `app/analysis/u08_engine.py`, `app/analysis/u08_result.py`

| Symbol | What it does | Runtime status |
|---|---|---|
| `run_cell_08` | Composes the existing Stage 8 components into a `Cell08Result` | Implemented + not reachable from Telegram |
| `Cell08Result` | Carries scenario, context, relative-performance, ranking, altcoin, narrative, and serialization data | Implemented + test-used |
| `run_cell08_regression_gate` | Validates Stage 8 invariants and regression conditions | Implemented + test-used |

The engine preserves dict/JSON serialization with Persian text and is deterministic for identical inputs.

### 5.2 Component inventory

| File | Existing responsibility | Runtime status |
|---|---|---|
| `u08_config.py` | Stage 8 configuration | Implemented + consumed by `run_cell_08` |
| `u08_normalize.py` | Input normalization | Implemented + consumed by `run_cell_08` |
| `u08_scenario.py` | Nine-scenario mapping and validation | Implemented + consumed by `run_cell_08` |
| `u08_context.py` | Context classification | Implemented + consumed by `run_cell_08` |
| `u08_relative.py` | Relative-performance calculation | Implemented + consumed by `run_cell_08` |
| `u08_ranking.py` | Stage 8 ranking | Implemented + consumed by `run_cell_08` |
| `u08_altcoin.py` | Altcoin structure and availability handling | Implemented + consumed by `run_cell_08` |
| `u08_narratives.py` | 27 Persian narratives and attachment | Implemented + consumed by `run_cell_08` |
| `u08_regression.py` | Regression gate | Implemented + test-used |
| `enums.py` | Shared `Context` and `RelativeDirection` enums | Implemented + consumed |

### 5.3 Stage 8 output and reachability

Stage 8 has a complete analysis result and regression path, including scenario resolution, context classification, relative performance, ranking, altcoin structure, and narrative attachment. It has no Telegram formatter, command, or bot connection. No Stage 8 output is currently sent to a Telegram user.

## 6. Stage 9 source inventory

### 6.1 Engine and consumer contract

**File:** `app/market/u09_engine.py`

| Symbol | What it does | Runtime status |
|---|---|---|
| `run_u09(orchestrator, audit, persist)` | Integrates U09 execution, audit, consumer validation, and optional persistence | Implemented + not reachable from Telegram |
| `u09_consumer_contract(result)` | Validates required result fields, types, safety locks, message contract, segment coverage, and confidence range | Implemented + test-used |
| `u09_regression_gate(orchestrator)` | Runs deterministic end-to-end validation | Implemented + test-used |
| `u09_e2e_integration(orchestrator)` | Checks configuration, providers, validation, segments, message, audit, contract, and safety locks | Implemented + test-used |

### 6.2 Market universe and provider path

**Files:** `app/market/universe.py`, `app/market/providers.py`, `app/market/validation.py`, `app/market/reference.py`, `app/config/market_universe.py`

- Four segments exist: `BTC`, `ETH`, `TOP10_ALT`, and `BROAD_ALT_11_125`.
- Provider failover and explicit unavailable behavior exist.
- The U09 message is a five-line market-participation message.
- The result and message are test-covered and serializable.
- No scenario, matrix, narrative, label, conclusion, or trading-signal logic exists in U09.

U09 is implemented and reusable as a market-universe path, but it is not connected to the current Telegram command path.

## 7. Stage 10 source inventory

### 7.1 Dynamic Top-10 consumer

**File:** `app/analysis/stage10_consumer.py`

| Symbol | What it does | Runtime status |
|---|---|---|
| `Stage10Config` | Holds view, selected exchange, timeframe, and rank bounds | Implemented + consumed indirectly by Stage 12 |
| `View.KITCHEN` / `View.EXCHANGE` | Selects Kitchen or exchange presentation | Implemented + contract used |
| `get_dynamic_top10()` | Consumes `dynamic_rank_assets()` from U06.5 on each call | Implemented + runtime used indirectly |
| `select_ranks()` | Selects ranks 2–10 and excludes BTC rank 1 | Implemented + runtime used indirectly |

The Top-10 list is dynamic and is not a permanently cached or stale list.

### 7.2 Exchange routing and fallback

**File:** `app/analysis/stage10_router.py`

| Symbol | What it does | Runtime status |
|---|---|---|
| `ExchangeRouter` | Validates the selected exchange and routes data | Implemented + runtime used indirectly |
| `build_exchange_choices()` | Returns the eight supported exchanges in priority order | Implemented + test-used |
| `get_fallback_chain()` | Builds a selected-to-higher-priority fallback chain | Implemented + runtime used indirectly |
| `is_higher_priority()` | Enforces fallback direction | Implemented + runtime used indirectly |
| `validate_fallback_direction()` | Rejects lower-priority fallback | Implemented + runtime used indirectly |
| `ExchangeRoutingResult` | Records requested/actual exchange and fallback provenance | Implemented + runtime used indirectly |

The source contract permits fallback only toward higher-priority exchanges.

### 7.3 USDT and BTC pair processing

**Files:** `app/analysis/stage10_usdt.py`, `app/analysis/stage10_btc.py`

| Component | Existing contract |
|---|---|
| USDT pairs | Symbol must be a valid USDT pair; requested timeframe is enforced; volume must be provider-supplied and USDT-only; freshness and finite values are validated |
| USDT provenance | Each field records source exchange; direct and fallback labels are preserved |
| BTC pairs | Selected-exchange pair is tried first, followed by eligible higher-priority fallback; USDT fallback exchange is preferred for BTC cohesion where valid |
| BTC availability | Explicit unavailable state is returned when no valid source exists |
| Kitchen BTC calculation | Used only where the existing contract permits it |
| Fake-pair prevention | BTC-only, malformed, empty, and fabricated pair forms are rejected |

These components are used by Stage 12 and therefore participate in the current bot path.

### 7.4 Stage 10 Telegram formatter

**File:** `app/analysis/stage10_telegram.py`

| Symbol | What it does | Runtime status |
|---|---|---|
| `TelegramOutput` | Carries message, view, asset count, source/fallback labels, volume state, and RTL-safety state | Implemented + test-used |
| `TelegramFormatter.format_top10()` | Formats Dynamic Top-10 output | Implemented + not used by the current bot path |
| `format_top10_telegram()` | Convenience formatter | Implemented + test-used |
| `check_rtl_safety()` | Intended RTL/LTR safety helper | Implemented as a stub that always returns `True` |

Existing exact formatter fragments include:

- `🏆 TOP 10 MARKET CAP`
- `Volume:`
- `Source`
- `Fallback from`
- RTL protection markers around mixed-direction content

The Stage 10 display order is asset, USDT pair and movement, USDT volume, source/fallback, BTC pair and movement, source/fallback. Volume is shown only for the USDT pair; BTC volume is not displayed.

## 8. Stage 11 source inventory

**File:** `app/analysis/stage11_strong_movers.py`

| Symbol | What it does | Runtime status |
|---|---|---|
| `run_strong_movers()` | Builds the ranks 11–125 candidate universe, evaluates candidates, selects five Strong Movers, resolves pairs, and builds output | Implemented + runtime used indirectly through Stage 12 |
| `build_candidate_universe()` | Consumes the dynamic ranking and excludes the Top-10/BTC region from the Strong Movers candidate set | Implemented + runtime used |
| `evaluate_candidate()` | Applies Strong Movement and Reliability scoring | Implemented + runtime used |
| `select_strong_movers()` | Selects exactly five candidates by the established score | Implemented + runtime used |
| `prepare_for_top3()` | Preserves structured data for the downstream Top 3 stage | Implemented + not called by the current runtime path |
| `format_strong_movers_telegram()` | Formats five Strong Movers for Telegram display | Implemented + not used by the current bot path |
| `StrongMoversOutput` | Carries the five selected movers and their pair/provenance data | Implemented + runtime used |

Stage 11 reuses Stage 10 exchange routing, USDT/BTC validation, fallback direction, provenance, and display semantics. It does not calculate or display Top 3 results.

The existing output order is:

1. Asset.
2. USDT pair and movement.
3. USDT volume.
4. `Source` or `Fallback from` exchange.
5. BTC pair and movement.
6. `Source` or `Fallback from` exchange.

The output includes the mandatory Scanner warning. The warning is defined in `SCANNER_WARNING` in `stage11_strong_movers.py` and is reused by the Top 3 path. The retained source finding confirms that it is Persian and begins with `توجه`; the full byte-for-byte body is not reconstructed in this report.

## 9. Stage 12 source inventory

**File:** `app/analysis/stage12_top3.py`

| Symbol | What it does | Runtime status |
|---|---|---|
| `run_top3()` | Final operational orchestration: U06.5 → Dynamic Top 10 → Strong Movers → Top 3 | Implemented + runtime used by the bot |
| `build_candidate_pool()` | Combines and deduplicates Stage 10 and Stage 11 candidates by canonical asset identity | Implemented + runtime used |
| `evaluate_candidate()` | Applies Strong Movement and Reliability scoring without adding an unsupported third metric | Implemented + runtime used |
| `select_top3()` | Selects exactly three candidates | Implemented + runtime used |
| `validate_exchange_continuity()` | Checks higher-priority-only exchange continuity using Stage 10 routing | Implemented + not called by the current runtime path |
| `build_top3_result()` | Builds the final result with USDT/BTC pair and provenance fields | Implemented + runtime used |
| `format_top3_telegram()` | Produces the compact Telegram-compatible Top 3 message | Implemented + runtime used |
| `_btc_source_label()` | Builds BTC source/fallback provenance labels | Implemented + runtime used |
| `prepare_for_top3()` | Existing preparation helper | Implemented + not called by the current runtime path |
| `Top3Output` | Final Top 3 result/message contract | Implemented + runtime used |

The current Top 3 formatter produces compact numbered output such as:

```text
1. SOLUSDT +8.4%
Volume: ...
Exchange: Binance
```

The exact source labels are `Source: <exchange>` and `Fallback from: <exchange>`. The output includes `TOP3_SCANNER_WARNING`, preserves USDT/BTC provenance, and contains no `BUY`, `SELL`, `LONG`, `SHORT`, `STOP`, `TAKE`, `TARGET`, `ENTRY`, or `EXIT` signal language.

A source defect previously found and fixed was the loss of BTC provenance for candidates whose initial `btc_source` was empty. `_btc_source_label()` now derives the label from the BTC result's actual exchange and fallback fields.

## 10. U06.5, market data, exchange, and validation components

### 10.1 Ranking and dynamic universe

**Files:** `app/core/u06_5.py`, `app/market/ranking.py`

- `dynamic_rank_assets()` is the ranking authority consumed by Stage 10 and the current bot path.
- The ranking is refreshed for each request rather than reused from a permanent cache.
- BTC rank 1 is excluded from the Dynamic Top-10 selection.
- The real integration run used CoinGecko market-cap data and observed 30 ranked assets.

### 10.2 Providers, exchange evidence, and HTTP

**Files:** `app/market/global_providers.py`, `app/market/providers.py`, `app/market/exchange_evidence.py`, `app/market/http.py`, `app/config/exchanges.py`, `app/config/quality.py`

Existing reusable behavior includes:

- Provider and exchange evidence tracking.
- Eight exchange choices and fixed display fallback priority.
- Higher-priority-only fallback.
- Per-field source/fallback provenance.
- HTTP timeout and freshness configuration.
- Explicit unavailable/error handling instead of fabricated values.
- Environment-based API-key discovery without hard-coded credentials.

### 10.3 Data validation and capture

**Files:** `app/data/validation/normalize.py`, `app/data/validation/candles.py`, `app/data/validation/u06_quality_gate.py`, `app/data/capture/router.py`, `app/data/capture/binance.py`, `app/data/capture/coinbase.py`, `app/data/models/candle.py`

These modules provide normalization, candle validation, quality-gate checks, and exchange capture adapters. They are reusable data infrastructure, but the current `/top3` runtime path reaches the ranking and Stage 10–12 components rather than a separate Telegram-specific capture path.

### 10.4 Configuration and runtime

**Files:** `app/config/settings.py`, `app/config/runtime.py`, `app/config/__init__.py`

- Existing runtime configuration covers environment, timezone, logging, host, port, and debug behavior.
- Bot-specific runtime configuration is in `app/bot/config.py`.
- No bot token or chat identifier is present in the environment configuration used by the recorded integration run.

## 11. User-facing output inventory

### Exact retained text and labels

| Text | Source | Use |
|---|---|---|
| `🏆 TOP 10 MARKET CAP` | `app/analysis/stage10_telegram.py` | Stage 10 formatter header |
| `Volume:` | `app/analysis/stage10_telegram.py`, Stage 11/12 formatting | USDT volume label |
| `Source` | Stage 10/11/12 source-label logic | Direct exchange provenance |
| `Fallback from` | Stage 10/11/12 source-label logic | Fallback exchange provenance |
| `توجه` | `SCANNER_WARNING` / Top 3 warning path | Mandatory Persian Scanner warning marker |
| `Source: Binance` | Stage 10–12 provenance output | Example of direct BTC/USDT source label |
| `Fallback from: Binance` | Stage 10–12 provenance output | Example of fallback source label |
| `1. SOLUSDT +8.4%` | `format_top3_telegram()` output contract | Example compact Top 3 line |
| `Exchange: Binance` | Stage 12 output | Example exchange display |

The Stage 11 and Stage 12 warning constants are the authoritative existing warning definitions. The source findings establish that the warning is mandatory, Persian, and reused across the operational output path. No warning text has been rewritten here.

### Output safety facts

- Stage 10–12 outputs are informational.
- No trading recommendations or signal language are emitted.
- USDT volume is displayed only for USDT pairs.
- BTC volume is not displayed.
- Fake pairs and fabricated values are rejected or reported unavailable.
- Source and fallback provenance are retained.
- Mixed Persian/Latin output is intended to be RTL/LTR safe, although the current `check_rtl_safety()` implementation is only a stub.

## 12. Validation, errors, retry, and resilience inventory

### Existing validation

- Stage 7 input validation: source identity, finite positive values, history length, no fabrication, freshness.
- Stage 7 calculations: non-finite, non-positive, mismatched, and edge-case data handling.
- Stage 10 USDT: symbol, timeframe, freshness, finite change, provider-supplied volume, non-zero volume, fallback direction.
- Stage 10 BTC: symbol format, freshness, timeframe, fallback direction, fake-pair prevention, explicit unavailable state.
- Stage 11: candidate universe, score, exchange continuity, pair validity, output safety.
- Stage 12: candidate pool, scoring, selection, result construction, provenance, warning, and no-signal checks.
- U09: consumer contract, segment coverage, confidence range, safety locks, and explicit `DATA_UNAVAILABLE`.

### Existing fallback and unavailable behavior

- Provider failover exists in the market-data foundation and U09.
- Exchange fallback is restricted to higher-priority exchanges.
- USDT and BTC fallback provenance is preserved.
- Missing or invalid data becomes an explicit unavailable result or validation rejection.
- No stale value is silently substituted.

### Not found

- Bot-level retry loop.
- Bot-level timeout/recovery handler.
- User-facing retry command.
- Telegram-specific error mapping.
- Persistent retry state.
- Per-user error history.

## 13. State, session, history, and memory

No source implementation was found for:

- User state or chat state.
- `ConversationHandler` or equivalent state machine.
- Session persistence.
- Per-user exchange selection.
- Previous-result tracking.
- Output history or memory.
- Anti-repetition or duplicate-message prevention.
- Database, Redis, SQLite, cache, or file-backed user state.

U09 has market-snapshot persistence/audit behavior, but that is market-data persistence, not Telegram user-session state.

## 14. Reusable, unused, duplicated, and conflicting findings

### Reusable and currently runtime-used

- `BotRunner.handle_command()`.
- `TelegramBot` command handlers.
- `/bot/webhook` and `/bot/status`.
- `run_top3()`.
- `format_top3_telegram()`.
- `dynamic_rank_assets()`.
- Stage 10 consumer, router, USDT, and BTC processors.
- `run_strong_movers()`.
- Stage 10/11/12 provenance and warning contracts.

### Implemented but not runtime-used from Telegram

- Stage 7 `run_stage7()` and `run_u07()`.
- Stage 8 `run_cell_08()` and `run_cell08_regression_gate()`.
- Stage 9 `run_u09()` and its consumer/regression/E2E functions.
- `format_top10_telegram()`.
- `format_strong_movers_telegram()`.
- Stage 12 `validate_exchange_continuity()`.
- Stage 12 `prepare_for_top3()`.
- Stage 7/8 scenario and narrative components when considered as Telegram outputs.

### Test-only or helper-only

- `tests/unit/test_bot_runner.py` exercises the bot runner and webhook behavior.
- `e2e_scanner_test.py` exercises the full Scanner chain and generates a Telegram-compatible message for verification.
- `check_rtl_safety()` is a helper/stub rather than a complete RTL validator.

### Parallel or potentially conflicting implementations

- Stage 7 has both `run_u07` and the newer `run_stage7` entry shape; the bot uses neither.
- Stage 10 has a complete Telegram formatter, while the current bot bypasses it and formats through Stage 12.
- Stage 11 and Stage 12 each have Telegram formatters; only the Stage 12 formatter is on the current `/top3` path.
- `HELP_TEXT` contains a shortened warning presentation compared with the full `SCANNER_WARNING` definition.
- `check_rtl_safety()` reports safety unconditionally and therefore does not independently validate bidi behavior.
- Stage 12 contains `validate_exchange_continuity()` and `prepare_for_top3()` as implemented helpers that are not invoked by the current runtime orchestration.

## 15. Genuinely absent from the inspected source

- Stage 13 implementation.
- Any Stage 13 command, screen, state, or output contract.
- `/start`.
- Buttons, keyboards, callbacks, navigation, Back, reset, or cancel behavior.
- Message handlers independent of the existing command handlers.
- Callback-query handling.
- Markdown or HTML parse-mode configuration.
- A complete RTL/LTR validator.
- Per-user configuration or exchange selection in Telegram.
- User session, persistence, history, memory, or anti-repetition.
- Bot retry, timeout recovery, or Telegram error-reply mapping.
- Stage 7, Stage 8, or Stage 9 Telegram formatters.
- A unified Telegram flow for Stages 7–11; the current operational path terminates at Stage 12 Top 3.
- A configured `BOT_TOKEN` or chat identifier in the recorded runtime environment.

## 16. Files reviewed in the completed discovery

### Bot, API, and runtime

- `app/bot/__init__.py`
- `app/bot/config.py`
- `app/bot/runner.py`
- `app/bot/telegram.py`
- `app/api/app.py`
- `app/api/__init__.py`
- `wsgi.py`
- `scripts/start_wsgi.sh`
- `requirements.txt`
- `app/config/settings.py`
- `app/config/runtime.py`
- `app/config/__init__.py`

### Stage 7

- `app/analysis/input_contract.py`
- `app/analysis/calculations.py`
- `app/analysis/engine.py`
- `app/analysis/matrix.py`
- `app/analysis/narratives.py`
- `app/analysis/range_engine.py`
- `app/analysis/range_analysis.py`
- `app/analysis/metrics.py`
- `app/analysis/dmi.py`
- `app/analysis/validation.py`
- `app/analysis/validation_helpers.py`
- `app/analysis/timeframe.py`
- `app/analysis/config.py`
- `app/analysis/enums.py`
- `app/analysis/regression.py`

### Stage 8

- `app/analysis/u08_engine.py`
- `app/analysis/u08_config.py`
- `app/analysis/u08_normalize.py`
- `app/analysis/u08_scenario.py`
- `app/analysis/u08_context.py`
- `app/analysis/u08_relative.py`
- `app/analysis/u08_ranking.py`
- `app/analysis/u08_altcoin.py`
- `app/analysis/u08_narratives.py`
- `app/analysis/u08_result.py`
- `app/analysis/u08_regression.py`

### Stage 9

- `app/market/u09_engine.py`
- `app/market/universe.py`
- `app/market/providers.py`
- `app/market/validation.py`
- `app/market/reference.py`
- `app/config/market_universe.py`

### Stages 10–12

- `app/analysis/stage10_consumer.py`
- `app/analysis/stage10_router.py`
- `app/analysis/stage10_usdt.py`
- `app/analysis/stage10_btc.py`
- `app/analysis/stage10_telegram.py`
- `app/analysis/stage11_strong_movers.py`
- `app/analysis/stage12_top3.py`

### U06.5, market data, and validation

- `app/core/u06_5.py`
- `app/market/ranking.py`
- `app/market/global_providers.py`
- `app/market/providers.py`
- `app/market/exchange_evidence.py`
- `app/market/http.py`
- `app/market/finalization.py`
- `app/config/exchanges.py`
- `app/config/quality.py`
- `app/data/validation/normalize.py`
- `app/data/validation/candles.py`
- `app/data/validation/u06_quality_gate.py`
- `app/data/capture/router.py`
- `app/data/capture/binance.py`
- `app/data/capture/coinbase.py`
- `app/data/models/candle.py`

### Tests and integration evidence

- `tests/unit/test_bot_runner.py`
- `tests/unit/test_u07_unit_1_input_contract.py`
- `tests/unit/test_u07_unit_2_calculations.py`
- `tests/unit/test_u07_unit_3_scenario_matrix.py`
- `tests/unit/test_u07_unit_4_intelligence.py`
- `tests/unit/test_u07_unit_5_integration.py`
- `tests/unit/test_u08_unit_*.py`
- `tests/unit/test_u09_unit_*.py`
- `tests/unit/test_u10_unit_1_contract.py`
- `tests/unit/test_u10_unit_2_router.py`
- `tests/unit/test_u10_unit_3_usdt.py`
- `tests/unit/test_u10_unit_4_btc.py`
- `tests/unit/test_u10_unit_5_telegram.py`
- `tests/unit/test_u11_unit_1_contract.py`
- `tests/unit/test_u11_unit_2_evaluation.py`
- `tests/unit/test_u11_unit_3_exchange.py`
- `tests/unit/test_u11_unit_4_output.py`
- `tests/unit/test_u11_unit_5_integration.py`
- `tests/unit/test_u11_unit_6_regression.py`
- `tests/unit/test_u12_unit_1_contract.py`
- `tests/unit/test_u12_unit_2_evaluation.py`
- `tests/unit/test_u12_unit_3_exchange.py`
- `tests/unit/test_u12_unit_4_output.py`
- `tests/unit/test_u12_unit_5_integration.py`
- `tests/unit/test_u12_unit_6_regression.py`
- `e2e_scanner_test.py`

## 17. Classification summary

- **Implemented + runtime used:** bot command handlers, Flask webhook/status endpoints, `BotRunner.handle_command()`, `run_top3()`, Stage 12 formatter, U06.5 dynamic ranking, Stage 10 data processors, and Stage 11 Strong Movers orchestration.
- **Implemented + not runtime used from Telegram:** Stage 7, Stage 8, Stage 9 engines; Stage 10 and Stage 11 Telegram formatters; Stage 12 continuity/preparation helpers.
- **Implemented + test-only:** bot runner tests, Stage-specific unit/integration tests, and the E2E Scanner utility.
- **Defined but unreachable from Telegram:** Stage 7/8/9 analysis results, scenario/narrative outputs, U09 market-universe output, and their formatters where present.
- **Duplicated or parallel:** legacy/current Stage 7 entry points; Stage 10/11/12 formatter implementations; Stage 12 preparation and continuity helpers.
- **Genuinely not found:** Stage 13 code, buttons/callbacks/navigation, user state/history/memory, bot retry/error recovery, `/start`, bot token/chat ID in the recorded environment, and Stage 7–9 Telegram output paths.
