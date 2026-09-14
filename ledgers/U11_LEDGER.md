# KITCHEN ASSISTANT V3.1 — U11 LEDGER

## Execution Unit

U11 — Strong Movers

## Validation

Global status: PASS
Technical lock: LOCKED

## Stage 11 Units Summary

### Unit 11.1 — Stage Contract + Candidate Universe
- Stage 11 configuration
- Consume U06.5 Dynamic Top-125
- Select ranks 11-125
- BTC rank 1 excluded
- Dynamic candidate refresh
- Structured candidate contract
- Status: PASSED

### Unit 11.2 — Strong Movement + Reliability Evaluation
- Requested-window movement
- Same-window USDT volume
- Volume consistency
- Persistence
- Liquidity when valid
- Spike/abnormal movement evaluation
- BTC-relative evidence when valid
- Source/data reliability
- Strong Movement + Reliability evaluation
- Status: PASSED

### Unit 11.3 — Exchange Selection + Fallback Cohesion
- Reuse Stage 10 exchange selection
- Selected exchange as Preferred Source
- Exact existing fallback priority
- Higher-priority-only fallback
- Per-asset validation
- USDT/BTC source cohesion
- Fallback provenance
- Status: PASSED

### Unit 11.4 — Five Strong Movers Output
- Final five selection
- Structured result
- USDT pair
- USDT volume
- BTC pair
- Reliability evidence
- Source/fallback presentation
- Telegram formatting
- RTL/LTR safety
- Existing Scanner warning
- Status: PASSED

### Unit 11.5 — Top-3 Preparation / Integration Contract
- Preserve Strong Movers result for downstream Top-3
- Preserve exchange contract
- Preserve source/fallback provenance
- Preserve movement evidence
- Preserve reliability evidence
- Preserve timeframe
- Preserve USDT/BTC data contract
- Status: PASSED

### Unit 11.6 — Full Integration + Regression
- All Stage 11 unit tests: PASSED (94 tests)
- U06.5 regression: PASSED
- Stage 10 regression: PASSED (110 tests)
- No trading execution
- Status: PASSED

## Test Results Summary

- Total Stage 11 tests: 94
- All passed: 94
- Failed: 0
- Existing tests regression: 1025 total (1025 passed)

## Real-Data Smoke Test

- Live exchange data not configured in test environment
- All tests are deterministic/synthetic
- Status: N/A (synthetic only)

## Source Integrity

- U06.5: UNMODIFIED
- Stage 7: UNMODIFIED
- Stage 8: UNMODIFIED
- Stage 9: UNMODIFIED
- Stage 10: UNMODIFIED
- Units 11.1-11.6: NEW (not modifications)
- Source data modified: FALSE

## Safety

- Trading: DISABLED
- Orders: DISABLED
- Strategy: DISABLED
- Portfolio Actions: DISABLED
- No trading, orders, entries, exits, long/short, setup, trigger, or recommendations.
- No trading signal produced.

## Files

- app/analysis/stage11_strong_movers.py
- tests/unit/test_u11_unit_1_contract.py
- tests/unit/test_u11_unit_2_evaluation.py
- tests/unit/test_u11_unit_3_exchange.py
- tests/unit/test_u11_unit_4_output.py
- tests/unit/test_u11_unit_5_integration.py
- tests/unit/test_u11_unit_6_regression.py

## Final Rule

U11 is technically locked only when every gate passes.
If validation fails, U11 remains NOT LOCKED.
