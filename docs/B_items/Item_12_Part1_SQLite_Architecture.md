Item_12 — Part 1: SQLite Architecture & Schema

تاریخ: ۲ نوامبر ۲۰۲۶
نسخه: 1.3
وضعیت: PROPOSED
نوع تغییر: اصلاح اسکیما (Schema Refinement)
نسخه پایه: Item_12 Part 1 v1.2

۰. هدف و دامنه

این سند، معماری و اسکیمای پایگاه داده SQLite را برای Item_12 تعریف می‌کند.

مسئولیت‌های آن محدود به موارد زیر است:

تعریف جداول و فیلدهای موردنیاز پایگاه داده.

تعریف Primary Keys، Foreign Keys، Constraints و Indexes.

فراهم‌کردن ساختار داده پایدار موردنیاز Item_11.

تعریف ساختار سطح پایگاه داده برای Jobs، Subscribers، Outbox و Pacing State.

مسئولیت‌های زیر خارج از این سند باقی می‌مانند:

Atomic Claim، اجرای تراکنش، مدیریت Lock، Lease، Fencing و Recovery ← Item_12 Part 2

Queue State Machine و مدیریت وضعیت Outbox ← Item_11

طبقه‌بندی خطا، سیاست Retry و زمان‌بندی Backoff ← Item_10

قالب‌بندی تلگرام و تحویل Telegram API ← Package D

این سند منطق داخلی این اجزا را دوباره تعریف نمی‌کند.

۱. محیط SQLite و محدودیت‌های ذخیره‌سازی

پایگاه داده در محیط PythonAnywhere اجرا می‌شود، جایی که فایل پایگاه داده روی فضای ذخیره‌سازی NFS قرار دارد.

محدودیت‌های زیر اعمال می‌شوند:

حالت WAL در SQLite نباید استفاده شود.

باید از حالت Rollback Journal Mode استفاده شود.

عملیات نوشتن در پایگاه داده باید کوتاه و کنترل‌شده باقی بمانند.

تراکنش‌های پایگاه داده نباید در حین عملیات شبکه‌ای باز بمانند.

رفتار File Locking باید در Stage B اعتبارسنجی شود.

عملیات چند Dispatcher روی SQLite/NFS تا زمانی که تست‌های Locking در Stage B پاس نشوند، اعتبارسنجی‌شده تلقی نمی‌شود.

جزئیات رفتار Lock، Busy Timeout، مدیریت تراکنش و Recovery در Item_12 Part 2 تعریف می‌شود.

۲. اسکیمای پایگاه داده

نسخه MVP از چهار جدول استفاده می‌کند:

Jobs | Subscribers | Outbox | Pacing_State

هیچ جدول اضافی برای این نسخه نیاز نیست.

۲.۱. جدول Jobs

رکوردهای پایدار Job را که توسط سیستم‌های Scanner و Fetch ایجاد می‌شوند، ذخیره می‌کند.

فیلدنوع دادهتوضیحاتjob_idTEXTUUID، Primary Keyjob_typeTEXTSCANNER یا FETCHnormalized_payloadTEXTPayload نرمال‌شده JSON برای مقایسه درخواست‌ها و ارزیابی همپوشانی بازه‌هاpayload_hashTEXTهش Payload نرمال‌شده درخواستstatusTEXTQUEUED, RUNNING, COMPLETED, PARTIAL, RETRY_WAIT, FAILEDlease_untilTIMESTAMPزمان انقضای Lease؛ می‌تواند NULL باشدfencing_tokenINTEGERشمارنده Fencing؛ NOT NULL، مقدار اولیه 0next_attempt_atTIMESTAMPزمان مجاز تلاش بعدی؛ برای Jobهای RETRY_WAIT الزامی و در سایر وضعیت‌ها می‌تواند NULL باشدcreated_atTIMESTAMPزمان ایجاد رکوردupdated_atTIMESTAMPزمان آخرین به‌روزرسانی 

قواعد:

normalized_payload داده‌های نرمال‌شده درخواست را برای Coalescing و مقایسه همپوشانی بازه‌ها ذخیره می‌کند.

payload_hash برای شناسایی درخواست‌های نرمال‌شده معادل استفاده می‌شود.

هش به‌تنهایی برای مقایسه همپوشانی بازه‌ها کافی نیست.

RETRY_WAIT یک وضعیت پایدار معتبر برای Job است.

برای Job با وضعیت RETRY_WAIT، مقدار next_attempt_at باید ثبت شود تا زمان مجاز تلاش بعدی پس از Restart نیز قابل بازیابی باشد.

فیلدهای Lease و Fencing اینجا ذخیره می‌شوند، اما رفتار عملیاتی آن‌ها متعلق به Item_12 Part 2 است.

