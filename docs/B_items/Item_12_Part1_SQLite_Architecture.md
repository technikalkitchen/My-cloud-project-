# Item_12_Storage.md — Part 1: SQLite Architecture & Schema (v2.2)

تاریخ: ۵ نوامبر ۲۰۲۶
نسخه: 2.2
وضعیت: PROPOSED
نوع تغییر: اصلاح اسکیما (Schema Refinement) و اعمال تصمیمات Cross_Item_Resolution

۰. هدف و دامنه

این سند، معماری و اسکیمای پایگاه داده SQLite را برای Item_12 تعریف می‌کند.

مسئولیت‌های آن محدود به موارد زیر است:
- تعریف جداول و فیلدهای موردنیاز پایگاه داده.
- تعریف Primary Keys، Foreign Keys، Constraints و Indexes.
- فراهم‌کردن ساختار داده پایدار موردنیاز Item_11.
- تعریف ساختار سطح پایگاه داده برای Jobs، Subscribers، Outbox و Pacing State.

مسئولیت‌های زیر خارج از این سند باقی می‌مانند:
- Atomic Claim، اجرای تراکنش، مدیریت Lock، Lease، Fencing و Recovery ← Item_12 Part 2
- Queue State Machine و مدیریت وضعیت Outbox ← Item_11
- طبقه‌بندی خطا، سیاست Retry و زمان‌بندی Backoff ← Item_10
- قالب‌بندی تلگرام و تحویل Telegram API ← Package D

این سند منطق داخلی این اجزا را دوباره تعریف نمی‌کند.

۱. محیط SQLite و محدودیت‌های ذخیره‌سازی

پایگاه داده در محیط PythonAnywhere اجرا می‌شود، جایی که فایل پایگاه داده روی فضای ذخیره‌سازی NFS قرار دارد.

محدودیت‌های زیر اعمال می‌شوند:
- حالت WAL در SQLite نباید استفاده شود.
- باید از حالت Rollback Journal Mode استفاده شود.
- عملیات نوشتن در پایگاه داده باید کوتاه و کنترل‌شده باقی بمانند.
- تراکنش‌های پایگاه داده نباید در حین عملیات شبکه‌ای باز بمانند.
- رفتار File Locking باید در Stage B اعتبارسنجی شود.
- عملیات چند Dispatcher روی SQLite/NFS تا زمانی که تست‌های Locking در Stage B پاس نشوند، اعتبارسنجی‌شده تلقی نمی‌شود.
- فرض تک‌نویسنده (Single-writer assumption) برای جلوگیری از قفل شدن NFS الزامی است. [A4]

جزئیات رفتار Lock، Busy Timeout، مدیریت تراکنش و Recovery در Item_12 Part 2 تعریف می‌شود.

۲. اسکیمای پایگاه داده

نسخه MVP از چهار جدول استفاده می‌کند: Jobs | Subscribers | Outbox | Pacing_State
هیچ جدول اضافی برای این نسخه نیاز نیست.

۲.۱. جدول Jobs (مدیریت صف)

رکوردهای پایدار Job را که توسط سیستم‌های Scanner و Fetch ایجاد می‌شوند، ذخیره می‌کند.

| فیلد | نوع داده | توضیحات |
|---|---|---|
| job_id | TEXT NOT NULL | UUID، Primary Key. در SQLite، TEXT PK به طور پیش‌فرض NULL می‌پذیرد؛ NOT NULL الزامی است. |
| job_type | TEXT NOT NULL | SCANNER یا FETCH. بدون NOT NULL، CHECK بی‌اثر می‌شود. |
| normalized_payload | TEXT | Payload نرمال‌شده JSON برای مقایسه درخواست‌ها و ارزیابی همپوشانی بازه‌ها. |
| payload_hash | TEXT | هش Payload نرمال‌شده درخواست. |
| status | TEXT NOT NULL | QUEUED, RUNNING, COMPLETED, PARTIAL, RETRY_WAIT, FAILED. |
| not_before | INTEGER | زمان مجاز برای Claim (پیاده‌سازی R-04). ذخیره به صورت Unix ms. |
| lease_until | INTEGER | زمان انقضای Lease؛ می‌تواند NULL باشد. |
| fencing_token | INTEGER NOT NULL DEFAULT 0 | شمارنده Fencing؛ NOT NULL الزامی است. |
| next_attempt_at | INTEGER | زمان مجاز تلاش بعدی؛ برای Jobهای RETRY_WAIT الزامی و در سایر وضعیت‌ها می‌تواند NULL باشد. |
| created_at | INTEGER | زمان ایجاد رکورد (Unix ms). |
| updated_at | INTEGER | زمان آخرین به‌روزرسانی (Unix ms). |

