# KITCHEN ROBOT — Production Deployment Specification (Final)

This document is the single source of truth for deploying the existing Telegram
Scanner Bot in production. It covers application entrypoints, runtime/dependency
requirements, the Flask API, the Telegram bot webhook/runtime flow, required
environment variables and secret-handling rules, PythonAnywhere deployment
requirements, webhook configuration, a verification checklist, and remaining
deploy blockers.

No Scanner code (U06.5, Stages 7–12) is modified by this specification.
The existing, verified implementation is documented rather than rebuilt.

---

## 1. Project Identity

| Field | Value |
|-------|-------|
| Project name | KITCHEN_ROBOT |
| Version | 2.7.0-dev |
| Execution unit (WSGI/API) | U01 (`EXECUTION_UNIT = "U01"`) |
| Scanner stage (final) | U12 — Top 3 Reliable Movers — status: LOCKED (PASSED) |
| Primary entry module | `wsgi.py` |
| WSGI callable | `application` |
| Python | 3.x (project targets CPython 3; no `python_requires` pin exists — test on the target runtime before deploying) |
| License / trading status | Read-only data analysis and reporting only; trading/orders/signals DISABLED |

Source of truth for identity: `app/core/version.py:1-3`.

---

## 2. Application Entrypoints

The repository exposes a single WSGI entrypoint that serves both the health/API
routes and the Telegram webhook endpoint.

| Entrypoint | Location | Purpose |
|------------|----------|---------|
| `wsgi.py` | repo root | Exposes module-level `application = app`. This is the object referenced by WSGI servers (`wsgi:application`). |
| `app.api.app.app` | `app/api/app.py:258` | Module-level Flask application created by `create_app()` at import time. Imported by `wsgi.py`. |
| `app.api.app.create_app()` | `app/api/app.py:201-255` | Factory that registers all Flask routes. |
| `scripts/start_wsgi.sh` | `scripts/` | Local/dev convenience script: `exec gunicorn --bind 0.0.0.0:5000 wsgi:application`. |

### Flask routes

| Method | Route | Behavior |
|--------|-------|----------|
| GET | `/health` | `{"status":"ok","project":..., "version":..., "execution_unit":...}` |
| GET | `/` | Service identity: `{"service":..., "version":..., "status":"running"}` |
| GET | `/bot/status` | `{"configured": <bool>, "status": "ready"|"no_token"}` — reflects whether `BOT_TOKEN` is present. |
| POST | `/bot/webhook` | Accepts a raw Telegram `Update` JSON payload, parses `/command` + args, dispatches to `BotRunner.handle_command`, and returns `{"ok": true, "chat_id": ..., "response": ...}`. |

Route registrations: `app/api/app.py:205-253`.

---

## 3. Dependencies

`requirements.txt` (repo root) contains all pinned dependencies:

```
Flask>=3,<4
gunicorn>=23,<24
pytest>=8,<9
python-telegram-bot>=22,<23
requests>=2,<3
```

- `Flask` 3.x — web framework hosting `/health`, `/`, `/bot/status`, `/bot/webhook`.
- `gunicorn` 23.x — WSGI HTTP server for production (used by `start_wsgi.sh`).
- `python-telegram-bot` 22.x — optional long-polling support via `app/bot/telegram.py` (`TelegramBot.run_polling()`).
- `requests` 2.x — outbound HTTP for CoinGecko market data in the bot runner.
- `pytest` 8.x — test runner (dev/test dependency).

Install: `pip install -r requirements.txt`

---

## 4. Flask / API Deployment Requirements

1. **WSGI server**: Production must serve the app behind a real WSGI/HTTP
   server. `wsgi.py` exposes `application`; PythonAnywhere consumes it as
   `wsgi:application` automatically when a WSGI configuration file is created
   on the Web tab. For self-managed hosts, use gunicorn:
   ```
   gunicorn --bind 0.0.0.0:5000 wsgi:application
   ```
   or the provided `bash scripts/start_wsgi.sh` (which execs the above).

2. **Port**: The app listens on `0.0.0.0:5000` by default (see
   `app/config/runtime.py` `APP_PORT` default `5000`). PythonAnywhere manages
   its own port behind the platform proxy; do not rely on binding 5000 there.

3. **Static/media**: None required. The app is API+webhook only.

4. **Data directory**: The bot runner reads historical candle files from
   `data/historical_u05/raw/` (e.g. `BTCUSDT_1m.json`, `ETHUSDT_1m.json`,
   `SOLUSDT_1m.json`, `XRPUSDT_1m.json`, `ADAUSDT_1m.json`). This directory set
   must be present in the deployed working directory. The five-symbol dataset
   index is `data/historical_u05/DATASET_INDEX.json`.

