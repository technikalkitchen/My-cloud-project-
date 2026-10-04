═══════════════════════════════════════════════════════════
ROADMAP_A.md — بسته A (امنیت + فنی + زیرساخت)
Kitchen Assistant Bot V4
نسخه: ۴ (نهایی — با تفکیک Bootstrap از Stage A1)
═══════════════════════════════════════════════════════════

این Roadmap بر پایه PREAMBLE_V4 نسخه ۱ نوشته شده است.
قواعد عمومی از آن گرفته می‌شود.

وضعیت این Roadmap: IN_PROGRESS
تعداد Stageها: [در حال تعریف]
آخرین بروزرسانی: [تاریخ]

═══════════════════════════════════════════════════════════
فهرست مطالب
═══════════════════════════════════════════════════════════

  • Preparation (خارج از Stage) — انتقال اسناد مرجع به v4
  • Stage A1 — پایه‌گذاری ساختار پروژه
  • Stage A2 تا An — [در جلسات بعدی تعریف می‌شوند]

═══════════════════════════════════════════════════════════
Preparation — انتقال اسناد مرجع به Branch v4
═══════════════════════════════════════════════════════════

وضعیت: PLANNED
نوع: Preparation (خارج از Stage)
پیچیدگی: بسیار پایین
وابستگی: ندارد

───────────────────────────────────────────────────────────
هدف
───────────────────────────────────────────────────────────

این Preparation، یک مرحله‌ی آماده‌سازی قبل از شروع Stage A1
است. خودش Stage نیست، جزو هیچ Stage هم نیست.

نقش: فراهم‌کردن اسناد مرجع روی Branch v4 قبل از شروع
کار واقعی در Stage A1.

───────────────────────────────────────────────────────────
Scope
───────────────────────────────────────────────────────────

  ۱. ساخت Branch v4 از main.
  ۲. انتقال (کپی بدون تغییر) اسناد مرجع:
       • docs/roadmap/PREAMBLE_V4.md
       • docs/roadmap/ROADMAP_A.md
  ۳. Commit با پیام:
       "Bootstrap: transfer reference documents to v4"

هیچ فایل دیگری در این Preparation ساخته نمی‌شود.
هیچ Stage commit نهایی اینجا زده نمی‌شود.

───────────────────────────────────────────────────────────
معیار پذیرش Preparation
───────────────────────────────────────────────────────────

  • Branch v4 روی GitHub وجود دارد.
  • دو سند مرجع روی v4 در مسیر docs/roadmap/ هستند.
  • هیچ فایل دیگری اضافه نشده است.
  • Commit پیامش دقیقاً:
    "Bootstrap: transfer reference documents to v4"

───────────────────────────────────────────────────────────
پیامدها
───────────────────────────────────────────────────────────

  • این Preparation، به‌عنوان Bootstrap ثبت می‌شود، نه
    به‌عنوان بخشی از Stage A1.
  • Stage A1 فقط پس از تکمیل این Preparation شروع می‌شود.
  • Commit این Preparation، با Commit نهایی Stage A1
    متفاوت است و با آن تداخل ندارد.

═══════════════════════════════════════════════════════════
Stage A1 — پایه‌گذاری ساختار پروژه
═══════════════════════════════════════════════════════════

وضعیت: PLANNED
نوع: Bootstrap اسکلت
پیچیدگی: پایین
وابستگی: Preparation (باید تکمیل شده باشد)

───────────────────────────────────────────────────────────
۱. هدف Stage
───────────────────────────────────────────────────────────

Stage A1 فقط دو کار انجام می‌دهد:

  ۱. ساخت اسکلت اولیه‌ی پروژه: پوشه‌ها، فایل‌های پایه،
     و فایل هویت پروژه.
  ۲. ساخت ساختار آرتیفکت‌های Stage در docs/stages/STAGE_A1/.

هیچ منطق، هیچ تحلیل، هیچ اتصال به سرور یا صرافی، هیچ
سیستم لاگینگ، هیچ امنیت. فقط اسکلت.

───────────────────────────────────────────────────────────
۲. Scope — داخل و خارج
───────────────────────────────────────────────────────────

داخل Scope:
  • ساخت ساختار پوشه‌های اصلی (با __init__.py در محل لازم)
  • ساخت فایل‌های ریشه:
      .gitignore, README.md, pyproject.toml, conftest.py
  • ساخت فایل هویت پروژه (stage_a1_version.py)
  • ساخت فایل config پایه (stage_a1_config.py، فقط placeholder)
  • ساخت پوشه‌های زیرساختی با .gitkeep:
      scripts/, data/, logs/
  • نوشتن تست ساختار
  • نوشتن چهار آرتیفکت Stage