قواعد:
- normalized_payload داده‌های نرمال‌شده درخواست را برای Coalescing و مقایسه همپوشانی بازه‌ها ذخیره می‌کند.
- payload_hash برای شناسایی درخواست‌های نرمال‌شده معادل استفاده می‌شود. هش به‌تنهایی برای مقایسه همپوشانی بازه‌ها کافی نیست.
- RETRY_WAIT یک وضعیت پایدار معتبر برای Job است. برای Job با وضعیت RETRY_WAIT، مقدار next_attempt_at باید ثبت شود تا زمان مجاز تلاش بعدی پس از Restart نیز قابل بازیابی باشد.
- فیلدهای Lease و Fencing اینجا ذخیره می‌شوند، اما رفتار عملیاتی آن‌ها متعلق به Item_12 Part 2 است.

۲.۲. جدول Subscribers (مشترکین)

رابطه بین درخواست‌های ورودی و Jobهای مرتبط با آن‌ها را ذخیره می‌کند.

| فیلد | نوع داده | توضیحات |
|---|---|---|
| request_id | TEXT NOT NULL | Primary Key (نوع TEXT، نیازمند NOT NULL). |
| job_id | TEXT NOT NULL | Foreign Key ← Jobs.job_id. |
| user_id | TEXT NOT NULL | شناسه کاربر تلگرام. |
| status | TEXT NOT NULL | WAITING, COMPLETED, FAILED. |
| created_at | INTEGER NOT NULL | زمان ثبت مشترک (Unix ms). [A1] |

قواعد:
- یک Subscriber نمایانگر یک درخواست ورودی مرتبط با یک Job است.
- چند Subscriber می‌توانند به یک Job اشاره کنند.
- وضعیت تحویل پیام تلگرام در اینجا ذخیره نمی‌شود. پیگیری تحویل تلگرام متعلق به Outbox است.
- request_id مرجعی است که برای ردیابی یک گزارش تحویل‌شده به درخواست مبدأ آن استفاده می‌شود.

۲.۳. جدول Outbox (پیام‌های تلگرام)

رکوردهای پایدار تحویل تلگرام را ذخیره می‌کند. این جدول هم از رکوردهای Parent (اصلی) و هم از رکوردهای Chunk (قطعه) مرتبط با آن پشتیبانی می‌کند.

| فیلد | نوع داده | توضیحات |
|---|---|---|
| message_id | TEXT NOT NULL | UUID، Primary Key (نیازمند NOT NULL). |
| record_type | TEXT NOT NULL | PARENT یا CHUNK (بدون NOT NULL، CHECK بی‌اثر می‌شود). |
| parent_id | TEXT | Foreign Key ← Outbox.message_id؛ برای PARENT مقدار NULL. |
| chunk_index | INTEGER | شماره ترتیبی قطعه؛ برای PARENT مقدار NULL. |
| request_id | TEXT | Foreign Key اختیاری ← Subscribers.request_id؛ فقط برای PARENT. [A5] |
| user_id | TEXT NOT NULL | شناسه کاربر تلگرام. |
| priority | TEXT NOT NULL | HIGH یا LOW. |
| payload_text | TEXT | متن دقیق و پایدار Payload برای این رکورد. |
| status | TEXT NOT NULL | وضعیت‌های Parent و Chunk. |
| telegram_message_id | TEXT | شناسه پیام تلگرام؛ می‌تواند NULL باشد. |
| retry_count | INTEGER NOT NULL DEFAULT 0 | تعداد تلاش‌های تحویل. |
| next_attempt_at | INTEGER | زمان مجاز تلاش بعدی؛ برای Chunk قابل استفاده است. |
| lease_until | INTEGER | زمان انقضای Lease ارسال برای Chunk؛ برای Parent همیشه NULL است. |
| fencing_token | INTEGER | شمارنده محافظ؛ برای Chunk مقدار NOT NULL DEFAULT 0، برای Parent NULL. |
| created_at | INTEGER | زمان ایجاد رکورد (Unix ms). |
| updated_at | INTEGER | زمان آخرین به‌روزرسانی (Unix ms). |

