# WORK_STATE.md — v1.0 (2026-11-21)

## Objective

Phase 1: familiarize Kilo with project.
Phase 2: extract required tests per Item.
Nothing else until both phases are complete.

## Current Task

Verify storage automation script path.
TEAM_PROTOCOL §10.2 references `tests/evidence/gen_manifest.py`, `scan_repo.sh`, `triage.tsv`, `pending.tsv` — not yet confirmed on disk.
Owner confirms automation exists but path unknown.

## Next Actions

1. Confirm storage script path (read-only inspection of `tests/evidence/` and any `*.py` / `*.sh` referencing "MANIFEST")
2. Begin Phase 2 — extract test requirements per Item (start with Item_08, Item_10, Item_01)

## Files In Scope (this task only)

- `tests/evidence/` (directory listing)
- Any `.py` or `.sh` containing "MANIFEST" or "manifest"

## Core Files (read at every session start)

- `AGENTS.md`
- `docs/Agents/00_START_HERE.md`
- `docs/Agents/WORK_STATE.md` (this file)
- `docs/Agents/LEDGER.md` (tail 30 lines only)

## Reference Files (read once; consult only when needed)

- `docs/TEAM_PROTOCOL.md` — laws, R-rules, DoD, header format
- `docs/MAP.md` — 30-item structure (LOCKED)
- `tests/TEST_MAP_v3.4_FINAL.md` — historical only per §5 of START_HERE
- `docs/B_items/Item_Registry.md` — WORKING NOTE (not locked); only CIN-03/04/05 present
- `docs/handoff/AM_03_SUM_part01-05.md` — AM-03 summaries; do NOT re-read underlying chat history

## Key Decisions (with refs)

- Branch `v4` is canonical — no switching.
- Test storage automation EXISTS (Owner confirmed) — path TBD.
- Only 2 phases: (1) familiarization, (2) test extraction.
- No item rewriting. No infrastructure build. Until phases 1+2 complete.
- R-30 resolved: 4 base TFs (5m, 15m, 1h, 1d); 5m rolling 1 day in memory; 15m/1h/1d stored permanently by Collector — ref: `docs/handoff/AM_03_SUM_part06.md`
- R-33 ACTIVE: every message starts with `<<EOT>>`, ends with `<<SOT>>` — ref: `docs/TEAM_PROTOCOL.md` §R-33
- 8 items flagged NEEDS_REWORK by AM-03: Item_01, 03, 04, 05, 06, 08, 09, 10 — ref: `docs/handoff/AM_03_SUM_part03.md`, `part04`, `part05`

## Blockers

- Storage script path unknown.
- No WORK_STATE.md or LEDGER.md existed before this task (being created now).

## Last Update

2026-11-21 — initial creation.
