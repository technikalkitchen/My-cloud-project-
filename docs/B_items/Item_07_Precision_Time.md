# Item_07_Precision_Time.md — Precision & Time

تاریخ: ۱۱ نوامبر ۲۰۲۶
نسخه: v1.0
وضعیت: APPROVED
Legacy: B12_Master (Time)، B13_Master (Decimal) — هر دو LOCKED
منابع حقیقت: B12 + B13 + TEST_MAP v3.4.5 (A4 CLOSED) + Item_08 §2/§3

---

## Section 0 — Purpose & Scope

**هدف:** تعریف قوانین اعداد اعشاری (Decimal) و زمان (UTC/ISO 8601) در کل پروژه. این Item_07 «قانون» است؛ Item_16 (OHLCV) و Item_18 (Price) «اجراکننده» هستند.

**In scope:**
- Decimal (ممنوعیت Float) برای قیمت/ساپلای/حجم
- UTC به عنوان استاندارد ذاتی
- ۴ فرمت Timestamp و تبدیل به canonical
- Rounding policy (کجا و چطور)
- Storage types در SQLite (TEXT / INTEGER)

**Out of scope:**
- Parse JSON → Item_16 (adapter)
- DB schema → Item_12
- Candle aggregation → Item_06
- OHLCV format per exchange → Item_08 §3 (raw format)

---

## Section 1 — Decimal (ممنوعیت Float)

### 1.1 — قانون طلایی (B13 §1)

> **هیچ عدد حساسی (قیمت، ساپلای، حجم، مارکت‌کپ) نباید از `float` عبور کند.**

**دلایل:**
- Float دقت محدود دارد (53-bit mantissa ≈ 15-16 رقم اعشار)
- خطای انباشتی در محاسبات (e.g., `0.1 + 0.2 != 0.3`)
- برای MC و Dominance (Items 25, 29) خطاها تشدید می‌شوند

**اعداد حساس (حریم مطلق):**
- قیمت (open, high, low, close)
- ساپلای (circulating, total)
- حجم (volume, turnover)
- مارکت‌کپ (total, per asset)
- Dominance (درصد)

**اعداد غیرحساس (Float مجاز):**
- تأخیر شبکه (ms)
- نسبت‌های تقریبی (coverage_ratio ≈ 0.95)
- Jitter در Backoff (Item_10)

### 1.2 — ذخیره‌سازی JSON (B13 §2)

- قیمت‌ها در JSON **همیشه** به صورت **String**: `"998.32"`
- ساپلای به صورت **String** یا **Integer**: `"16077337"` یا `16077337`
- حجم به صورت **String**: `"1234.56"`
- در Python: `Decimal("998.32")` (نه `float`)

**قانون Item_08 §3.2:** قیمت در canonical candle String است (نه float).

### 1.3 — دقت (Decimal places)

| نوع داده | دقت | مثال |
|---|---|---|
| قیمت (USDT) | ۸ رقم اعشار | `"998.32000000"` |
| قیمت (BTC) | ۱۰ رقم اعشار | `"0.0001234567"` |
| ساپلای | ۰-۲ رقم (integer یا 2 اعشار) | `16077337` / `"16077337.50"` |
| حجم (Base) | ۸ رقم | `"1234.56789012"` |
| حجم (Quote) | ۲ رقم | `"1234567.89"` |
| Dominance (%) | ۴ رقم | `"42.3456"` |

**قاعده:** دقت ذخیره‌سازی = دقت منبع (صرافی) — نه کمتر، نه بیشتر.

### 1.4 — پچ ۱ — Coinbase Float Trap

> **کشف A4:** Coinbase تنها صرافی است که قیمت را به صورت **float** برمی‌گرداند (بقیه String).

**قانون اجباری:**

```python
import json
from decimal import Decimal

# CORRECT (Decimal preserves precision):
data = json.loads(response, parse_float=Decimal)
```