خارج از Scope:
  • هیچ سیستم لاگینگی
  • هیچ امنیتی
  • هیچ اتصال به Google Drive
  • هیچ اتصال به Exchange یا Provider
  • هیچ منطق تحلیل
  • هیچ رابط Telegram
  • هیچ انتخاب Web Server نهایی
  • هیچ منطق runtime, environment loading, secret handling
  • هیچ فایل LICENSE (تصمیم در Stage جداگانه)
  • هیچ پوشه‌ی خالی برای آینده
  • هیچ Branch ساختنی (در Preparation انجام شد)

───────────────────────────────────────────────────────────
۳. پیش‌نیازها
───────────────────────────────────────────────────────────

قبل از شروع Stage A1 باید این‌ها موجود باشند:

  • Preparation تکمیل شده باشد (Branch v4 + اسناد مرجع).
  • PythonAnywhere فعال.
  • دسترسی Kilo به Repository.

───────────────────────────────────────────────────────────
۴. فهرست دقیق فایل‌ها و پوشه‌هایی که ساخته می‌شوند
───────────────────────────────────────────────────────────

در شاخه v4، این ساختار ساخته می‌شود.

── فایل‌های ریشه پروژه ──

  .gitignore
    محتوا:
      # Python
      __pycache__/
      *.pyc
      *.pyo
      *.egg-info/
      .pytest_cache/
      .mypy_cache/
      .ruff_cache/
      .coverage
      htmlcov/

      # Virtual environments
      .venv/
      venv/
      env/

      # Environment / secrets
      .env
      .env.*

      # IDE
      .idea/
      .vscode/

      # Runtime data (با .gitkeep نگه داشته می‌شوند)
      data/*
      !data/.gitkeep
      logs/*
      !logs/.gitkeep
      logs/runtime/
      data/runtime/
      scripts/*
      !scripts/.gitkeep

  README.md
    محتوا:
      # Kitchen Assistant Bot

      Version: V4
      Current Stage: A1

      ## Status
      In development — bootstrap phase.

      ## Reference Documents
      - `docs/roadmap/PREAMBLE_V4.md` — قواعد عمومی پروژه
      - `docs/roadmap/ROADMAP_A.md` — Roadmap بسته A

      ## Structure
      See PREAMBLE_V4.md for full project structure.

  pyproject.toml
    محتوا:
      [build-system]
      requires = ["setuptools>=68"]
      build-backend = "setuptools.build_meta"

      [project]
      name = "kitchen-assistant-bot"
      version = "4.0.0"
      description = "Kitchen Assistant Telegram Bot"
      requires-python = ">=3.11"
      dependencies = []

      [project.optional-dependencies]
      dev = [
          "pytest>=8,<9",
      ]

      [tool.pytest.ini_options]
      testpaths = ["tests"]
      python_files = ["test_*.py"]
      python_classes = ["Test*"]
      python_functions = ["test_*"]

  conftest.py
    محتوا:
      # pytest root marker
      # این فایل وجود دارد تا pytest از ریشه پروژه اجرا شود.

── پوشه app و زیرپوشه‌ها ──

  app/__init__.py                (خالی)
  app/config/__init__.py         (خالی)
  app/core/__init__.py           (خالی)
  app/data/__init__.py           (خالی)
  app/market/__init__.py         (خالی)
  app/analysis/__init__.py       (خالی)
  app/bot/__init__.py            (خالی)
  app/api/__init__.py            (خالی)

── فایل‌های کد پایه ──

  app/core/stage_a1_version.py
    محتوا:
      """Project identity — single source of truth."""

      PROJECT_NAME = "Kitchen Assistant Bot"
      PROJECT_VERSION = "V4"
      CURRENT_STAGE = "A1"

    نقش: منبع واحد هویت پروژه.
    بدون logic، بدون import اضافی.

  app/config/stage_a1_config.py
    محتوا:
      """Stage A1 — Configuration Placeholders.

      این فایل فقط placeholder است.
      هیچ منطق runtime، environment loading، یا secret handling
      در این فایل وجود ندارد.
      """

      PYTHON_VERSION_TARGET = "3.11"
      ENV_PLACEHOLDER: dict = {}

    نقش: نقطه شروع config — فقط placeholder.

── پوشه tests ──

  tests/stages/STAGE_A1/test_stage_a1_structure.py
    محتوا: ۱۳ تست (بخش ۵).

نکته: از `__init__.py` در پوشه‌های tests/ استفاده نمی‌شود
تا از تداخل نام ماژول‌ها جلوگیری شود.

── پوشه‌های زیرساختی با .gitkeep ──

  scripts/.gitkeep                (خالی)
  data/.gitkeep                   (خالی)
  logs/.gitkeep                   (خالی)

── پوشه docs و آرتیفکت‌ها ──

  docs/stages/STAGE_A1/                  (پوشه Stage)
  docs/stages/STAGE_A1/CURRENT_STATE.md  (از ابتدا ساخته و آپدیت می‌شود)
  docs/stages/STAGE_A1/LEDGER.md         (در پایان Stage)
  docs/stages/STAGE_A1/MANIFEST.json     (در پایان Stage)
  docs/stages/STAGE_A1/SHA256.json       (در پایان Stage)

── پوشه‌هایی که در Stage A1 ساخته نمی‌شوند ──

  ✗ app/logging/     ← Stage لاگینگ
  ✗ app/trading/     ← فاز Trade Management
  ✗ app/journal/     ← فاز Trading Journal
  ✗ app/orderbook/   ← فاز Order Book
  ✗ ledgers/         ← حذف شد
  ✗ LICENSE          ← تصمیم در Stage جداگانه

───────────────────────────────────────────────────────────
۵. تست‌ها
───────────────────────────────────────────────────────────

فایل تست: tests/stages/STAGE_A1/test_stage_a1_structure.py

تست‌های الزامی (۱۳ تست):

  test_01_structure_exists
    بررسی: پوشه‌های app/ و زیرپوشه‌هایش، docs/stages/STAGE_A1/
           موجود باشند.

  test_02_init_files_present
    بررسی: همه‌ی __init__.py در پوشه‌های app/ باشند.

  test_03_version_identity
    بررسی:
      • app/core/stage_a1_version.py قابل import است.
      • PROJECT_NAME == "Kitchen Assistant Bot"
      • PROJECT_VERSION == "V4"
      • CURRENT_STAGE == "A1"

  test_04_pyproject_valid
    بررسی:
      • pyproject.toml موجود است.
      • قابل parse است (با tomllib در Python 3.11).
      • requires-python == ">=3.11"
      • بخش [tool.pytest.ini_options] موجود است.

  test_05_gitignore_present
    بررسی:
      • .gitignore موجود است.
      • شامل __pycache__/, .venv/, .env, logs/runtime/,
        data/* با !data/.gitkeep, logs/* با !logs/.gitkeep

  test_06_readme_present
    بررسی:
      • README.md موجود است.
      • غیرخالی است.
      • شامل "Kitchen Assistant Bot" و "V4"

  test_07_conftest_present
    بررسی: conftest.py در ریشه پروژه موجود است.

  test_08_gitkeep_files_present
    بررسی:
      • scripts/.gitkeep موجود است.
      • data/.gitkeep موجود است.
      • logs/.gitkeep موجود است.

  test_09_no_forbidden_folders
    بررسی: پوشه‌های app/logging/، app/trading/،
           app/journal/، app/orderbook/، ledgers/
           وجود ندارند.

  test_10_stage_folder_exists
    بررسی: docs/stages/STAGE_A1/ موجود است.

  test_11_config_imports
    بررسی: app/config/stage_a1_config.py قابل import است.
           متغیر PYTHON_VERSION_TARGET == "3.11".

  test_12_no_external_imports
    بررسی: هیچ‌کدام از فایل‌های Stage A1 نباید این
           ماژول‌ها را import کنند:
             requests, urllib, http, socket,
             telegram, flask, httpx, aiohttp.

  test_13_no_runtime_logic
    بررسی: stage_a1_config.py نباید شامل این‌ها باشد:
             - تعریف تابع (def)
             - os.environ, os.getenv
             - .open, read_text, read_bytes

اجرای تست:
  pytest tests/stages/STAGE_A1/test_stage_a1_structure.py -v

───────────────────────────────────────────────────────────
۶. معیار پذیرش
───────────────────────────────────────────────────────────

Stage A1 زمانی PASSED می‌شود که:

  ۱. تمام فایل‌ها و پوشه‌های Scope (بخش ۴) موجود باشند.
  ۲. تمام پوشه‌های ممنوع (بخش ۴) موجود نباشند.
  ۳. تمام ۱۳ تست بخش ۵ پاس شوند.
  ۴. هیچ منطق تحلیل، اتصال سرور، یا منطق تجاری در
     کد Stage A1 نباشد.
  ۵. چهار آرتیفکت Stage (LEDGER، MANIFEST، SHA256،
     CURRENT_STATE) تولید شده باشند.
  ۶. MANIFEST با SHA256 سازگار باشد.
  ۷. هیچ فایل خارج از Scope بخش ۴ ساخته نشده باشد.

───────────────────────────────────────────────────────────
۷. ریسک‌ها
───────────────────────────────────────────────────────────

ریسک A1-1: ساخت پوشه‌های اضافی
  خطر: Kilo برای «کامل بودن» پوشه‌های آینده را بسازد.
  کاهش: Scope بخش ۴ صریح است. قاعده ۳ PREAMBLE اجرا می‌شود.

ریسک A1-2: drift نسخه
  خطر: نسخه در فایل‌های مختلف متفاوت نوشته شود.
  کاهش: فقط stage_a1_version.py منبع نسخه است.

ریسک A1-3: گسترش ناخواسته config به Runtime
  خطر: Kilo در stage_a1_config.py منطق runtime بنویسد.
  کاهش: test_13 این را چک می‌کند.

ریسک A1-4: خطا در SHA256
  خطر: فایل‌های سیستمی وارد hash شوند.
  کاهش: پیش از hash، فهرست Scope اعمال می‌شود.

ریسک A1-5: ناپدید شدن پوشه‌های خالی در Git
  خطر: بدون .gitkeep، پوشه‌ها بعد از clone ناپدید می‌شوند.
  کاهش: .gitkeep در scripts/، data/، logs/ + الگوی درست
         در .gitignore.

───────────────────────────────────────────────────────────
۸. آرتیفکت‌های مورد انتظار در پایان Stage
───────────────────────────────────────────────────────────

  docs/stages/STAGE_A1/LEDGER.md
    شامل: Identity، Scope، Changes، Tests، Results،
           Limitations، Integrity، Next Step.

  docs/stages/STAGE_A1/MANIFEST.json
    شامل: project، version، stage، execution_unit،
           status، scope، artifacts، tests،
           generated_at، completed_at، file_count.

  docs/stages/STAGE_A1/SHA256.json
    شامل: hash تمام فایل‌های داخل Scope.
    خارج از Scope (طبق PREAMBLE):
      .git/, __pycache__/, .venv/, .env, *.pyc,
      CURRENT_STATE.md, runtime-generated data,
      logs/runtime/

  docs/stages/STAGE_A1/CURRENT_STATE.md
    از ابتدای Stage ساخته می‌شود و در طول کار آپدیت
    می‌شود.

───────────────────────────────────────────────────────────
۹. نکات اجرایی برای Kilo
───────────────────────────────────────────────────────────

  ۱. Kilo قبل از شروع، بررسی می‌کند که Preparation
     تکمیل شده باشد (Branch v4 + اسناد مرجع).
  ۲. اگر CURRENT_STATE.md وجود نداشت، Kilo اول آن را
     با وضعیت IN_PROGRESS می‌سازد، بعد شروع می‌کند.
  ۳. بعد از ساخت هر فایل، CURRENT_STATE.md آپدیت می‌شود.
  ۴. در پایان Stage، LEDGER، MANIFEST، SHA256 نهایی می‌شوند.
  ۵. Commit نهایی Stage A1، فقط بعد از تأیید طراح و
     مالک زده می‌شود.
     فرمت پیام Commit:
       "Stage A1: project skeleton"
  ۶. Kilo روی main هیچ تغییری نمی‌دهد.
  ۷. Python Version نهایی این پروژه: **3.11**
     این تصمیم در همین Stage A1 ثبت و قفل می‌شود.

───────────────────────────────────────────────────────────
۱۰. قدم بعدی
───────────────────────────────────────────────────────────

پس از تأیید Stage A1 توسط طراح و مالک:

  • Stage A2 شروع می‌شود.
  • موضوع Stage A2: [در جلسه بعدی تعریف می‌شود]

───────────────────────────────────────────────────────────
پایان Stage A1 — نسخه نهایی
───────────────────────────────────────────────────────────

═══════════════════════════════════════════════════════════
پایان ROADMAP_A.md — نسخه ۴ (نهایی)
═══════════════════════════════════════════════════════════
