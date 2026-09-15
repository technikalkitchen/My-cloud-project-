# Stage 10 — Dynamic Top 10 Market-Cap View
## Professional Roadmap / Kilo Implementation Contract

**Status:** PLANNED  
**Stage:** 10  
**Subsystem:** Operational Scanner  
**Depends on:** U06.5 Market Data Foundation + Stage 7 + Stage 8 + Stage 9  
**Purpose:** Dynamic display of the current Kitchen Top-10 market-cap assets, excluding BTC, with user-selectable data view and explicit exchange/fallback provenance.

---

## 0. Stage Objective

Stage 10 adds a Dynamic Top 10 Market-Cap view to the Scanner.

The stage MUST:

1. Refresh/recompute the current Kitchen Dynamic Top-125 on every user request.
2. Select current market-cap ranks 2–10.
3. Exclude BTC (rank 1) from display.
4. Display the nine non-BTC assets corresponding to ranks 2–10.
5. Let the user choose **Kitchen Data** or **Exchange Data** before the result is sent.
6. In Exchange Data mode, let the user select a preferred exchange.
7. Treat the selected exchange as the preferred display source.
8. If it cannot provide valid data, use the agreed higher-priority fallback mechanism.
9. Handle USDT and BTC pairs explicitly and independently, while preferring one common fallback exchange for the same asset whenever valid.
10. Display Volume only for the USDT pair.
11. Never fabricate pairs, prices, volume, timestamps, or sources.
12. Preserve Scanner-wide safety rules.
13. Produce information only; no trading signals, recommendations, scenarios, matrices, or narratives.

---

## 1. Source-of-Truth Hierarchy

Before implementation Kilo MUST study:

1. `SCANNER_MASTER_ROADMAP.md`
2. `Kitchen Assistant v3.1.4.ipynb`
3. `KILO_ANALYSIS.md`
4. `KILO_MIGRATION_AUDIT.md`
5. `README.md`

`SCANNER_MASTER_ROADMAP.md` is the primary Scanner roadmap.

`KILO_MIGRATION_AUDIT.md` is the migration-preservation reference.

Kilo MUST NOT invent historical requirements where the source material does not define them.

Stage 10 MUST consume existing U06.5 capabilities rather than duplicating or replacing them.

---

## 2. Core Architecture

Stage 10 separates **ranking authority** from **display-data source**.

### 2.1 Ranking / Universe Authority

The authoritative source for determining which assets are Top 10 is Kitchen.

```text
Exchange Layer + Global Providers
            ↓
U06.5 validation / reliability / aggregation
            ↓
Kitchen reference price
            ↓
validated circulating supply
            ↓
Kitchen market cap
            ↓
Dynamic Top-125
            ↓
calculated ranks
            ↓
ranks 2–10
            ↓
Stage 10
```

Stage 10 MUST NOT obtain an independent Top-10 ranking directly from CMC, CoinGecko, Binance, OKX, or another exchange.

CMC/CoinGecko remain upstream providers/evidence according to U06.5.

Stage 10 MUST NOT create a second competing ranking universe.

### 2.2 Display Data Source

Once Kitchen has selected ranks 2–10, display market data may come from:

- Kitchen View, or
- User-selected Exchange View.

These are separate concerns.

---

## 3. Existing U06.5 Foundation

Stage 10 MUST reuse the existing U06.5 Market Data Foundation.

The existing eight core public spot exchanges are:

1. Binance
2. OKX
3. Bybit
4. KuCoin
5. Coinbase
6. Gate
7. Upbit
8. Bitget

U06.5 already provides:

- provider normalization
- identity/numeric/timestamp/freshness validation
- outlier filtering
- reliability scoring
- reliability-weighted reference price
- validated circulating supply
- Kitchen market-cap calculation
- Dynamic Top-125
- deterministic ranking
- asset rank metadata

Relevant existing concepts include:

- `dynamic_rank_assets(valid_assets)`
- `calculated_rank`
- `provider_rank`
- `rank_consistency`
- `TARGET_EXCHANGE_COUNT = 8`
- `MIN_VALIDATED_EXCHANGE_COUNT = 7`
- `PROVIDER_PRIORITY`
- `MULTI_EXCHANGE_SPECS`

