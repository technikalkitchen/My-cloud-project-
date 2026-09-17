# KILO — STAGES 7–12 TELEGRAM OUTPUT AUDIT REPORT
## READ-ONLY — NO IMPLEMENTATION

---

## PHASE 1 — VERIFIED CONTRACTS FOR STAGE 13

### 1A. Exchange/Display Fallback Contract (Shared Across Stages 7-12)
- **EXPLICITLY AGREED / APPROVED** across all roadmaps (Stage 10 §4.2, Stage 11 §9, Stage 12 §12)
- **Source**: `STAGE_10_DYNAMIC_TOP10_ROADMAP.md` §4.2; `STAGE_11_STRONG_MOVERS_ROADMAP_COMPLETE.md` §9; `STAGE_12_TOP_3_RELIABLE_MOVERS_ROADMAP_COMPLETE.md` §12
- **Exact priority order** (8 exchanges):
  1. Binance  2. OKX  3. Bybit  4. KuCoin  5. Coinbase  6. Gate  7. Upbit  8. Bitget
- **Rule**: Selected exchange = Preferred Display Source. Fallback moves ONLY toward higher-priority exchanges. Lower-priority fallback forbidden.
- **Implemented in**: `app/analysis/stage10_consumer.py:37-46` (DISPLAY_FALLBACK_PRIORITY), `app/analysis/stage10_router.py:49-202` (ExchangeRouter), `app/analysis/stage11_strong_movers.py:333-352` (reuses router), `app/analysis/stage12_top3.py:407-417` (validate_exchange_continuity)

### 1B. BTC Pair Contract (Shared)
- **EXPLICITLY AGREED**: Stage 10 §13, Stage 11 §15, Stage 12 §15
- **Resolution chain**: Real selected-exchange pair → eligible fallback exchange → approved Kitchen calculation (only where existing contract permits) → Unavailable
- **Fake BTC pairs forbidden** (e.g., BTCBTC, BTC, FAKEBTC)
- **Implemented in**: `app/analysis/stage10_btc.py:224-242` (_is_valid_btc_pair), `app/analysis/stage10_btc.py:98-133` (fallback direction validation)

### 1C. USDT Pair + Volume Contract (Shared)
- **EXPLICITLY AGREED**: Stage 10 §10/§12, Stage 11 §13, Stage 12 §14
- Volume belongs ONLY to USDT pair. Never BTC pair.
- Volume must match requested timeframe/window. No 24h substitution.
- Provider-supplied traded base-asset volume. No fabrication.
- **Implemented in**: `app/analysis/stage10_usdt.py:34-213` (UsdtPairProcessor)

### 1D. Mandatory Scanner Warning
- **EXPLICITLY AGREED / APPROVED** (exact text):
  ```
  ⚠️ توجه: اطلاعات و انتخاب‌های ارائه‌شده توسط Scanner به‌هیچ‌وجه سیگنال ورود یا خروج از معامله نیستند و نباید به‌تنهایی مبنای تصمیم معاملاتی قرار گیرند. هدف Scanner، صرفه‌جویی در زمان و مشخص‌کردن دارایی‌های برتر، جریان حرکت سرمایه و جهت کلی بازار است تا بتوانید روی گزینه‌هایی که ارزش بررسی بیشتری دارند تمرکز کنید. تصمیم نهایی برای معامله، از جمله تشخیص Setup، Entry و Trigger، بر عهده خود شماست.
  ```
- **Source**: `SCANNER_MASTER_ROADMAP.md` §18 (line 452); `STAGE_10_DYNAMIC_TOP10_ROADMAP.md` §22; `STAGE_11_STRONG_MOVERS_ROADMAP_COMPLETE.md` §26; `STAGE_12_TOP_3_RELIABLE_MOVERS_ROADMAP.md` §20 (lines 418-423)
- **Implemented as constant**: `app/analysis/stage11_strong_movers.py:36-44` (SCANNER_WARNING), reused by Stage 12 (`stage12_top3.py:143` imports it)
- **In bot/config**: `app/bot/config.py:11-18` (HELP_TEXT — partial warning, ends at "سیگنال ورود یا خروج از معامله نیستند.") and `app/bot/runner.py:21-29` (HELP_TEXT — same partial warning)
- **CONFLICT/INCONSISTENCY**: The HELP_TEXT in `app/bot/config.py` and `app/bot/runner.py` contains an INCOMPLETE version of the warning (ends at "ورود یا خروج از معامله نیستند.") vs. the full warning in `stage11_strong_movers.py`. The full version is the approved text per SCANNER_MASTER_ROADMAP.md §18. The HELP_TEXT version is IMPLEMENTED BUT NOT EXPLICITLY AGREED as the complete warning.

