═══════════════════════════════════════════════════════════  
PREAMBLE_V4 — قواعد عمومی پروژه V4  
Kitchen Assistant Bot V4  
نسخه: ۱ (نهایی)  
وضعیت: LOCKED  
═══════════════════════════════════════════════════════════

این سند، قواعد عمومی و ثابت پروژه V4 است.  
برای همه بسته‌ها (A، B، C، D) و همه Stageها یکسان اعمال می‌شود.

مبنا: سند صفر نسخه ۳ (LOCKED) + تصمیم‌های پایه طراح + تصویب‌های مالک

═══════════════════════════════════════════════════════════  
بخش ۱ — اسناد مرجع  
═══════════════════════════════════════════════════════════

اسناد مرجع پروژه V4، به‌ترتیب اعتبار:

۱. سند صفر نسخه ۳ — نقشه ارتباط بسته‌ها (LOCKED)  
۲. PREAMBLE_V4.md (این سند)  
۳. ROADMAP_A.md / ROADMAP_B.md / ROADMAP_C.md / ROADMAP_D.md  
۴. CURRENT_STATE.md هر Stage (برای Resume)  
۵. LEDGER.md هر Stage (برای تاریخچه)

هر تغییر در این اسناد، نیازمند تأیید صریح مالک است.

نکته: CURRENT_STATE.md در همان ابتدای شروع هر Stage  
ساخته می‌شود و در طول کار آپدیت می‌شود. اگر یک Stage  
دوباره اجرا شود، این فایل به‌عنوان منبع Resume استفاده  
می‌شود. هر Stage، مستقل از بقیه، اولین تلاشش بدون  
CURRENT_STATE شروع می‌شود و خودش آن را می‌سازد.

═══════════════════════════════════════════════════════════  
بخش ۲ — نحوه شروع هر Stage توسط Kilo  
═══════════════════════════════════════════════════════════

قبل از شروع هر Stage، Kilo این ترتیب را طی می‌کند:

۱. PREAMBLE_V4.md را می‌خواند (این سند)  
۲. ROADMAP بسته مربوطه را می‌خواند  
(مثلاً برای Stage A1 → ROADMAP_A.md)  
۳. Stage مورد نظر را در ROADMAP پیدا می‌کند  
۴. Scope همان Stage را می‌خواند  
۵. بررسی می‌کند که CURRENT_STATE.md همان Stage وجود دارد یا نه:  
• اگر وجود دارد (تلاش قبلی): آن را می‌خواند و از  
همان‌جا ادامه می‌دهد.  
• اگر وجود ندارد (اولین تلاش): خودش آن را می‌سازد  
با وضعیت IN_PROGRESS و شروع می‌کند.  
۶. از همان‌جا که CURRENT_STATE می‌گوید، ادامه می‌دهد.

Kilo هرگز از خودش شروع نمی‌کند. همیشه بر اساس ROADMAP  
و CURRENT_STATE عمل می‌کند.

═══════════════════════════════════════════════════════════  
بخش ۳ — قواعد عمومی برای Kilo  
═══════════════════════════════════════════════════════════

قاعده ۱ — دامنه محدود  
Kilo فقط همان چیزی را انجام می‌دهد که در Stage نوشته شده.  
هیچ چیز اضافی، هیچ بهبود خودسرانه، هیچ پیشنهاد معماری.

قاعده ۲ — صرفه‌جویی توکن  
• از خواندن کل Repository بدون نیاز خودداری کند.  
• فقط فایل‌های مربوط به Stage را بخواند.  
• گزارش‌های طولانی نسازد.  
• اگر لازم است جایی را ببیند، فقط همان بخش را بخواند.  
• از جستجوهای گسترده در GitHub خودداری کند.

