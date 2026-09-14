# STAGE 12 --- TOP 3 RELIABLE MOVERS

## Final Operational Scanner Stage --- Roadmap & Specification

**Stage:** 12\
**Scope:** Final business/operational stage of the Scanner\
**Status:** Ready for controlled implementation

------------------------------------------------------------------------

## 1. Purpose

Stage 12 completes the Scanner's operational/business workflow.

Its single business responsibility is to select **3 Reliable Movers**
from the combined pool of:

1.  Dynamic Top 10
2.  Five Strong Movers from Stage 11

The primary principle is:

**Strong Movement + Reliability**

This is a prioritization layer for deeper human review. It is **not** a
trading decision engine.

The Master Roadmap explicitly places Top 3 after Dynamic Top 10 and the
five Strong Movers.

------------------------------------------------------------------------

## 2. Final Scanner Boundary

Stage 12 is the **last operational Scanner stage**.

After Stage 12, Scanner business functionality is complete. Any later
work is separate technical/production integration work, such as Telegram
runtime integration or PythonAnywhere deployment compatibility.

That later technical work must not be silently added to Stage 12.

The Master Roadmap defines Scanner completion after Top 3 works and the
final end-to-end verification succeeds.

------------------------------------------------------------------------

## 3. Source-of-Truth Hierarchy

Implementation must follow:

1.  This Stage 12 specification
2.  `SCANNER_MASTER_ROADMAP.md`
3.  Existing approved Stage 11 contracts/implementation
4.  Existing Dynamic Top 10 / Stage 10 contracts
5.  U06.5 market-data foundation
6.  Existing validation, timeframe, source, provenance, RTL/LTR, and
    Scanner-safety contracts

Do not replace an established contract with a newly invented equivalent.

Do not weaken U06.5 quality gates, validation, ranking, source
reliability, timestamp normalization, or safety locks.

U06.5 is a critical market-data foundation and its logic must not be
weakened merely for implementation convenience.

------------------------------------------------------------------------

## 4. Candidate Pool

Stage 12 consumes:

### Pool A --- Dynamic Top 10

Use the existing Dynamic Top 10 output.

Do not rebuild its ranking logic.

### Pool B --- Five Strong Movers

Use the existing Stage 11 output.

Do not rebuild Strong Movers selection.

### Combined Pool

Combine:

**Dynamic Top 10 + Five Strong Movers**

The same asset may appear in both pools.

Such an asset is **one candidate**, not two.

Deduplicate using the project's existing canonical asset identity.

Do not create an artificial bonus merely because an asset appears in
both upstream lists.

------------------------------------------------------------------------

## 5. Core Selection Principle

The Master Roadmap defines:

**Strong Movement + Reliability**

as the primary criterion for Top 3. fileciteturn19file1L188-L204

Therefore:

-   meaningful movement matters
-   reliability matters
-   neither dimension should be ignored
-   a large percentage move alone is insufficient
-   excellent data reliability alone is insufficient if the asset has no
    meaningful movement

The final selection should prioritize assets that combine meaningful
movement with trustworthy supporting data.

------------------------------------------------------------------------

## 6. No Top-3-by-Gain Shortcut

Do **not** implement:

``` text
sort by percentage gain
take first 3
```

That would violate the Stage 12 contract.

Stage 12 must not simply choose the three largest percentage gainers.

------------------------------------------------------------------------

## 7. No Invented Third Metric

The Master Roadmap explicitly states that a third metric may be defined
in the future, but must not be invented as a mandatory requirement
before it is formally specified.

Do not invent:

-   Generic Intelligence Score
-   AI Score
-   Confidence Index
-   Market Intelligence score
-   arbitrary third-factor weighting
-   any other new mandatory business metric

unless an already-approved project contract explicitly defines it.

------------------------------------------------------------------------

## 8. Reuse Existing Strong-Mover Information

Where available, Stage 12 should consume the validated upstream
information already established by Stage 11, including:

-   Price Movement in the requested window
-   USDT Trading Volume in the same window
-   Volume Consistency
-   Liquidity when valid data exists
-   Persistence
-   Spike/anomaly information
-   Relative Strength when a valid BTC pair exists
-   Reliability of data/source

These are the factors identified by the Master Roadmap for Strong
Movers.

Do not recalculate existing approved values differently merely because
Stage 12 is the final stage.

------------------------------------------------------------------------

## 9. Large Movement Rule

A large move is not automatically bad.

The Master Roadmap explicitly gives the principle that a large movement
can remain valid when supported by strong/persistent volume and reliable
data, while a large move with weak volume, poor liquidity, or abnormal
spike behavior should have lower reliability.

Do not add an arbitrary maximum-percentage rejection rule.

------------------------------------------------------------------------

## 10. Candidate Eligibility

Candidates must satisfy the established data-quality requirements.

Do not turn invalid data into a valid candidate by guessing.

Reject or mark unavailable according to existing contracts when there
is:

-   missing asset identity
-   invalid numeric data
-   stale data where freshness is required
-   invalid timeframe/window
-   invalid source
-   invalid pair identity
-   fabricated pair
-   fabricated price/movement
-   fabricated volume
-   unsupported provider substitution

Unavailable is preferable to fabricated.

------------------------------------------------------------------------

## 11. Time Window

Use the same requested analysis window/timeframe semantics established
by the existing Scanner flow.

Do not silently switch windows.

Do not compare candidates using inconsistent windows.

When Stage 11 already provides validated movement/volume for the
requested window, consume that established data.

------------------------------------------------------------------------

## 12. Exchange Contract

Stage 12 must preserve the established Stage 10/11 exchange
architecture.

The user's selected exchange remains the **Preferred Source**.

Fallback is allowed only toward higher-priority exchanges.

Priority:

1.  Binance
2.  OKX
3.  Bybit
4.  KuCoin
5.  Coinbase
6.  Gate
7.  Upbit
8.  Bitget

Examples:

**Selected Bitget:**

`Bitget → Upbit → Gate → Coinbase → KuCoin → Bybit → OKX → Binance`

**Selected OKX:**

`OKX → Binance`

**Selected Binance:**

No fallback.

Do not introduce lower-priority fallback.

Do not silently replace the user's preferred exchange merely because
ranking originated from Kitchen/U06.5.

------------------------------------------------------------------------

## 13. Source and Provenance

Preserve upstream provenance.

Where applicable, retain:

-   requested exchange
-   actual exchange
-   fallback status
-   fallback exchange
-   pair
-   timeframe
-   data timestamp
-   validation status

Do not erase provenance merely because the final output is short.

------------------------------------------------------------------------

## 14. USDT Contract

For any displayed USDT pair:

-   asset identity must be correct
-   pair must be valid
-   movement must belong to the requested window
-   USDT volume must belong to that same window
-   source must be truthful
-   fallback label must be truthful
-   fabricated values are forbidden

Volume belongs only to the USDT pair.

Do not introduce BTC volume.

------------------------------------------------------------------------

## 15. BTC Contract

If BTC information is displayed, preserve the established BTC resolution
contract:

1.  Real ASSETBTC pair on selected exchange
2.  Eligible higher-priority fallback exchange
3.  Approved existing Kitchen BTC calculation only where the existing
    contract permits it
4.  Unavailable

Never fabricate:

-   BTC pair
-   BTC price
-   BTC movement
-   BTC volume
-   timestamp
-   source

If Stage 11 already provides validated BTC information, consume it
rather than inventing another BTC-resolution system.

------------------------------------------------------------------------

## 16. Exchange Cohesion

When both USDT and BTC information are available:

-   preserve the valid upstream source
-   prefer the same valid fallback for both when possible
-   if different fallbacks are genuinely required, preserve the actual
    provenance

Do not falsify provenance to make output look uniform.

------------------------------------------------------------------------

## 17. Output Count

Target:

**3 Reliable Movers**

If at least three eligible candidates exist, return three.

If fewer than three genuinely eligible candidates exist, do not
fabricate candidates.

