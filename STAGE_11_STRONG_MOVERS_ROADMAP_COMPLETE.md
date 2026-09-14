# Stage 11 — Strong Movers Roadmap
## Kitchen Assistant — Scanner Subsystem
## Single-File Kilo Implementation Contract

> **This document is exclusively for Stage 11.**
> It is the complete Stage 11 roadmap and implementation contract for Kilo.
> Do not treat this file as a replacement for the Scanner Master Roadmap.
> Do not add requirements from other stages unless they are explicitly inherited
> here as dependencies/contracts required by Stage 11.

---

## 0. Stage Status and Authority

This file is the **official Stage 11 implementation roadmap** for Strong Movers.

Stage 11 must be treated as a separate, controlled stage.

The required lifecycle is:

```text
Study
→ Plan
→ Implement
→ Test
→ Inspect
→ Fix
→ Re-test
→ Verify
→ Backup / Commit
→ Next Stage
```

Do not start the next stage until Stage 11 is fully verified.

Do not re-implement or re-test completed Stage 10 business logic except where a focused compatibility/regression check is required.

---

# 1. Purpose

Stage 11 implements the Scanner's **5 Strong Movers** selection.

The Scanner must select **five strong and reliable assets from the Alt 11–125 candidate range**.

The selection must NOT be reduced to:

```text
Top 5 percentage gainers
```

The intended principle is:

```text
Strong Movement + Reliability
```

The purpose is to identify assets whose movement is strong enough to deserve attention while preserving data quality, volume quality, persistence, liquidity where valid data exists, BTC-relative strength where valid BTC data exists, and source reliability.

Stage 11 is an information/market-scanning subsystem.

It is NOT a trading strategy.

---

# 2. Source-of-Truth Hierarchy

Stage 11 must respect the existing Scanner architecture.

## 2.1 Primary roadmap authority

`SCANNER_MASTER_ROADMAP.md` is the primary Scanner roadmap.

## 2.2 Ranking authority

U06.5 / Kitchen Dynamic Top-125 remains the ranking authority.

Stage 11 must consume the already-calculated ranking.

Stage 11 must NOT create a competing ranking universe from:

- CMC
- CoinGecko
- Binance
- OKX
- Bybit
- another exchange
- another external ranking

The candidate universe must come from the existing Kitchen/U06.5 Dynamic Top-125.

## 2.3 Existing Stage 10 contract authority

The exchange-selection and fallback behavior already approved for Stage 10 is a shared Scanner contract.

Stage 11 MUST inherit and reuse that contract.

It must NOT create a second exchange-selection system.

---

# 3. Candidate Universe

The Strong Movers candidate universe is:

```text
U06.5 / Kitchen Dynamic Top-125
            ↓
exclude BTC rank 1
            ↓
candidate ranks 11–125
            ↓
Strong Movement + Reliability evaluation
            ↓
5 Strong Movers
```

## Mandatory rules

1. Candidate assets come from the current Dynamic Top-125.
2. Only ranks **11 through 125** are eligible for Strong Movers.
3. BTC rank 1 is not part of the Strong Movers candidate universe.
4. Stage 11 must not independently rank the market.
5. The candidate universe must remain dynamic.
6. A newly refreshed ranking must be respected on a new request.
7. The stage must not use a permanently cached list when the existing Scanner contract requires a fresh ranking.

If fewer than five candidates can be validated under the existing data contracts, Stage 11 must not invent assets to fill the list.

---

# 4. Core Selection Principle

The central rule is:

```text
Strong Movement + Reliability
```

Strong Movers are NOT simply the assets with the largest percentage increase.

A large movement can be valid.

Example:

```text
+18% movement
+ strong and sustained USDT volume
+ reliable source/data
```

may be a valid Strong Mover.

By contrast:

```text
+18% movement
+ negligible volume
+ weak liquidity
+ abnormal spike
+ unreliable source
```

must receive lower reliability treatment.

The implementation must preserve this distinction.

---

# 5. Strong-Movement Evaluation Inputs

Where valid data exists, evaluation may include the following factors defined by the Master roadmap:

- Price Movement in the requested Window
- USDT Trading Volume in the same Window
- Volume Consistency
- Liquidity
- Persistence of the movement
- Spike / abnormal-movement detection
- Relative Strength when a valid BTC pair exists
- Data and Source Reliability

These are evaluation inputs.

They must not be silently converted into an invented trading signal.

---

# 6. No Invented Third Metric

The Master roadmap explicitly defines the Top-3 principle as:

```text
Strong Movement + Reliability
```

Stage 11 must not invent a new mandatory third metric merely to make the implementation appear more sophisticated.

A third metric may be added only in a future roadmap revision where it is formally defined.

Until then:

```text
NO INVENTED THIRD REQUIREMENT
```

---

# 7. Exchange Selection Contract — CRITICAL

## 7.1 One shared Scanner exchange contract

Stage 11 must use the **same exchange selection system already approved for Stage 10**.

This is a hard architectural requirement.

There must be:

```text
ONE exchange-selection contract
```

not:

```text
Stage 10 exchange system
+
Stage 11 exchange system
```

The same contract must remain usable for future Scanner stages.

---

# 8. User-Selected Exchange Is the Preferred Source

When the user selects Exchange View:

```text
Selected Exchange = Preferred Display Source
```

It does NOT mean:

```text
Selected Exchange = Ranking Authority
```

Ranking still comes from Kitchen/U06.5.

Example:

```text
User selects Bybit

Kitchen/U06.5:
    determines ranks 11–125

Stage 11:
    evaluates Strong Movers

Display-data source:
    Bybit first
```

If Bybit has valid data, use Bybit.

If Bybit cannot provide valid data, use the already-approved fallback contract.

---

# 9. Exchange Priority / Fallback Contract

The existing Stage 10 Display Fallback Priority is:

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

When the user selects an exchange, fallback moves only toward exchanges with **higher system priority**.

Examples:

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

```text
Selected OKX (#2)
→ Binance (#1)
```

```text
Selected Binance (#1)
→ no higher-priority fallback
```

Lower-priority fallback is forbidden.

Stage 11 must not alter this order.

---

# 10. Exchange Consistency Across the Entire Strong-Mover Pipeline

This requirement is especially important.

If the user selects:

```text
Bybit
```

then the Strong Movers pipeline must use Bybit as the preferred display source for:

- candidate market-data validation
- price movement
- USDT pair
- USDT volume
- BTC pair
- BTC-relative movement when valid
- Strong Mover validation
- final five Strong Movers display
- inputs passed to the later Top-3 stage

If the selected exchange cannot provide valid data for a particular field, fallback may occur only according to the existing Stage 10 fallback rules.

The same principle applies if the user selects:

```text
OKX
```

or any of the other supported exchanges.

The user-selected exchange preference must remain a stable architectural contract.

It must not be silently replaced by a different exchange merely because another exchange is convenient.

---

# 11. Important Distinction: Ranking vs Display Source

Do not confuse these two concepts:

### Ranking authority

```text
Kitchen / U06.5 Dynamic Top-125
```

### Display-data preference

```text
User-selected exchange
```

Therefore:

```text
Kitchen determines WHICH assets are candidates.
Selected exchange determines WHERE display market data is requested first.
```

This distinction must remain intact.

---

# 12. Per-Asset and Per-Field Fallback

Fallback remains data-driven and validated.

For each asset:

1. Try the selected exchange first.
2. Validate the returned data.
3. If invalid, unavailable, stale, incomplete, or otherwise outside the existing validity contract, try the next eligible higher-priority exchange.
4. Continue only through the approved higher-priority direction.
5. Never fabricate data.
6. If no valid source exists, return an explicit unavailable state.

USDT and BTC fields are independently validated.

However, related fields for the same asset should remain on the same actual exchange whenever possible.

Preferred behavior:

```text
same asset
→ same actual exchange
→ valid USDT pair
→ valid USDT volume
→ valid BTC pair
```

If different valid sources are genuinely required, the difference must remain traceable.

---

# 13. USDT Pair and Volume Contract

For Strong Movers:

- USDT pair must be real and valid.
- USDT Volume belongs to the USDT pair.
- Volume must correspond to the requested Window.
- Do not substitute unrelated 24h volume when another timeframe is requested.
- Do not fabricate volume.
- Do not create a separate BTC volume.
- Do not duplicate the USDT volume under the BTC pair.