قاعده ۳ — عدم تغییر خارج از Scope  
• فایل‌های Stageهای قبلی را دست نزند.  
• فایل‌های Legacy (main branch) را دست نزند.  
• ساختار پوشه‌ها را خودسرانه عوض نکند.  
• فقط فایل‌هایی که در Scope همان Stage صراحتاً  
فهرست شده‌اند را بسازد. فایل اضافی نسازد.

قاعده ۴ — ثبت دقیق  
• هر تغییری که انجام داد، در Ledger ثبت کند.  
• چه فایلی، چه تغییر، چه نتیجه.  
• اگر جایی شکست خورد، صریح بنویسد.  
• اگر چیزی را نتوانست انجام دهد، دلیلش را بنویسد.

قاعده ۵ — توقف در ابهام  
اگر Stage چیزی مبهم بود یا نیاز به تصمیم داشت:  
• متوقف شود.  
• سؤال خود را صریح بنویسد.  
• منتظر پاسخ بماند.  
• حدس نزند.

قاعده ۶ — عدم تکرار تست‌های قبلی  
• فقط تست‌های Stage جاری را اجرا کند.  
• تست‌های Stageهای قبلی را دوباره اجرا نکند  
(مگر Stage جاری به آن‌ها وابسته باشد).

قاعده ۷ — ادامه از حالت قبلی  
اگر Kilo وسط کار متوقف شد (قطعی اتصال، بستن پنجره، و ...):  
• اول فایل CURRENT_STATE.md همان Stage را بخواند.  
• بفهمد تا کجا رفته و چه کارهایی نیمه‌کاره است.  
• از همان‌جا ادامه دهد، نه از صفر.  
• توکن خود را صرف کشف مجدد وضعیت نکند.

اگر Stage تازه شروع شده و CURRENT_STATE.md وجود ندارد:  
• Kilo اول آن را می‌سازد با وضعیت IN_PROGRESS.  
• بعد شروع به کار می‌کند.

CURRENT_STATE.md باید قبل و بعد از هر فایل کامل‌شده  
به‌روزرسانی شود. نقش آن Resume State است، نه جایگزین  
MANIFEST. تفکیک:  
• CURRENT_STATE.md → وضعیت زنده برای ادامه کار  
• MANIFEST.json → وضعیت رسمی Stage  
• ROADMAP → وضعیت برنامه‌ریزی

قاعده ۸ — وفاداری به Legacy  
• منطق Legacy را حفظ کند، اما کد را کپی نکند.  
• از درس‌های Legacy استفاده کند، اما implementation  
را از نو بسازد.

قاعده ۹ — ممنوعیت رها کردن Stage  
Kilo هرگز Stage را نیمه‌کاره رها نمی‌کند و به Stage بعدی  
نمی‌رود. تا Stage تمام نشده و تأیید نشده، Stage بعدی  
شروع نمی‌شود.

اگر واقعاً قادر به ادامه نیست (خطای محیطی، ابهام حل‌نشده):  
• Stage را متوقف کند.  
• Status را در CURRENT_STATE روی BLOCKED بگذارد.  
• صریح بنویسد چرا متوقف شد.  
• منتظر پاسخ بماند.

═══════════════════════════════════════════════════════════  
بخش ۴ — محیط اجرا  
═══════════════════════════════════════════════════════════

Branch: v4  
• شاخه main دست‌نخورده می‌ماند (Legacy).  
• تمام کار V4 روی شاخه v4 انجام می‌شود.  
• Kilo هیچ‌گاه روی main تغییر نمی‌دهد.  
• شاخه v4 از ابتدا خالی است — فایل‌های Legacy روی آن  
وجود ندارند. Kilo فقط فایل‌هایی را که خودش می‌سازد  
روی v4 می‌بیند.

محیط:  
• PythonAnywhere فعال  
• Python Version: 3.12 (تأیید نهایی در Stage A1)  
• Package Management: pyproject.toml

فضای ذخیره‌سازی:  
• Google Drive آماده است (فقط برای Stage لاگینگ)  
• در بسته A، اتصال واقعی به Drive در Stage خودش انجام می‌شود