5. **No `.env` loading**: The codebase does not load a `.env` file at runtime
   (no `python-dotenv` dependency). All configuration is read from process
   environment variables.

---

## 5. Telegram Bot Runtime / Webhook Flow

The bot integrates with Telegram over the **webhook** path hosted inside the
Flask app. There are two distinct components:

### 5.1 Webhook entry (Flask) — `app/api/app.py:231-253`

`POST /bot/webhook` receives the raw Telegram `Update` object, extracts
`message.text` and `message.chat.id`, splits a leading `/command` from its
arguments, and calls:

```
BotRunner().handle_command(command, args)
```

`BotRunner` (`app/bot/runner.py:31`) drives the Scanner pipeline:
CoinGecko ranking data → Binance 5m candles (local `data/historical_u05/raw/`)
→ Stage pipeline (U06.5 → Stage 10 → Stage 11 → Stage 12) → Top 3 — and returns
the formatted Telegram message string. The route returns it as JSON:

```json
{"ok": true, "chat_id": 12345, "response": "..."}
```

### 5.2 Token + long-polling support — `app/bot/telegram.py`

`TelegramBot` wraps `python-telegram-bot` v22 and is available for optional
long-polling (e.g. a separate worker process) via `run_polling()`. The HTTP
webhook route does **not** require this class at runtime; it only needs
`app/bot/runner.py`.

### 5.3 Output contract preserved

The bot reuses the existing Scanner output formatters, so the produced
Telegram message already enforces:
- USDT and BTC contract continuity (Binance preferred source, higher-priority-only fallback).
- Source/Fallback provenance preserved.
- Mandatory Scanner warning (sub-daily / no-signal disclaimer).
- No entry/exit/long-short/recommendation language (not a trading signal).

---

## 6. Required Environment Variables

| Variable | Required | Default | Source | Notes |
|----------|----------|---------|--------|-------|
| `BOT_TOKEN` | **YES (production)** | `""` | `app/bot/config.py:5` | Primary Telegram bot token. Must be supplied. |
| `TELEGRAM_BOT_TOKEN` | Fallback for `BOT_TOKEN` | `""` | `app/bot/config.py:5` | Used only if `BOT_TOKEN` is unset. |
| `BOT_USERNAME` | No | `KitchenAssistantBot` | `app/bot/config.py:6` | Display username. |
| `APP_ENV` | No | `development` | `app/config/settings.py`, `config/.env.example` | e.g. `production`. |
| `APP_TIMEZONE` | No | `UTC` | `app/config/settings.py`, `config/.env.example` | |
| `LOG_LEVEL` | No | `INFO` | `app/config/settings.py`, `config/.env.example` | |
| `APP_HOST` | No | `0.0.0.0` | `app/config/runtime.py` | Listen host. |
| `APP_PORT` | No | `5000` | `app/config/runtime.py` | Listen port (self-managed only). |
| `APP_DEBUG` | No | `0` | `app/config/runtime.py` | Set to `1` only for local debugging. |

`config/.env.example` documents `APP_ENV`, `APP_TIMEZONE`, `LOG_LEVEL`.
`app/bot/config.py:5-6` reads the token/username from the environment.

### Secret-handling rules (BOT_TOKEN)

`BOT_TOKEN` is a secret and **must never be**:

1. Hard-coded anywhere in source.
2. Committed to the repository (no token is committed; verified via grep — none found).
3. Logged or echoed by the application.
4. Written into any artifact, manifest, ledger, notebook, or report.
5. Included in `DEPLOYMENT_SPECIFICATION_FINAL.md` or any other doc.

The runtime treats an unset/missing token as "no_token": `/bot/status` returns
`{"configured": false, "status": "no_token"}`, and only the `/health`, `/`,
and `/bot/status` routes function. The `/bot/webhook` route will still parse
incoming text but the underlying pipeline does not require the token to run —
however, Telegram will not deliver updates until `setWebhook` is registered with
a valid token (see §7).

To provide the token at runtime, export it in the process environment before
starting the WSGI server, e.g. in PythonAnywhere's Web → "Environment variables"
section, or for self-managed hosts:
```
export BOT_TOKEN=123456789:ABCDEF....
gunicorn --bind 0.0.0.0:5000 wsgi:application
```

---

## 7. PythonAnywhere Deployment Requirements