### 1E. No Trading Signal Contract (Shared)
- **EXPLICITLY AGREED**: All roadmaps (Stage 10 §21, Stage 11 §26, Stage 12 §24/§39)
- Forbidden: entry, exit, long, short, buy/sell, trade recommendation, scenario, scenario matrix, narrative, generic intelligence conclusion
- **Verified in**: `app/analysis/stage10_telegram.py` (no signal language), `app/analysis/stage11_strong_movers.py` (formatting has no signal), `app/analysis/stage12_top3.py:496` (format_top3_telegram includes warning only)
- **Verified in tests**: `tests/unit/test_bot_runner.py:446-469` (test_bot_no_signal_in_top3_response), `tests/unit/test_u12_unit_4_output.py:344-384` (test_no_signal_language)

---

## PHASE 2 — BYTE-FOR-BYTE SOURCE OF TRUTH

### 2A. Exact Approved Texts

#### A1. SCANNER_WARNING (Full Text)
- **Status**: EXPLICITLY AGREED / APPROVED
- **Exact text** (byte-for-byte from `app/analysis/stage11_strong_movers.py:36-44`):
```python
SCANNER_WARNING = (
    "⚠️ توجه: اطلاعات و انتخاب‌های ارائه‌شده توسط Scanner "
    "به‌هیچ‌وجه سیگنال ورود یا خروج از معامله نیستند و نباید به‌تنهایی "
    "مبنای تصمیم معاملاتی قرار گیرند. هدف Scanner، صرفه‌جویی در زمان و "
    "مشخص‌کردن دارایی‌های برتر، جریان حرکت سرمایه و جهت کلی بازار است تا "
    "بتوانید روی گزینه‌هایی که ارزش بررسی بیشتری دارند تمرکز کنید. "
    "تصمیم نهایی برای معامله، از جمله تشخیص Setup، Entry و Trigger، "
    "بر عهده خود شماست."
)
```
- **Source**: `app/analysis/stage11_strong_movers.py:36-44` (also in `STAGE_11_STRONG_MOVERS_ROADMAP_COMPLETE.md` as approved narrative)
- **Contractual**: YES — referenced by SCANNER_MASTER_ROADMAP.md §18, Stage 10 §22, Stage 11 §26, Stage 12 §20
- **Reused by**: `stage12_top3.py:143` (TOP3_SCANNER_WARNING = SCANNER_WARNING)

#### A2. Telegram TelegramFormatter labels (Stage 10)
- **Status**: EXPLICITLY AGREED (from Stage 10 roadmap §19)
- **TOP10_HEADER**: `"🏆 TOP 10 MARKET CAP"` — `app/analysis/stage10_telegram.py:30`
- **VOLUME_LABEL**: `"Volume:"` — `app/analysis/stage10_telegram.py:31`
- **SOURCE_LABEL**: `"Source"` — `app/analysis/stage10_telegram.py:32`
- **FALLBACK_LABEL**: `"Fallback from"` — `app/analysis/stage10_telegram.py:33`

#### A3. Telegram TelegramFormatter labels (Stage 11)
- **Status**: EXPLICITLY AGREED (implied by Stage 11 §25 reusing Stage 10 rules)
- **STRONG_MOVERS_HEADER**: `"🏆 5 STRONG MOVERS"` — `app/analysis/stage11_strong_movers.py:46`
- **Source/Fallback labels**: Same as Stage 10 via `_format_source_label` at `stage11_strong_movers.py:377-386`

#### A4. Telegram TelegramFormatter labels (Stage 12)
- **Status**: EXPLICITLY AGREED (from Stage 12 §19)
- **TOP3_HEADER**: `"🏆 TOP 3 RELIABLE MOVERS"` — `app/analysis/stage12_top3.py:142`
- **TOP3_SCANNER_WARNING**: Reuses SCANNER_WARNING — `stage12_top3.py:143`

