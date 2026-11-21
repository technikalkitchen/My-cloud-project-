# AGENTS — Kitchen Assistant Bot V4 (keep <90 lines)

Owner = the human. Owner decides, you execute. Memory lives in files, not in chat.

## Session start (this order, then STOP)

1. This file. 2. docs/Agents/STATE.md. 3. Router below, for the task only.

Task not in router -> ask Owner. Do NOT scan the repo.

## Hard rules

- Report a step as done only after verifying it (ls/grep/wc/run). Unsure -> say "unverified".
- Never delete, never `git reset --hard`, `git clean`, or force-push. Move files with `git mv`. Deleting needs Owner's explicit OK.
- Do only the step Owner named. No extras, no refactor.
- Never guess. Unknown -> write "unknown" and ask.
- Do not invent rules. Only docs/memory/registry.md holds confirmed rules. Add an entry ONLY after Owner explicitly confirms it in this session.
- Owner is not a programmer: reports in simple Persian; English technical terms only when needed. No other languages.

## Source of truth (highest wins)

1. docs/memory/registry.md (Owner-confirmed decisions)
2. Owner's explicit instruction in the current session
3. docs/Agents/00_START_HERE.md (operating rules; section numbers are stable references)
4. docs/memory/lessons.md (experience; the data/exchange facts section may be stale: verify before relying)

NOT rules, raw material only: docs/memory/draft/*, docs/B_items/* (old), docs/archive/*, docs/legacy/*, tests/TEST_MAP_v3.4_FINAL.md. Read them only when router/Owner says. Never copy a claim from them into registry.

## Map (use this; do not scan)

- docs/Agents/: AGENTS.md (this), STATE.md (live status), LEDGER.md (append-only log), 00_START_HERE.md (operating rules)
- docs/memory/: registry.md (confirmed decisions), lessons.md, CONFLICTS.md (X-xx by Item), OPEN_QUESTIONS.md (Q-xx), TEST_QUEUE.md (T-xx), draft/ (+INDEX.md)
- docs/B_items/: old Item docs (Items 13,14,16-30 are empty; write fresh)
- docs/PLAN_MEMORY_SETUP.md: setup plan with ticks
- docs/reports/LAST_REPORT.md: report for Owner (overwrite)
- docs/archive/, docs/legacy/: backups, never read
- MAP.md: docs/MAP.md; team protocol: docs/TEAM_PROTOCOL.md; test evidence: tests/evidence/; storage script: tests/evidence/gen_manifest.py

## Router

| Task | Read |
| Write/rewrite Item N | registry.md; START_HERE s3; lessons.md; `grep "Item_N" CONFLICTS.md OPEN_QUESTIONS.md`; draft/item_N.md (raw material only). First resolve that Item's conflicts with Owner; never write over unresolved conflicts |
| Design/run a test | its T-xx entry in TEST_QUEUE.md; lessons.md; START_HERE s7 and s8; registry.md |
| Resolve conflicts/decisions with Owner | CONFLICTS.md, OPEN_QUESTIONS.md, registry.md header. Max 5 per batch, numbered options, record in registry only after Owner confirms |
| Record a decision | registry.md (format: ID | status | date | text | confirmed by) |
| Change structure/rules | START_HERE s12; PLAN |
| Memory-system setup | docs/PLAN_MEMORY_SETUP.md |
| Anything else | ask Owner |

## End of every task (definition of done)

1. Overwrite docs/Agents/STATE.md (<=40 lines: phase, current task, exact next step, blockers).
2. Append ONE line to docs/Agents/LEDGER.md: HH:MM | CODE | what | -> result. Read LEDGER only with `tail -20`.
3. Tick the plan step in docs/PLAN_MEMORY_SETUP.md if the task is a plan step.
4. git add, commit (clear message), push.
5. Report: short (<=10 lines) in chat. Anything Owner must copy goes to docs/reports/LAST_REPORT.md (overwrite, <=40 lines unless Owner allows more). Owner reads on a phone: no raw logs, no long JSON.

## Cold start or cut session

Read STATE.md, `git status`, `git log -5 --oneline`. Continue from STATE "Next step". Half-written or uncommitted files: verify, finish, commit. Never redo finished work.

## Tests

Raw test output is saved to disk by the test script (START_HERE s7); JSON is evidence. Summarize, never paste long output.

## Branch

Canonical branch: `v4`