پیامد برای Item_16: Adapter Coinbase باید `parse_float=Decimal` استفاده کند. در غیر این صورت، قیمت‌های Coinbase با دقت کمتر از بقیه صرافی‌ها ثبت می‌شوند.

اثر روی محاسبات:
- Item_25 (Kitchen MC): خطای ~1e-15 (انباشتی)
- Item_29 (Dominance): اگر یک صرافی خطا داشت، مجموع ≠ 100%
- Item_27 (Ranking): در مرزهای رقابتی می‌تواند رتبه را جابه‌جا کند

---

## Section 2 — Time (UTC & ISO 8601)

### 2.1 — قانون طلایی (B12 §1)

**UTC تنها منطقه زمانی مجاز در سیستم است.** تمام محاسبات، مقایسه‌ها، و ذخیره‌سازی بر UTC.

مناطق ممنوع:
- Tehran local (فقط در UI)
- Server local time (Codespace UTC است ولی نباید فرض شود)
- Exchange local time (OKX از UTC+8 استفاده می‌کند ولی API UTC برمی‌گرداند)

### 2.2 — فرمت نمایش (JSON)

قانون Item_08 §2: زمان در JSON = **ISO 8601 با suffix Z**.
مثال: `"2026-11-11T18:30:00Z"` (نه `+00:00`، نه `Z` بدون `T`).
نگه‌داری: دقت تا ثانیه (milliseconds فقط در storage).

### 2.3 — ۴ فرمت Timestamp (کشف A4)

| صرافی | unit | type | مثال |
|---|---|---|---|
| Binance | ms | int | 1483228800000 |
| Crypto.com | ms | int | 1483228800000 |
| OKX | ms | str | "1483228800000" |
| Bybit | ms | str | "1483228800000" |
| Coinbase | s | int | 1483228800 |
| Bitstamp | s | str | "1483228800" |

**قانون تبدیل (پچ ۲):**

```python
def normalize_timestamp(ts_raw, exchange):
    if isinstance(ts_raw, str):
        ts = int(ts_raw)
    else:
        ts = ts_raw
    
    if exchange in ('coinbase', 'bitstamp'):
        ts *= 1000
        
    assert 1_230_768_000_000 < ts < 2_145_916_800_000, f"ts out of range: {ts}"
    return ts
```

**قاعده اجباری:**
- فقط `timestamp_ms` (int, ms) در Canonical Candle (Item_08 §3.2)
- تبدیل فقط در adapter layer (Item_16)
- در JSON خروجی نهایی → ISO 8601 Z

### 2.4 — Parsing ISO 8601 (B12 §2)

```python
from datetime import datetime, timezone
dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
assert dt.tzinfo == timezone.utc, "must be UTC"
```
ممنوع: `datetime.strptime()` که timezone را نادیده بگیرد.

### 2.5 — Time-zone Conversion (Edge Case)

وضعیت: A4 نشان داد همه ۶ صرافی UTC برمی‌گردانند. این edge case فعلاً استفاده نمی‌شود — ثبت به عنوان `RESOLVED` (تأیید A4).

---

## Section 3 — Rounding & Storage

### 3.1 — Rounding Policy

قانون طلایی: تا زمانی که ممکن است هیچ rounding انجام نده. فقط در لحظه نمایش (UI) گرد کن.

| مرحله | Rounding | دلیل |
|---|---|---|
| Ingestion (Adapter) | ❌ هیچ | حفظ دقت منبع |
| Canonical Candle | ❌ هیچ | String کامل |
| Aggregation (Item_06) | ❌ هیچ | Decimal math |
| MC/Dominance (Item_25/29) | ⚠️ فقط در خروجی | ۴ رقم اعشار |
| JSON خروجی B→C | ⚠️ String با دقت کامل | Item_08 §3.2 |
| UI نمایش | ✅ گرد کردن | خوانایی |