#### A5. NARRATIVES (Stage 7 — U07)
- **Status**: EXPLICITLY AGREED (Stage 7 roadmap §9 mandates exact text preservation)
- **27 locked Persian narrative texts**: `app/analysis/narratives.py:11-83`
- Structure: 9 scenarios × 3 patterns = 27 texts
- **Contractual**: YES — `KILO_MIGRATION_AUDIT.md` line 659: "U07 NARRATIVES: 9 scenarios × 3 patterns = 27 exact Persian narrative texts. Locked; do not rewrite."

#### A6. NARRATIVES (Stage 8 — Cell 8)
- **Status**: EXPLICITLY AGREED (Stage 8 roadmap mandates exact text preservation)
- **27 locked Persian narrative patterns**: `app/analysis/u08_narratives.py:11-238`
- Structure: 9 scenarios × 3 patterns = 27 patterns with {pattern, title, text} fields
- **Contractual**: YES — `KILO_MIGRATION_AUDIT.md` line 660: "U08 NARRATIVES: 9 scenarios × 3 patterns = 27 exact Persian narrative texts with pattern, title, text fields. Locked; do not rewrite."

#### A7. HELP_TEXT (Bot)
- **Status**: IMPLEMENTED BUT NOT EXPLICITLY AGREED (partial)
- **Location**: `app/bot/config.py:11-18`, `app/bot/runner.py:21-29`
- **Note**: Contains an abbreviated warning (not the full SCANNER_WARNING). The command `/top3` description and `/help` are implemented but not specified in any Stage 7-12 roadmap. The warning portion overlaps with but does NOT match the full approved text.

### 2B. Scenario Matrix (Stage 7 — 9-cell U07 Matrix)
- **Status**: EXPLICITLY AGREED — `app/analysis/matrix.py:12-57`
- **Exact 9 mappings** (Direction, Direction) → {scenario_id, scenario_type}:
  - (INCREASE, DECREASE) → 1, MIRROR
  - (DECREASE, INCREASE) → 2, MIRROR
  - (INCREASE, INCREASE) → 3, PARALLEL
  - (DECREASE, DECREASE) → 4, PARALLEL
  - (INCREASE, RANGE) → 5, RANGE_COMPATIBLE_STATE
  - (DECREASE, RANGE) → 6, RANGE_COMPATIBLE_STATE
  - (RANGE, INCREASE) → 7, RANGE_COMPATIBLE_STATE
  - (RANGE, DECREASE) → 8, RANGE_COMPATIBLE_STATE
  - (RANGE, RANGE) → 9, NEUTRAL_FLAT
- **Source**: `app/analysis/matrix.py`, `STAGE_10_DYNAMIC_TOP10_ROADMAP.md` references U07 scenario usage
- **CONFLICT/INCONSISTENCY**: The test file `tests/unit/test_u07_unit_3_scenario_matrix.py` (lines 28-37) lists scenario_type as "RANGE-COMPATIBLE STATE" (with hyphen) and "NEUTRAL / FLAT" (with spaces), but the enum in `app/analysis/enums.py:33-36` defines them as `RANGE_COMPATIBLE_STATE = "RANGE-COMPATIBLE STATE"` and `NEUTRAL_FLAT = "NEUTRAL / FLAT"`. These match. However `STAGE_10_DYNAMIC_TOP10_ROADMAP.md` §12 (line 265) references "Scenario Matrix" generically without specifying the exact types.

### 2C. Scenario Matrix (Stage 8 — Cell 8, 9-cell Matrix)
- **Status**: EXPLICITLY AGREED — `app/analysis/u08_scenario.py:10-50`
- **Exact 9 mappings** (BTC direction, BTC.D direction) → {scenario_id, scenario_type}:
  - (INCREASE, INCREASE) → 1, BTC_UP_BTC_D_UP
  - (INCREASE, DECREASE) → 2, BTC_UP_BTC_D_DOWN
  - (INCREASE, RANGE) → 3, BTC_UP_BTC_D_RANGE
  - (DECREASE, INCREASE) → 4, BTC_DOWN_BTC_D_UP
  - (DECREASE, DECREASE) → 5, BTC_DOWN_BTC_D_DOWN
  - (DECREASE, RANGE) → 6, BTC_DOWN_BTC_D_RANGE
  - (RANGE, INCREASE) → 7, BTC_RANGE_BTC_D_UP
  - (RANGE, DECREASE) → 8, BTC_RANGE_BTC_D_DOWN
  - (RANGE, RANGE) → 9, BTC_RANGE_BTC_D_RANGE