توضیح تکمیلی درباره Google Drive:
• اتصال واقعی به Google Drive بخشی از Stage A2 نیست.
• Stage A2 فقط Logging محلی (Local File) را پیاده‌سازی می‌کند.
• اتصال واقعی به Drive در یک Stage جداگانه بعد از A2 انجام
  خواهد شد.
• این تفکیک برای جلوگیری از تفسیر نادرست و حفظ اصل
  «هر Stage کوچک و قابل اثبات» است.

═══════════════════════════════════════════════════════════  
بخش ۵ — ممنوعیت‌های قطعی  
═══════════════════════════════════════════════════════════

• تغییر در main branch  
• نصب کتابخانه اضافی بدون تأیید  
• اتصال به Exchange یا Provider در بسته A  
• ورود به منطق تحلیل یا رابط کاربری در بسته A  
• ذخیره Secret در GitHub یا هر جای عمومی  
• تولید فایل خارج از فهرست Scope همان Stage  
• جستجوی گسترده در Repository بدون نیاز  
• تولید گزارش طولانی بدون درخواست  
• تغییر ساختار پوشه‌های مصوب

═══════════════════════════════════════════════════════════  
بخش ۶ — گزارش پایانی هر Stage  
═══════════════════════════════════════════════════════════

Kilo در پایان هر Stage، این چهار فایل را تحویل می‌دهد:

۱. docs/stages/STAGE_XX/LEDGER.md  
۲. docs/stages/STAGE_XX/MANIFEST.json  
۳. docs/stages/STAGE_XX/SHA256.json  
۴. docs/stages/STAGE_XX/CURRENT_STATE.md

CURRENT_STATE.md از ابتدای Stage ساخته می‌شود و در طول اجرا  
مداوم آپدیت می‌شود. سه فایل دیگر در پایان Stage نهایی  
می‌شوند.

اگر Stage قابل تحویل نبود، صریح دلیل در LEDGER ثبت می‌شود.

═══════════════════════════════════════════════════════════  
بخش ۷ — قالب اجرای هر Stage  
═══════════════════════════════════════════════════════════

هر Stage دقیقاً این چرخه را طی می‌کند:

Study → Plan → Implement → Test → Verify → Report

هیچ مرحله‌ای نباید حذف یا ترکیب شود.

اگر Stage بزرگ است، به Unitهای کوچک‌تر تقسیم می‌شود  
و هر Unit همین چرخه را طی می‌کند.

═══════════════════════════════════════════════════════════  
بخش ۸ — تحویل کد و آرتیفکت‌ها  
═══════════════════════════════════════════════════════════

هر Stage دو نوع خروجی دارد:

الف) کد اصلی و تست  
• کد اصلی در مسیر واقعی خودش:  
app/config/stage_a1_config.py  
app/core/stage_a1_version.py  
• تست Stage:  
tests/stages/STAGE_A1/test_stage_a1_structure.py  
• این‌ها توسط Kilo نوشته و اجرا می‌شوند.

ب) آرتیفکت‌های Stage  
• docs/stages/STAGE_A1/LEDGER.md  
• docs/stages/STAGE_A1/MANIFEST.json  
• docs/stages/STAGE_A1/SHA256.json  
• docs/stages/STAGE_A1/CURRENT_STATE.md

نقش MANIFEST:  
پل بین کد و Stage. فهرست تمام فایل‌های .py که Stage ساخته

-   فهرست تست‌ها + مسیر هرکدام.

═══════════════════════════════════════════════════════════  
بخش ۹ — تصمیم‌های پایه‌ای (تصویب‌شده)  
═══════════════════════════════════════════════════════════

۱. ساختار تست:  
Stage-محور → tests/stages/STAGE_XX/  
عمومی → tests/unit/