The existing U06.5 business logic MUST NOT be rewritten merely to implement Stage 10.

---

## 4. Priority Distinction — Critical

There are two different concepts of priority.

### 4.1 Kitchen Calculation Reliability

U06.5 uses dynamic reliability scoring and reliability-weighted aggregation.

Stage 10 MUST NOT replace that internal reliability model with a fixed exchange-quality ranking.

### 4.2 Stage 10 Display Fallback Priority

For user-selected Exchange View, the selected exchange is the preferred display source.

If it cannot provide valid data, Stage 10 uses the agreed display fallback order:

```text
1. Binance
2. OKX
3. Bybit
4. KuCoin
5. Coinbase
6. Gate
7. Upbit
8. Bitget
```

When the user selects an exchange, fallback proceeds toward exchanges with **higher system priority**.

Example:

```text
Selected Bitget (#8)
→ Upbit (#7)
→ Gate (#6)
→ Coinbase (#5)
→ KuCoin (#4)
→ Bybit (#3)
→ OKX (#2)
→ Binance (#1)
```

Example:

```text
Selected OKX (#2)
→ Binance (#1)
```

Example:

```text
Selected Binance (#1)
→ no higher-priority exchange exists
```

This Display Fallback Priority MUST NOT alter U06.5's internal reliability-weighting algorithm.

---

## 5. User Data-View Selection

Before sending the result, the user chooses:

### Option A — Kitchen Data

Display source:

`Source: Kitchen`

There is **no exchange fallback** for Kitchen View.

Kitchen View MUST NOT silently switch to an exchange.

### Option B — Exchange Data

The user selects one of the eight exchanges.

The selected exchange becomes:

`Preferred Source`

User preference does NOT change the Kitchen ranking.

---

## 6. User-Selected Exchange Contract

The meanings are:

```text
Selected Exchange = Preferred Display Source
```

NOT:

```text
Selected Exchange = Ranking Authority
```

Example:

User selects OKX.

Kitchen still determines ranks 2–10.

OKX is then used for display data for those assets.

---

## 7. Exchange Fallback Contract

For each required market-data item:

1. Try the user-selected exchange first.
2. Validate the result.
3. If unavailable/invalid/stale/incomplete, move through the higher-priority Display Fallback order.
4. Never fabricate data.
5. If no valid eligible source exists, return an explicit unavailable state.

Fallback is not allowed to move toward lower-priority exchanges.

---

## 8. Per-Asset / Per-Field Fallback

USDT and BTC pair data are independently validated.

However, for the same asset, the system SHOULD keep related fields on the same exchange whenever possible.

Preferred behavior:

```text
same asset
→ same exchange
→ valid USDT pair
→ valid BTC pair
→ valid volume
```

If this cannot be achieved without using invalid data, validity wins and field-level fallback is allowed.

Internal provenance MUST remain available for every field.

---

## 9. Fallback Cohesion Rule

For the same asset, if both USDT and BTC pairs require fallback:

**Prefer the same fallback exchange for both whenever that exchange can validly provide both.**

Example:

```text
Selected: Binance

SOLUSDT
Binance ❌
OKX ✅

SOLBTC
Binance ❌
OKX ✅
```

Preferred result:

```text
SOLUSDT → OKX
SOLBTC  → OKX
```

If the USDT fallback is OKX but OKX does not have a valid SOLBTC, continue BTC-pair resolution according to the Display Fallback Priority.

Do NOT force source unification at the expense of validity.

---

## 10. USDT Pair Contract

For every displayed asset, attempt:

`COINUSDT`

The USDT pair supplies:

- USDT price movement
- displayed Volume
- the primary source/fallback label for the USDT block

Volume MUST refer only to the USDT pair.

No BTC-pair volume is displayed.

Volume MUST correspond to the requested timeframe/window.

The existing U06.5 Volume Contract MUST be preserved:

- provider-supplied traded base-asset volume
- each trade counted once
- no buyer/seller double counting
- no `close * volume` fabrication
- no market-cap-derived volume
- no interpolation/fabrication

A generic 24h volume MUST NOT silently replace the requested timeframe.

---

## 11. Source / Fallback Display Contract

If the user-selected exchange supplies valid data:

```text
Source: Binance
```