- **Source**: `app/analysis/u08_scenario.py`, `SCANNER_MASTER_ROADMAP.md` §10, `KILO_MIGRATION_AUDIT.md` §U08

### 2D. 27-cell Matrix (Combined)
- **NOT FOUND as a single 27-cell entity**: There is no single "27-cell Matrix" data structure combining Stage 7 and Stage 8 matrices. Each stage has its own 9-scenario matrix (9+9=18 scenarios across both). The "27" count comes from narratives (9×3=27 per stage, 27 total per stage).
- **Stage 7 narratives**: 9 scenarios × 3 patterns = 27 texts in `app/analysis/narratives.py`
- **Stage 8 narratives**: 9 scenarios × 3 patterns = 27 patterns in `app/analysis/u08_narratives.py`

---

## PHASE 3 — TELEGRAM OUTPUT FLOW (Stages 7-12)

### Stage 7 (Total + USDT.D) — Telegram Output Flow
1. User request → BotRunner → run_stage7/run_u07
2. Range analysis → Scenario Matrix lookup (9 scenarios) → Narrative selection (27 patterns)
3. **No Telegram-specific output module found for Stage 7**: `app/analysis/stage10_telegram.py` is for Stage 10. Stage 7 has no dedicated Telegram formatter file.
4. The narrative text (Persian) would be the user-facing output, but the exact Telegram formatting for Stage 7 is **OPEN / NOT AGREED** in the current codebase.

### Stage 8 (BTC + BTC.D) — Telegram Output Flow
1. User request → run_cell_08
2. BTC/BTC.D context analysis → Cell 8 scenario → Narrative selection (27 patterns with {pattern, title, text})
3. **No Telegram-specific output module found for Stage 8**. `app/analysis/u08_narratives.py` provides the narrative content but no Telegram formatter.
4. **OPEN / NOT AGREED**: Stage 8 Telegram output format is not defined in any Stage 7-12 roadmap or implementation file.

### Stage 9 (Smart Market Participation) — Telegram Output Flow
1. User request → execute_u09
2. U09 produces `build_message()` — a compact 5-line message
3. **No dedicated Telegram formatter for Stage 9** found in implementation.
4. `KILO_MIGRATION_AUDIT.md` (line 651-654) describes the U09 message contract: exactly 5 lines, 24h movements only, Persian labels (📊 MARKET PARTICIPATION, ₿ BTC Price, 🔷 ETH Price, 🔹 TOP10 ALT MC, ◈ BROAD 11–125 MC)
5. **IMPLEMENTED**: `app/market/u09_engine.py` contains `build_message()`. **NOT YET READ in this audit** but referenced in KILO_ANALYSIS.md and KILO_MIGRATION_AUDIT.md.

### Stage 10 (Dynamic Top 10) — Telegram Output Flow
- **EXPLICITLY AGREED** structure per `STAGE_10_DYNAMIC_TOP10_ROADMAP.md` §19:
```
🏆 TOP 10 MARKET CAP

2. SOL

   SOLUSDT   +1.84%
   Volume:   284.6M USDT
   Source:   Binance

   SOLBTC    +0.72%
   Source:   Binance
```
- **Implemented in**: `app/analysis/stage10_telegram.py:56-176` (TelegramFormatter.format_top10)
- **Section order**: Header → Rank + Symbol → USDT change → USDT Volume → USDT Source/Fallback → BTC change → BTC Source/Fallback
- **Source/Fallback display** per §11: `Source: <exchange>` (no fallback) or `Fallback from: <exchange>` (fallback used)
- **Volume**: Only for USDT pair, labeled `Volume: <amount> USDT`
- **RTL/LTR**: `app/analysis/stage10_telegram.py:157-165` (check_rtl_safety — currently returns True always, not fully implemented)

