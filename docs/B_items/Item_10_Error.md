# Item_10_Error.md — Error Handling & Retry

تاریخ: ۱۱ نوامبر ۲۰۲۶
نسخه: v1.0
وضعیت: APPROVED
Legacy: B15_Master (LOCKED، ۱۸ Oct 2026) — اسکلت اصلی
منابع حقیقت: B15 + TEST_MAP v3.4.5 (A3، A9، A4) + Item_08 §1 (Data States) + Item_09 (Rate Limits)

---

## Section 0 — Purpose & Scope

**هدف:** لایه واکنش (Reaction Layer) به خطاها. B14/Item_09 لایه پیشگیری است (Rate Limit)؛ Item_10 وقتی خطا رخ داد، واکنش کنترل‌شده نشان می‌دهد. **هرگز Retry کورکورانه** که Rate Limit را تشدید کند یا Ban بیاورد.

**In scope:**
- تاکسونومی خطاها (۱۰ دسته)
- Retry/Backoff (exponential + Jitter)
- Ban (418) handling — توقف + آلارم + بک‌آف تطبیقی
- Rate Limit (429) — هماهنگی با Item_09
- Data State Mapping (→ Item_08: UNAVAILABLE/PARTIAL)
- Data Validation (schema + semantic)

**Out of scope:**
- Rate limit **values** (C-001..C-021) → Item_09
- Cache/retention → Item_11
- Logging storage/rotation → Item_12
- Alert delivery (Telegram/Email) → Package D
- Alarm cooldown persistence → Item_12

---

## Section 1 — Error Taxonomy (۱۰ دسته)

| # | دسته | مثال | واکنش |
|---|---|---|---|
| 1 | شبکه/اتصال | ConnectionError, DNS | Retry محدود (Backoff) |
| 2 | Timeout | ۵/۱۰ ثانیه | Retry محدود (Backoff) |
| 3 | Rate Limit | HTTP 429 | Parse Retry-After → sleep → retry (Item_09 هماهنگ) |
| 4 | Server Error | 500, 502, 503 | Retry محدود (Backoff) |
| 5 | Ban/Security | 418, 403 (WAF) | **توقف فوری + بک‌آف تطبیقی + آلارم** |
| 6 | Auth | 401 | بدون Retry، توقف + آلارم Owner |
| 7 | Bad Request | 400 | بدون Retry، لاگ (پچ ۱ پایین) |
| 8 | Not Found | 404 | بدون Retry، علامت‌گذاری Pair |
| 9 | Invalid Data | High < Low، قیمت منفی | رد داده (INVALID)، بدون ورود به Cache (پچ ۳) |
| 10 | Program Error | TypeError, KeyError | Traceback، بدون Retry شبکه‌ای |

**پچ ۱ — Coinbase HTTP 400:**
در B15، 400 = «بدون Retry، لاگ». اما در Coinbase، 400 ممکن است معنی «پنجره درخواست > ۳۰۰ کندل» باشد (A3، A9). واکنش صحیح:
۱. Parse خطا (Coinbase `{"message": "..."}`)
۲. اگر پیام شامل "too many" یا "range" بود ← split window به ۶ ماهه و retry (نه retry کور)
۳. اگر خطای دیگری بود ← بدون Retry، لاگ

---

## Section 2 — Retry & Backoff Strategy

### 2.1 — قواعد پایه (از B15)

| نوع خطا | Retry؟ | سقف | فاصله |
|---|---|---|---|
| شبکه | ✅ | ۳ تلاش (۱ + ۲ retry) | `base × 2^attempt + jitter` |
| Timeout | ✅ | ۳ تلاش | همان |
| 5xx | ✅ | ۳ تلاش | همان |
| 429 | مشروط | بسته به Retry-After | Retry-After یا Backoff |
| 418 | ❌ | ۰ | تعلیق کامل (Section 3) |
| 400, 401, 404 | ❌ | ۰ | لاگ/آلارم |
| Invalid data | مشروط | ۲ تلاش | فقط برای دریافت مجدد |
| Program error | ❌ | ۰ | Traceback |

### 2.2 — فرمول Backoff