Example conceptual output:

```text
ATOMUSDT  +N%
Volume:   ...
Source:   Bybit
```

or, when fallback is required:

```text
ATOMUSDT  +N%
Volume:   ...
Fallback from: Bybit
```

The existing Stage 10 presentation rules remain authoritative.

---

# 14. Timeframe / Window Contract

Strong Movement and USDT Volume must refer to the **same requested analysis Window**.

The implementation must not silently mix:

```text
Price movement in requested Window
+
24h volume
```

when the requested Window is different.

The requested Window must be preserved through:

- candidate evaluation
- source retrieval
- validation
- ranking/selection
- final result
- Telegram output
- provenance

A timeframe mismatch is a data-validity failure.

---

# 15. BTC Pair Contract

BTC-relative evaluation may be used only when a valid BTC pair exists.

The Stage 10 BTC Pair contract remains authoritative.

For every non-BTC asset:

### Step 1 — Selected exchange

Check the real BTC pair on the user-selected exchange first.

### Step 2 — Eligible fallback

If unavailable/invalid, search only eligible higher-priority fallback exchanges.

### Step 3 — Fallback cohesion

If the USDT pair already resolved to a valid fallback exchange, prefer that same exchange for the BTC pair when possible.

### Step 4 — Existing approved Kitchen calculation

Use an already-approved Kitchen BTC value only if an existing Kitchen contract explicitly permits it.

Stage 11 must NOT invent a new BTC calculation method.

### Step 5 — Unavailable

If no valid real exchange BTC pair and no explicitly approved Kitchen calculated value exists:

```text
BTC pair = Unavailable
```

Fake BTC pairs are forbidden.

---

# 16. Relative Strength

Relative Strength may be used only when a valid BTC pair is available under the existing BTC Pair contract.

If the BTC pair is unavailable:

- do not fabricate it
- do not fabricate BTC movement
- do not manufacture a synthetic Relative Strength value unless an existing approved contract explicitly provides it

The absence of a BTC pair must be represented honestly.

---

# 17. Reliability Evaluation

Reliability is a core part of Strong Movers.

Reliability evaluation should account for the valid evidence available from the existing data contracts, including where applicable:

- data/source reliability
- valid USDT volume
- volume consistency
- persistence
- liquidity
- abnormal/spike behavior
- valid BTC-relative evidence

Do not punish a large move merely because it is large.

Do not reward a large move merely because it is large.

The implementation must distinguish:

```text
Strong + supported
```

from:

```text
Strong + weakly supported
```

---

# 18. Spike / Abnormal Movement Handling

A sudden spike is not automatically invalid.

The system must distinguish:

```text
large but supported movement
```

from:

```text
large movement with abnormal/weak supporting evidence
```

Spike detection is an evaluation input, not an automatic rule that rejects every large mover.

Do not create an unsupported hard threshold unless it is explicitly defined by an existing project contract.

---

# 19. Liquidity

Liquidity may be considered when valid liquidity information exists.

If valid liquidity data does not exist:

- do not invent it
- do not silently substitute an unrelated metric
- continue according to the remaining valid requirements

Liquidity is not a reason to introduce an unrelated new data subsystem.

---

# 20. Order Book

Order Book is **not an obligatory dependency** of Stage 11.

The Master roadmap treats Order Book as a future independent subsystem.

Therefore Stage 11 must not block Strong Movers waiting for an Order Book subsystem that has not been formally integrated.

Do not build a parallel Order Book system inside Stage 11.

---

# 21. Dynamic Behavior

Strong Movers must be dynamic.

A new request must be capable of reflecting:

- changed Dynamic Top-125 ranks
- changed price movement
- changed volume
- changed persistence
- changed reliability
- changed exchange availability
- changed fallback resolution

The stage must not permanently pin five assets.

---

# 22. Output Contract — Five Strong Movers

The output must contain up to five validated Strong Movers according to the stage contract.

When five valid candidates exist, five should be selected.

The output must preserve:

- Kitchen rank
- asset identity
- symbol
- movement
- requested Window
- USDT pair
- USDT volume
- actual source
- fallback state where applicable
- BTC pair where valid
- BTC-relative data where valid
- reliability information needed by the existing result contract

