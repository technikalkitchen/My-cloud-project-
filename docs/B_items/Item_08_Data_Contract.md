# Item_08_Data_Contract.md — Data Contract

تاریخ: ۱۱ نوامبر ۲۰۲۶
نسخه: v1.0
وضعیت: APPROVED
Legacy: B43, B46, B47, B48 — همه Placeholder خالی
منابع حقیقت: TEST_MAP v3.4.5 (Appendix A-E) + Item_03 §8 + Item_05 §1.3/§3

---

## Section 0 — Purpose & Scope

**هدف:** تعریف قرارداد داده استاندارد که از Package B به Package C تحویل می‌شود.

**In scope:**
- واژگان Data State (FULL, PARTIAL, UNAVAILABLE, N_A, PENDING)
- Candle Schema per exchange
- Provenance Metadata
- Price Path Taxonomy (Direct_USDT, Direct_BTC, Direct_USD_Converted, Implied)
- Supply structure
- B→C JSON interface

**Out of scope:**
- Ranking/Dominance/Coverage → Items 25-27
- Rate limit policy → Item_09
- Cache strategy → Item_11
- SQLite NOT NULL constraints → Item_12 v2.2 (R-07)

---

## Section 1 — Data States

| State | معنی | مثال |
|---|---|---|
| **FULL** | داده کامل و معتبر | BTC/USDT OHLCV کل بازه |
| **PARTIAL** | داده هست ولی ناقص | BTC/USDT با ۳ روز گپ |
| **UNAVAILABLE** | تست شد، داده نیست | BTC/USDT روی OKX قبل از 2018-Q1 |
| **N_A** | بی‌معنی | BTC/BTC، USD/USD |
| **PENDING** | تست نشده، تصمیم‌گیری لازم | ۷ NO_DATA (SPX, XPL, ...) |

**قواعد:**
- `UNAVAILABLE` ≠ `N_A`: اولی تست شد نیست، دومی تست شد بی‌معنی
- `PARTIAL` باید `coverage_ratio` (0.0-1.0) و `missing_ranges` داشته باشد
- `PENDING` موقت است — در یک سشن تبدیل می‌شود
- `PARTIAL` اگر downstream FULL می‌خواهد → escalate

**مرجع متقابل:** presence_status (Item_03 §8) = FULL/PARTIAL/UNAVAILABLE؛ N_A و PENDING مخصوص Item_08

---

## Section 2 — Identity & Versioning

| فیلد | نوع | مثال | منبع |
|---|---|---|---|
| asset_id | string | "BTC" | Item_03 §3 |
| cmc_id | int | 1 | CMC top 150 (Appendix C) |
| coingecko_id | string | "bitcoin" | Item_03 §3 |
| symbol | string | "BTC" | CMC |
| available_from | YYYY-MM-DD | "2017-01-01" | Appendix B |
| listing_dates | object | {"binance": "2017-08-17", "coinbase": "2015-07-20"} | Appendix A |
| policy_date | YYYY-MM-DD | "2023-11-02" | Item_04 (فقط برای بک‌گراند) |
| is_stablecoin | bool | false | Item_03 §4 |
| is_wrapped | bool | false | Item_03 §5 |
| migration | object/null | {"from": "MATIC", "to": "POL", "effective_at": "2024-09-04"} | Item_04 |

**قواعد:**
- `cmc_id` canonical (از CMC top 150، نه final_125_supply — TEST_MAP §2.2.5)
- `available_from` = CMC data limit، نه actual launch (SOL=2021-01-01 = CMC limit)
- `listing_dates` = actual exchange listing از Appendix A (OKX، Binance، Bybit، Coinbase، Bitstamp).
- `policy_date` = فقط برای منطق درون‌سیستمی، در UI نمایش داده نمی‌شود.
- `asset_id` string، نه numeric
- `schema_version: "1.0"` در هر JSON

---

## Section 3 — Candle Schema