### Stage 11 (Strong Movers) — Telegram Output Flow
- **Structure** (per Stage 11 §22/§24, implemented in `app/analysis/stage11_strong_movers.py:441-479`):
```
🏆 5 STRONG MOVERS
⚠️ [warning]

1. SOL (Rank 15)

   +5.50%
   SOLUSDT
   Volume: 200.0M USDT
   Source: Binance

   +1.20%
   SOLBTC
   Source: Binance
```
- **Section order**: Header → Warning → Rank + Symbol → USDT change → USDT pair → USDT Volume → USDT Source/Fallback → BTC change → BTC pair → BTC Source/Fallback
- **Rank shown**: Yes (e.g., "(Rank 15)")

### Stage 12 (Top 3 Reliable Movers) — Telegram Output Flow
- **Structure** per `STAGE_12_TOP_3_RELIABLE_MOVERS_ROADMAP.md` §19:
```
1. SOLUSDT +8.4%
   Volume: ...
   Exchange: Binance
```
- **Implemented in**: `app/analysis/stage12_top3.py:482-526` (format_top3_telegram)
- **Actual output structure** (more detailed than roadmap example):
```
🏆 TOP 3 RELIABLE MOVERS
⚠️ [warning]

1. SOL

   +5.50%
   SOLUSDT
   Volume: 200.0M USDT
   Source: Binance
```
- **CONFLICT/INCONSISTENCY**: Stage 12 roadmap §19 shows format `1. SOLUSDT +8.4%` (single line), but implementation `format_top3_telegram` shows `1. SOL` then `+5.50%` then `SOLUSDT` on separate lines. The roadmap's compact example differs from the implementation's expanded format. This is a CONFLICT.

---

## PHASE 4 — SCENARIO / MATRIX / MEMORY CONTRACT

### Scenario Contracts
| Stage | Scenarios | Patterns | Source |
|-------|-----------|----------|--------|
| 7 (U07) | 9 | 3 per scenario = 27 | `app/analysis/narratives.py` + `app/analysis/matrix.py` |
| 8 (Cell 8) | 9 | 3 per scenario = 27 | `app/analysis/u08_scenario.py` + `app/analysis/u08_narratives.py` |
| 9 | None | N/A | `STAGE_9` — no scenario/matrix per roadmap |
| 10 | None | N/A | `STAGE_10` — no scenario/matrix per roadmap |
| 11 | None | N/A | `STAGE_11` — no scenario/matrix per roadmap |
| 12 | None | N/A | `STAGE_12` — no scenario/matrix per roadmap |

### Variation / Memory / History
- **NOT FOUND**: No anti-repetition rules, variation selection mechanism, or output history/memory system found in the codebase for Stages 7-12.
- **pattern_index** (1, 2, or 3) is the only variation mechanism for narratives, per `app/analysis/narratives.py:90-120` (select_narrative) and `app/analysis/engine.py:174-186`.
- **OPEN**: How narrative variation is selected for user-facing output is NOT specified in any Stage 7-12 roadmap. pattern_index appears to be a parameter but its selection logic for end users is undefined.

### Anti-Repetition Rules
- **NOT FOUND**: No anti-repetition mechanism found in any Stage 7-12 file.

---

## PHASE 5 — TELEGRAM INTERACTION (Stages 7-12)

### Commands
- **EXPLICITLY AGREED**: Only `/top3` and `/help` — `app/bot/telegram.py:41-42`, `app/bot/config.py:8-9`
- **NOT FOUND**: Stage 7-12 roadmaps do NOT specify any Telegram commands. The command definitions are in the bot implementation only.

### Buttons / Callbacks
- **NOT FOUND**: No inline keyboard buttons, callback queries, or navigation buttons found in any Stage 7-12 implementation or roadmap.

### Navigation
- **NOT FOUND**: No navigation flow (beyond `/top3` → response) found for Stages 7-12.

### Error/Retry Behavior
- **PARTIALLY FOUND**: Exchange fallback mechanism serves as a data-level retry (`ExchangeRouter.route` at `stage10_router.py:121-161`). Bot-level error/retry behavior is NOT specified.

---

## PHASE 6 — EXPLICITLY FORBIDDEN OUTPUT BEHAVIOR