۲.۲. جدول Subscribers

رابطه بین درخواست‌های ورودی و Jobهای مرتبط با آن‌ها را ذخیره می‌کند.

فیلدنوع دادهتوضیحاتrequest_idTEXTPrimary Keyjob_idTEXTForeign Key ← Jobs.job_iduser_idTEXTشناسه کاربر تلگرامstatusTEXTWAITING, COMPLETED, FAILED 

قواعد:

یک Subscriber نمایانگر یک درخواست ورودی مرتبط با یک Job است.

چند Subscriber می‌توانند به یک Job اشاره کنند.

وضعیت تحویل پیام تلگرام در اینجا ذخیره نمی‌شود.

پیگیری تحویل تلگرام متعلق به Outbox است.

request_id مرجعی است که برای ردیابی یک گزارش تحویل‌شده به درخواست مبدأ آن استفاده می‌شود.

۲.۳. جدول Outbox

رکوردهای پایدار تحویل تلگرام را ذخیره می‌کند.

این جدول هم از رکوردهای Parent (اصلی) و هم از رکوردهای Chunk (قطعه) مرتبط با آن پشتیبانی می‌کند.

فیلدنوع دادهتوضیحاتmessage_idTEXTUUID، Primary Keyrecord_typeTEXTPARENT یا CHUNKparent_idTEXTForeign Key ← Outbox.message_id؛ برای PARENT مقدار NULLchunk_indexINTEGERشماره ترتیبی قطعه؛ برای PARENT مقدار NULLrequest_idTEXTForeign Key اختیاری ← Subscribers.request_id؛ فقط برای PARENTuser_idTEXTشناسه کاربر تلگرامpriorityTEXTHIGH یا LOWpayload_textTEXTمتن دقیق و پایدار Payload برای این رکوردstatusTEXTوابسته به record_typetelegram_message_idTEXTشناسه پیام تلگرام؛ می‌تواند NULL باشدretry_countINTEGERتعداد تلاش‌های تحویلnext_attempt_atTIMESTAMPزمان مجاز تلاش بعدی؛ برای Chunk قابل استفاده است و می‌تواند NULL باشدlease_untilTIMESTAMPزمان انقضای Lease ارسال برای Chunk؛ پیش از Claim می‌تواند NULL باشد و برای Parent همیشه NULL استfencing_tokenINTEGERشمارنده محافظ برای جلوگیری از تداخل ارسال‌کننده‌ها؛ برای Chunk مقدار اولیه 0 و NOT NULL، برای Parent مقدار NULLcreated_atTIMESTAMPزمان ایجاد رکوردupdated_atTIMESTAMPزمان آخرین به‌روزرسانی 

مقادیر وضعیت Parent:

PENDING, SENDING, DELIVERED, PARTIAL, RETRY_WAIT, FAILED

مقادیر وضعیت Chunk:

PENDING, SENDING, DELIVERED, RETRY_WAIT, DELIVERY_UNKNOWN, FAILED

قواعد Payload:

یک رکورد PARENT خروجی کامل قالب‌بندی‌شده دریافت‌شده برای تحویل را ذخیره می‌کند.

هر رکورد CHUNK متن Payload دقیق خودش را ذخیره می‌کند.

Payloadهای قطعات باید ذخیره شوند تا در صورت Retry، همان محتوا بدون تولید مجدد یا تغییر، دوباره ارسال شود.

Payload ذخیره‌شده همان محتوای آماده تحویل است که از مرز Package D / Item_11 ارائه می‌شود.

Item_12 فقط Payload را ذخیره می‌کند؛ آن را تولید، قالب‌بندی یا تغییر نمی‌دهد.

قواعد Parent/Chunk:

یک رکورد PARENT باید parent_id = NULL و chunk_index = NULL داشته باشد.

یک رکورد CHUNK باید parent_id و chunk_index غیر NULL داشته باشد.

یک CHUNK باید به یک رکورد PARENT ارجاع دهد، نه به یک CHUNK دیگر.

chunk_index باید در محدوده Parent خود یکتا باشد.

request_id اختیاری است و متعلق به رکورد PARENT است. رکوردهای CHUNK از رابطه Parent برای ردیابی استفاده می‌کنند.

lease_until برای Parent همیشه NULL است. برای Chunk تا زمان Claim می‌تواند NULL باشد.

fencing_token برای Parent همیشه NULL است. برای Chunk باید NOT NULL باشد و مقدار اولیه آن 0 باشد.

وضعیت تحویل Parent طبق قواعد مدیریت وضعیت تعریف‌شده در Item_11 حفظ می‌شود.

۲.۴. جدول Pacing_State

رکوردهای پایدار رزرو و مصرف Pacing را ذخیره می‌کند.

