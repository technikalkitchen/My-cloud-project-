# KITCHEN ASSISTANT V3.1 — U08 LEDGER

## Execution Unit

U08 — BTC + BTC.D Context & Relative-Movement Engine

## Validation

Global status: PASS
Technical lock: LOCKED

## Unit Coverage

### Unit 0 — Configuration / Enums
- CELL08_CONFIG with top_n, strong_movers_n, relative_movers_n, epsilon
- Direction, Context, RelativeDirection enums
- Tests: PASS

### Unit 1 — Enums
- Context, RelativeDirection enum definitions
- Tests: PASS

### Unit 2 — Normalization
- _safe_float, _normalize_direction, normalize_asset
- Tests: PASS

### Unit 3 — Scenario Matrix
- 9-scenario mapping for BTC/DIR x BTC.D/DIR
- validate_scenario_matrix
- Tests: PASS

### Unit 4 — Context Classification
- classify_context from BTC direction only
- Tests: PASS

### Unit 5 — Relative Performance
- calculate_relative_btc_performance
- classify_relative_performance
- Tests: PASS

### Unit 6 — Ranking
- rank_strong_movers, rank_relative_movers, rank_top_assets
- Tests: PASS

### Unit 7 — Altcoin Structure Context
- build_altcoin_structure_context
- build_scenario_ranking
- Tests: PASS

### Unit 8 — Narratives
- 27 locked patterns (9 scenarios x 3 patterns)
- validate_narratives
- Tests: PASS

### Unit 9 — Result
- Cell08Result dataclass, cell08_to_dict, cell08_to_json
- Tests: PASS

### Unit 10 — Engine
- run_cell_08 main engine entry point
- cell08_self_tests
- Tests: PASS

### Unit 11 — Regression Gate
- run_cell08_regression_tests
- Comprehensive Cell 8 invariants validation
- Tests: PASS

### Unit 12 — Integration
- End-to-end integration verification
- Tests: PASS

## Source Integrity

U08 does not modify U01-U07, U06.5, Cell 7, or Cell 8 source files.
Source data modified: FALSE

## Safety

Trading: DISABLED
Orders: DISABLED
Strategy: DISABLED
Portfolio Actions: DISABLED
No trading, orders, entries, exits, long/short, setup, trigger, or recommendations.

## Final Rule

U08 is technically locked only when every gate passes.
If validation fails, U08 remains NOT LOCKED.