### Forbidden (All Stages 7-12):
1. **Trading signals**: entry, exit, long, short, buy/sell, trade recommendation
2. **Scenario/Matrix/Narrative generation** (Stages 10-12 specifically)
3. **Generic Intelligence conclusions** (Stages 10-12)
4. **Fabricated data**: prices, volume, timestamps, sources, pairs
5. **Fake BTC pairs**: BTCBTC, BTC, FAKEBTC, etc.
6. **Lower-priority exchange fallback** (Stages 10-12)
7. **24h volume substitution** when other timeframe requested (Stages 10-12)
8. **BTC volume display** (Stages 10-12)
9. **Independent ranking universe** (Stages 10-12)
10. **Order Book dependency** (Stages 10-12, unless approved contract requires)
11. **Invented third metric** (Stages 11-12)
12. **Three-month historical data requirement** (Stages 11-12)

---

## PHASE 7 — IMPLEMENTED BUT NOT EXPLICITLY AGREED

1. **HELP_TEXT in bot**: `app/bot/config.py:11-18` — partial warning, no scenario/matrix/narrative content
2. **TelegramBot class**: `app/bot/telegram.py` — only `/top3` and `/help` handlers, parse_mode="HTML"
3. **BotRunner._collect_ranking_data**: `app/bot/runner.py:57-92` — uses CoinGecko API directly (not Kitchen/U06.5)
4. **BotRunner._collect_pair_data**: `app/bot/runner.py:94-135` — uses local historical candle data
5. **format_top10_telegram** convenience function: `app/analysis/stage10_telegram.py:168-176`
6. **check_rtl_safety**: `app/analysis/stage10_telegram.py:157-165` — currently a stub (always returns True)
7. **TOP3_HEADER constant**: `app/analysis/stage12_top3.py:142` — `"🏆 TOP 3 RELIABLE MOVERS"` (roadmap doesn't specify exact header emoji/text)
8. **Stage 11 STRONG_MOVERS_HEADER**: `app/analysis/stage11_strong_movers.py:46` — `"🏆 5 STRONG MOVERS"` (roadmap doesn't specify exact header)
9. **Rank display in Stage 11**: `(Rank N)` suffix in `stage11_strong_movers.py:455` — not in roadmap
10. **Stage 12 format_top3_telegram format**: Multi-line structure differs from roadmap §19 compact format
11. **BotRunner handle_command**: `app/bot/runner.py:39-44` — returns "Unknown command" for unrecognized commands
12. **Exchange enum values**: `app/analysis/stage10_consumer.py:26-34` — English names (Binance, OKX, etc.) — not specified in Persian roadmaps
13. **DISPLAY_FALLBACK_PRIORITY list**: `app/analysis/stage10_consumer.py:37-46` — Python enum, not in Persian roadmaps as code

---

## PHASE 8 — OPEN / NOT AGREED

1. **Stage 7-9 Telegram output format**: No formatter or output contract found for Stage 7, 8, or 9
2. **Narrative selection logic for end users**: How pattern_index (1/2/3) is selected for user-facing output — NOT specified
3. **Stage 9 build_message exact format**: Referenced in KILO_MIGRATION_AUDIT but not verified in code in this audit
4. **Anti-repetition rules**: No mechanism found for preventing repetitive narrative patterns
5. **Output memory/history**: No history/memory mechanism found for Stages 7-12
6. **Stage 7-9 bot commands**: Only `/top3` exists; no stage-specific commands found
7. **Inline keyboard/button interactions**: Not found for any stage
8. **Stage 12 exact Telegram format**: CONFLICT between roadmap (compact) and implementation (expanded)
9. **HELP_TEXT warning completeness**: Partial vs. full warning
10. **Stage 13 input**: What data Stage 13 will consume is undefined (Stage 13 does not exist)

---

## PHASE 9 — CONFLICTS / INCONSISTENCIES

| # | Description | Files |
|---|-------------|-------|
| 1 | Stage 12 output format: roadmap §19 shows `1. SOLUSDT +8.4%` on one line, implementation splits into multiple lines | `STAGE_12_TOP_3_RELIABLE_MOVERS_ROADMAP.md:364-376` vs `stage12_top3.py:482-526` |
| 2 | HELP_TEXT warning: bot config has truncated warning vs. full SCANNER_WARNING constant | `app/bot/config.py:16-18` vs `app/analysis/stage11_strong_movers.py:36-44` |
| 3 | No Stage 7/8/9 Telegram output formatter exists despite narratives being locked | Narratives exist but no output path to Telegram |
| 4 | Stage 10 roadmap §19 header is `🏆 TOP 10 MARKET CAP`; implementation `stage10_telegram.py:30` matches | No conflict — both match |
| 5 | `check_rtl_safety` always returns True (not a real RTL check) despite RTL/LTR requirements | `app/analysis/stage10_telegram.py:157-165` vs multiple roadmap RTL requirements |
| 6 | BotRunner uses CoinGecko directly for ranking, but Stage 10 roadmap mandates Kitchen/U06.5 ranking | `app/bot/runner.py:58` vs `STAGE_10_DYNAMIC_TOP10_ROADMAP.md` §4.1 |

---

## PHASE 10 — NOT FOUND / REQUIRES DECISION

1. **Stage 7-12 individual command handlers** (e.g., `/total`, `/btc`, `/top10`, `/strongmovers`) — NOT FOUND
2. **Inline keyboards for user interaction** — NOT FOUND
3. **Callback/navigation framework** — NOT FOUND
4. **Stage 7-9 Telegram output formatters** — NOT FOUND
5. **Anti-repetition / variation selection rules** — NOT FOUND
6. **Output memory/history mechanism** — NOT FOUND
7. **Stage 13 specification** — NOT FOUND (by design)
8. **27-cell Matrix as a unified structure** — NOT FOUND (only 9+9=18 scenario cells across two stages)

---

## PHASE 11 — STAGE 13 INPUT SUMMARY

### MUST PRESERVE (from Stages 7-12)
- [ ] Exchange Display Fallback Priority (8 exchanges, fixed order)
- [ ] Selected exchange = Preferred Source (NOT Ranking Authority)
- [ ] Higher-priority-only fallback direction (no lower-priority fallback)
- [ ] BTC Pair Contract (real pair → fallback → approved Kitchen → unavailable)
- [ ] Fake BTC pair prevention (BTCBTC, BTC, FAKEBTC forbidden)
- [ ] USDT pair + Volume contract (USDT only, requested timeframe, no fabrication)
- [ ] Full SCANNER_WARNING text (exact byte-for-byte)
- [ ] No trading signals (entry/exit/long/short/buy/sell)
- [ ] No scenario/matrix/narrative/generic intelligence (Stages 10-12)
- [ ] Persian RTL/LTR readability requirements
- [ ] Source/Fallback display semantics (`Source: <exchange>` / `Fallback from: <exchange>`)
- [ ] Volume only for USDT pair (never BTC)
- [ ] Kitchen/U06.5 as ranking authority (no independent exchange ranking)
- [ ] Dynamic refresh (no stale cache)
- [ ] All 27 Stage 7 narratives (locked Persian texts)
- [ ] All 27 Stage 8 narratives (locked Persian texts)
- [ ] Stage 7 scenario matrix (9 scenarios, exact mapping)
- [ ] Stage 8 scenario matrix (9 scenarios, exact mapping)
- [ ] Timeframe validation rules (including uppercase M = MONTH)
- [ ] Provider-supplied volume semantics (traded base-asset, no double counting)

### MUST NOT CHANGE
- [ ] Existing U06.5 business logic
- [ ] DISPLAY_FALLBACK_PRIORITY order
- [ ] Narrative texts (byte-for-byte)
- [ ] Scenario matrix mappings
- [ ] Exchange enum values and names
- [ ] Stage 10/11/12 existing output formatters (do not redesign)
- [ ] Safety locks (trading disabled)

### OPEN FOR STAGE 13 DESIGN
- [ ] Stage 13 scope and purpose (not defined)
- [ ] Whether Stage 13 has its own Telegram output or reuses Stage 10-12 formatters
- [ ] How Stage 13 inputs relate to existing pipeline (Dynamic Top 10 + 5 Strong Movers → ?)
- [ ] Stage 13 command/button/interaction design
- [ ] Whether narrative/matrix/scenario generation enters scope
- [ ] Whether Stage 13 introduces new data contracts or reuses existing ones
- [ ] Anti-repetition/output memory requirements (if any)
- [ ] Stage 13 output format and structure
- [ ] Whether Stage 13 continues the "no trading signal" constraint
- [ ] Stage 13 RTL/LTR requirements (assumed same)
- [ ] Whether Stage 13 needs new test artifacts (U13_*)
- [ ] Stage 13 scenario/matrix requirements (if any)
- [ ] 27-cell Matrix — whether it refers to combined Stage 7+8 scenarios or something new

---

## KEY SOURCE FILE INDEX

### Roadmaps
- `SCANNER_MASTER_ROADMAP.md` — Master roadmap (Stages 1-6, 7-12 overview)
- `STAGE_10_DYNAMIC_TOP10_ROADMAP.md` — Stage 10 full contract
- `STAGE_11_STRONG_MOVERS_ROADMAP_COMPLETE.md` — Stage 11 full contract
- `STAGE_12_TOP_3_RELIABLE_MOVERS_ROADMAP_COMPLETE.md` — Stage 12 full contract

### Implementation
- `app/bot/telegram.py` — Telegram bot (commands: /top3, /help)
- `app/bot/runner.py` — Bot runner
- `app/bot/config.py` — Bot config (BOT_TOKEN, HELP_TEXT, COMMANDs)
- `app/analysis/stage10_telegram.py` — Stage 10 Telegram formatter
- `app/analysis/stage10_consumer.py` — Stage 10 (Exchange, DISPLAY_FALLBACK_PRIORITY, get_dynamic_top10)
- `app/analysis/stage10_router.py` — Stage 10 ExchangeRouter
- `app/analysis/stage10_usdt.py` — Stage 10 USDT pair processor
- `app/analysis/stage10_btc.py` — Stage 10 BTC pair processor
- `app/analysis/stage11_strong_movers.py` — Stage 11 Strong Movers (SCANNER_WARNING, formatter, orchestrator)
- `app/analysis/stage12_top3.py` — Stage 12 Top 3 (TOP3_HEADER, formatter, orchestrator)
- `app/analysis/matrix.py` — Stage 7 scenario matrix (9 scenarios)
- `app/analysis/narratives.py` — Stage 7 narratives (27 locked texts)
- `app/analysis/u08_scenario.py` — Stage 8 scenario matrix (9 scenarios)
- `app/analysis/u08_narratives.py` — Stage 8 narratives (27 locked patterns)
- `app/analysis/engine.py` — Stage 7 main engine (run_u07)
- `app/analysis/enums.py` — Shared enums (Direction, Context, ScenarioType, etc.)
- `app/analysis/timeframe.py` — Timeframe parser
- `app/analysis/config.py` — RangeConfig
- `app/analysis/range_engine.py` — Range analysis engine
- `app/analysis/metrics.py` — Movement metrics
- `app/analysis/validation.py` — Input validation
- `app/analysis/regression.py` — U07 regression tests

### Tests
- `tests/unit/test_u10_unit_5_telegram.py` — Stage 10 Telegram tests
- `tests/unit/test_u11_unit_4_output.py` — Stage 11 output tests
- `tests/unit/test_u12_unit_4_output.py` — Stage 12 output tests
- `tests/unit/test_u07_unit_3_scenario_matrix.py` — Stage 7 matrix tests
- `tests/unit/test_bot_runner.py` — Bot integration tests
- `tests/unit/test_u12_unit_1_contract.py` — Stage 12 contract tests
- `tests/unit/test_u11_unit_1_contract.py` — Stage 11 contract tests
- `tests/unit/test_u10_unit_1_contract.py` — Stage 10 contract tests
- `tests/unit/test_u08_unit_3_scenario.py` — Stage 8 scenario tests

### Reference
- `KILO_ANALYSIS.md` — Notebook analysis (describes all units)
- `KILO_MIGRATION_AUDIT.md` — Migration audit (describes all units in detail)
- `Kitchen Assistant v3.1.4.ipynb` — Original notebook (reference source-of-truth for approved texts)

---

*Audit completed read-only. No files modified, created, or deleted.*
*Stage 13 is NOT implemented. This report is INPUT ONLY for Stage 13 design.*