If fallback was required:

```text
Fallback from: OKX
```

Do NOT display both `Source` and `Fallback from` for the same field.

The user already knows which exchange was selected.

`Fallback from: OKX` means OKX became the actual source after the preferred exchange could not provide valid data.

---

## 12. Volume Display Contract

Volume belongs to the USDT pair.

Do NOT create a separate Volume Source line.

Correct structure:

```text
SOLUSDT   +1.84%
Volume:   284.6M USDT
Source:   Binance

SOLBTC    +0.72%
Source:   Binance
```

If USDT falls back:

```text
SOLUSDT   +1.84%
Volume:   284.6M USDT
Fallback from: OKX

SOLBTC    +0.72%
Fallback from: OKX
```

Volume MUST NOT be repeated for the BTC pair.

If USDT and BTC come from the same fallback exchange, each relevant field may show the same fallback source.

---

## 13. BTC Pair Contract

For every non-BTC asset, the display may include:

`COINBTC`

### Step 1 — Selected Exchange

First check whether the real BTC pair exists and is valid on the user-selected exchange.

If valid, use it.

### Step 2 — Exchange Fallback

If the selected exchange has no valid BTC pair, search eligible fallback exchanges using the same Display Fallback Priority.

### Step 3 — Fallback Cohesion

If the USDT pair already resolved to a valid fallback exchange, prefer that exchange for the BTC pair when possible.

Example:

```text
SOLUSDT → OKX
```

Then try:

```text
SOLBTC → OKX
```

before continuing to the next eligible higher-priority fallback if needed.

### Step 4 — Approved Kitchen Calculation

If no valid real exchange BTC pair exists, use the previously approved/calculated Kitchen BTC-pair value only where an existing Kitchen contract explicitly permits it.

Stage 10 MUST NOT invent a new BTC calculation method.

### Step 5 — Unavailable

If neither a valid exchange BTC pair nor an approved Kitchen calculated value exists:

```text
SOLBTC Unavailable
```

Fake pairs are forbidden.

---

## 14. BTC Pair Source Display

USDT and BTC source/fallback status must remain independently traceable.

### Both from selected exchange

```text
SOLUSDT   +1.84%
Volume:   284.6M USDT
Source:   Binance

SOLBTC    +0.72%
Source:   Binance
```

### USDT fallback, BTC remains on selected exchange

```text
SOLUSDT   +1.84%
Volume:   284.6M USDT
Fallback from: OKX

SOLBTC    +0.72%
Source:   Binance
```

### Both use same fallback

```text
SOLUSDT   +1.84%
Volume:   284.6M USDT
Fallback from: OKX

SOLBTC    +0.72%
Fallback from: OKX
```

### Different fallback required

```text
SOLUSDT   +1.84%
Volume:   284.6M USDT
Fallback from: OKX

SOLBTC    +0.72%
Fallback from: Bybit
```

The last case is allowed only when actual valid-data availability requires it.

---

## 15. Kitchen View Output

If Kitchen Data is selected:

```text
Source: Kitchen
```

No Exchange fallback is applied.

Kitchen View MUST use existing Kitchen-calculated data contracts.

---

## 16. Dynamic Refresh Requirement

Stage 10 MUST be dynamic.

Every user request must refresh/recompute the current Kitchen Dynamic Top-125.

A static Top-10 cache MUST NOT be treated as permanently current.

Example:

At T0:

```text
ETH rank 2
XRP rank 3
SOL rank 4
```

At T1:

```text
SOL rank 2
ETH rank 3
XRP rank 4
```

The T1 request MUST reflect the new Kitchen ranking.

---

## 17. Timeframe Contract

Supported timeframes must remain compatible with the existing foundation:

- 1m
- 5m
- 15m
- 1h
- 4h
- 1d

For every displayed asset:

- USDT movement
- BTC movement
- Volume

must use the requested timeframe/window according to the existing data contract.

Do NOT silently substitute another timeframe.

---

## 18. Top-10 Selection Rules

Use the current Kitchen Dynamic Top-125.

Select:

```text
rank 2
rank 3
rank 4
rank 5
rank 6
rank 7
rank 8
rank 9
rank 10
```

BTC rank 1 is excluded from display.