Target platform: **PythonAnywhere**. The app is WSGI-compatible and is served
via the platform's standard Python/WSGI pipeline.

1. **Create a web app** via the PythonAnywhere Dashboard → "Web" tab → "Add a new
   web app". Select the CPython version (3.x; the repo targets Python 3) and
   "Manual configuration (WSGI)".

2. **WSGI configuration**: PythonAnywhere generates a WSGI file (e.g.
   `/var/www/<username>_pythonanywhere_com_wsgi.py`). Point its application
   object at this project:
   ```python
   import sys
   project_home = '/home/<username>/My-cloud-project-'
   if project_home not in sys.path:
       sys.path.insert(0, project_home)
   from wsgi import application  # exposes `wsgi:application`
   ```
   The project root must be on `sys.path` so `wsgi.py` → `app.api.app` resolves.

3. **Install dependencies** in a Bash console:
   ```
   pip install -r /home/<username>/My-cloud-project-/requirements.txt
   ```
   Or, if using a virtualenv, activate it from the Web tab's WSGI config and
   install there. Pin versions per `requirements.txt` (Flask 3, gunicorn 23,
   python-telegram-bot 22, requests 2).

4. **Environment variables**: Add `BOT_TOKEN` (and `TELEGRAM_BOT_TOKEN` if
   preferred) via the Web tab → "Environment variables" section. Add
   `APP_ENV=production`, `APP_TIMEZONE=UTC`, `LOG_LEVEL=INFO` as desired.
   **Never** place the token in the WSGI file or any source file.

5. **Working directory / data**: Ensure the deployed working directory contains
   `data/historical_u05/raw/` with the five candle files (see §4). PythonAnywhere
   serves the project from its home directory; clone/copy the repository there.

6. **Reload**: After configuration, click "Reload" on the Web tab. Then verify:
   - `https://<username>.pythonanywhere.com/health` returns `ok`.
   - `https://<username>.pythonanywhere.com/bot/status` returns
     `{"configured": true, "status": "ready"}` (only after `BOT_TOKEN` is set).

7. **No custom domain SSL**: SSL is terminated by PythonAnywhere. Telegram
   webhooks require `https://`; the platform default
   `<username>.pythonanywhere.com` is already HTTPS, satisfying Telegram's
   requirement.

---

## 8. Webhook Configuration Requirements

The Flask app hosts the webhook *receiver* at `POST /bot/webhook`, but it does
**not** automatically register itself with Telegram. Registration is a separate
step the owner must perform with the Telegram Bot API:

```
POST https://api.telegram.org/bot<BOT_TOKEN>/setWebhook
Content-Type: application/json

{
  "url": "https://<username>.pythonanywhere.com/bot/webhook"
}
```

- The `url` must be reachable over HTTPS (PythonAnywhere HTTPS satisfies this).
- After registration, Telegram POSTs each `Update` to `/bot/webhook`, which
  dispatches to the Scanner pipeline and returns a JSON response (Telegram
  ignores the HTTP body for delivery but a `200` short-circuits retries).
- If using a custom domain, ensure the `url` matches the custom-domain HTTPS
  endpoint and that the certificate is valid.
- To inspect registration status:
  `GET https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo`
- To disable: `POST .../deleteWebhook` (passing `BOT_TOKEN`).

Because `setWebhook` is an owner-side action requiring `BOT_TOKEN`, the bot
cannot self-register. This is an expected, documented flow — not a code defect.

---

## 9. Verification / Test Checklist for Production

Run these checks before considering deployment complete.

### 9.1 Local pre-flight

```
pip install -r requirements.txt
pytest        # existing test suite; Scanner stages U06.5, 10, 11, 12 remain LOCKED/unchanged
```
- All tests pass (regression: 1129 passed including 104 Stage-12 tests).
- Core Scanner business logic (U06.5, Stages 7–12) is UNMODIFIED. A formatting
  helper (`_btc_source_label`) was added to `app/analysis/stage12_top3.py` for
  BTC source/provenance display in Top 3 output — no logic change.
- Flask bot routes (`/bot/status`, `/bot/webhook`) and `BOT_TOKEN` import were
  added to `app/api/app.py` for bot integration — not Scanner code.
- `requirements.txt` updated with `python-telegram-bot>=22,<23` for optional
  polling support (`app/bot/telegram.py`).

### 9.2 Service startup

```
export BOT_TOKEN=<owner_token>
bash scripts/start_wsgi.sh        # gunicorn --bind 0.0.0.0:5000 wsgi:application
```

### 9.3 HTTP checks