Internal provenance must not be discarded even if the user-facing message is concise.

---

# 23. Top-3 Integration Contract

The next stage will select:

```text
Dynamic Top 10
+
5 Strong Movers
↓
3 Top Reliable Movers
```

The Top-3 stage must use the Strong Movers output produced here.

The Strong Movers result must therefore preserve enough structured information for the next stage to evaluate:

```text
Strong Movement + Reliability
```

The Top-3 stage must not receive a lossy representation that removes the source/fallback, timeframe, movement, volume, or reliability evidence needed by its contract.

---

# 24. Exchange Contract Must Continue Into Top 3

The selected exchange preference must not stop at Stage 11.

Example:

```text
User selects OKX

Dynamic Top 10:
    OKX preferred
    → approved fallback if necessary

Strong Movers:
    OKX preferred
    → approved fallback if necessary

Top 3:
    same exchange-selection contract
    → same approved fallback rules
```

The Top-3 stage must not invent another exchange policy.

This is a long-lived Scanner architecture requirement.

It must remain valid months later when the same user preference is used again.

This does NOT create a new “three-month historical data” requirement.

It simply means the exchange-selection contract is stable and reusable.

---

# 25. Telegram Output and RTL/LTR

The existing Scanner Telegram safety rules remain mandatory.

The output must preserve:

- readable Persian RTL
- readable ticker/symbol LTR
- readable numbers
- readable percentages
- readable exchange names
- Source / Fallback wording
- timeframe clarity
- existing Scanner warning

Avoid formatting that causes:

- ticker corruption
- percentage reversal
- exchange-name confusion
- broken pair names
- duplicated volume
- ambiguous source attribution

No trading signal may be produced.

---

# 26. Scanner Safety

Stage 11 MUST NOT produce:

- entry signals
- exit signals
- long/short recommendations
- buy/sell recommendations
- trade execution
- stop-loss instructions
- take-profit instructions
- scenario matrices
- generic “intelligence” narratives
- unsupported confidence claims
- a replacement for the existing Scanner warning

Strong Movers are a market-scanning output only.

---

# 27. Regression Protection

Stage 11 must consume existing contracts.

Do not rewrite business logic of:

- U06.5
- Stage 7
- Stage 8
- Stage 9
- Stage 10

unless a real defect is demonstrated.

Any compatibility change must be:

- minimal
- justified
- tested
- documented

Stage 10 is already verified and must not be unnecessarily reopened.

---

# 28. Unit Breakdown

## Unit 11.1 — Stage Contract + Candidate Universe

### Implement

- Stage 11 configuration
- consume U06.5 Dynamic Top-125
- select ranks 11–125
- exclude BTC rank 1
- dynamic candidate refresh
- structured candidate contract

### Test

- correct candidate range
- BTC excluded
- current ranking consumed
- changed ranking reflected
- no independent ranking source

---

## Unit 11.2 — Strong Movement + Reliability Evaluation

### Implement

- requested-window movement
- same-window USDT volume
- volume consistency
- persistence
- liquidity when valid
- spike/abnormal movement evaluation
- BTC-relative evidence when valid
- source/data reliability
- Strong Movement + Reliability evaluation

### Test

- high move + strong volume
- high move + weak volume
- moderate move + strong supporting evidence
- inconsistent volume
- abnormal spike
- persistent movement
- unavailable optional evidence
- no fabricated values
- no Top-5-gainers-only logic

---

## Unit 11.3 — Exchange Selection + Fallback Cohesion

### Implement

- reuse Stage 10 exchange selection
- selected exchange as Preferred Source
- exact existing fallback priority
- higher-priority-only fallback
- per-asset validation
- USDT/BTC source cohesion
- fallback provenance

### Test

For every supported Exchange View:

- Binance
- OKX
- Bybit
- KuCoin
- Coinbase
- Gate
- Upbit
- Bitget

Test:

- selected source valid
- selected source unavailable
- selected source stale
- selected source invalid
- one-step fallback
- multi-step fallback
- highest-priority fallback
- no eligible fallback
- no lower-priority fallback