The stage is still called Dynamic Top 10 because it represents the current Top-10 market-cap ranking while intentionally omitting BTC from the displayed asset blocks.

---

## 19. Expected Telegram Structure

Example:

```text
🏆 TOP 10 MARKET CAP

2. SOL

   SOLUSDT   +1.84%
   Volume:   284.6M USDT
   Source:   Binance

   SOLBTC    +0.72%
   Source:   Binance
```

Fallback example:

```text
2. SOL

   SOLUSDT   +1.84%
   Volume:   284.6M USDT
   Fallback from: OKX

   SOLBTC    +0.72%
   Fallback from: OKX
```

The final typography may be adapted for Telegram readability, but the semantic fields MUST remain.

---

## 20. RTL / LTR Rules

Telegram output must remain readable in Persian RTL context.

MUST test:

- Persian text
- Latin tickers
- percentages
- numbers
- exchange names
- Source/Fallback labels

Ticker symbols should preferably occupy dedicated lines.

Avoid mixed-direction formatting that causes tickers, percentages, or exchange names to visually reorder.

Do not begin a Persian message with an uncontrolled English word.

---

## 21. No Trading Signal

Stage 10 is informational only.

It MUST NOT introduce:

- Entry
- Exit
- Long
- Short
- Buy recommendation
- Sell recommendation
- Trade recommendation
- Scenario
- Scenario Matrix
- Narrative
- Generic Intelligence conclusion

---

## 22. Scanner Warning

Stage 10 must remain compatible with the existing Scanner-wide warning:

`⚠️ توجه: اطلاعات و انتخاب‌های ارائه‌شده توسط Scanner به‌هیچ‌وجه سیگنال ورود یا خروج از معامله نیستند ...`

Do not remove or weaken the existing warning.

Do not create a contradictory duplicate warning.

---

## 23. Data Validity Rules

No displayed data may be fabricated.

Invalid conditions include:

- missing pair
- wrong symbol identity
- stale timestamp
- invalid numeric data
- invalid price
- invalid volume
- missing requested timeframe
- fabricated BTC pair
- fabricated volume
- silent unsupported provider substitution
- unsupported calculation

Invalid data must trigger fallback or an explicit unavailable state.

---

## 24. Internal Provenance Contract

Even when Telegram output is concise, internal result data MUST retain enough provenance to distinguish:

- requested exchange
- actual exchange
- whether fallback occurred
- fallback exchange
- pair
- timeframe
- data timestamp
- validation status

User-facing output does not need to expose every internal field.

Internal provenance MUST NOT be discarded.

---

## 25. Suggested Stage 10 Result Contract

Conceptually:

```text
Stage10Result
├── requested_view
│   ├── KITCHEN
│   └── EXCHANGE
├── selected_exchange
├── display_fallback_priority
├── timeframe
├── ranking_snapshot
│   ├── kitchen_rank
│   ├── asset_id
│   └── symbol
└── assets[]
    ├── kitchen_rank
    ├── symbol
    ├── usdt_pair
    │   ├── change
    │   ├── volume
    │   ├── requested_exchange
    │   ├── actual_exchange
    │   ├── fallback_used
    │   ├── timestamp
    │   └── validation
    └── btc_pair
        ├── change
        ├── requested_exchange
        ├── actual_exchange
        ├── fallback_used
        ├── calculated_kitchen_value
        ├── timestamp
        └── validation
```

Follow existing project schemas and avoid unnecessary duplicate models.

---

## 26. Unit Breakdown

### Unit 10.1 — Stage Contract + Dynamic Top-10 Consumer

Implement:

- Stage 10 configuration
- Kitchen/Exchange View selection
- current Dynamic Top-125 refresh
- ranks 2–10 selection
- BTC exclusion
- dependency on U06.5 calculated ranking
- no independent CMC/exchange ranking

Test:

- rank 1 excluded
- ranks 2–10 selected
- changed ranking appears on a new request
- no permanently stale Top-10 list

### Unit 10.2 — Exchange Selection + Fallback Router

Implement:

- eight exchange choices
- selected exchange as Preferred Source
- Display Fallback Priority
- higher-priority fallback direction
- no lower-priority fallback
- per-asset/per-field validation
- fallback provenance

Test:

- Binance
- OKX
- Bitget
- selected source succeeds
- selected source fails
- one-step fallback
- multi-step fallback
- no invalid fallback

### Unit 10.3 — USDT Pair + Volume

Implement:

- USDT pair
- requested timeframe
- provider-supplied volume
- Volume only for USDT
- Source/Fallback presentation
- internal provenance

Test:

- valid pair
- missing pair
- stale data
- invalid data
- correct timeframe
- no 24h substitution
- no fabricated volume
- correct Source
- correct Fallback from

### Unit 10.4 — BTC Pair + Fallback Cohesion

Implement:

- selected-exchange BTC pair check
- fallback BTC pair search
- prefer USDT fallback exchange when valid
- independent BTC validation
- approved Kitchen BTC calculation only where already defined
- Unavailable state
- fake-pair prevention

Test:

- BTC pair on selected exchange
- BTC pair missing
- BTC pair on USDT fallback exchange
- BTC pair only on another eligible higher-priority exchange
- no BTC pair anywhere
- approved Kitchen calculation fallback
- fake-pair prevention
- provenance

### Unit 10.5 — Telegram Output + RTL/LTR

Implement:

- Top 10 message formatting
- asset blocks
- USDT pair
- Volume
- Source/Fallback
- BTC pair
- BTC Source/Fallback
- RTL/LTR safety
- timeframe consistency
- Scanner warning compatibility

Test:

- normal Source
- fallback
- mixed Source/Fallback
- same fallback
- different fallback
- Kitchen View
- Exchange View
- Persian + ticker + numbers
- no duplicated Volume Source

### Unit 10.6 — Full Integration + Regression

Run:

- Stage 10 tests
- U06.5 regression
- Stage 7 regression
- Stage 8 regression
- Stage 9 regression
- relevant Scanner regression
- safe real-data smoke test
- no trading execution

Verify:

- ranking
- dynamic refresh
- source
- fallback
- volume
- timeframe
- BTC pair
- fake-pair prevention
- RTL/LTR
- safety
- no trade signal

---

## 27. Explicit Acceptance Criteria

Stage 10 is VERIFIED only if:

1. Current Top-125 comes from Kitchen/U06.5.
2. Current ranks 2–10 are selected dynamically.
3. BTC rank 1 is excluded from display.
4. No independent exchange/CMC ranking is introduced.
5. Kitchen View exists.
6. Exchange View exists.
7. User can select a preferred exchange.
8. Selected exchange is the Preferred Source.
9. Fallback follows the agreed higher-priority direction.
10. Lower-priority fallback is not used.
11. USDT pair data are valid.
12. USDT Volume is valid and window-correct.
13. Volume is displayed only for USDT.
14. `Source` is shown only when the requested source was actually used.
15. Fallback display uses only `Fallback from: <exchange>`.
16. USDT and BTC Pair provenance are independently traceable.
17. The same fallback exchange is preferred for both pairs when possible.
18. BTC Pair is checked on the selected exchange first.
19. BTC Pair fallback uses the same Display Fallback Priority.
20. Approved Kitchen BTC calculation is used only according to an existing contract.
21. No fake BTC pair exists.
22. Unavailable data are explicitly handled.
23. No fabricated volume exists.
24. No fabricated price exists.
25. Requested timeframe is respected.
26. New requests can reflect changed rankings.
27. RTL/LTR output is readable.
28. Existing Scanner warning is preserved.
29. No trade signal is produced.
30. Existing stages remain unaffected.
31. Relevant regression tests pass.
32. Safe real-data smoke test passes where applicable.
33. No unrelated files are modified.

---

## 28. Regression Protection

Kilo MUST NOT modify business logic of:

- U06.5
- Stage 7
- Stage 8
- Stage 9

unless a real defect is demonstrated.

Stage 10 should consume their existing contracts.

Any compatibility change must be:

- minimal
- justified
- tested
- documented

---

## 29. Required Test Matrix

### View selection

- Kitchen
- Binance
- OKX
- Bybit
- KuCoin
- Coinbase
- Gate
- Upbit
- Bitget

### Source availability

- selected exchange valid
- selected exchange unavailable
- selected exchange stale
- selected exchange invalid

### Fallback

