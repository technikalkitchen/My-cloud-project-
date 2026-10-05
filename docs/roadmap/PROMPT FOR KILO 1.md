# FINAL MANAGERIAL DIRECTIVE — STAGE A1 UNBLOCKING
## Python 3.12 Alignment + CURRENT_STATE Token-Efficiency Rule + A1 Resume

Dear Agent Manager,

The Owner has reviewed the current Stage A1 situation and authorizes the following controlled action.

This directive has TWO purposes:

1. Complete the one-time project-wide alignment from Python 3.11 to Python 3.12.
2. Establish a permanent, strict Token Efficiency Rule for `CURRENT_STATE.md`, so that the live resume state remains extremely concise and useful.

After these amendments are completed and verified, the affected documents are considered aligned again and locked.

No other project requirement is changed.


============================================================
# 1. OWNER AUTHORITY
============================================================

This is an explicit Owner-authorized directive.

The previous Python 3.11 decision is superseded.

The current authoritative project Python target is:

**Python 3.12**

The 3.11 → 3.12 transition is a:

**ONE-TIME OWNER-AUTHORIZED AMENDMENT**

This authorization exists only to resolve the current transition conflict and establish the new permanent target.

It does NOT grant permission for future changes to:

- Python version;
- architecture;
- Scope;
- Roadmaps;
- locked requirements;
- Stage definitions;
- dependencies;
- project structure;

without a new explicit Owner decision.

After this amendment is completed and verified, Python 3.12 must be treated as locked.

If any future change is requested without explicit Owner authorization:

**STOP and report BLOCKED.**


============================================================
# 2. IMPORTANT: DO NOT START A1 IMPLEMENTATION YET
============================================================

Do NOT begin normal Stage A1 implementation until the document-alignment phase below is completed and verified.

The required order is:

1. Apply the authorized document alignment.
2. Verify the alignment.
3. Begin/resume Stage A1.
4. Immediately create `docs/stages/STAGE_A1/CURRENT_STATE.md` with `IN_PROGRESS`.
5. Only after that begin A1 implementation.
6. Maintain the minimal CURRENT_STATE checklist during execution.
7. Complete testing and verification.
8. Report final Stage status.
9. Do NOT make the final A1 commit yet.


============================================================
# 3. REQUIRED DOCUMENT ALIGNMENT
============================================================

Apply ONLY the following authorized changes.

Do not make unrelated edits.

------------------------------------------------------------
3A. STAGE_A1_PAYLOAD.md
------------------------------------------------------------

Update the Python target consistently:

Change:

`Python target: 3.11`

to:

`Python target: 3.12`

Change:

`requires-python = ">=3.11"`

to:

`requires-python = ">=3.12"`

In Stop Conditions, change:

`Python 3.11 execution cannot be established.`

to:

`Python 3.12 execution cannot be established.`


------------------------------------------------------------
3B. ROADMAP_A.md
------------------------------------------------------------

Update the A1 Python requirements:

1. In the `pyproject.toml` specification:

Change:

`requires-python = ">=3.11"`

to:

`requires-python = ">=3.12"`

2. In the `stage_a1_config.py` specification:

Change:

`PYTHON_VERSION_TARGET = "3.11"`

to:

`PYTHON_VERSION_TARGET = "3.12"`

3. Remove:

`ENV_PLACEHOLDER: dict = {}`

This placeholder is no longer part of the approved A1 configuration requirement.

4. In the A1 tests:

Change the expected `requires-python` value from:

`">=3.11"`

to:

`">=3.12"`

5. Change the expected:

`PYTHON_VERSION_TARGET == "3.11"`

to:

`PYTHON_VERSION_TARGET == "3.12"`

6. In the relevant Execution Notes / Python Version note, change the project target from 3.11 to 3.12.


------------------------------------------------------------
3C. PREAMBLE_V4.md
------------------------------------------------------------

Verify the relevant Python references in the active Preamble.

The applicable Python project target must consistently be:

**3.12**

Do not alter unrelated Preamble content.

If a relevant active Preamble reference still states 3.11, update only that Python-version reference as part of this Owner-authorized transition.

No other Preamble requirement may be changed.


============================================================
# 4. PERMANENT CURRENT_STATE TOKEN-EFFICIENCY RULE
============================================================

Add the following rule to the appropriate CURRENT_STATE artifact guidance in `PREAMBLE_V4.md`:

**Token Efficiency Rule for CURRENT_STATE.md**