| Check | Request | Expected |
|-------|---------|----------|
| Health | `GET /health` | `200`, `{"status":"ok",...}` |
| Root | `GET /` | `200`, `{"service":"KITCHEN_ROBOT",...}` |
| Bot config | `GET /bot/status` | `200`, `{"configured":true,"status":"ready"}` |
| Webhook | `POST /bot/webhook` with a fake `Update` (`{"message":{"text":"/top3","chat":{"id":123}}}`) | `200`, `{"ok":true,"chat_id":123,"response":"..."}` |

### 9.4 Telegram side

- `getWebhookInfo` confirms the registered URL matches the HTTPS endpoint.
- Send `/top3` to the bot in Telegram; confirm a formatted Top 3 message is
  returned with the mandatory disclaimer and no signal/recommendation language.

---

## 10. Known Remaining Blockers

1. **`BOT_TOKEN` not provided.** This is by design — the token is the owner's
   secret and is never stored in the repository. Until `BOT_TOKEN` is exported
   in the process environment, `/bot/status` reports `{"configured": false,
   "status": "no_token"}`, and `setWebhook` cannot be registered with Telegram.
   Resolution requires the owner to supply the token (see §6).

2. **`setWebhook` is owner-side only.** The application hosts the receiving
   endpoint but does not call the Telegram `setWebhook` API. The owner must
   register the webhook URL (§8). This is expected and documented, not a code gap.

3. **No `.gitignore` present.** The repository root has no `.gitignore`. Because
   configuration is environment-based (no `.env` loaded at runtime), local
   `.env`/credential files created by operators must be added to `.gitignore`
   before running, to prevent accidental commits of secrets. Recommend creating
   `.gitignore` with entries for `*.env`, `.env.*`, `__pycache__/`, `.pytest_cache/`,
   `logs/`, and any local virtualenvs. (No code change required for deployment
   itself.)

4. **Python version not pinned.** The repo does not declare `python_requires`
   or a `.python-version`. Operators should pin and test against a specific
   CPython 3.x on the target platform (PythonAnywhere + local `python3`
   reported via `python3 --version`).

5. **No trading/signals.** By construction the bot performs read-only analysis
   and never produces trading signals. Any production use must treat all output
   as analytical reporting only, with no entry/exit recommendation.

No code changes are required to satisfy this specification. The existing
`wsgi.py`, `app/api/app.py`, `app/bot/config.py`, `app/bot/runner.py`,
`app/bot/telegram.py`, `scripts/start_wsgi.sh`, and `requirements.txt` already
implement every requirement above.

---

## 11. Files Inspected (deployment-relevant)

- `wsgi.py` — WSGI entry, exposes `application`
- `requirements.txt` — pinned dependencies
- `config/.env.example` — documented env vars
- `scripts/start_wsgi.sh` — gunicorn launcher
- `app/core/version.py` — project identity
- `app/config/runtime.py` — host/port/debug env
- `app/config/settings.py` — env/timezone/loglevel env
- `app/api/app.py` — Flask routes + `create_app()`
- `app/bot/config.py` — `BOT_TOKEN`/`BOT_USERNAME` env handling
- `app/bot/runner.py` — `BotRunner` Scanner dispatch
- `app/bot/telegram.py` — optional polling wrapper
- `data/historical_u05/DATASET_INDEX.json` + `data/historical_u05/raw/*.json` — bot data inputs
- `ledgers/U12_LEDGER.md`, `U12_MANIFEST.json`, `U12_AUDIT_METADATA.json` — final Scanner lock state
- `app/bot/__init__.py` — package marker (future import only)

## 12. Deployment Report Summary

1. **File created**: `DEPLOYMENT_SPECIFICATION_FINAL.md`
2. **Files inspected**: see §11.
3. **Real deployment blockers**:
   - `BOT_TOKEN` must be supplied by the owner (not present in repo — intentional).
   - `setWebhook` is an owner-side Telegram API call (documented in §8).
   - Missing `.gitignore` (recommend adding before local `.env` usage).
   - Python runtime version not pinned.
4. **Code changes in working tree**: Core Scanner business logic
    (U06.5, Stages 7–12) is unchanged. Minor changes: a formatting
    helper (`_btc_source_label`) was added to `app/analysis/stage12_top3.py`
    for BTC source display — no logic change; Flask bot routes
    (`/bot/status`, `/bot/webhook`) and `BOT_TOKEN` import were added to
    `app/api/app.py`; `requirements.txt` gained `python-telegram-bot`.
    These implement the bot integration described in this specification
    and are NOT Scanner logic modifications.