Critical consistency tests:

- selected Bybit → all five Strong Movers obey Bybit-first contract
- selected OKX → all five Strong Movers obey OKX-first contract
- selected Bitget → exact reverse higher-priority chain
- selected Binance → no fallback

---

## Unit 11.4 — Five Strong Movers Output

### Implement

- final five selection
- structured result
- USDT pair
- USDT volume
- BTC pair
- reliability evidence
- source/fallback presentation
- Telegram formatting
- RTL/LTR safety
- existing Scanner warning

### Test

- exactly five when five valid candidates exist
- fewer only when valid data genuinely prevents five
- no duplicate asset
- correct ranks
- correct movement
- correct volume window
- correct source
- correct fallback
- correct BTC handling
- no fake pair
- readable Telegram output

---

## Unit 11.5 — Top-3 Preparation / Integration Contract

### Implement

- preserve Strong Movers result for downstream Top-3
- preserve exchange contract
- preserve source/fallback provenance
- preserve movement evidence
- preserve reliability evidence
- preserve timeframe
- preserve USDT/BTC data contract

### Test

- Top-3 can consume Strong Movers without reconstructing data
- selected exchange remains traceable
- fallback remains traceable
- no second exchange system
- no lossy transformation
- no invented third metric

---

## Unit 11.6 — Full Integration + Regression

### Run

- all Stage 11 unit tests
- U06.5 regression
- Stage 7 regression
- Stage 8 regression
- Stage 9 regression
- Stage 10 regression
- relevant Scanner regression
- safe real-data smoke test where applicable
- no trading execution

### Verify

- candidate universe
- rank range
- Strong Movement
- Reliability
- exchange preference
- fallback direction
- fallback cohesion
- USDT pair
- USDT volume
- BTC pair
- timeframe
- freshness
- provenance
- Telegram formatting
- Scanner warning
- no trading signal
- no unrelated changes

---

# 29. Required Test Matrix

## Candidate Universe

- Dynamic Top-125 consumed
- ranks 11–125 accepted
- rank 10 excluded
- rank 126 excluded
- BTC rank 1 excluded
- ranking changes reflected

## Movement

- strong positive movement
- moderate movement
- weak movement
- large movement with strong volume
- large movement with weak volume
- persistent movement
- abnormal spike
- missing movement

## Volume

- valid USDT volume
- same requested Window
- inconsistent volume
- missing volume
- stale volume
- no 24h substitution
- no fabricated volume
- no BTC volume

## Reliability

- reliable source
- unreliable source
- valid supporting evidence
- weak supporting evidence
- missing optional evidence
- no invented score components

## Exchange View

- Binance
- OKX
- Bybit
- KuCoin
- Coinbase
- Gate
- Upbit
- Bitget

## Fallback

- selected source valid
- selected source unavailable
- selected source stale
- selected source invalid
- one-step fallback
- multi-step fallback
- highest-priority fallback
- no eligible fallback
- lower-priority fallback forbidden

## Pair Availability

- USDT exists
- USDT missing
- BTC exists on selected exchange
- BTC exists on fallback
- BTC exists on same USDT fallback
- BTC requires another eligible fallback
- BTC unavailable everywhere
- fake BTC pair prevention

## Output

- Kitchen View
- Exchange View
- Source
- Fallback from
- same fallback
- different fallback
- RTL/LTR
- Persian + ticker + numbers
- timeframe
- Scanner warning
- no trading signal

## Downstream

- Dynamic Top 10 + Strong Movers can form Top-3 input
- exchange preference preserved
- fallback contract preserved
- provenance preserved
- no third metric invented

---

# 30. Acceptance Criteria

Stage 11 is VERIFIED only if all applicable criteria are satisfied:

1. Candidate universe comes from U06.5 / Kitchen Dynamic Top-125.
2. Only ranks 11–125 are eligible.
3. BTC rank 1 is excluded.
4. No independent ranking universe is introduced.
5. Selection is not merely Top 5 percentage gainers.
6. Strong Movement + Reliability is the governing principle.
7. Requested price-movement Window is respected.
8. USDT Volume uses the same requested Window.
9. Volume is not fabricated.
10. BTC volume is not introduced.
11. Large movement is not automatically rejected.
12. Weakly supported large movement receives appropriate reliability treatment.
13. Spike detection does not become an unsupported automatic rejection rule.
14. Optional data is never fabricated.
15. Order Book is not made a mandatory dependency.
16. User-selected exchange is the Preferred Source.
17. Kitchen remains the ranking authority.
18. Stage 10 exchange selection contract is reused.
19. Fallback uses the exact approved higher-priority direction.
20. Lower-priority fallback is never used.
21. Selected Bybit remains Bybit-first for Strong Movers.
22. Selected OKX remains OKX-first for Strong Movers.
23. Selected Bitget follows the exact higher-priority chain.
24. Selected Binance has no higher-priority fallback.
25. USDT and BTC provenance remain traceable.
26. Same fallback exchange is preferred for related fields when possible.
27. BTC pair is checked on the selected exchange first.
28. Fake BTC pairs are impossible.
29. Explicit Unavailable states exist where valid data cannot be obtained.
30. Top-3 downstream input preserves Strong Mover evidence.
31. The same exchange contract can continue into Top 3.
32. No three-month historical-data requirement is invented.
33. Dynamic requests can reflect changed rankings/data.
34. Telegram RTL/LTR remains readable.
35. Existing Scanner warning remains present.
36. No trade signal is produced.
37. U06.5, Stage 7, Stage 8, Stage 9, and Stage 10 business logic remains unaffected unless a real defect is demonstrated.
38. Relevant regression tests pass.
39. Safe real-data smoke test passes where applicable.
40. No unrelated files are modified.
41. Final audit is completed.
42. Required artifacts are generated.
43. SHA256/manifest state is internally consistent.
44. Only relevant Stage 11 files are committed.

---

# 31. Final Stage Audit

Before declaring Stage 11 complete, perform a read-only audit of:

- candidate universe
- Dynamic Top-125 source
- ranks 11–125
- BTC exclusion
- movement Window
- USDT Volume Window
- volume validity
- reliability evaluation
- spike handling
- liquidity handling
- BTC pair handling
- exchange preference
- fallback direction
- fallback provenance
- source provenance
- same-exchange preference
- Unavailable handling
- Strong Movers count
- duplicate prevention
- Top-3 integration contract
- exchange consistency into Top 3
- RTL/LTR
- Scanner warning
- trading safety
- regression status
- modified files
- artifacts
- hashes
- manifest

No code changes should be made during the final read-only audit unless a real defect is discovered.

---

# 32. Stage 11 Artifacts

After successful implementation and verification, create according to project conventions:

```text
ledgers/U11_LEDGER.md
U11_AUDIT_METADATA.json
U11_MANIFEST.json
U11_SHA256.json
```

The artifacts must document:

- implemented units
- test results
- regression results
- integration status
- real-data smoke status where applicable
- verified files
- file hashes
- final audit status

The manifest must list only the files belonging to the verified Stage 11 checkpoint.

SHA256 must be calculated for the manifest's relevant files according to project conventions.

Do not include unrelated pre-existing files.

---

# 33. Git / Backup Policy

Do NOT commit after every unit.

Units may be independently implemented and tested.

The final Stage 11 checkpoint is committed only after:

```text
all units complete
→ tests pass
→ integration passes
→ regression passes
→ real-data smoke passes where applicable
→ final audit passes
→ artifacts complete
→ hashes verified
→ git status/diff inspected
```

Use:

```text
git status
git diff
git add <only relevant Stage 11 files>
git commit
git push
```

NEVER use:

```text
git add .
```

Do not commit unrelated pre-existing files.

---

# 34. Controlled Kilo Execution Rules

Kilo must work in small controlled units.

## First command

The first Kilo instruction for Stage 11 should be **Study / Plan only**.

It must:

- read the Stage 11 roadmap
- inspect only the directly relevant existing contracts
- identify reusable Stage 10 exchange/fallback components
- identify the U06.5 Dynamic Top-125 contract
- identify Stage 10 result/provenance structures that should be reused
- produce a focused implementation plan for Unit 11.1

It must NOT modify code during the study/plan checkpoint.

## Unit execution

Then proceed:

```text
11.1 → Test → Verify
11.2 → Test → Verify
11.3 → Test → Verify
11.4 → Test → Verify
11.5 → Test → Verify
11.6 → Integration → Regression → Audit
```

Do not skip a unit.

Do not implement all six units in one uncontrolled pass.

---

# 35. Kilo Scope-Control Rules

Kilo must NOT:

- perform a broad repository rewrite
- rescan unrelated project history
- recreate completed Stage 10 work
- rewrite U06.5
- rewrite Stage 7
- rewrite Stage 8
- rewrite Stage 9
- create a new exchange priority system
- create a new fallback direction
- create an independent ranking universe
- introduce Order Book as a dependency
- invent a third Top-3 metric
- invent a three-month historical-data requirement
- fabricate missing market data
- fabricate BTC pairs
- fabricate volume
- create trade signals
- modify unrelated files

When compatibility work is genuinely necessary, it must be minimal, justified, tested, and documented.

---

# 36. If Kilo Hits Its Limit

If Kilo reaches its processing limit:

Do not restart the stage.

Do not rescan the whole repository.

Continue from the last verified checkpoint using only:

- this Stage 11 roadmap
- the last unit's implementation files
- the last unit's tests
- the immediate test output
- the relevant existing Stage 10/U06.5 contract files

The continuation must explicitly state:

```text
CONTINUE FROM LAST VERIFIED STAGE 11 CHECKPOINT.
DO NOT REDO COMPLETED WORK.
DO NOT PERFORM A BROAD REPOSITORY SCAN.
```

---

# 37. Architecture Summary

The intended architecture is:

```text
U06.5 / Kitchen Dynamic Top-125
            ↓
        ranks 11–125
            ↓
   Strong Movement Evaluation
            +
      Reliability Evaluation
            ↓
      Exchange Contract
            ↓
Selected Exchange = Preferred Source
            ↓
Higher-Priority Fallback Only
            ↓
USDT Pair + Same-Window Volume
            +
Valid BTC Pair when available
            ↓
      5 Strong Movers
            ↓
Dynamic Top 10 + 5 Strong Movers
            ↓
       Top 3 Reliable Movers
```

And the exchange contract remains:

```text
ONE Scanner exchange-selection system
                ↓
Stage 10
                ↓
Stage 11
                ↓
Top 3
                ↓
future Scanner stages
```

---

# 38. Final Non-Negotiable Principles

1. **Kitchen/U06.5 owns ranking.**
2. **Stage 11 consumes ranks 11–125.**
3. **Strong Movers are not Top 5 gainers.**
4. **Strong Movement + Reliability is the core principle.**
5. **Large movement is not automatically bad.**
6. **Weakly supported movement must be treated as less reliable.**
7. **Requested Window controls movement and USDT volume.**
8. **The user's selected exchange is the Preferred Source.**
9. **The same Stage 10 exchange contract MUST be reused.**
10. **Fallback moves only toward higher-priority exchanges.**
11. **No lower-priority fallback.**
12. **USDT and BTC fields remain independently validated.**
13. **Related fields should use the same actual fallback exchange when possible.**
14. **Fake BTC pairs are forbidden.**
15. **Fabricated volume is forbidden.**
16. **Order Book is not a Stage 11 dependency.**
17. **No invented third Top-3 metric.**
18. **The exchange contract continues into Top 3.**
19. **No invented three-month historical requirement.**
20. **No trade signal, entry, exit, recommendation, or execution.**
21. **Do not rewrite completed Scanner stages.**
22. **Every unit is implemented, tested, and verified separately.**
23. **Final integration/regression is performed only at the end.**
24. **Artifacts are generated only after successful verification.**
25. **Only relevant Stage 11 files are committed.**
26. **Never use `git add .`.**
27. **If Kilo hits a limit, continue from the last verified checkpoint without redoing completed work.**

---

# 39. Stage Completion Definition

Stage 11 is complete only when:

```text
11.1 verified
→ 11.2 verified
→ 11.3 verified
→ 11.4 verified
→ 11.5 verified
→ 11.6 integration verified
→ regression verified
→ final audit verified
→ artifacts verified
→ Git checkpoint committed
```

Only then may the project proceed to the next Scanner stage.
