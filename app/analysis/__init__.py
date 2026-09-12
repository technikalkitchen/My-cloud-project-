"""Kitchen Assistant V3.1 — Stage 7 (U07) Market Structure Scenario Engine.

Stage 7 consumes the frozen U06.5 Market Data Foundation as source of truth
and implements:
  - Unit 7.1 Input contract (validation of the U07 adapter from U06.5)
  - Unit 7.2 Calculations (Total-market and USDT.D movements)
  - Unit 7.3 Scenario Matrix (canonical 9-scenario mapping)
  - Unit 7.4 Intelligence (locked Persian narratives)
  - Unit 7.5 Integrated pipeline (orchestrator)

No trading execution, entry, exit, long, short, or trade signal logic is
implemented. Output is analysis/classification only.
"""