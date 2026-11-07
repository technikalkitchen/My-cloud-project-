# A4 — OHLCV Format per Exchange

- **تاریخ:** ۷ نوامبر ۲۰۲۶ (سشن ۲)
- **هدف:** کشف فرمت پاسخ کندل هر ۶ صرافی
- **وضعیت:** ✅ CLOSED
- **استفاده در:** Item_16 (OHLCV)، Item_07 (Precision)

---

## جدول خلاصه

| صرافی | نوع | ترتیب فیلدها | timestamp | قیمت | جهت | یک call |
|---|---|---|---|---|---|---|
| Binance | list | [ts, o, h, l, c, v, ...] (۱۲ فیلد) | ms (int) | str | صعودی | ✅ |
| OKX | dict.data[] | [ts, o, h, l, c, v, ...] (۹ فیلد) | ms (str) | str | نزولی | ✅ |
| Coinbase | list | [ts, **l, h, o**, c, v] (۶ فیلد) | s (int) | **num** | نزولی | ✅ |
| Bitstamp | dict.data.ohlc[] | {timestamp, open, high, low, close, volume} | s (str) | str | صعودی | ✅ |
| Crypto.com | dict.result.data[] | {t, o, h, l, c, v} | ms (int) | str | صعودی | ✅ |
| Bybit | dict.result.list[] | [ts, o, h, l, c, v, turnover] (۷ فیلد) | ms (str) | str | نزولی | ✅ |

---

## ۵ ناسازگاری حیاتی (پیامد برای Item_16 و Item_07)

### ۱. Coinbase ترتیب OHLC معکوس

`[ts, low, high, open, close, volume]` — نه استاندارد.
اگر Item_16 استاندارد parse کند → کندل خراب.

### ۲. timestamp سه فرمت

- ms+int: Binance, Crypto.com
- ms+str: OKX, Bybit
- s+int: Coinbase
- s+str: Bitstamp

### ۳. Coinbase تنها صرافی با قیمت عددی (float)

بقیه ۵ صرافی رشته می‌دهند. ریسک Decimal در Item_07.

### ۴. جهت کندل — ۳ صعودی، ۳ نزولی

- صعودی: Binance, Bitstamp, Crypto.com
- نزولی: OKX, Coinbase, Bybit

### ۵. فیلدهای اضافی متفاوت

Binance ۱۲، OKX ۹، Bybit ۷، بقیه ۶.

---

## جدول مرجع Item_16 — ExchangeCandleSchema

| صرافی | field_order | ts_unit | ts_type | price_type | direction |
|---|---|---|---|---|---|
| Binance | [ts,o,h,l,c,v,...] | ms | int | str | asc |
| OKX | [ts,o,h,l,c,v,...] | ms | str | str | desc |
| Coinbase | [ts,l,h,o,c,v] | s | int | num | desc |
| Bitstamp | {ts,o,h,l,c,v} | s | str | str | asc |
| Crypto.com | {t,o,h,l,c,v} | ms | int | str | asc |
| Bybit | [ts,o,h,l,c,v,tn] | ms | str | str | desc |

**این جدول، مرجع اجباری Item_16 است.**

---

## پیامدها

- **Item_16** باید `ExchangeCandleSchema` را پیاده کند
- **Item_07** باید `timestamp_unit/type` و `price_type` را ثبت کند
- **TEST_MAP** — Section 16 بعداً اضافه می‌شود (Patcher)

---

**پایان A4 — 2026-11-07**