### 3.1 — Raw formats (Appendix E، A4 CLOSED)

| صرافی | field_order | ts_unit | ts_type | price_type | direction | count |
|---|---|---|---|---|---|---|
| **Binance** | `[ts,o,h,l,c,v,close_ts,quote_v,trades,taker_base,taker_quote,ignore]` | ms | int | str | asc | 12 |
| **OKX** | `[ts,o,h,l,c,vol,volCcy,volCcyQuote,confirm]` | ms | str | str | desc | 9 |
| **Coinbase** | `[ts,LOW,HIGH,OPEN,close,vol]` | s | int | **num** | desc | 6 |
| **Bitstamp** | `{timestamp,open,high,low,close,volume}` | s | str | str | asc | 6 |
| **Crypto.com** | `{t,o,h,l,c,v}` | ms | int | str | asc | 6 |
| **Bybit** | `[ts,o,h,l,c,v,turnover]` | ms | str | str | desc | 7 |

### 3.2 — Canonical Candle

```json
{
  "timestamp_ms": 1483228800000,
  "open": "998.32",
  "high": "1013.05",
  "low": "990.10",
  "close": "1010.50",
  "volume": "1234.56",
  "exchange": "Binance",
  "quote": "USDT",
  "direction": "asc"
}
```

Normalization:
- timestamp_ms: int, ms (Coinbase/Bitstamp s → ×1000)
- OHLCV: str (Coinbase num → str، دقت ۸ رقم)
- direction: asc (desc → reverse)
- Field order: [ts,o,h,l,c,v] (Coinbase reorder)

3.3 — Critical Gotchas

| Gotcha | قاعده |
|---|---|
| Coinbase field order | `[ts, LOW, HIGH, OPEN, close, vol]` — LOW قبل OPEN |
| Coinbase price float | → `Decimal(str(x))` |
| ۴ timestamp format | `ms+int / ms+str / s+int / s+str` — normalize |
| Direction mix | ۳ asc, ۳ desc — reverse on ingest |
| Extra fields | Binance 12, OKX 9, Bybit 7, بقیه 6 — نادیده |

---

## Section 4 — Provenance & Metadata

### 4.1 — Price Path Taxonomy (Item_05 §1.3)

| Type | تعریف | مثال |
|---|---|---|
| Direct_USDT | XXX/USDT دارد | Binance ETH/USDT |
| Direct_BTC | XXX/BTC + BTC/USDT | Binance ETH/BTC → USDT |
| Direct_USD_Converted | XXX/USD + USDT/USD | Coinbase ETH/USD → USDT |
| Implied | triangular | OKX ETH/BTC via OKX BTC/USDT |
| N_A | بی‌معنی | BTC/BTC |

### 4.2 — Provenance Object

```json
{
  "quote": "USDT",
  "price_path": "Direct_USDT",
  "source_exchange": "Binance",
  "source_pair": "ETH/USDT",
  "conversion_rate_used": null,
  "rate_source": null,
  "rate_effective_time": null,
  "timestamp_ms": 1483228800000,
  "fetched_at": "2026-11-11T18:30:00Z",
  "validation_status": "FULL"
}
```

### 4.3 — Effective Start & Imprecise

```json
{
  "asset": "BTC",
  "exchange": "Coinbase",
  "quote": "USDT",
  "direct_start": null,
  "converted_start": "2021-05-04",
  "effective_min": "2021-05-04",
  "imprecise": false,
  "iterations": 5
}
```

قواعد:
- `direct_start`: اگر Direct موجود
- `converted_start`: max(usd_start, usdt_usd_start)
- `effective_min`: min(direct, converted)
- `imprecise`: true اگر walk-back به max_iter یا count_at_start >= 182

---

## Section 5 — Supply Structure

```json
{
  "BTC": [
    {"date": "2017-01-01", "supply": 16077337, "price": 998.33},
    {"date": "2017-01-02", "supply": 16081234, "price": 1013.05}
  ]
}
```

