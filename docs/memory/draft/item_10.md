# draft item_10 — پیش‌نویس تأییدنشده، قاعده نیست
Source: docs/B_items/Item_10_Error.md (242 خط) | Extracted: 2026-11-21 | وضعیت سند: APPROVED (v1.0، ۱۱ نوامبر ۲۰۲۶)

## ادعاهای سند (به ترتیب بخش‌ها)
- [§0] هدف: لایه واکنش (Reaction Layer) به خطاها؛ B14/Item_09 لایه پیشگیری؛ هرگز Retry کورکورانه
- [§0] In scope: تاکسونومی خطا (۱۰ دسته)، Retry/Backoff (exponential + Jitter)، Ban (418) handling، Rate Limit (429)، Data State Mapping، Data Validation
- [§0] Out of scope: Rate limit values (Item_09)، Cache/retention (Item_11)، Logging storage/rotation (Item_12)، Alert delivery (Package D)، Alarm cooldown persistence (Item_12)
- [§1] ۱۰ دسته خطا: شبکه/اتصال (Retry محدود)، Timeout ۵/۱۰s (Retry)، 429 (Parse Retry-After)، 5xx (Retry)، 418/403 (توقف+بک‌آف تطبیقی+آلارم)، 401 (بدون Retry، آلارم Owner)، 400 (بدون Retry، لاگ، پچ ۱)، 404 (بدون Retry، علامت‌گذاری Pair)، Invalid Data (رد+INVALID، بدون Cache)، Program Error (Traceback)
- [§1 پچ ۱] Coinbase 400 ممکن است "too many"/"range" باشد → split window به ۶ ماهه و retry
- [§2.1] Retry table: شبکه/Timeout/5xx: ۳ تلاش، base×2^attempt+jitter؛ 429 مشروط؛ 418: ۰؛ 400/401/404: ۰؛ Invalid data: ۲ تلاش؛ Program error: ۰
- [§2.2] فرمول Backoff: delay = base_seconds × 2^attempt + jitter (jitter 0.5-1.5، base=1، attempt ∈ {0,1})
- [§2.3] قانون طلایی: هیچ Retry نباید Rate Limiter را دور بزند؛ هر تلاش = درخواست جدید از فیلتر Rate Limiter مشترک
- [§2.3 پچ ۲] Pacing > Retry برای صرافی‌های بدون هدر RL (OKX, Bitstamp, Crypto.com)
- [§3.1] 418: Retry-After موجود → صبر طبق هدر؛ بدون هدر → Adaptive Backoff [1h,2h,4h,8h,16h,32h] (cap 48h) + Safe Probe؛ سقف ۴۸ ساعت → تعلیق صرافی + آلارم Owner
- [§3.2] 429: Retry-After → صبر طبق هدر؛ بدون هدر → Backoff کوتاه (5s,15s,60s)؛ هماهنگی با Item_09
- [§3.3] آلارم: Telegram (اصلی) + Email (پشتیبان)؛ Cooldown: رخداد اول فوری، بعدی Summary هر ۱ ساعت، رفع → پیام بازگشت؛ Storage Item_12
- [§4] Error→Data State Mapping: موفق+معتبر=FULL؛ موفق+ناقص=PARTIAL؛ Retry×3 موفق=FULL؛ Retry×3 شکست=UNAVAILABLE؛ 418=UNAVAILABLE (موقت)؛ 429 پس از retries=UNAVAILABLE (موقت)؛ 401/403=UNAVAILABLE؛ 400 Coinbase split=PARTIAL؛ 400 سایر=UNAVAILABLE؛ 404=UNAVAILABLE؛ Invalid data=UNAVAILABLE (INVALID)؛ BTC/BTC=N_A
- [§5.1] اعتبارسنجی ساختاری: JSON سالم، فیلدهای الزامی (Item_08 §3)، schema_version شناخته‌شده
- [§5.2] اعتبارسنجی معنایی: High>=Low، High>=Open/Close، Low<=Open/Close، Volume>=0، Price>0
- [§5.3 پچ ۳] Parse قبل از Validation: Adapter parse (ExchangeCandleSchema) → Canonical Candle → semantic validation → INVALID → UNAVAILABLE
- [§6] Logging: DEBUG/INFO/WARNING/ERROR/CRITICAL؛ فیلدهای اجباری: timestamp_utc, run_id, exchange, endpoint, attempt, http_status, duration_ms, action؛ توکن‌ها/API Keys هرگز لاگ نمی‌شوند
- [§7] Boundaries: Error taxonomy/Retry/Backoff/418/429/Alarm trigger ✅؛ Alarm cooldown storage/Log storage/Rate limit values/Pacing tokens/Data State vocab خارج
- [§8] Open Questions: ۱ RESOLVED (OKX 429 هدر ندارد)، ۲ P2 (Coinbase 400 pattern، Stage B)، ۳ RESOLVED (418 cap 48h)، ۴ RESOLVED (Alarm cooldown 1h)، ۵ P2 (Safe Probe endpoint، Item_01 adapter)، ۶ RESOLVED (Invalid data retry: ۲)
- [§9] MVP-First: Reuse B15 taxonomy، Retry ۳ تلاش، Exponential backoff+Jitter، 418 توقف+آلارم، 429 Retry-After/backoff، Coinbase 400 split window، Pacing>Retry، Parse قبل از validation
- [§10] Test Requirements: Unit (taxonomy, Jitter, رد INVALID، عدم Retry دائمی)، Integration (Rate Limiter، 429/418)، Concurrency، Logging/Alarm، Smoke (418 mock)، Patch 3 (Coinbase ترتیب معکوس)

## سؤال‌های باز و TODOهای خود سند
- Coinbase 400 pattern: P2 (Stage B test)
- Safe Probe endpoint: P2 (Item_01 adapter)

## تکیه بر تصمیم/Item دیگر
- Item_08 (Data States)، Item_09 (Rate Limits)، Item_11 (Pacing/Queue)، Item_12 (Logging storage/Alarm cooldown)، Item_16 (OHLCV parse)، Item_01 (adapter)، Package D (Alert delivery)

## چک کامل بودن
بخش‌های سند: 11 (Section 0-10) | در خلاصه: 11 | ردشده با دلیل: هیچ
EOF