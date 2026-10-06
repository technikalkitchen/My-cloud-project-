# PROMPT FOR KILO ZERO CORRECTION 1
## PREAMBLE_V4 SECTION 14 POSITION FIX

STATUS:
OWNER-AUTHORIZED CORRECTIVE WRITE ACTION

The RAW Report for the already-completed Zero action established one specific blocker:

`docs/roadmap/PREAMBLE_V4.md`

Section 14 — REPORT COMPLETENESS RULE is currently positioned between Section 12 and Section 13.

The required position is immediately after Section 13.

This prompt authorizes ONE corrective action only:
reposition Section 14 so that it appears immediately after Section 13.

This is NOT a new Stage.
This is NOT a Zero re-execution.
This is NOT an A1 review.
No additional evidence-collection cycle is required.

---

## 1. AUTHORIZED FILE

The ONLY file you may modify is:

`docs/roadmap/PREAMBLE_V4.md`

No other file may be modified.

---

## 2. EXACT AUTHORIZED CHANGE

Open:

`docs/roadmap/PREAMBLE_V4.md`

Locate the existing Section 14 by its title (`REPORT COMPLETENESS RULE`) and its current position between Section 12 and Section 13.

The heading text may be formatted as `## 14 — ...` or `## Section 14 — ...`.

Report the exact heading text you find before moving it.

Perform ONLY the following operation:

1. Remove the existing Section 14 from its current position.
2. Insert that exact same Section 14 immediately after Section 13.
3. Preserve the complete Section 14 content exactly as-is.
4. Do not rewrite, reformat, shorten, expand, trim, or reinterpret Section 14.

The final order must be:

`Section 12`
→
`Section 13`
→
`Section 14`

Any content that currently follows Section 13 must remain following Section 14 after the correction. The relative order of all other sections must not change.

Do not alter any other line.

---

## 3. PRESERVATION REQUIREMENTS

The following must remain unchanged:

- Section 12 content
- Section 13 content
- Section 14 content
- every other existing PREAMBLE section
- version `v1`
- `LOCKED` status
- Python 3.12 alignment
- CURRENT_STATE Token Efficiency Rule
- all existing governance wording

Section 14 must be byte-identical to its pre-correction content, except for its position in the document.

No other content change is authorized.

---

## 4. FORBIDDEN CHANGES

Do NOT modify:

`docs/roadmap/KILO_MASTER_PROMPT_V4.md`

Do NOT modify:

- Stage A1 files
- Stage A1 tests
- Stage artifacts
- ROADMAP_A.md
- STAGE_A1_PAYLOAD.md
- configuration files
- source code
- any other project file

Do NOT:

- create files
- delete files
- modify `main`
- commit
- push
- reset
- checkout
- stash
- change branches
- re-execute Zero
- restart Stage A1
- perform an A1 audit
- perform a repository-wide audit
- perform another RAW evidence-collection cycle

---

## 5. KILO_MASTER_PROMPT_V4.md — VERIFICATION ONLY

Read:

`docs/roadmap/KILO_MASTER_PROMPT_V4.md`

Do NOT modify it.

Verify whether its Section 14 is already immediately after the last existing section of that document, which is the Final Response Contract section.

If it is correctly positioned:
- report it as verified.

If it is also misplaced:
- STOP.
- Report `BLOCKED`.
- Do NOT fix it.

A separate Owner-authorized directive would be required for any correction to that file.

---

## 6. REQUIRED VERIFICATION

After the correction, verify:

1. Section 13 remains intact.
2. Section 14 now appears immediately after Section 13.
3. Section 14 content is unchanged.
4. Section 12 content is unchanged.
5. No other PREAMBLE section changed.
6. PREAMBLE version remains `v1`.
7. PREAMBLE remains `LOCKED`.
8. KILO_MASTER_PROMPT_V4.md was not modified.
9. No other project file was modified.
10. `main` was not touched.

To prove Section 14 content is unchanged, use:

`git diff HEAD -- docs/roadmap/PREAMBLE_V4.md`

and show that the removed Section 14 lines and the added Section 14 lines contain identical content. Only the position has changed. Report the relevant diff evidence.

---

## 7. REPORT COMPLETENESS

The completion report must follow the existing Report Completeness Rule.

Include:

### Repo State
- Current branch
- Exact `git status --short`
- Latest commit hash and message
- Exact `git diff HEAD --stat`

### Scope Evidence
- Confirm that the only file modified by this corrective action is:
  `docs/roadmap/PREAMBLE_V4.md`
- Confirm that no other file was modified by this action.

### Alignment Evidence
- Confirm Section 14 was moved only in position.
- Confirm Section 14 content is unchanged.
- Confirm Section 12 and Section 13 are unchanged.
- Confirm Section 14 is now immediately after Section 13.
- Confirm version `v1` and `LOCKED` status remain unchanged.
- Confirm KILO_MASTER_PROMPT_V4.md Section 14 was verified but not modified.

### Test Evidence
`None required — document-only correction.`

### Artifact Evidence
`Not applicable.`

### Commit Evidence
`No commit created; main untouched.`

### Anomaly Disclosure
Report any relevant anomaly or unexpected condition explicitly.

Note that `git diff HEAD` on `PREAMBLE_V4.md` may include both the original Zero addition of Section 14 AND the current position correction. Only the position correction is authorized by this directive. Explicitly distinguish them in the report.

Do not use ambiguous wording such as:

- EXISTS
- PRESENT
- FOUND

Use exact, verifiable statements.

---

## 8. STOP CONDITIONS

STOP and report:

`Status: BLOCKED`

if:

- Section 14 cannot be located in PREAMBLE_V4.md.
- Section 14 cannot be moved without changing its content.
- Section 14 in KILO_MASTER_PROMPT_V4.md is also misplaced.
- Any other file would need to be modified.
- The exact target position is ambiguous.
- The correction would affect `main`.
- Success would require guessing.
- Any unexpected condition prevents the authorized correction from being completed safely.

Do not broaden the scope to resolve a blocker.

---

## 9. EXISTING FINAL RESPONSE CONTRACT

Use the existing Final Response Contract without modification.

After successful correction:

Next action:
`APPROVAL_REQUIRED`

---

## 10. COMPLETION CONDITION

The corrective action is complete only when:

`docs/roadmap/PREAMBLE_V4.md`

has the final order:

`Section 12 → Section 13 → Section 14`

with Section 14 content preserved exactly as it existed before the correction.

No other file may have been modified by this corrective action.

Do not begin any other task after completing this correction.