- `CURRENT_STATE.md` is the live resume state.
- It must remain extremely concise.
- It must use short, one-line checklist items only.
- Do not write long paragraphs.
- Do not write descriptive reports.
- Do not repeat technical explanations.
- Do not place detailed test reports in CURRENT_STATE.
- Do not place architectural reasoning in CURRENT_STATE.
- Do not use CURRENT_STATE as a substitute for LEDGER.md or the final Stage report.
- Update it after each major step or meaningful file-creation group.
- Keep every update minimal and directly useful for resuming work.
- The purpose of CURRENT_STATE is seamless resumption, not detailed documentation.

Preferred style:

`Status: IN_PROGRESS`

`- [x] Project skeleton created`

`- [x] A1 configuration created`

`- [ ] Structural tests pending`

Avoid long prose such as:

`The project skeleton has now been successfully created and all required files were carefully reviewed...`

The second style is prohibited.

The objective is to minimize token usage while preserving enough state to resume the Stage reliably.


============================================================
# 5. KILO_MASTER_PROMPT_V4.md
============================================================

Update Section 10 (Artifacts) to explicitly state:

`CURRENT_STATE.md` must be maintained as a minimalist live checklist.

It must not contain long paragraphs or detailed reporting.

It must be updated after each major action or meaningful execution step so that the Stage can be resumed reliably with minimal token usage.

This is a permanent operating rule.

Do not change any other Kilo Master Prompt rule.


============================================================
# 6. VERIFY THE AMENDMENT BEFORE EXECUTION
============================================================

After making the authorized document changes, verify:

1. Relevant active Python references are consistently 3.12.
2. A1 Payload requires Python 3.12.
3. ROADMAP_A requires Python 3.12.
4. A1 configuration target is 3.12.
5. A1 test expectations are 3.12.
6. `ENV_PLACEHOLDER` is removed from the affected A1 requirement.
7. PREAMBLE contains the new CURRENT_STATE Token Efficiency Rule.
8. KILO_MASTER_PROMPT_V4 contains the corresponding CURRENT_STATE rule.
9. No unrelated requirement was changed.
10. No architecture was changed.
11. No Stage Scope was expanded.
12. No unrelated files were modified.

If any unrelated conflict appears:

**STOP and report BLOCKED.**

Do not improvise.


============================================================
# 7. BEGINNING / RESUMING STAGE A1
============================================================

Only after the document-alignment phase is verified may normal Stage A1 execution resume.

The FIRST execution action of Stage A1 must be:

Create:

`docs/stages/STAGE_A1/CURRENT_STATE.md`

with a minimal live state indicating:

`Status: IN_PROGRESS`

This file must exist BEFORE A1 implementation begins.

Do NOT wait until the end of A1 to create CURRENT_STATE.

Do NOT write a long initialization report into it.

The initial state should be minimal.


============================================================
# 8. CURRENT_STATE MAINTENANCE DURING A1
============================================================

During Stage A1:

- update CURRENT_STATE after each major step or meaningful file-creation group;
- keep updates extremely short;
- use one-line checklist items;
- do not write paragraphs;
- do not duplicate the Ledger;
- do not record detailed technical reasoning;
- do not record long test output;
- do not turn CURRENT_STATE into a progress report.

Example:

`Status: IN_PROGRESS`

`- [x] Root files created`

`- [x] App package structure created`

`- [x] Project identity created`

`- [ ] A1 structural tests pending`

This is the intended level of detail.

The goal is:

**minimum token cost + reliable resume state.**

Do not optimize for verbosity.

Do not add unnecessary status prose.


============================================================
# 9. STAGE A1 EXECUTION
============================================================

After CURRENT_STATE has been created:

Follow the approved Stage A1 lifecycle:

Study → Plan → Implement → Test → Verify → Report

Execute only the approved A1 Scope.

Implement the V4 project skeleton exactly according to the aligned:

- PREAMBLE_V4;
- ROADMAP_A;
- STAGE_A1_PAYLOAD;
- KILO_MASTER_PROMPT_V4.

Use Python 3.12 as the project target.

Do not add business logic.

Do not add future-stage infrastructure.

Do not expand Scope.


============================================================
# 10. REQUIRED A1 ARTIFACTS
============================================================

Create and maintain the four required Stage artifacts:

- `CURRENT_STATE.md`
- `LEDGER.md`
- `MANIFEST.json`
- `SHA256.json`

`CURRENT_STATE.md` is the live minimalist resume state.

`LEDGER.md` is for execution history/details.

`MANIFEST.json` is the Stage manifest.

`SHA256.json` is the integrity artifact.

Do not use CURRENT_STATE as a replacement for the other artifacts.


============================================================
# 11. A1 VALIDATION
============================================================

Run the required Stage A1 structural test:

`pytest tests/stages/STAGE_A1/test_stage_a1_structure.py -v`

All 13 required tests must pass.

Verify at minimum:

- project structure;
- init files;
- project identity;
- pyproject validity;
- gitignore;
- README;
- conftest;
- gitkeep files;
- forbidden folders;
- Stage artifact folder;
- configuration import;
- forbidden external imports;
- absence of runtime logic.

Also explicitly verify:

`pyproject.toml`

declares:

`requires-python = ">=3.12"`

and:

`app/config/stage_a1_config.py`

contains:

`PYTHON_VERSION_TARGET = "3.12"`

with no `ENV_PLACEHOLDER`.


============================================================
# 12. STRICT SCOPE PROTECTION
============================================================

Work only on branch:

`v4`

Do NOT modify:

`main`

Do NOT create:

- future-stage folders;
- logging system;
- security system;
- exchange connections;
- provider connections;
- Telegram implementation;
- analysis logic;
- trading logic;
- orderbook implementation;
- journal implementation;
- unapproved dependencies;
- files outside A1 Scope.

Do not silently improve unrelated project design.

Do not modify unrelated requirements.


============================================================
# 13. FINAL COMMIT
============================================================

Do NOT make the final A1 commit now.

The final commit is still subject to:

- successful A1 implementation;
- successful required validation;
- verification;
- Technical Designer review;
- Owner approval.

When eventually approved, the required commit message is:

`Stage A1: project skeleton`

Do not create that final commit until explicitly authorized.


============================================================
# 14. STOP CONDITIONS
============================================================

Stop and report `BLOCKED` if:

- the Scope is ambiguous;
- authoritative documents conflict after alignment;
- an architectural decision is required;
- a required file is unclear;
- Python 3.12 cannot be established;
- required repository access is unavailable;
- required tests cannot be validly executed;
- continuing requires an out-of-Scope file/folder;
- continuing requires a new dependency not approved;
- continuing requires changing a locked requirement;
- continuing requires modifying main;
- continuing would violate PREAMBLE_V4;
- success would require guessing.

Do NOT silently resolve such conditions.

Do NOT invent requirements.

Do NOT continue through a genuine blocker.


============================================================
# 15. NO UNAUTHORIZED FUTURE CHANGES
============================================================

After the Python 3.12 alignment is complete:

Python 3.12 is LOCKED.

After the CURRENT_STATE Token Efficiency Rule is added:

that rule is LOCKED.

These changes do not create general permission to modify the project rules.

Any future change to:

- Python version;
- architecture;
- Scope;
- Roadmap;
- Preamble;
- Kilo Master Prompt;
- Stage Payload;
- project structure;

requires explicit Owner authorization.


============================================================
# 16. FINAL RESPONSE CONTRACT
============================================================

After completing the requested work, respond using exactly this structure:

Status: PASSED | BLOCKED | FAILED

Completed:
- ...

Tests:
- ...

Verification:
- ...

Artifacts:
- ...

Out-of-scope changes:
- None
  OR
- ...

Blockers:
- None
  OR
- ...

Next action:
- APPROVAL_REQUIRED
  OR
- RESOLVE_BLOCKER
  OR
- CONTINUE_CURRENT_STAGE

Keep the final response concise.

Do not write a long narrative outside this structure.


============================================================
# 17. MOST IMPORTANT EXECUTION ORDER
============================================================

The execution order is mandatory:

PHASE 1 — DOCUMENT ALIGNMENT
1. Align Python references to 3.12.
2. Remove the affected ENV_PLACEHOLDER requirement.
3. Add the permanent CURRENT_STATE Token Efficiency Rule.
4. Add the corresponding rule to KILO_MASTER_PROMPT_V4.
5. Verify all alignment.
6. Verify no unrelated requirement changed.

PHASE 2 — A1 RESUME
7. Create `CURRENT_STATE.md`.
8. Set it to `IN_PROGRESS`.
9. Begin A1 implementation.
10. Maintain CURRENT_STATE as a minimal checklist.
11. Complete A1 Scope.
12. Create/maintain all four artifacts.
13. Run the 13 required tests.
14. Verify acceptance.
15. Report the Stage result.

PHASE 3 — APPROVAL
16. Do NOT make the final A1 commit.
17. Wait for Technical Designer review and Owner approval.


============================================================
# FINAL PRINCIPLE
============================================================

The purpose of this directive is NOT to give Kilo freedom.

It is to remove one known blocker and make the execution rules more precise.

The intended outcome is:

- one authoritative Python version: 3.12;
- no stale 3.11 conflict;
- no obsolete ENV_PLACEHOLDER requirement;
- a real CURRENT_STATE from the beginning of A1;
- extremely low token usage for CURRENT_STATE;
- reliable Stage resumption;
- no Scope expansion;
- no unauthorized architecture changes;
- no unauthorized future requirement changes;
- no final commit before approval.

Execute exactly this directive.
Do not improvise.