فیلدنوع دادهتوضیحاتreservation_idTEXTUUID، Primary Keychunk_message_idTEXTForeign Key ← Outbox.message_idtoken_keyTEXTGLOBAL یا USER_{user_id}reserved_atTIMESTAMPزمان ایجاد رزروexpires_atTIMESTAMPزمان انقضای رزروused_atTIMESTAMPزمان واقعی مصرف رزرو؛ می‌تواند NULL باشدstatusTEXTACTIVE, USED, EXPIRED 

قواعد:

هر رزرو از طریق chunk_message_id به رکورد CHUNK مربوطه متصل می‌شود.

هر رکورد Pacing_State باید به یک رکورد CHUNK متصل باشد، نه Parent.

یک Chunk ممکن است در تلاش‌های مختلف تحویل، چندین رکورد رزرو داشته باشد.

رزروهای Global و Per-User به صورت رکوردهای جداگانه ذخیره می‌شوند.

reserved_at نمایانگر زمان ایجاد رزرو است، نه زمان واقعی مصرف آن.

used_at زمان مصرف ظرفیت Pacing رزروشده را ثبت می‌کند.

یک رزرو ACTIVE که دیگر معتبر نیست ممکن است با وضعیت EXPIRED علامت‌گذاری شود.

رزروی که توسط یک تلاش تحویل مصرف شده است، با وضعیت USED و یک مقدار used_at علامت‌گذاری می‌شود.

چرخه حیات رزرو و منطق اجرای Pacing تحت مسئولیت Item_11 باقی می‌ماند.

۳. محدودیت‌ها و ایندکس‌ها (Constraints & Indexes)

۳.۱. کلیدهای اصلی (Primary Keys)

کلیدهای اصلی زیر باید تعریف شوند:

Jobs.job_id

Subscribers.request_id

Outbox.message_id

Pacing_State.reservation_id

۳.۲. کلیدهای خارجی (Foreign Keys)

کلیدهای خارجی زیر باید اجرا شوند:

Subscribers.job_id ← Jobs.job_id

Outbox.parent_id ← Outbox.message_id

Outbox.request_id ← Subscribers.request_id

Pacing_State.chunk_message_id ← Outbox.message_id

اجرای Foreign Key در SQLite باید برای هر اتصال به پایگاه داده فعال شود:

PRAGMA foreign_keys = ON;

۳.۳. محدودیت‌های الزامی (Constraints)

Jobs: job_type باید SCANNER یا FETCH باشد. status باید یکی از وضعیت‌های تعریف‌شده Job باشد. fencing_token نباید NULL باشد و مقدار اولیه آن 0 است. اگر status برابر RETRY_WAIT باشد، next_attempt_at باید غیر NULL باشد.

Subscribers: status باید WAITING، COMPLETED یا FAILED باشد.

Outbox: record_type باید PARENT یا CHUNK باشد. priority باید HIGH یا LOW باشد. status باید با مجموعه وضعیت‌های مجاز Parent یا Chunk مطابقت داشته باشد.

رکوردهای PARENT باید parent_id و chunk_index برابر با NULL داشته باشند. lease_until و fencing_token نیز برای Parent باید NULL باشند.

رکوردهای CHUNK باید parent_id و chunk_index غیر NULL داشته باشند. chunk_index نباید منفی باشد. lease_until می‌تواند NULL باشد؛ fencing_token نباید NULL باشد و مقدار اولیه آن 0 است.

UNIQUE(parent_id, chunk_index) باید اجرا شود.

request_id می‌تواند NULL باشد؛ در صورت وجود، فقط متعلق به یک رکورد PARENT است.

یک CHUNK باید به یک PARENT ارجاع دهد، نه به یک CHUNK دیگر. این رابطه باید از طریق Trigger در سطح پایگاه داده اجرا شود.

status رکوردهای PARENT و CHUNK باید به ترتیب با مجموعه وضعیت‌های مجاز Parent و Chunk مطابقت داشته باشد.

Pacing_State: token_key باید GLOBAL یا یک توکن خاص USER را شناسایی کند. status باید ACTIVE، USED یا EXPIRED باشد. رکوردهای USED باید مقدار used_at غیر NULL داشته باشند. رکوردهای ACTIVE و EXPIRED نباید مقدار used_at داشته باشند.

هر رکورد Pacing_State باید به یک رکورد CHUNK ارجاع دهد. این شرط باید در سطح پایگاه داده اجرا شود.

۳.۴. ایندکس‌های الزامی (Indexes)

ایندکس‌های زیر باید ایجاد شوند:

Jobs:

Jobs(status)

Jobs(job_type, payload_hash, status)

Jobs(status, next_attempt_at)

Subscribers:

Subscribers(job_id)

Outbox:

Outbox(status, priority, next_attempt_at)