- one-step fallback
- multi-step fallback
- highest-priority fallback
- no eligible fallback
- no lower-priority fallback

### Pair availability

- USDT exists
- USDT missing
- BTC exists
- BTC missing
- BTC exists only on fallback
- BTC exists on same fallback as USDT
- BTC requires different fallback
- BTC unavailable everywhere

### Volume

- exact requested window
- provider-supplied volume
- no fabricated volume
- no BTC volume

### Dynamic ranking

- unchanged ranking
- changed ranking
- asset enters Top 10
- asset leaves Top 10
- BTC remains excluded

### Output

- Source
- Fallback from
- Kitchen
- same fallback
- different fallback
- RTL/LTR
- Telegram readability

---

## 30. Stage Execution Protocol

Kilo MUST execute Stage 10:

```text
Study
→ Plan
→ Implement
→ Test
→ Inspect
→ Fix
→ Re-test
→ Verify
→ Backup/Commit
→ Next Stage
```

Do NOT commit after every Unit.

Units may be implemented/tested independently, but the Stage checkpoint is committed only after final Stage verification.

---

## 31. Final Stage Audit

Before declaring Stage 10 complete, perform a read-only final audit of:

- ranking source
- ranks 2–10
- BTC exclusion
- view selection
- selected exchange
- fallback direction
- fallback provenance
- USDT pair
- BTC pair
- fallback cohesion
- Volume
- timeframe
- freshness
- fake-pair prevention
- RTL/LTR
- trading safety
- regression status
- modified files

No code changes during the read-only audit unless a real defect is discovered.

---

## 32. Stage 10 Artifacts

After successful verification, create according to project conventions:

- `ledgers/U10_LEDGER.md`
- `U10_AUDIT_METADATA.json`
- `U10_MANIFEST.json`
- `U10_SHA256.json`

Artifacts must document verified implementation and test state.

---

## 33. Git / Backup Policy

Only after implementation, tests, final audit, smoke test, and defect resolution are complete:

```text
git status
git diff
git add <only relevant Stage 10 files>
git commit
git push
```

NEVER use:

```text
git add .
```

Do not commit unrelated pre-existing files.

---

## 34. Explicit Non-Goals

Stage 10 MUST NOT introduce:

- independent market-cap ranking
- new ranking authority
- CMC direct Top-10 authority
- CoinGecko direct Top-10 authority
- fixed exchange reliability replacing U06.5
- TradingView
- fake BTC pairs
- fabricated volume
- fabricated prices
- order-book dependency
- trading signals
- entry/exit logic
- Long/Short logic
- scenarios
- matrices
- narratives
- generic intelligence
- trade recommendations

---

## 35. Final Architecture Summary

```text
User
  ↓
Select Data View
  ├── Kitchen
  │     ↓
  │   Current Kitchen Dynamic Top-125
  │     ↓
  │   Ranks 2–10
  │     ↓
  │   Kitchen data
  │
  └── Exchange
        ↓
      Select Preferred Exchange
        ↓
      Current Kitchen Dynamic Top-125
        ↓
      Ranks 2–10
        ↓
      Selected Exchange = Preferred Source
        ↓
      If invalid/unavailable:
      Higher-priority Display Fallback
        ↓
      USDT Pair + Volume
      BTC Pair
        ↓
      Prefer same fallback exchange for both pairs when possible
        ↓
      Validate
        ↓
      Preserve provenance
        ↓
      Telegram Output
```

### Final principles

**Ranking Authority:** Kitchen

**Exchange Display:** User-selected exchange

**Display Fallback:** Higher-priority exchanges

**Kitchen View:** No exchange fallback

**USDT Volume:** USDT pair only

**BTC Pair:**
Real selected-exchange pair
→ fallback exchange pair
→ approved Kitchen calculation
→ unavailable

**Fake Pair:** Forbidden

**Trading Signal:** Forbidden

**Dynamic:** Refresh/recompute on every request

The three concepts must never be merged:

1. **WHAT IS TOP?** → Kitchen Dynamic Top-125 / calculated rank
2. **WHERE DOES THE USER WANT MARKET DATA FROM?** → User-selected exchange
3. **WHAT HAPPENS IF IT IS UNAVAILABLE?** → Higher-priority Display Fallback