Use the established insufficient-data/unavailable behavior.

------------------------------------------------------------------------

## 18. Deterministic Ordering

The final Top 3 must have deterministic ordering.

Ordering must reflect the approved Strong Movement + Reliability
selection principle.

Do not use arbitrary ordering.

If a tie occurs, use an already-approved deterministic rule/field where
one exists.

Do not invent a new business metric solely as a tie-breaker.

------------------------------------------------------------------------

## 19. Telegram Output

The final output should remain compact and Scanner-oriented.

Semantic structure:

``` text
1. SOLUSDT +8.4%
   Volume: ...
   Exchange: Binance

2. XRPUSDT +6.9%
   Volume: ...
   Exchange: Binance

3. LINKUSDT +5.8%
   Volume: ...
   Exchange: Coinbase
```

The exact typography may follow existing Stage 10/11 conventions.

Preserve Source/Fallback semantics.

Do not add unnecessary narrative.

Do not add a trade conclusion.

The Master Roadmap's example output follows this compact structure and
explicitly states that the stage has no Scenario, Matrix, Narrative,
Entry Signal, Exit Signal, Long/Short Signal, or Trade Recommendation.

------------------------------------------------------------------------

## 20. Mandatory Scanner Warning

The final Scanner output must preserve the mandatory warning defined in
the Master Roadmap:

> ⚠️ **توجه:** اطلاعات و انتخاب‌های ارائه‌شده توسط Scanner به‌هیچ‌وجه سیگنال
> ورود یا خروج از معامله نیستند و نباید به‌تنهایی مبنای تصمیم معاملاتی
> قرار گیرند. هدف Scanner، صرفه‌جویی در زمان و مشخص‌کردن دارایی‌های برتر،
> جریان حرکت سرمایه و جهت کلی بازار است تا بتوانید روی گزینه‌هایی که ارزش
> بررسی بیشتری دارند تمرکز کنید. تصمیم نهایی برای معامله، از جمله تشخیص
> Setup، Entry و Trigger، بر عهده خود شماست.

This warning is mandatory.

If the exact warning already exists in the implementation, reuse it. Do
not create a competing warning.

------------------------------------------------------------------------

## 21. RTL / LTR

Preserve existing Scanner RTL/LTR rules:

-   Persian text should not begin with an English word.
-   Tickers should preferably remain in their own line/field.
-   Percentages and numbers must remain readable.
-   Exchange names must remain associated with their field.
-   Existing official narratives must not be changed.
-   New text must be designed for Telegram RTL/LTR readability.

The Master Roadmap explicitly defines these formatting rules.

------------------------------------------------------------------------

## 22. Previous Outputs Must Remain Available

Stage 12 must not hide or delete important previous Scanner outputs.

The Scanner must remain able to provide:

-   Total + USDT.D
-   BTC + BTC.D
-   Smart Market Participation
-   Dynamic Top 10
-   5 Strong Movers
-   Top 3 Reliable Movers

The Master Roadmap explicitly requires preservation of previous outputs.

------------------------------------------------------------------------

## 23. No Generic Intelligence

Do not create a generic final intelligence layer.

Do not generate unsupported conclusions, repetitive output, or
statements that the data does not establish.

The final new capability is only:

**prioritize 3 assets for deeper review.**

The Master Roadmap explicitly rejects unnecessary Generic Intelligence.

------------------------------------------------------------------------

## 24. No Scenario / Matrix / Narrative

Stage 12 must not create:

-   Scenario Matrix
-   new Scenario labels
-   new Narrative patterns
-   generic market conclusion
-   trade-plan narrative

Top 3 selection itself is the output.

------------------------------------------------------------------------

## 25. No Order Book Dependency

Order Book is not an obligatory dependency for this stage unless an
already-approved project contract explicitly requires it.

Do not build an Order Book subsystem inside Stage 12.

------------------------------------------------------------------------

# 26. Unit Breakdown

## Unit 12.1 --- Stage Contract + Candidate Pool

Implement:

-   consume Dynamic Top 10
-   consume five Strong Movers
-   combine them
-   deduplicate canonical assets
-   validate candidate eligibility
-   preserve upstream structured data

Test:

-   correct pool
-   overlap/deduplication
-   invalid candidate
-   missing data
-   fewer-than-three eligible candidates

Do not perform final selection yet.

------------------------------------------------------------------------

## Unit 12.2 --- Strong Movement + Reliability Evaluation

Implement:

-   final evaluation of the combined pool
-   reuse approved upstream movement/reliability information
-   apply Strong Movement + Reliability
-   prevent gain-only selection
-   do not invent a third metric

Test:

-   large move + strong supporting volume
-   large move + weak supporting volume
-   persistence
-   spike/anomaly behavior
-   reliability differences
-   deterministic result

------------------------------------------------------------------------

## Unit 12.3 --- Exchange + Data Contract Continuity

Verify/implement only what is necessary to preserve:

-   selected exchange as Preferred Source
-   higher-priority-only fallback
-   USDT contract
-   BTC contract
-   provenance
-   timeframe/window

Test all supported exchange selections and fallback directions.

Do not create a second exchange architecture.

------------------------------------------------------------------------

## Unit 12.4 --- Final Top 3 + Telegram Output

Implement:

-   select 3 eligible assets when possible
-   deterministic ordering
-   preserve USDT/BTC/source information
-   produce compact output
-   preserve RTL/LTR
-   preserve mandatory warning

Test:

-   exactly three
-   duplicate removal
-   source/fallback display
-   warning
-   no signal/recommendation language

------------------------------------------------------------------------

## Unit 12.5 --- Full Scanner Integration

Verify the full operational chain:

``` text
U06.5
→ Stage 7
→ Stage 8
→ Stage 9
→ Dynamic Top 10
→ Stage 11 Strong Movers
→ Stage 12 Top 3
```

Verify that previous outputs remain available.

Do not rewrite previous stages merely to make integration convenient.

------------------------------------------------------------------------

## Unit 12.6 --- Full Regression + Final Scanner Audit

Perform:

-   full Stage 12 tests
-   U06.5 regression
-   Stage 10 regression
-   Stage 11 regression
-   full Scanner integration
-   safe real-data smoke where the established method permits it
-   Inspect
-   Fix
-   Re-test
-   Verify
-   artifact verification
-   Git verification

No known genuine defect should remain.

------------------------------------------------------------------------

# 27. Test Matrix

At minimum cover:

### Candidate Pool

-   Dynamic Top 10 consumed
-   five Strong Movers consumed
-   overlap/deduplication
-   invalid candidates
-   missing fields
-   fewer than three valid candidates

### Selection

-   not Top-3-by-gain-only
-   movement + reliability
-   strong movement with strong volume
-   strong movement with weak volume
-   spike/anomaly handling
-   persistence
-   deterministic ordering
-   ties

### Exchange

-   Binance
-   OKX
-   Bybit
-   KuCoin
-   Coinbase
-   Gate
-   Upbit
-   Bitget
-   valid higher-priority fallback
-   forbidden lower-priority fallback
-   Binance no-fallback case

### USDT

-   valid pair
-   invalid pair
-   correct window
-   correct volume
-   source
-   fallback provenance
-   no BTC volume

### BTC

-   selected exchange
-   higher-priority fallback
-   same-fallback preference
-   different legitimate fallback
-   approved Kitchen calculation where permitted
-   unavailable
-   fabricated-pair rejection

### Output

-   three assets
-   no duplicates
-   source/fallback
-   RTL/LTR
-   mandatory warning
-   no signal language
-   no recommendation language
-   previous outputs preserved

### Regression

-   U06.5
-   Stage 7
-   Stage 8
-   Stage 9
-   Dynamic Top 10
-   Stage 11
-   complete Scanner

------------------------------------------------------------------------

# 28. Real-Data Verification

Passing synthetic tests alone does not prove completion.

Use the project's established safe real-data smoke-test method.

Verify:

-   current Dynamic Top 10
-   current five Strong Movers
-   current Top 3
-   source
-   volume
-   timeframe/window
-   BTC pair validity
-   exchange/fallback behavior
-   no fabricated data
-   final output structure

Do not invent a new production data pipeline for testing.

------------------------------------------------------------------------

# 29. Safety Locks

Preserve all existing safety controls, including the project's
trading-disabled safety chain.

Stage 12 must not enable:

-   orders
-   portfolio actions
-   strategy execution
-   entry signals
-   exit signals
-   long/short signals
-   trade recommendations

The Scanner remains analysis-only.

The Master Roadmap defines Scanner as selection and initial analysis,
not final trade decision.

------------------------------------------------------------------------

# 30. Data Honesty

The existing project honesty rules remain mandatory:

-   no fabrication
-   no prohibited interpolation
-   no silent substitution
-   no fake pair
-   no fake volume
-   no fake timestamp
-   no unsupported provider substitution
-   no unsupported calculation

If information is unavailable, preserve explicit unavailable behavior.

------------------------------------------------------------------------

# 31. Performance / Scope Control

Keep Stage 12 efficient.

Do not:

-   repeatedly rebuild rankings
-   unnecessarily re-fetch data already available upstream
-   scan/rewrite the entire repository
-   duplicate U06.5 logic
-   duplicate Stage 10 exchange logic
-   duplicate Stage 11 Strong Movers logic

Preferred flow:

**consume → validate → evaluate → select → display**

------------------------------------------------------------------------

# 32. Previous Stages

Do not alter completed Stage 7--11 business logic unnecessarily.

If an existing implementation is correct, reuse it.

If a genuine compatibility defect is discovered:

1.  identify it
2.  make the smallest justified fix
3.  add/update focused tests
4.  run regression
5.  document the correction

Do not refactor completed stages for style alone.

------------------------------------------------------------------------

# 33. Artifacts

Use the same artifact convention as previous stages:

-   `ledgers/U12_LEDGER.md`
-   `U12_AUDIT_METADATA.json`
-   `U12_MANIFEST.json`
-   `U12_SHA256.json`

Exact implementation/test filenames should follow the repository's
established conventions.

Artifacts must describe the final verified state.

Regenerate SHA256 after final modifications.

------------------------------------------------------------------------

# 34. Execution Protocol

Use the established lifecycle:

``` text
Study
→ Plan
→ Implement
→ Test
→ Inspect
→ Fix
→ Re-test
→ Verify
→ Backup/Commit
→ Next Unit
```

Do not consider a unit complete merely because code runs.

The Master Roadmap explicitly states that execution alone is not
completion and requires source, volume, time-window, BTC-pair,
quality-gate, output, and no-fabrication checks.

------------------------------------------------------------------------

# 35. Controlled Unit-by-Unit Execution

Kilo should work unit-by-unit.

For each unit:

1.  Study the relevant existing contracts.
2.  Identify the smallest required scope.
3.  Implement only that scope.
4.  Run focused tests.
5.  Inspect results.
6.  Fix defects.
7.  Re-test.
8.  Continue only when stable.

At Unit 12.6, perform full Scanner regression and final audit.

Do not implement Stage 12 blindly in one large operation.

------------------------------------------------------------------------

# 36. If a Problem Is Found

Every genuine defect must be addressed, even if small.

Do not ignore:

-   contract violations
-   wrong formulas
-   incorrect source/fallback
-   invalid data handling
-   output inconsistencies
-   missing edge cases
-   stale artifacts
-   regression failures

At the same time, do not modify unrelated pre-existing repository work.

------------------------------------------------------------------------

# 37. Final Scanner Verification

After Stage 12 is implemented, perform the Master Roadmap's final
Scanner verification.

The Scanner must be exercised from beginning to end.

Verify:

-   Technical Foundation is stable
-   U06.5 logic is preserved
-   Stage 7 works
-   Stage 8 works
-   Stage 9 works
-   Dynamic Top 10 works
-   Strong Movers works
-   Top 3 Reliable Movers works
-   previous outputs remain available
-   Source is identifiable
-   Volume is correct for the requested window
-   BTC Pair Rules are respected
-   no fake pair exists
-   mandatory warning exists
-   full Scanner regression passes
-   real defects are fixed

The Master Roadmap defines this as the final Scanner verification before
delivery as a stable subsystem.

------------------------------------------------------------------------

# 38. Definition of Done

Stage 12 is complete only when:

-   [ ] Dynamic Top 10 is consumed correctly.
-   [ ] Five Strong Movers are consumed correctly.
-   [ ] Combined candidate pool is correct.
-   [ ] Duplicate assets are handled correctly.
-   [ ] Three valid candidates are selected when at least three are
    eligible.
-   [ ] Selection is not simply Top 3 percentage gainers.
-   [ ] Strong Movement + Reliability is the primary principle.
-   [ ] No invented third metric is used.
-   [ ] Existing approved contracts are reused.
-   [ ] Selected exchange remains Preferred Source.
-   [ ] Fallback is only toward higher-priority exchanges.
-   [ ] USDT data is valid.
-   [ ] USDT volume uses the correct window.
-   [ ] No BTC volume is fabricated/displayed.
-   [ ] BTC pair rules are preserved.
-   [ ] Provenance is preserved.
-   [ ] RTL/LTR is safe.
-   [ ] Mandatory Scanner warning is present.
-   [ ] No Entry Signal exists.
-   [ ] No Exit Signal exists.
-   [ ] No Long/Short Signal exists.
-   [ ] No Trade Recommendation exists.
-   [ ] No Generic Intelligence layer exists.
-   [ ] No Mega Matrix exists.
-   [ ] No unnecessary Order Book dependency exists.
-   [ ] Previous Scanner outputs remain available.
-   [ ] Full Scanner regression passes.
-   [ ] Real-data smoke passes where applicable.
-   [ ] All genuine defects are fixed.
-   [ ] U12 ledger is accurate.
-   [ ] U12 audit metadata is accurate.
-   [ ] U12 manifest is accurate.
-   [ ] U12 SHA256 is accurate.
-   [ ] Git state is verified.
-   [ ] Stage 12 is professionally audited.
-   [ ] Final Scanner verification passes.

------------------------------------------------------------------------

# 39. What Stage 12 Must NOT Become

Stage 12 must not become:

-   a trading strategy
-   a signal generator
-   an entry/exit engine
-   a portfolio manager
-   a risk manager
-   an order executor
-   a generic AI conclusion engine
-   a Mega Matrix
-   an Order Book subsystem
-   a replacement for previous Scanner stages

Its only new business responsibility is:

**Select and present the 3 assets from Dynamic Top 10 + 5 Strong Movers
that best satisfy Strong Movement + Reliability and therefore deserve
deeper review.**

------------------------------------------------------------------------

# 40. Final Operational Boundary

When Stage 12 passes final verification:

**The Scanner's operational/business roadmap is complete.**

The Master Roadmap says that after the final Scanner verification,
Scanner development stops and the project proceeds to the next
subsystem.

Any subsequent PythonAnywhere/Telegram productionization, deployment,
scheduling, persistence, logging, or runtime work must be treated as
separate technical integration work rather than new Scanner business
logic.

------------------------------------------------------------------------

# 41. Final Flow

``` text
U06.5 Dynamic Market Foundation
        ↓
Stage 7 — Total + USDT.D
        ↓
Stage 8 — BTC + BTC.D
        ↓
Stage 9 — Smart Market Participation
        ↓
Dynamic Top 10
        ↓
Stage 11 — 5 Strong Movers
        ↓
Stage 12 — Top 3 Reliable Movers
        ↓
FINAL SCANNER VERIFICATION
        ↓
SCANNER OPERATIONAL COMPLETION
        ↓
Separate Technical / Production Integration
```

**Stage 12 is the final operational Scanner stage.**

**Scanner = selection and initial analysis, not final trading
decision.**