Outbox(parent_id, chunk_index)

Outbox(request_id)

Pacing_State:

Pacing_State(token_key, status, expires_at)

Pacing_State(chunk_message_id)

Pacing_State(token_key, status, used_at)

این ایندکس‌ها از کوئری‌های مورد انتظار برای جستجو، زمان‌بندی، روابط و مصرف رزرو پشتیبانی می‌کنند.

۴. مالکیت و مرزهای مسئولیت

مسئولیتمالکاسکیمای پایگاه داده، جداول، فیلدها، محدودیت‌ها و ایندکس‌هاItem_12 Part 1نوشتن اتمیک، تراکنش‌ها، مدیریت Lock، Lease، Fencing و RecoveryItem_12 Part 2Queue State Machine و منطق وضعیت تحویل OutboxItem_11سیاست Pacing و چرخه حیات رزروItem_11طبقه‌بندی خطا، سیاست Retry و زمان‌بندی BackoffItem_10قالب‌بندی تلگرام و فراخوانی Telegram APIPackage D 

قواعد مرزی:

Item_12 ذخیره‌سازی پایدار و یکپارچگی سطح پایگاه داده را فراهم می‌کند.

Item_12 State Machine یا سیاست Pacing مربوط به Item_11 را دوباره تعریف نمی‌کند.

Item_12 سیاست Retry یا Backoff مربوط به Item_10 را پیاده‌سازی نمی‌کند.

Item_12 قالب‌بندی تلگرام یا تحویل API را انجام نمی‌دهد.

Item_11 همچنان مسئول هماهنگی رفتار Outbox و Pacing با استفاده از قابلیت‌های ذخیره‌سازی فراهم‌شده توسط Item_12 است.

۵. اعتبارسنجی در Stage B

رفتارهای زیر پایگاه داده باید در Stage B اعتبارسنجی شوند:

حالت SQLite Rollback Journal Mode در محیط هدف PythonAnywhere/NFS به درستی کار می‌کند.

رفتار File Locking تحت الگوی دسترسی مورد انتظار تست می‌شود.

اجرای Foreign Key روی هر اتصال پایگاه داده فعال است.

محدودیت‌های رابطه Parent/Chunk اجرا می‌شوند.

محدودیت‌های وضعیت و فیلدهای وابسته به نوع رکورد اجرا می‌شوند.

ایندکس‌های الزامی وجود دارند.

Payloadهای پایدار Outbox پس از راه‌اندازی مجدد فرآیند در دسترس باقی می‌مانند.

رکوردهای رزرو و مصرف Pacing قابل ردیابی به رکوردهای Chunk مرتبط با خود هستند.

مقدار next_attempt_at برای Jobهای RETRY_WAIT پس از Restart قابل بازیابی است.

مقدار fencing_token برای Jobها و Chunkها همیشه معتبر و غیر NULL است.

پاس شدن این تست‌ها قبل از اتکا به پایگاه داده برای حجم کار تولیدی مربوطه الزامی است.

تست‌های دقیق همزمانی، Atomic Claim، Lock recovery، Lease، Fencing و جریان تراکنش متعلق به Item_12 Part 2 هستند.

۶. خلاصه تغییرات نسخه ۱.۳

تغییرات نسبت به نسخه ۱.۲:

افزودن Jobs.next_attempt_at برای ذخیره زمان تلاش بعدی Jobهای RETRY_WAIT.

الزام NOT NULL DEFAULT 0 برای Jobs.fencing_token.

الزام NOT NULL DEFAULT 0 برای Outbox.fencing_token در رکوردهای CHUNK.

شفاف‌سازی اینکه lease_until برای Parent همیشه NULL است و برای Chunk تا زمان Claim می‌تواند NULL باشد.

شفاف‌سازی اینکه fencing_token برای Parent همیشه NULL و برای Chunk همیشه غیر NULL است.

الزام به ارجاع Pacing_State به رکورد CHUNK، نه Parent.

شفاف‌سازی اجرای محدودیت‌های Parent/Chunk و روابط Pacing در سطح پایگاه داده.

افزودن ایندکس Jobs(status, next_attempt_at).

اصلاح ایندکس Pacing برای پشتیبانی از بررسی زمان مصرف رزروها.

معماری چهار جدولی موجود، مدل Job، مدل Subscriber، مدل Outbox، مالکیت وضعیت‌ها و مرزهای مسئولیت Item_10، Item_11 و Package D حفظ شده‌اند.

وضعیت: PROPOSED
اقدام بعدی: AM (ایجنت منیجر) برای بررسی و تأیید Item_12 Part 1 v1.3 قبل از LOCK.
موارد باز: اعتبارسنجی NFS/File Locking در Stage B؛ Item_12 Part 2.


