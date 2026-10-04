# STAGE_A1_PAYLOAD

**Payload Version:** 1.0  
**Status:** APPROVED FOR EXECUTION  
**Package:** A  
**Stage:** A1  
**Roadmap:** ROADMAP_A.md

----------

## Identity

-   Stage ID: `STAGE_A1`
-   Package: `A`
-   Type: Bootstrap Skeleton
-   Dependency: Preparation must already be complete
-   Branch creation: NOT PART OF A1
-   Reference-document transfer: NOT PART OF A1

----------

## 3. CURRENT STAGE

Execute only:

`STAGE_A1 — Project Structure Bootstrap`

Do not execute A2 or any later Stage.

----------

## 4. OBJECTIVE

Establish the initial V4 project skeleton and Stage A1 artifact structure.

The Stage must provide:

-   approved project folders;
-   approved base files;
-   project identity;
-   configuration placeholders;
-   structural tests;
-   Stage A1 artifacts.

No business capability is to be implemented.

----------

## 5. SCOPE

Create only the files and folders defined by the approved ROADMAP_A Stage A1 Scope.

### Root files

```text
.gitignore
README.md
pyproject.toml
conftest.py

```

### App structure

```text
app/__init__.py
app/config/__init__.py
app/core/__init__.py
app/data/__init__.py
app/market/__init__.py
app/analysis/__init__.py
app/bot/__init__.py
app/api/__init__.py

```

### Project identity

```text
app/core/stage_a1_version.py

```

Required values:

```python
PROJECT_NAME = "Kitchen Assistant Bot"
PROJECT_VERSION = "V4"
CURRENT_STAGE = "A1"

```

No additional logic or unnecessary imports.

### Configuration placeholder

```text
app/config/stage_a1_config.py
```

Allowed content is limited to a single project-level constant.
No runtime logic. No environment placeholder. No secret handling.

```python
PYTHON_VERSION_TARGET = "3.11"
```

### Tests

```text
tests/stages/STAGE_A1/test_stage_a1_structure.py

```

The test file must contain the 13 required Stage A1 tests defined in the Roadmap.

### Infrastructure storage directories

Create:

```text
scripts/.gitkeep
data/.gitkeep
logs/.gitkeep

```

These directories are explicitly part of A1 Scope.

### Stage artifacts

Create:

```text
docs/stages/STAGE_A1/
├── CURRENT_STATE.md
├── LEDGER.md
├── MANIFEST.json
└── SHA256.json

```

Follow PREAMBLE_V4 artifact rules.

----------

## 6. OUT OF SCOPE

Do not create or implement:

-   `app/logging/`
-   `app/trading/`
-   `app/journal/`
-   `app/orderbook/`
-   `ledgers/`
-   `LICENSE`
-   logging system;
-   security system;
-   Google Drive integration;
-   exchange/provider connections;
-   analysis logic;
-   Telegram interface;
-   final Web Server selection;
-   runtime environment loading;
-   secret handling;
-   trading functionality;
-   future-stage folders;
-   unapproved dependencies;
-   files outside Scope.

Do not create a Branch.

Do not transfer PREAMBLE or ROADMAP documents.

Those actions belong to Preparation, which is outside A1.

----------

## 8. TECHNICAL CONSTRAINTS

-   Python target: `3.11`
-   `pyproject.toml` must declare `requires-python = ">=3.11"`.
-   No runtime/environment loading.
-   No secret handling.
-   No exchange/network access.
-   No unapproved dependency.
-   No business logic.
-   No analysis logic.
-   No server implementation.
-   No Telegram implementation.
-   No modifications to `main`.
-   `scripts/`, `data/`, and `logs/` are allowed only as empty infrastructure directories represented by `.gitkeep`.
-   Do not create additional future folders.

Final A1 commit is permitted only after technical-designer and owner approval.

Required final commit message:

```text
Stage A1: project skeleton

```

----------

## 9. VALIDATION / ACCEPTANCE

Run:

```text
pytest tests/stages/STAGE_A1/test_stage_a1_structure.py -v

```

All 13 tests must pass.

Required tests:

1.  `test_01_structure_exists`
2.  `test_02_init_files_present`
3.  `test_03_version_identity`
4.  `test_04_pyproject_valid`
5.  `test_05_gitignore`
6.  `test_06_readme`
7.  `test_07_conftest`
8.  `test_08_gitkeep`
9.  `test_09_no_forbidden_folders`
10.  `test_10_stage_folder_exists`
11.  `test_11_config_imports`
12.  `test_12_no_external_imports`
13.  `test_13_no_runtime_logic`

External imports forbidden by the Stage test:

```text
requests
urllib
http
socket
telegram
flask
httpx
aiohttp

```

Runtime logic checks include absence of:

```text
def
os.environ
os.getenv
.open
read_text
read_bytes

```

Acceptance requires:

1.  All Scope files/folders exist.
2.  All forbidden folders are absent.
3.  All 13 tests pass.
4.  No analysis/server/business logic exists.
5.  Four Stage artifacts exist.
6.  MANIFEST is compatible with SHA256.
7.  No out-of-Scope files were created.

These criteria follow the approved A1 Roadmap.

----------

## 12. STOP CONDITIONS

Stop and report `BLOCKED` if:

-   Scope is ambiguous.
-   A required file is not clearly defined.
-   A requirement conflicts with PREAMBLE_V4 or the approved Roadmap.
-   An architectural decision is required.
-   Python 3.11 execution cannot be established.
-   Required repository access is unavailable.
-   A required test cannot be executed or validly verified.
-   Continuing would require an out-of-Scope file/folder.
-   Continuing would require network, exchange, server, security, Telegram, or runtime functionality.
-   Continuing would violate PREAMBLE_V4.
-   Success would require guessing.

Do not improvise.

Do not silently expand Scope.

Do not advance to A2.

----------

## Approval

This Payload must be reviewed by the Technical Designer and approved by the Owner before being sent to Kilo.