۲. نام فایل کد:  
با پیشوند Stage، به‌جز فایل‌های همیشه ثابت  
(مثل **init**.py, pyproject.toml, wsgi.py)

۳. Git Commit:  
یک Commit نهایی بعد از تأیید Stage.  
فرمت پیام Commit:  
"Stage A1: project skeleton"  
"Stage A2: logging foundation"  
"Stage B1: data engine core"  
Kilo قبل از تأیید، Commit نهایی نمی‌زند.

۴. Rollback:  
Kilo خودش Rollback نمی‌کند.  
فقط گزارش می‌دهد. تصمیم با مالک/طراح.

۵. State Tracking:  
MANIFEST = وضعیت رسمی  
CURRENT_STATE.md = وضعیت زنده  
Roadmap = وضعیت برنامه

۶. Python Version:
     3.12 (تأییدشده در Stage A1).

۷. Ledger:  
نتیجه + خطاهای مهم + اصلاحات + محدودیت‌ها.  
بدون جزئیات بی‌ارزش.

۸. Package Management:  
pyproject.toml (نه requirements.txt).

۹. API Config:  
فقط env template. هیچ placeholder جداگانه.

۱۰. فایل‌های عمومی ریشه:  
.gitignore و README.md در Stage A1 ساخته می‌شوند.

═══════════════════════════════════════════════════════════  
بخش ۱۰ — مسیر بازبینی و تأیید  
═══════════════════════════════════════════════════════════

پس از پایان هر Stage:

۱. Kilo چهار فایل آرتیفکت را تحویل می‌دهد.  
۲. نتیجه به طراح فنی و مالک ارسال می‌شود.  
۳. طراح فنی بررسی می‌کند:  
• آیا Scope رعایت شده؟  
• آیا تست‌ها پاس شده‌اند؟  
• آیا آرتیفکت‌ها کامل هستند؟  
• آیا قاعده‌ای نقض شده؟  
۴. اگر ایراد داشت:  
• طراح ایراد را مشخص می‌کند.  
• به Kilo برگشت داده می‌شود.  
• Kilo اصلاح می‌کند.  
• دوباره بررسی می‌شود.  
۵. اگر تأیید شد:  
• مالک تأیید نهایی می‌دهد.  
• Stage به‌عنوان PASSED ثبت می‌شود.  
• Stage بعدی شروع می‌شود.

═══════════════════════════════════════════════════════════  
بخش ۱۱ — Stage Artifact Standard  
═══════════════════════════════════════════════════════════

ساختار پوشه‌ی Stage:

docs/stages/STAGE_XX/  
├── LEDGER.md  
├── MANIFEST.json  
├── SHA256.json  
└── CURRENT_STATE.md

فایل AUDIT_METADATA جداگانه وجود ندارد.  
اطلاعات Audit بین چهار فایل بالا تقسیم می‌شود.  
Artifact Timing:

-   CURRENT_STATE.md از ابتدای Stage ساخته می‌شود و  
    در طول اجرا مداوم آپدیت می‌شود.
-   LEDGER.md، MANIFEST.json و SHA256.json در پایان Stage  
    نهایی می‌شوند — یعنی بعد از اینکه همه‌ی تست‌ها اجرا  
    و همه‌ی معیارهای پذیرش بررسی شدند.
-   SHA256.json باید آخرین فایل نهایی‌شده باشد، چون  
    hash سایر فایل‌ها را در خود دارد.

ساختار LEDGER.md:

# Stage XX — V4

## Identity

```
- Project, Version, Stage, Execution Unit
- Status, Started At, Completed At

```

## Scope

```
- این Stage چه کاری باید انجام می‌داد

```

## Changes

```
- چه چیزی ساخته شد
- چه چیزی تغییر کرد
- چه چیزی انجام نشد

```

## Tests

```
- Test command
- Test count, Passed, Failed, Skipped

```

## Results

```
- معیار پذیرش
- نتیجه هر معیار

```