الگوریتم: `ROUND_HALF_EVEN` (Banker's Rounding).

### 3.2 — پچ ۳ — SQLite Storage Types

هماهنگی با Item_12 v2.2:

| نوع داده | SQLite Type | چرا |
|---|---|---|
| قیمت (Decimal) | **TEXT** | حفظ precision |
| ساپلای (Integer) | INTEGER | اگر integer کامل باشد |
| ساپلای (Decimal) | **TEXT** | اگر ۲ رقم اعشار لازم |
| Timestamp | INTEGER (ms) | مقایسه + range query |
| Volume (Decimal) | **TEXT** | مثل قیمت |

**چرا TEXT برای Decimal:** SQLite REAL = IEEE 754 (مثل float). تنها راه حفظ Decimal، ذخیره به صورت TEXT است.

### 3.3 — Serialization JSON

```python
import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

json.dumps({"price": Decimal("998.32")}, cls=DecimalEncoder)
# → '{"price": "998.32"}'
```

---

## Section 4 — Boundaries

| موضوع | Item_07 | آیتم دیگر |
|---|---|---|
| Decimal rule | ✅ تعریف | همه اجرا می‌کنند |
| UTC rule | ✅ تعریف | همه اجرا می‌کنند |
| ۴ format Timestamp | ✅ جدول تبدیل | Item_16 اجرا |
| parse_float=Decimal | ✅ قانون | Item_16 adapter |
| ISO 8601 Z در JSON | ✅ (با Item_08) | Item_08 format |
| SQLite storage type | ✅ تعریف | Item_12 impl |
| Candle OHLCV format | ❌ | Item_08 §3 |
| Rounding در محاسبات MC | ❌ | Item_25/29 اجرا |
| UI rounding | ❌ | Package D |

---

## Section 5 — Open Questions (PENDING)

| # | سؤال | وضعیت (۱۱ Nov) |
|---|---|---|
| 1 | OKX/Bitstamp/Crypto.com هدر timestamp | ✅ RESOLVED (A4: همه UTC) |
| 2 | دقت ساپلای: Integer یا ۲ رقم | ✅ RESOLVED (TEXT برای حفظ ۲ رقم) |
| 3 | ISO 8601: با `.000Z` یا بدون | ✅ RESOLVED (بدون ms، طبق Item_08) |
| 4 | SQLite PRAGMA | ⏳ DEFERRED (Stage B، Item_12) |
| 5 | Rounding Dominance: ۴ یا ۶ رقم | ✅ RESOLVED (۴ رقم کافی است) |

---

## Section 6 — MVP-First Notes

✅ Decimal برای قیمت/ساپلای/حجم
✅ parse_float=Decimal برای Coinbase
✅ UTC فقط
✅ ISO 8601 Z در JSON
✅ ۴ format Timestamp → ms+int
✅ SQLite: TEXT برای Decimal، INTEGER برای timestamp
✅ Rounding فقط در خروجی

❌ Custom Decimal library
❌ BSON/MessagePack
❌ Fixed-point arithmetic
❌ NTP synchronization
❌ Historical timezone registry

---

## Section 7 — Test Requirements (Stage B)

1. **Unit — Decimal:**
   - `json.loads(coinbase_response, parse_float=Decimal)` → همه float → Decimal
   - `Decimal("0.1") + Decimal("0.2") == Decimal("0.3")`
   - Serialization: `str(Decimal("998.32000000")) == "998.32000000"`
2. **Unit — Timestamp:**
   - ۴ format → ms+int
   - ISO 8601 parse: `"2026-11-11T18:30:00Z"` → UTC datetime
   - Range check: reject pre-Bitcoin و post-int32
3. **Integration — Coinbase:**
   - ۱۰ کندل واقعی Coinbase → parse با `parse_float=Decimal` → assert type == Decimal
4. **Integration — SQLite:**
   - ذخیره `Decimal("998.32")` → SELECT → `"998.32"`
5. **Regression — Aggregation:**
   - 1000 candle × Decimal vs float → اختلاف < 1e-10

---
End of Item_07 v1.0 APPROVED