قواعد:
- Dict keyed by asset_id
- Daily candles، sorted ascending
- Coverage: 117/125 (۷ NO_DATA → PENDING، USD1 → PENDING)
- PROVISIONAL — بعد از رفع ۷ NO_DATA تغییر می‌کند

---

## Section 6 — Aggregate Structures

Market Cap: MC(a,d) = supply(a,d) × price(a,d) — missing → UNAVAILABLE
Dominance: D(a,d) = MC(a,d) / Total_MC(d)
Kitchen Price: KP(a,d) = Σ(w_i × p_i) / Σ w_i — w_i از Item_20+21

---

## Section 7 — B→C Interface

Package B ۴ فایل تحویل می‌دهد:

7.1 — universe.json

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-11-11T18:30:00Z",
  "cmc_snapshot": "cmc_top150_2026-11-08",
  "count": 125,
  "assets": [{"asset_id": "BTC", "cmc_id": 1, "symbol": "BTC", "rank_cmc": 1, "is_stablecoin": false, "is_wrapped": false, "available_from": "2017-01-01", "listing_dates": {"binance": "2017-08-17"}, "policy_date": null, "migration": null, "presence_status": "FULL"}]
}
```

7.2 — prices.json

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-11-11T18:30:00Z",
  "assets": {"BTC": {"exchanges": {"Binance": {"USDT": {"...provenance"}}}, "kitchen_price": [], "effective_min": "2017-08-17"}}
}
```

7.3 — supply.json (Section 5 structure)

7.4 — ohlcv.json

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-11-11T18:30:00Z",
  "assets": {"BTC": {"Binance": {"15m": [], "1h": [], "1d": []}}}
}
```

Versioning: هر فایل generated_at + schema_version: "1.0". Package C فایل با version ناشناخته → reject.

---

## Section 8 — Boundaries

| موضوع | Item_08 | آیتم دیگر |
|---|---|---|
| Data state vocabulary | ✅ تعریف | Item_03 (presence_status) |
| Candle raw format | ✅ تعریف | Item_16 مصرف |
| Canonical candle | ✅ تعریف | Item_16 تولید |
| Price path taxonomy | ✅ تعریف | Item_05 + Item_18 |
| Provenance object | ✅ تعریف | Item_18, 23, 30 |
| Supply structure | ✅ تعریف | Item_15 |
| Aggregate formulas (shape) | ✅ تعریف | Item_25, 29 |
| SQLite NOT NULL | ❌ | Item_12 v2.2 (R-07) |
| Rate limit | ❌ | Item_09 |
| Cache | ❌ | Item_11 |

---

## Section 9 — Open Questions

| # | سؤال | وضعیت |
|---|---|---|
| 1 | ۷ NO_DATA cmc_id | ✅ RESOLVED (SPX=28081, NFT=9816, MON=30495) — ۲۰۱۷ supply ندارند |
| 2 | KMNO 32415 vs 30986 | ✅ RESOLVED (30986) |
| 3 | Coinbase BTC-USDT start | ✅ RESOLVED (2021-05-04 direct) |
| 4 | RNDR dual date (R-32) | ✅ RESOLVED — `listing_dates` از Appendix A استفاده می‌شود، `policy_date` فقط بک‌گراند است. |
| 5 | 币安人生 (rank 82) | ⏳ OPEN (P2 Extractor) — فعلاً در Universe |
| 6 | Appendix B available_from = CMC limit | ✅ RESOLVED (کامنت Schema) |

---

## Section 10 — MVP-First Notes

✅ JSON only (بدون Parquet/Protobuf)
✅ ISO 8601 Z در JSON، Unix ms در SQLite
✅ String price در B→C (حفظ precision)
✅ Provenance صریح
✅ Version هر فایل

❌ Backward compat layer
❌ Schema registry
❌ Field-level encryption
❌ Streaming interface

---

End of Item_08 v1.0 APPROVED