مقادیر وضعیت Parent: PENDING, SENDING, DELIVERED, PARTIAL, RETRY_WAIT, FAILED
مقادیر وضعیت Chunk: PENDING, SENDING, DELIVERED, RETRY_WAIT, DELIVERY_UNKNOWN, FAILED

قواعد Payload:
- یک رکورد PARENT خروجی کامل قالب‌بندی‌شده دریافت‌شده برای تحویل را ذخیره می‌کند.
- هر رکورد CHUNK متن Payload دقیق خودش را ذخیره می‌کند.
- Payloadهای قطعات باید ذخیره شوند تا در صورت Retry، همان محتوا بدون تولید مجدد یا تغییر، دوباره ارسال شود.
- Payload ذخیره‌شده همان محتوای آماده تحویل است که از مرز Package D / Item_11 ارائه می‌شود. Item_12 فقط Payload را ذخیره می‌کند؛ آن را تولید، قالب‌بندی یا تغییر نمی‌دهد.

قواعد Parent/Chunk:
- یک رکورد PARENT باید parent_id = NULL و chunk_index = NULL داشته باشد.
- یک رکورد CHUNK باید parent_id و chunk_index غیر NULL داشته باشد.
- یک CHUNK باید به یک رکورد PARENT ارجاع دهد، نه به یک CHUNK دیگر.
- chunk_index باید در محدوده Parent خود یکتا باشد.
- request_id اختیاری است و متعلق به رکورد PARENT است. رکوردهای CHUNK از رابطه Parent برای ردیابی استفاده می‌کنند.
- lease_until برای Parent همیشه NULL است. برای Chunk تا زمان Claim می‌تواند NULL باشد.
- fencing_token برای Parent همیشه NULL است. برای Chunk باید NOT NULL باشد و مقدار اولیه آن 0 باشد.
- وضعیت تحویل Parent طبق قواعد مدیریت وضعیت تعریف‌شده در Item_11 حفظ می‌شود.

۲.۴. جدول Pacing_State (مدیریت سهمیه)

رکوردهای پایدار رزرو و مصرف Pacing را ذخیره می‌کند.

| فیلد | نوع داده | توضیحات |
|---|---|---|
| reservation_id | TEXT NOT NULL | UUID، Primary Key (نیازمند NOT NULL). |
| chunk_message_id | TEXT NOT NULL | Foreign Key ← Outbox.message_id (ارجاع فقط به CHUNK مجاز است). |
| token_key | TEXT NOT NULL | GLOBAL یا USER_{user_id}. |
| reserved_at | INTEGER | زمان ایجاد رزرو (Unix ms). |
| expires_at | INTEGER | زمان انقضای رزرو (Unix ms). |
| used_at | INTEGER | زمان واقعی مصرف رزرو؛ می‌تواند NULL باشد. |
| status | TEXT NOT NULL | ACTIVE, USED, EXPIRED. |

قواعد:
- هر رزرو از طریق chunk_message_id به رکورد CHUNK مربوطه متصل می‌شود.
- هر رکورد Pacing_State باید به یک رکورد CHUNK متصل باشد، نه Parent.
- یک Chunk ممکن است در تلاش‌های مختلف تحویل، چندین رکورد رزرو داشته باشد.
- رزروهای Global و Per-User به صورت رکوردهای جداگانه ذخیره می‌شوند.
- reserved_at نمایانگر زمان ایجاد رزرو است، نه زمان واقعی مصرف آن.
- used_at زمان مصرف ظرفیت Pacing رزروشده را ثبت می‌کند.
- یک رزرو ACTIVE که دیگر معتبر نیست ممکن است با وضعیت EXPIRED علامت‌گذاری شود.
- رزروی که توسط یک تلاش تحویل مصرف شده است، با وضعیت USED و یک مقدار used_at علامت‌گذاری می‌شود.
- چرخه حیات رزرو و منطق اجرای Pacing تحت مسئولیت Item_11 باقی می‌ماند.

۳. محدودیت‌ها و ایندکس‌ها (Constraints & Indexes)

۳.۱. کلیدهای اصلی (Primary Keys)
کلیدهای اصلی زیر باید تعریف شوند (همگی نیازمند NOT NULL هستند):
- Jobs.job_id
- Subscribers.request_id
- Outbox.message_id
- Pacing_State.reservation_id