delay(attempt) = base_seconds × 2^attempt + jitter_seconds
jitter_seconds = random.uniform(0.5, 1.5)
base_seconds = 1
attempt ∈ {0, 1}

**نمونه:**
- Attempt 0 (اولیه): اجرا
- Attempt 1 (retry 1): delay = 1×2^0 + [0.5-1.5] = [1.5, 2.5]s
- Attempt 2 (retry 2): delay = 1×2^1 + [0.5-1.5] = [2.5, 3.5]s

### 2.3 — قانون طلایی (B15 §5)

**هیچ Retry نباید Rate Limiter را دور بزند.** هر تلاش مجدد یک درخواست جدید است و باید از فیلتر Rate Limiter مشترک (Item_09 + Item_11 Queue) عبور کند.

**پچ ۲ — Pacing > Retry (OKX و صرافی‌های بدون هدر RL):**
در صرافی‌هایی که هدر `X-RateLimit-*` ندارند (OKX، Bitstamp، Crypto.com — از A2)، لایه پیشگیری (Pacing، Item_11) همیشه باید بر لایه واکنش (Retry) اولویت داشته باشد.

---

## Section 3 — Ban (418) و Rate Limit (429)

### 3.1 — 418 (Ban / Security Block)

| سناریو | اقدام |
|---|---|
| هدر `Retry-After` موجود | صبر دقیقاً طبق هدر |
| بدون هدر | Adaptive Backoff with Safe Probing |
| سقف نهایی | ۴۸ ساعت، بعد آن صرافی تعلیق + آلارم Owner |

**Adaptive Backoff (بدون هدر):**
wait_sequence = [1h, 2h, 4h, 8h, 16h, 32h] (مجموع = 63h ← cap at 48h)
بعد از هر انتظار ← Safe Probe (درخواست سبک مثل `GET /api/v1/time`). اگر 200 ← بازگشت. اگر 418 مجدد ← انتظار بعدی.

### 3.2 — 429 (Rate Limit)

- هدر `Retry-After` موجود ← صبر دقیقاً طبق هدر
- بدون هدر ← Backoff کوتاه (5s, 15s, 60s)
- هماهنگی با Item_09: 429 سیگنال است که Pacing کافی نبوده. کاهش rate موقت.

### 3.3 — آلارم‌ها (B15 §1.1)

**کانال اصلی:** Telegram. **پشتیبان:** Email.
**Cooldown (B15 §1.3):** رخداد اول ← آلارم فوری. رخدادهای بعدی ← Summary هر ۱ ساعت. رفع مشکل ← پیام بازگشت به حالت عادی.
**Storage:** Item_12 (SQLite).

---

## Section 4 — Error → Data State Mapping

اتصال به Item_08 (Data States):

| سناریو | Result State | توضیح |
|---|---|---|
| درخواست موفق + داده معتبر | **FULL** | — |
| درخواست موفق + داده ناقص | **PARTIAL** | `coverage_ratio` + `missing_ranges` |
| Retry × ۳ موفق | **FULL** | state پایانی |
| Retry × ۳ شکست (شبکه/5xx) | **UNAVAILABLE** | + ثبت در provenance |
| 418 Ban | **UNAVAILABLE** (موقت) | + صرافی معلق + آلارم |
| 429 پس از retries | **UNAVAILABLE** (موقت) | + کاهش pacing |
| 401/403 | **UNAVAILABLE** | + آلارم Owner |
| 400 (Coinbase window) | **PARTIAL** (پس از split) | با پنجره کوچک‌تر retry |
| 400 (سایر) | **UNAVAILABLE** | — |
| 404 | **UNAVAILABLE** | pair علامت‌گذاری |
| Invalid data | **UNAVAILABLE** | provenance: `validation_status: INVALID` |
| BTC/BTC (semantic) | **N_A** | Item_08 §1 |

---

## Section 5 — Data Validation

### 5.1 — اعتبارسنجی ساختاری (B15 §6.1)
- JSON سالم (parse موفّق)
- فیلدهای الزامی طبق Item_08 Section 3
- `schema_version` شناخته‌شده

### 5.2 — اعتبارسنجی معنایی

