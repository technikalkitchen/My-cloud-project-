# draft item_11 — پیش‌نویس تأییدنشده، قاعده نیست
Source: docs/B_items/Item_11_Part1-4.md (100+95+114+121 خط) | Extracted: 2026-11-21 | وضعیت سند: PROPOSED (v1.4/v1.5/v1.2/v1.4)

## ادعاهای سند (به ترتیب بخش‌ها)
- [P1§1] دو لایه کش: Live RAM (5m، ۱ روز اخیر، WebSocket، Deque ۲۸۸ کندل) و Persistent Storage (15m/1h/1d، Google Drive، Collector)
- [P1§2] Routing: Expected Layer → Market Status (Not Listed/Unknown/Listed) → Cache Status (Hit/Partial/Miss) → Candle Status (Open/Closed) → Routing (Hit/Partial/Miss)
- [P1§3] مرز: معماری کش Item_11؛ زمان‌بندی Item_14؛ ذخیره‌سازی Item_12؛ TF بالاتر Item_06؛ زیرساخت Package A؛ Outbox Package D؛ OHLCV Item_16
- [P2§1] دو سطح Coalescing: Scanner-level (پنجره ثابت ۵ دقیقه) و Fetch-level (Range Merging برای بازه‌های هم‌پوشان/پیوسته)
- [P2§1] Partial Overlap: بخش موجود subscribe، بخش گمشده Gap-Aware Fetch
- [P2§2] Hashing: Scanner Payload Hash (SHA-256) و Fetch Job Identity (Exchange+Pair+Timeframe + مقایسه Start/End)
- [P2§3] Buffer: Open Candle Buffer (به‌روزرسانی WebSocket) و Closed Candle Deque (فقط کندل بسته در تحلیل نهایی)
- [P2§3] Disconnect: ذخیره آخرین زمان معتبر + Gap-Aware Fetch (HTTP) برای پر کردن
- [P2§4] Subscription Lifecycle: Register → Lookup → Subscribe (با تحویل جزئی) → Completed State → Publish
- [P3§1] Gap-Aware Fetch: Time-to-Candle Conversion بر اساس مرزهای کندل (Item_16)
- [P3§1] Multi-layer Gap Filling: Live RAM → Persistent Storage → HTTP Fetch
- [P3§1] Mandatory Queue Rule: هر HTTP Fetch فقط از طریق Background Queue
- [P3§1] Large Gap Chunking: اندازه Chunk بر اساس سقف صرافی (C-002: ۳۰۰ فقط Binance)
- [P3§2] Background Queue: ظرفیت همزمان ۱ Job (MVP)؛ Drip-feeding؛ Priority High (Default Range) / Low (Custom Range)؛ FIFO در هر سطح؛ Anti-Starvation ۵ High → ۱ Low
- [P3§2] Rate Limit Enforcement پیش از هر درخواست HTTP
- [P3§2] Job Lifecycle: QUEUED, RUNNING, COMPLETED, FAILED, PARTIAL, RETRY_WAIT
- [P3§3] PythonAnywhere: فقط Coordination (نه پردازش سنگین)؛ Executor = GitHub Actions (مشروط، C-011 ASSUMED)
- [P3§4] Not Listed: حذف از صف + ثبت Metadata (Exchange+Pair, وضعیت, زمان آخرین بررسی, منبع) با TTL (Item_16)
- [P3§4] Partial Response: داده موفق ذخیره، گپ باقی‌مانده مجدداً محاسبه
- [P4§1] Outbox State Machine: Parent (PENDING, SENDING, DELIVERED, PARTIAL, RETRY_WAIT, FAILED) و Chunk (PENDING, SENDING, DELIVERED, RETRY_WAIT, DELIVERY_UNKNOWN, FAILED)
- [P4§1] Parent State Precedence: FAILED > DELIVERED > SENDING > RETRY_WAIT > PARTIAL > PENDING
- [P4§2] Pacing: Global ۲۵ پیام/ثانیه، Per-User ۱ ثانیه بین دو پیام تحلیلی (O-2)؛ Atomic reservation
- [P4§2] Anti-Starvation: پس از ۵ HIGH، ۱ LOW
- [P4§3] ترتیب عملیات: ۱۰ مرحله (Package C → Package D → Item_11 Chunking → Outbox → Selection → Pacing → Atomic Claim → Telegram → Result → Record)
- [P4§3] مرز Chunking و Markdown: Package D Payload با نقاط امن تقسیم؛ Item_11 مجاز به تغییر معنا نیست
- [P4§4] Delivery Uncertainty (Timeout): DELIVERY_UNKNOWN → Retry (O-1: Duplicate پذیرفته)
- [P4§4] Telegram 429: Item_10 محدوده اثر و Backoff؛ Item_11 ارسال‌های مشمول را متوقف می‌کند

## سؤال‌های باز و TODOهای خود سند
- WebSocket هم‌زمان ۵ اتصال: Stage B اندازه‌گیری (C-019 OPEN)
- GitHub Actions به عنوان Executor: مشروط (C-011 ASSUMED)
- Reuse Policy برای Completed Job: هنوز تعریف نشده
- Not Listed TTL: در Item_16 تعریف شود

## تکیه بر تصمیم/Item دیگر
- Item_09 (Rate Limit/Pacing)، Item_10 (Error/Retry)، Item_12 (SQLite/Persistence)، Item_16 (OHLCV/Open/Closed Candle)، Item_14 (Cron)، Package A (زیرساخت)، Package D (Telegram delivery/formatting)، Package C (Payload)

## چک کامل بودن
بخش‌های سند: 4 Part (Part1: 3 بخش، Part2: 5 بخش، Part3: 5 بخش، Part4: 5 بخش) | در خلاصه: تمام بخش‌ها پوشش داده شد | ردشده با دلیل: هیچ
EOF