۳.۲. کلیدهای خارجی (Foreign Keys)
کلیدهای خارجی زیر باید اجرا شوند:
- Subscribers.job_id ← Jobs.job_id
- Outbox.parent_id ← Outbox.message_id
- Outbox.request_id ← Subscribers.request_id
- Pacing_State.chunk_message_id ← Outbox.message_id

اجرای Foreign Key در SQLite باید برای هر اتصال به پایگاه داده فعال شود:
PRAGMA foreign_keys = ON;

۳.۳. محدودیت‌های الزامی (Constraints)

Jobs:
- job_type باید SCANNER یا FETCH باشد.
- status باید یکی از وضعیت‌های تعریف‌شده Job باشد.
- fencing_token نباید NULL باشد و مقدار اولیه آن 0 است.
- اگر status برابر RETRY_WAIT باشد، next_attempt_at باید غیر NULL باشد.

Subscribers:
- status باید WAITING، COMPLETED یا FAILED باشد.

Outbox:
- record_type باید PARENT یا CHUNK باشد.
- priority باید HIGH یا LOW باشد.
- status باید با مجموعه وضعیت‌های مجاز Parent یا Chunk مطابقت داشته باشد.
- CHECK برای اطمینان از تطابق status با record_type:
  CHECK (
    (record_type = 'PARENT' AND status IN ('PENDING', 'SENDING', 'DELIVERED', 'PARTIAL', 'RETRY_WAIT', 'FAILED'))
    OR
    (record_type = 'CHUNK' AND status IN ('PENDING', 'SENDING', 'DELIVERED', 'RETRY_WAIT', 'DELIVERY_UNKNOWN', 'FAILED'))
  )
- رکوردهای PARENT باید parent_id و chunk_index برابر با NULL داشته باشند. lease_until و fencing_token نیز برای Parent باید NULL باشند.
- رکوردهای CHUNK باید parent_id و chunk_index غیر NULL داشته باشند. chunk_index نباید منفی باشد (chunk_index IS NOT NULL AND chunk_index >= 0). lease_until می‌تواند NULL باشد؛ fencing_token نباید NULL باشد و مقدار اولیه آن 0 است.
- UNIQUE(parent_id, chunk_index) باید اجرا شود.
- request_id می‌تواند NULL باشد؛ در صورت وجود، فقط متعلق به یک رکورد PARENT است.
- یک CHUNK باید به یک PARENT ارجاع دهد، نه به یک CHUNK دیگر. این رابطه باید از طریق Trigger در سطح پایگاه داده اجرا شود.

Pacing_State:
- token_key باید GLOBAL یا یک توکن خاص USER را شناسایی کند.
- status باید ACTIVE، USED یا EXPIRED باشد.
- رکوردهای USED باید مقدار used_at غیر NULL داشته باشند.
- رکوردهای ACTIVE و EXPIRED نباید مقدار used_at داشته باشند.
- هر رکورد Pacing_State باید به یک رکورد CHUNK ارجاع دهد. این شرط باید در سطح پایگاه داده (Trigger) اجرا شود.

۳.۴. ایندکس‌های الزامی (Indexes)

- Jobs: (status, not_before) [R-04]، (job_type, payload_hash, status)، (status, next_attempt_at)
- Subscribers: (job_id)
- Outbox: (status, priority, next_attempt_at)، (parent_id, chunk_index)، (request_id)
- Pacing_State: (token_key, status, expires_at)، (chunk_message_id)، (token_key, status, used_at)

این ایندکس‌ها از کوئری‌های مورد انتظار برای جستجو، زمان‌بندی، روابط و مصرف رزرو پشتیبانی می‌کنند.

۴. مالکیت و مرزهای مسئولیت

| مسئولیت | مالک |
|---|---|
| اسکیمای پایگاه داده، جداول، فیلدها، محدودیت‌ها و ایندکس‌ها | Item_12 Part 1 |
| نوشتن اتمیک، تراکنش‌ها، مدیریت Lock، Lease، Fencing و Recovery | Item_12 Part 2 |
| Queue State Machine و منطق وضعیت تحویل Outbox | Item_11 |
| سیاست Pacing و چرخه حیات رزرو | Item_11 |
| طبقه‌بندی خطا، سیاست Retry و زمان‌بندی Backoff | Item_10 |
| قالب‌بندی تلگرام و فراخوانی Telegram API | Package D |

