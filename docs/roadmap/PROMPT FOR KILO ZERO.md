# KILO DIRECTIVE — PERMANENT REPORT COMPLETENESS RULE

## 1. STATUS

OWNER-AUTHORIZED DOCUMENT GOVERNANCE CHANGE

This directive authorizes a permanent documentation/governance amendment only.

It does NOT authorize:
- Stage A1 implementation;
- Stage execution or resumption;
- code changes;
- test changes;
- architecture changes;
- scope expansion;
- repository restructuring;
- changes to `main`;
- new dependencies;
- commits or pushes beyond the document amendment itself.

The purpose of this directive is to permanently establish the Report Completeness Rule for all future Stage completion reports.

────────────────────────────────────────
## 2. PURPOSE

The A1 completion process demonstrated that an implementation may pass all required tests while the completion report remains incomplete or ambiguous.

To prevent repeated evidence-collection cycles, a permanent Report Completeness Rule shall be added to the authoritative governance documents.

This rule applies to every future Stage, including but not limited to:
- A2
- A3
- B1
- and all subsequent Stages.

The rule is a permanent governance requirement, not a Stage-specific requirement.

────────────────────────────────────────
## 3. AUTHORIZED FILES

Modify only these two files:

1. `docs/roadmap/PREAMBLE_V4.md`
2. `docs/roadmap/KILO_MASTER_PROMPT_V4.md`

No other file may be modified.

Do not modify:
- Roadmaps;
- Stage Payloads;
- CURRENT_STATE files;
- Stage artifacts;
- source code;
- tests;
- README;
- configuration;
- repository structure;
- any other project document.

────────────────────────────────────────
## 4. PREAMBLE_V4.md — EXACT INSERTION

In:

`docs/roadmap/PREAMBLE_V4.md`

insert the new section as:

`Section 14 — REPORT COMPLETENESS RULE`

immediately after existing Section 13.

Do not insert it elsewhere.

The new Section 14 shall establish the permanent requirement that every Stage completion report must contain sufficient evidence for independent verification without requiring a separate evidence-collection cycle.

The Report Completeness Rule must require the completion report to contain, as applicable and with explicit factual wording:

### 14.1 Repo State
- current branch;
- `git status --short`;
- latest commit hash and message;
- `git diff main..<branch> --stat`.

### 14.2 Scope Evidence
- complete list of created/modified files and folders;
- explicit confirmation that no out-of-scope changes were made;
- explicit results for forbidden paths/items.

### 14.3 Alignment Evidence
- searches/checks for stale, forbidden, or conflicting values;
- clear distinction between active/current repository state and historical/legacy records;
- exact relevant configuration/document values where needed.

### 14.4 Test Evidence
- exact command executed;
- collected/passed/failed/skipped results;
- relevant warnings or deviations.

### 14.5 Artifact Evidence
- confirmation of all required Stage artifacts;
- MANIFEST consistency;
- SHA256 consistency where applicable.

### 14.6 Commit Evidence
- status of the final Stage commit where applicable;
- confirmation that `main` was not modified.

### 14.7 Anomaly Disclosure
- any legacy, historical, deleted, archived, or otherwise non-current reference that could be mistaken for an active repository item must be explicitly identified and clarified.

The report must distinguish active repository state from historical records.

The report must not use ambiguous statements such as:
- `EXISTS`
- `PRESENT`
- `FOUND`

without identifying whether the item is:
- currently present in the working tree;
- tracked by Git;
- historical only;
- deleted;
- or otherwise non-current.

Summary-only completion reports are prohibited.

The completion report must be self-contained enough that a reviewer can determine what was actually completed, tested, verified, and changed without relying on inference.

If mandatory report evidence is missing, the implementation may not be reported as fully `PASSED`; the reporting result is incomplete/failed even if the implementation itself succeeded.

The rule must remain token-efficient and must not require unnecessary narrative.

────────────────────────────────────────
## 5. KILO_MASTER_PROMPT_V4.md — EXACT INSERTION

In:

`docs/roadmap/KILO_MASTER_PROMPT_V4.md`

add:

`Section 14 — Report Completeness (Reference to PREAMBLE_V4 Section 14)`

immediately after existing Section 13.

Do not insert it elsewhere.

Section 14 of KILO_MASTER_PROMPT_V4.md shall explicitly reference and defer to:

`PREAMBLE_V4 Section 14 — REPORT COMPLETENESS RULE`

It shall state that Kilo must follow the permanent Report Completeness Rule when producing every future Stage completion report.

It must preserve the distinction between:
- implementation success;
- verification evidence;
- repository state;
- current vs historical records;
- and reporting completeness.

PREAMBLE_V4 Section 14 remains the authoritative source for the rule.

────────────────────────────────────────
## 6. VERSION AND LOCKED STATUS

Do NOT change the version number.

Keep:

`PREAMBLE_V4 v1`

Do NOT change the `LOCKED` status.

Simply add the new Section 14.