| چک | قاعده | واکنش |
|---|---|---|
| High >= Low | ✅ | رد + INVALID |
| High >= Open, Close | ✅ | رد + INVALID |
| Low <= Open, Close | ✅ | رد + INVALID |
| Volume >= 0 | ✅ | رد + INVALID |
| Price > 0 | ✅ | رد + INVALID |

### 5.3 — پچ ۳ (A4) — ترتیب Parse قبل از Validation

مشکل: B15 می‌گوید «High < Low ← رد داده». اما A4 کشف کرد Coinbase ترتیب OHLC را `[ts, LOW, HIGH, OPEN, close, vol]` برمی‌گرداند.
اگر بدون parse صحیح اعتبارسنجی شود، High و Low جابجا شده و false positive می‌دهد.

**قاعده صریح:**
۱. Adapter ابتدا parse طبق ExchangeCandleSchema (Item_08 §3.1)
۲. تبدیل به Canonical Candle (Item_08 §3.2)
۳. سپس اعتبارسنجی معنایی (این Section)
۴. اگر validation fail ← INVALID ← رد + لاگ + `UNAVAILABLE`

---

## Section 6 — Logging (B15 §7)

| Level | کِی |
|---|---|
| DEBUG | جزئیات تست |
| INFO | درخواست موفق، Cache hit، بازیابی از retry |
| WARNING | Retry، 429، داده INVALID اولیه |
| ERROR | شکست نهایی، داده ردشده |
| CRITICAL | 418، توقف صرافی، خرابی سیستم |

**فیلدهای اجباری:** `timestamp_utc, run_id, exchange, endpoint, attempt, http_status, duration_ms, action`
**امنیت:** توکن‌ها، API Keys هرگز لاگ نمی‌شوند.

---

## Section 7 — Boundaries

| موضوع | Item_10 | آیتم دیگر |
|---|---|---|
| Error taxonomy | ✅ | — |
| Retry/Backoff formula | ✅ | — |
| 418/429 handling | ✅ | — |
| Alarm trigger | ✅ | Package D (delivery) |
| Alarm cooldown storage | ❌ | Item_12 |
| Log storage/rotation | ❌ | Item_12 |
| Rate limit values | ❌ | Item_09 |
| Pacing tokens | ❌ | Item_11 |
| Data State vocab | ❌ (استفاده) | Item_08 |

---

## Section 8 — Open Questions

| # | سؤال | وضعیت (۱۱ Nov) |
|---|---|---|
| 1 | OKX 429 هدر Retry-After دارد؟ | ✅ RESOLVED (A2: ندارد ← Pacing) |
| 2 | Coinbase 400 pattern? | ⏳ P2 (Stage B test) |
| 3 | 418 Backoff cap 48h؟ | ✅ RESOLVED (B15 §1.2) |
| 4 | Alarm cooldown 1h؟ | ✅ RESOLVED (B15 §1.3) |
| 5 | Safe Probe endpoint? | ⏳ P2 (Item_01 adapter) |
| 6 | Invalid data retry: 2 یا 3؟ | ✅ RESOLVED (۲ تلاش کافی است) |

---

## Section 9 — MVP-First Notes

✅ Reuse B15 taxonomy کامل (۱۰ دسته)
✅ Retry فقط ۳ تلاش (نه بی‌نهایت)
✅ Exponential backoff + Jitter (simple)
✅ 418: توقف + آلارم (نه retry)
✅ 429: Retry-After یا backoff
✅ Coinbase 400: split window (نه retry کور)
✅ Pacing > Retry (پچ ۲)
✅ Parse قبل از validation (پچ ۳)

❌ Circuit breaker پیشرفته
❌ Multi-tier retry
❌ Error aggregation analytics
❌ Chaos engineering

---

## Section 10 — Test Requirements (Stage B)

1. Unit: taxonomy mapping، Jitter، رد INVALID، عدم Retry دائمی
2. Integration: Rate Limiter پاس شود، 429/418 متوقف
3. Concurrency: عدم قفل بی‌دلیل صرافی‌های دیگر
4. Logging/Alarm: عدم نشت secret، deduplication
5. Smoke: 418 mock (بدون Ban واقعی)
6. Patch 3 test: BTC-USD Coinbase ترتیب معکوس ← validation pass (نه false positive)

---
End of Item_10 v1.0 APPROVED