## Limitations / UNKNOWN

```
- محدودیت‌ها
- موارد UNKNOWN

```

## Integrity

```
- SHA256 artifact generated: YES/NO

```

## Next Step

```
- Stage بعدی

```

ساختار MANIFEST.json:  
{  
"project": "Kitchen Assistant Bot",  
"version": "V4",  
"stage": "A1",  
"execution_unit": "STAGE_A1",  
"status": "PASSED",  
"scope": [],  
"artifacts": [  
{"path": "...", "type": "source", "required": true},  
{"path": "...", "type": "test", "required": true}  
],  
"tests": [],  
"generated_at": "",  
"completed_at": "",  
"file_count": 0  
}

ساختار CURRENT_STATE.md:

# STAGE_XX — Current State

## وضعیت کلی

```
IN_PROGRESS / BLOCKED / PASSED / FAILED

```

## کارهای انجام‌شده

```
- [x] ...

```

## کارهای نیمه‌کاره

```
- [ ] ...

```

## کارهای باقی‌مانده

```
- [ ] ...

```

## آخرین بروزرسانی

```
تاریخ و ساعت

```

ساختار SHA256.json:  
فهرست فایل‌ها با hash SHA-256 هرکدام.

خارج از Hash Scope:  
.git/, .pytest_cache/, **pycache**/,  
.venv/, venv/, .env, *.pyc,  
runtime-generated data, logs/runtime/,  
CURRENT_STATE.md (فایل زنده برای Resume)

خود SHA256.json در hash خودش نیست.  
SHA256.json آخرین Artifact تولیدشده است.

وضعیت‌های استاندارد Stage:  
PLANNED / IN_PROGRESS / PASSED / FAILED / BLOCKED

═══════════════════════════════════════════════════════════  
بخش ۱۲ — ارجاع Roadmapها به PREAMBLE  
═══════════════════════════════════════════════════════════

هر Roadmap بسته (A، B، C، D) در ابتدای خود این جمله را دارد:

«این Roadmap بر پایه PREAMBLE_V4 نسخه ۱ نوشته شده است.  
قواعد عمومی از آن گرفته می‌شود.»

═══════════════════════════════════════════════════════════  
بخش ۱۳ — ساختار پوشه‌های نهایی V4  
═══════════════════════════════════════════════════════════

kitchen-assistant-bot/  
├── app/  
│ ├── config/  
│ ├── core/  
│ ├── data/  
│ ├── market/  
│ ├── analysis/  
│ ├── bot/  
│ └── api/  
├── tests/  
│ ├── stages/  
│ │ ├── STAGE_A1/  
│ │ ├── STAGE_A2/  
│ │ └── ...  
│ └── unit/  
├── scripts/  
├── data/  
├── logs/  
└── docs/  
├── roadmap/  
│ ├── PREAMBLE_V4.md  
│ ├── ROADMAP_A.md  
│ ├── ROADMAP_B.md  
│ ├── ROADMAP_C.md  
│ └── ROADMAP_D.md  
├── stages/  
│ ├── STAGE_A1/  
│ │ ├── LEDGER.md  
│ │ ├── MANIFEST.json  
│ │ ├── SHA256.json  
│ │ └── CURRENT_STATE.md  
│ └── STAGE_A2/...  
└── reports/

نکته: پوشه ledgers/ در ریشه حذف شد.

پوشه‌هایی که در Stage A1 ساخته نمی‌شوند:  
• app/logging/ (در Stage لاگینگ)  
• app/trading/ (فاز Trade Management)  
• app/journal/ (فاز Trading Journal)  
• app/orderbook/ (فاز Order Book)

═══════════════════════════════════════════════════════════  
# 14. REPORT COMPLETENESS RULE

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
═══════════════════════════════════════════════════════════

پایان PREAMBLE_V4 — نسخه ۱ (LOCKED)  
═══════════════════════════════════════════════════════════