Optionally, a one-line amendment note may be added at the top of PREAMBLE:

`Amended by Owner authorization: Report Completeness Rule (Section 14) added.`

No other version or status wording changes are allowed.

Do not create a new version number.

Do not rename the documents.

Do not introduce a new governance version.

────────────────────────────────────────
## 7. PRESERVATION AND VALIDATION

The amendment is strictly additive.

Verify that:

- Section 14 was inserted at the exact required position in PREAMBLE_V4;
- Section 14 was inserted at the exact required position in KILO_MASTER_PROMPT_V4;
- both documents remain internally coherent;
- existing locked requirements remain intact;
- existing authority hierarchy remains intact;
- Python 3.12 remains the current Owner-authorized project target;
- existing CURRENT_STATE Token Efficiency Rule remains intact;
- A1 boundaries remain intact;
- existing lifecycle remains intact;
- existing artifact rules remain intact;
- existing Final Response Contract remains intact;
- no pre-existing section, rule, or wording was removed, truncated, or rewritten;
- only additive changes are authorized for this directive;
- no unrelated wording was changed.

Verify that no pre-existing section, rule, or wording was removed, truncated, or rewritten. Only additive changes are authorized for this directive.

Verify that no contradictory Report Completeness wording was introduced.

Verify that no other project file was modified.

Verify that `main` remains untouched.

No new tests are required for this document-only amendment.

────────────────────────────────────────
## 8. LOCKING RULE

The Report Completeness Rule is permanent.

After this amendment, both documents remain in LOCKED status. This amendment is additive and does not unlock them.

The new Section 14 applies to every future Stage unless a future Owner-authorized governance amendment explicitly changes it.

Kilo must not weaken, remove, bypass, or reinterpret the rule.

────────────────────────────────────────
## 9. FINAL RESPONSE CONTRACT

Use the existing KILO_MASTER_PROMPT_V4 Final Response Contract.

Do not alter the structure of that contract.

For this document-only amendment, in the `Tests:` field, report exactly:

`None required — document-only amendment.`

The final response must still clearly report:
- what was changed;
- what was verified;
- that only the two authorized documents were modified;
- that no out-of-scope changes were made;
- whether any blocker exists.

Next action must remain:

`APPROVAL_REQUIRED`

────────────────────────────────────────
## 10. SCOPE RESTRICTION

This directive does NOT authorize:

- Stage A1 execution;
- Stage A1 modification;
- Stage A1 re-testing;
- Stage A2 preparation;
- source-code changes;
- test-code changes;
- architecture changes;
- Roadmap changes;
- Stage Payload changes;
- CURRENT_STATE changes;
- new files;
- deleted files;
- new dependencies;
- repository restructuring;
- changes to `main`;
- push operations outside the authorized document amendment.

Only the two files explicitly named in Section 3 may be modified.

────────────────────────────────────────
## 11. REPORTING REQUIREMENT

The completion report for this directive must itself comply with the newly established Report Completeness Rule.

Therefore the report must include sufficient evidence for:

1. Repo State
2. Scope Evidence
3. Alignment Evidence
4. Test Evidence
5. Artifact Evidence, where applicable
6. Commit Evidence, where applicable
7. Anomaly Disclosure

Do not create a separate evidence cycle by omitting these facts from the initial report.

Do not use ambiguous repository-state wording.

────────────────────────────────────────
## 12. NO IMPLEMENTATION EXPANSION

This directive exists only to establish the permanent Report Completeness Rule.

Do not add:
- new governance systems;
- new reporting formats beyond the required rule;
- new audit systems;
- new artifact types;
- new approval systems;
- new Stage requirements;
- new technical requirements.

Preserve all existing V4 governance unless explicitly changed by the six clarifications in this directive.

────────────────────────────────────────
## 13. AUTHORITY

This is an OWNER-AUTHORIZED DOCUMENT GOVERNANCE CHANGE.

The Owner remains the final authority.

Kilo is authorized only to perform the explicitly described document amendment.

If any requirement in this directive is ambiguous or conflicts with a higher-authority locked rule, STOP and report `BLOCKED`.

Do not guess.

Do not silently reconcile conflicts.

Do not expand Scope.

────────────────────────────────────────
## 14. COMPLETION CONDITION

The directive is complete only when:

- PREAMBLE_V4 Section 14 exists at the exact required position;
- KILO_MASTER_PROMPT_V4 Section 14 exists at the exact required position;
- the Report Completeness Rule is permanently established;
- both documents remain `v1` and `LOCKED`;
- no pre-existing content was removed, truncated, or rewritten;
- only the two authorized documents were modified;
- no unrelated changes were made;
- the amendment is verified;
- the completion report itself satisfies the Report Completeness Rule.

If all conditions are satisfied:

Status: PASSED

Otherwise:

Status: BLOCKED or FAILED, according to the existing KILO_MASTER_PROMPT_V4 rules.

Next action:

APPROVAL_REQUIRED
