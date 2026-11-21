# draft item_12 — پیش‌نویس تأییدنشده، قاعده نیست
Source: docs/B_items/Item_12_Part1-3.md (274+194+150 خط) | Extracted: 2026-11-21 | وضعیت سند: PROPOSED (v2.2/v2.1/v2.1)

## ادعاهای سند (به ترتیب بخش‌ها)
- [P1§0] مسئولیت: جداول، فیلدها، PK/FK/Constraints/Indexes؛ فراهم‌کردن ساختار پایدار برای Item_11
- [P1§1] SQLite روی NFS (PythonAnywhere): WAL ممنوع، Rollback Journal Mode، تراکنش‌های کوتاه، busy_timeout 5000ms، Single-writer assumption (A4)
- [P1§2] ۴ جدول: Jobs, Subscribers, Outbox, Pacing_State
- [P1§2.1] Jobs: job_id (PK), job_type (SCANNER/FETCH), normalized_payload, payload_hash, status, not_before, lease_until, fencing_token (NOT NULL DEFAULT 0), next_attempt_at, created_at, updated_at
- [P1§2.2] Subscribers: request_id (PK), job_id (FK), user_id, status (WAITING/COMPLETED/FAILED), created_at
- [P1§2.3] Outbox: message_id (PK), record_type (PARENT/CHUNK), parent_id (FK), chunk_index, request_id (FK اختیاری), user_id, priority (HIGH/LOW), payload_text, status, telegram_message_id, retry_count, next_attempt_at, lease_until, fencing_token, created_at, updated_at
- [P1§2.3] Parent: parent_id=NULL, chunk_index=NULL, lease_until=NULL, fencing_token=NULL
- [P1§2.3] Chunk: parent_id و chunk_index NOT NULL, fencing_token NOT NULL DEFAULT 0
- [P1§2.4] Pacing_State: reservation_id (PK), chunk_message_id (FK→CHUNK), token_key (GLOBAL/USER_{id}), reserved_at, expires_at, used_at, status (ACTIVE/USED/EXPIRED)
- [P1§3] Constraints: PK NOT NULL (SQLite TEXT PK پیش‌فرض NULL)، FK enforcement (PRAGMA foreign_keys=ON)، CHECK status/record_type/priority/token_key، UNIQUE(parent_id,chunk_index)، Trigger برای Parent/Chunk و Pacing_State→CHUNK
- [P1§3.4] Indexes: Jobs (status,not_before),(job_type,payload_hash,status),(status,next_attempt_at)؛ Subscribers (job_id)؛ Outbox (status,priority,next_attempt_at),(parent_id,chunk_index),(request_id)؛ Pacing_State (token_key,status,expires_at),(chunk_message_id),(token_key,status,used_at)
- [P1§5] Stage B validation: 10 مورد (Rollback Journal Mode، File Locking، FK، Parent/Chunk constraints، status/type constraints، indexes، Payload durability، Pacing traceability، next_attempt_at recovery، fencing_token validity)
- [P1§6] زمان: JSON ISO 8601 Z، SQLite Unix ms INTEGER
- [P1§6] مهاجرت: Drop and Recreate (v1.3 هرگز production نبود)
- [P2§1] تراکنش: BEGIN IMMEDIATE (نه DEFERRED)، تراکنش‌های کوتاه، busy_timeout=5000ms، WAL ممنوع، Rollback Journal Mode
- [P2§2] Atomic Claim: شرایط QUEUED (not_before NULL/فرا رسیده)، RUNNING (lease منقضی)، RETRY_WAIT (next_attempt_at فرا رسیده)؛ مراحل BEGIN IMMEDIATE → SELECT → UPDATE (status RUNNING, lease_until +120s, fencing_token+1, updated_at) → COMMIT → changes()=1
- [P2§2] Fencing Token: مقدار اولیه 0، +1 هر Claim، Worker باید حفظ کند، تمام نوشتن‌ها WHERE job_id+fencing_token؛ Fencing از ثبت نتیجه قدیمی جلوگیری می‌کند اما عملیات شبکه‌ای قبلاً انجام‌شده را لغو نمی‌کند
- [P2§2] Chunk Atomic Claim: Outbox CHUNK، BEGIN IMMEDIATE، UPDATE status SENDING + lease_until + fencing_token + updated_at، شرط WHERE PENDING/RETRY_WAIT (next_attempt_at رسیده) + fencing_token معتبر
- [P2§3] Atomic Pacing Reservation: BEGIN IMMEDIATE → بررسی ظرفیت Global و User → بررسی ACTIVE (منقضی نشده) و USED (used_at بازه) → ثبت ۲ رکورد (GLOBAL + USER_{id}) ACTIVE → COMMIT؛ اگر یکی قابل ثبت نباشد هیچ‌کدام
- [P2§3] ترتیب: Reserve → Claim → Send (الزامی)؛ Reserve→Claim fail: رزروها EXPIRED (R-05، اتلاف جزئی پذیرفته)؛ retry_count در این حالت افزایش نمی‌یابد
- [P2§3] R-06: UPDATE Pacing_State SET status='USED', used_at=? WHERE reservation_id=? AND status='ACTIVE'؛ changes()=1
- [P2§4] Recovery: قبل از فعال شدن Worker/Dispatcher؛ Jobs RUNNING با lease منقضی → RETRY_WAIT + next_attempt_at (Item_10)؛ Outbox SENDING → DELIVERY_UNKNOWN (P2-7: retry_count افزایش نمی‌یابد)؛ Pacing_State ACTIVE با expires_at گذشته → EXPIRED؛ Recovery قابل اجرای مجدد، تراکنش‌های کوتاه، بدون عملیات شبکه‌ای
- [P3§0] 5m هرگز در Google Drive ذخیره نمی‌شود (فقط RAM)؛ تبدیل 5m→15m و آپلود بر عهده Item_14
- [P3§1] فرمت آرایه‌ای: [Timestamp, Open, High, Low, Close, Volume] (حذف فیلدهای تکراری، کاهش ۴۰٪)
- [P3§1] Gzip compression قبل از آپلود (کاهش ۷۰٪ دیگر)؛ mtime=0 برای deterministic
- [P3§2] 15m تایم‌فریم پایه ذخیره‌سازی (9 سال، 5 صرافی ~1.5GB)؛ 15m native در همه صرافی‌ها
- [P3§2] دلیل تبدیل 5m→15m محلی: Rate Limit (C-01x) و Consistency (مرز کندل یکسان)
- [P3§2] 5m تاریخی >1 روز در MVP پشتیبانی نمی‌شود
- [P3§3] ساختار پوشه: /data/{15m,1h,1d,supply}/{exchange}/YYYY/MM/YYYY-MM-DD.json.gz
- [P3§3] 15m توسط Item_14 ساخته/آپلود؛ 1h/1d توسط Item_16 on-demand از 15m ساخته/کش؛ زنجیره‌سازی 1h→1d ممنوع
- [P3§3] Cache Invalidation: کلید (exchange,timeframe,date)؛ source_hash=SHA-256(فایل 15m)؛ تغییر source_hash → cache 1h/1d باطل
- [P3§4] بودجه: 15m ~1.5GB (9 سال)، 1h ~1GB، 1d ~50MB، Supply ~5MB، Snapshots 30 روز ~500MB؛ جمع ~3GB از 15GB
- [P3§4] Finalize روز: Item_14 در 00:00-00:05 روز بعد، فایل 15m روز قبل را finalize؛ اگر Cron خارج از پنجره، idempotent rewrite
- [P3§4] Snapshots: SHA-256 هر فایل روزانه + متادیتای نسخه + تاریخچه تغییرات (Item_30 تعریف می‌کند)
- [P3§5] فرمت فایل روزانه: data = آرایه کندل‌ها [Timestamp,O,H,L,C,V]؛ _metadata = {expected_candles, actual_candles, coverage, missing_indices, source_hash, finalized_at}
- [P3§5] coverage = {expected, actual, missing_indices}; کندل گمشده = null (نه صفر)
- [P3§5] _metadata هرگز NULL ندارد؛ برای غیرقابل محاسبه از "N/A"
- [P3§6] مرز مسئولیت‌ها: ساختار پوشه/فرمت Item_12؛ فشرده‌سازی/تبدیل آرایه Item_14/Package A؛ Google Drive API Package A؛ زمان‌بندی آپلود Item_14؛ ساخت 1h/1d on-demand Item_16

## سؤال‌های باز و TODOهای خود سند
- File Locking روی NFS: Stage B (P1§1)
- Multi-Dispatcher روی SQLite/NFS: تا تأیید Stage B اعتبارسنجی نشده (P1§1)
- GitHub Actions به عنوان Executor: مشروط (P3§3)
- SAFE_PROBE endpoint: Item_01 adapter (پچ ۱ Coinbase 400)
- Payload durability و Recovery: Stage B

## تکیه بر تصمیم/Item دیگر
- Item_11 (Queue/Pacing/Outbox State Machine)، Item_10 (Error/Retry/Backoff)، Item_09 (Rate Limit)، Item_16 (OHLCV/Cache Invalidation)، Item_14 (Collector/Finalize)، Item_30 (Snapshot)، Package A (زیرساخت)، Package D (Telegram delivery)

## چک کامل بودن
بخش‌های سند: Part1: 7 بخش، Part2: 6 بخش، Part3: 6 بخش | در خلاصه: تمام بخش‌ها پوشش داده شد | ردشده با دلیل: هیچ
EOF