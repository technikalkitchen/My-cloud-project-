# KITCHEN ASSISTANT V3.1 — U12 LEDGER

## Execution Unit

U12 — Top 3 Reliable Movers (Final Operational Scanner Stage)

## Validation

Global status: PASS
Technical lock: LOCKED

## Stage 12 Units Summary

### Unit 12.1 — Stage Contract + Candidate Pool
- Consume Dynamic Top 10 (Stage 10 output)
- Consume five Strong Movers (Stage 11 output)
- Combine by canonical asset identity
- Deduplicate overlapping candidates
- Validate candidate eligibility
- Preserve upstream structured data
- Tests: PASS

### Unit 12.2 — Strong Movement + Reliability Evaluation
- Evaluate combined pool using Strong Movement + Reliability
- Reuse approved upstream movement/reliability scoring
- Prevent gain-only selection
- No invented third metric
- Deterministic ordering by total_score
- Tests: PASS

### Unit 12.3 — Exchange + Data Contract Continuity
- Selected exchange as Preferred Source
- Higher-priority-only fallback
- USDT contract preserved
- BTC contract preserved
- Provenance preserved
- Timeframe/window preserved
- Tests: PASS

### Unit 12.4 — Final Top 3 + Telegram Output
- Select 3 eligible assets when possible
- Compact Telegram format per roadmap
- Preserve Source/Fallback semantics
- Mandatory Scanner warning present
- No signal/recommendation language
- RTL/LTR safe
- Tests: PASS

### Unit 12.5 — Full Scanner Integration
- U06.5 → Stage 7 → Stage 8 → Stage 9 → Dynamic Top 10
- → Stage 11 Strong Movers → Stage 12 Top 3 chain verified
- Previous outputs remain available
- All 8 exchanges tested
- Tests: PASS

### Unit 12.6 — Full Regression + Final Scanner Audit
- All Stage 12 tests: PASSED (104 tests)
- U06.5 regression: PASSED
- Stage 10 regression: PASSED
- Stage 11 regression: PASSED
- Full Scanner integration: PASSED
- Safety locks verified: PASSED
- No fabricated data
- Tests: PASSED

## Test Results Summary

- Total Stage 12 tests: 104
- All passed: 104
- Failed: 0
- Existing tests regression: 1129 total (1129 passed)

## Source Integrity

- U06.5: UNMODIFIED
- Stage 7: UNMODIFIED
- Stage 8: UNMODIFIED
- Stage 9: UNMODIFIED
- Stage 10: UNMODIFIED
- Stage 11: UNMODIFIED
- Units 12.1-12.4: NEW (not modifications)
- Source data modified: FALSE

## Safety

- Trading: DISABLED
- Orders: DISABLED
- Strategy: DISABLED
- Portfolio Actions: DISABLED
- No trading, orders, entries, exits, long/short, setup, trigger, or recommendations.
- No trading signal produced.

## Final Rule

U12 is technically locked only when every gate passes.
If validation fails, U12 remains NOT LOCKED.