قواعد مرزی:
- Item_12 ذخیره‌سازی پایدار و یکپارچگی سطح پایگاه داده را فراهم می‌کند.
- Item_12 State Machine یا سیاست Pacing مربوط به Item_11 را دوباره تعریف نمی‌کند.
- Item_12 سیاست Retry یا Backoff مربوط به Item_10 را پیاده‌سازی نمی‌کند.
- Item_12 قالب‌بندی تلگرام یا تحویل API را انجام نمی‌دهد.
- Item_11 همچنان مسئول هماهنگی رفتار Outbox و Pacing با استفاده از قابلیت‌های ذخیره‌سازی فراهم‌شده توسط Item_12 است.

۵. اعتبارسنجی در Stage B

رفتارهای زیر پایگاه داده باید در Stage B اعتبارسنجی شوند:
۱. حالت SQLite Rollback Journal Mode در محیط هدف PythonAnywhere/NFS به درستی کار می‌کند.
۲. رفتار File Locking تحت الگوی دسترسی مورد انتظار تست می‌شود.
۳. اجرای Foreign Key روی هر اتصال پایگاه داده فعال است.
۴. محدودیت‌های رابطه Parent/Chunk اجرا می‌شوند.
۵. محدودیت‌های وضعیت و فیلدهای وابسته به نوع رکورد اجرا می‌شوند.
۶. ایندکس‌های الزامی وجود دارند.
۷. Payloadهای پایدار Outbox پس از راه‌اندازی مجدد فرآیند در دسترس باقی می‌مانند.
۸. رکوردهای رزرو و مصرف Pacing قابل ردیابی به رکوردهای Chunk مرتبط با خود هستند.
۹. مقدار next_attempt_at برای Jobهای RETRY_WAIT پس از Restart قابل بازیابی است.
۱۰. مقدار fencing_token برای Jobها و Chunkها همیشه معتبر و غیر NULL است.

پاس شدن این تست‌ها قبل از اتکا به پایگاه داده برای حجم کار تولیدی مربوطه الزامی است.
تست‌های دقیق همزمانی، Atomic Claim، Lock recovery، Lease، Fencing و جریان تراکنش متعلق به Item_12 Part 2 هستند.

۶. فرمت زمان و استراتژی مهاجرت

[A2] فرمت زمان:
- نمایش در JSON و خروجی‌ها: ISO 8601 با پسوند Z (مثال: 2026-10-19T00:00:00Z).
- ذخیره‌سازی داخلی در SQLite: Unix Timestamp بر حسب میلی‌ثانیه (INTEGER).

[A3] استراتژی مهاجرت:
با توجه به اینکه نسخه v1.3 هرگز در محیط عملیاتی (Production) اجرا نشده است، استراتژی مهاجرت از v1.3 به v2.2 به صورت Drop and Recreate (حذف جداول قدیمی و ساخت مجدد) است. نیازی به اسکریپت‌های پیچیده انتقال داده (Data Migration) نیست.

۷. خلاصه تغییرات نسخه ۲.۲

تغییرات نسبت به نسخه ۱.۳ (و اعمال قوانین Resolution):
- افزودن Jobs.next_attempt_at برای ذخیره زمان تلاش بعدی Jobهای RETRY_WAIT.
- افزودن Jobs.not_before و ایندکس (status, not_before) برای پیاده‌سازی R-04.
- اعمال NOT NULL برای تمام Primary Keyها (به دلیل رفتار خاص SQLite با TEXT PRIMARY KEY).
- اعمال NOT NULL برای تمام فیلدهای status، record_type، priority، token_key، user_id، job_type و chunk_message_id.
- الزام NOT NULL DEFAULT 0 برای Jobs.fencing_token و Outbox.fencing_token در رکوردهای CHUNK.
- افزودن CHECK برای تطابق status با record_type در Outbox.
- الزام به ارجاع Pacing_State به رکورد CHUNK از طریق Trigger.
- شفاف‌سازی اینکه lease_until برای Parent همیشه NULL است و برای Chunk تا زمان Claim می‌تواند NULL باشد.
- افزودن Subscribers.created_at [A1].
- اصلاح محدودیت CHUNK به chunk_index IS NOT NULL AND chunk_index >= 0.
- حفظ کامل ۴۰ مورد چک‌لیست بریف AM در این نسخه.
