# TEST_MAP.md — Comprehensive Test Registry

**نسخه: v2.1**
**تاریخ آپدیت: ۷ نوامبر ۲۰۲۶**
**منبع: AM + Data Extractor + TD (سه‌نفره تأیید شد)**

---

## هدف این سند

این سند، مرجع رسمی همه تست‌های پروژه است. هر ایجنتی که این سند را بخواند، بدون نیاز به باز کردن فایل‌های تست، دقیقاً می‌داند:
- چه تستی انجام شده
- نتیجه دقیق چیست
- در کدام آیتم استفاده می‌شود
- آیا نیازمند تست مجدد است

**قانون طلایی (R-20):** قبل از هر تست جدید، این سند باید بررسی شود. اگر تست قبلاً انجام شده و نتیجه معتبر دارد، تست مجدد انجام نمی‌شود.

---

## Legend — علامت‌ها

| علامت | معنی |
|---|---|
| ✅ SUCCESS | تست موفق، نتیجه معتبر |
| ⚠️ PARTIAL / BUGGY | ناقص یا باگ دارد |
| ❌ FAILED | شکست خورد |
| 💎 GOLDEN | مرجع اصلی |
| 📖 META | مستند/خلاصه |
| 📌 SUPERSEDED | با تست جدیدتر جایگزین شد |

---

## Section 1 — تست‌های امروز (۷ نوامبر ۲۰۲۶)

### ۱.۱ — A1: مبدأ ۵ دقیقه هر صرافی ✅

**نتیجه:**

| صرافی | مبدأ ۵m | شاهد |
|---|---|---|
| Bitstamp | ۲۰۱۵-۰۱-۰۱ | ۳ تست مستقل، count=۱۰۰ |
| Coinbase | ~۲۰۱۵-۰۷-۲۰ | ۹ تست (Phase 1+2)، count=۴۲→۳۰۱ |
| Binance | ۲۰۱۷-۰۸-۱۷ | ۳ تست، همه یکسان |
| OKX | ~۲۰۱۸-۰۱-۱۱ | pagination-limited (approx) |
| Crypto.com | ~۲۰۲۰-۰۹-۲۹ | verified |
| Bybit | ۲۰۲۱-۰۷-۰۵ | ۳ تست |

**استفاده در:** Item_03 (مبدأ صرافی)، Item_13 (Bootstrap).

---

### ۱.۲ — A2: تایم‌فریم‌ها برای هر صرافی ✅

| صرافی | 5m | 15m | 30m | 1h | 1d | سطح |
|---|---|---|---|---|---|---|
| Bitstamp | ۲۰۱۵-۰۱-۰۱ | ۲۰۱۵-۰۱-۰۱ | ۲۰۱۵-۰۱-۰۱ | ۲۰۱۵-۰۱-۰۱ | ۲۰۱۵-۰۱-۰۱ | DEFINITIVE |
| Coinbase | ۲۰۱۵-۰۷-۲۰ | ۲۰۱۵-۰۷-۲۰ | **ندارد** | ۲۰۱۵-۰۷-۲۰ | ۲۰۱۵-۰۷-۲۰ | DEFINITIVE |
| Binance | ۲۰۱۷-۰۸-۱۷ | ۲۰۱۷-۰۸-۱۷ | ۲۰۱۷-۰۸-۱۷ | ۲۰۱۷-۰۸-۱۷ | ۲۰۱۷-۰۸-۱۷ | DEFINITIVE |
| OKX | ~۲۰۱۸-۰۱-۱۱ | ~۲۰۱۸-۰۱-۱۱ | ~۲۰۱۸-۰۱-۱۱ | ۲۰۱۸-۰۱-۱۱ | ۲۰۱۷-۱۰-۱۰ | 1h/1d=DEF، بقیه=APPROX |
| Crypto.com | ۲۰۲۰-۰۹-۲۹ | ۲۰۲۰-۱۱-۲۷ | ~۲۰۲۰-۱۱-۲۷ | ۲۰۲۰-۱۱-۱۸ | ۲۰۲۰-۰۹-۲۲ | 1d/5m=DEF، M15/H1=CONS |
| Bybit | ۲۰۲۱-۰۷-۰۵ | ۲۰۲۱-۰۷-۰۵ | ۲۰۲۱-۰۷-۰۵ | ۲۰۲۱-۰۷-۰۵ | ۲۰۲۱-۰۷-۰۵ | DEFINITIVE |

**نکته:** ۱۵دقیقه و ۳۰دقیقه **قبلاً هرگز تست نشده بودند** — A2 امروز اولین بار.

---

### ۱.۳ — A2.5a: OKX + Crypto.com (دو مرز) ✅

**OKX:**
- Default boundary (کیبورد) = ۲۰۱۷-۱۰-۱۰ (از 1d)
- Custom boundary (بازه کاربر) = ۲۰۱۸-۰۱-۱۵ (از 5m)

**Crypto.com:**
- Default boundary = ۲۰۲۰-۰۹-۲۲ (از 1d)
- Custom boundary = ۲۰۲۰-۱۱-۲۷ (از M15، conservative)

**کشف مهم:** Crypto.com سقف API = ۳۰۰ کندل (count=1000 نادیده گرفته می‌شود).

---

### ۱.۴ — A3: سقف کندل هر صرافی ✅

| صرافی | سقف | شاهد | سطح |
|---|---|---|---|
| Binance | ≥۱۰۰۰ | ۱۰۰۰ برگشت | DEFINITIVE |
| Bitstamp | ≥۱۰۰۰ | ۱۰۰۰ برگشت | DEFINITIVE |
| Bybit | ≥۱۰۰۰ | ۱۰۰۰ برگشت | DEFINITIVE |
| OKX | ۳۰۰ | ۱۰۰۰ خواستیم، ۳۰۰ داد | DEFINITIVE |
| Crypto.com | ۳۰۰ | ۱۰۰۰ خواستیم، ۳۰۰ داد | DEFINITIVE |
| Coinbase | ۳۰۰ | window=۴۰۰→ERROR 400؛ window=۳۰۰→۳۰۰ کندل (HTTP 200) | DEFINITIVE |

**همه ۶ صرافی قطعی.** A3 بسته.

---

### ۱.۵ — Bitstamp Coverage ✅

- ۲۵۲ جفت کل
- ۷ جفت USDT
- ۱۱۴ جفت USD

**استفاده در:** Item_03، Item_20.

---

## Section 2 — Coverage Tests (تست‌های قدیمی)

### ۲.۱ — `tests/coverage/2026-10-28_5m_since_2017.tsv` ⚠️ BUGGY

**تست چه چیزی:** تاریخ شروع ۵m برای ۱۵ دارایی در ۵ صرافی.

**نتیجه (نمونه):**

| دارایی | Binance | OKX | Bitstamp | Coinbase | Crypto.com |
|---|---|---|---|---|---|
| BTC | ۲۰۱۷-۰۸-۱۷ | **۲۰۲۶-۱۰-۲۸ (باگ)** | **۲۰۱۷-۰۱-۰۱** | **۲۰۱۷-۰۱-۰۱** | **۲۰۲۶-۱۰-۲۸ (باگ)** |
| ETH | ۲۰۱۷-۰۸-۱۷ | باگ | **N/A** | ۲۰۱۷-۰۱-۰۱ | باگ |

**باگ‌ها:**
1. OKX و Crypto.com = تاریخ امروز (یعنی «داده نداریم» ولی N/A نشده)
2. **⚠️ نکته مهم (TD کشف):** ستون Bitstamp BTC = ۲۰۱۷-۰۱-۰۱، اما A1 امروز نشان داد Bitstamp BTC از **۲۰۱۵-۰۱-۰۱** داده دارد. این فایل فقط «از ۲۰۱۷ به بعد» جستجو کرده، نه اولین کندل واقعی.

**استفاده در:** Item_03، Item_13.

**وضعیت:** 📌 SUPERSEDED برای ستون Bitstamp BTC (با A1).

---

### ۲.۲ — `tests/coverage/2026-10-28_coverage_matrix.tsv` ⚠️ BUGGY

**تست چه چیزی:** ماتریس ۱۲۵×۵ با LISTED/NOT_LISTED + ۴ timestamp.

**نتیجه (نمونه):**

| دارایی | Binance | OKX | Bitstamp | Coinbase | Crypto.com |
|---|---|---|---|---|---|
| BTC | ۲۰۱۷-۰۸-۱۷ | ۲۰۱۸-۰۱-۱۱ | ۲۰۲۱-۰۶-۱۰ | ۲۰۲۱-۰۵-۰۴ | NOT_LISTED (باگ) |

**باگ:** ستون Crypto.com برای همه ۱۲۵ = NOT_LISTED. بعداً `bitstamp_coinbase_cryptocom_safe.txt` ثابت کرد BTC_USDT وجود دارد.

**⚠️ نکته مهم (TD کشف):** ستون Bitstamp BTC = ۲۰۲۱-۰۶-۱۰ و Coinbase BTC = ۲۰۲۱-۰۵-۰۴ — این‌ها **pairهای متفاوت** با A1 هستند (احتمالاً BTC-USD vs BTC-USDT). A1 امروز BTC-USDT را تست کرد (۲۰۱۵-۰۱-۰۱ برای Bitstamp، ۲۰۱۵-۰۷-۲۰ برای Coinbase).

**استفاده در:** Item_03، Item_20.

**وضعیت:** 📌 SUPERSEDED (برای Bitstamp/Coinbase BTC).

---

### ۲.۳ — `tests/coverage/2026-10-28_test_real_check.txt` ⚠️ PARTIAL

**تست چه چیزی:** ۶ سناریو مبدأ ۵m با درخواست واقعی.

**نتیجه:**

| # | سناریو | نتیجه |
|---|---|---|
| ۱ | Binance BTC | ✅ ۲۰۱۷-۰۸-۱۷ ۰۴:۰۰ UTC |
| ۲ | Binance ZEC | ✅ ۲۰۲۱-۰۱-۰۱ |
| ۳ | OKX BTC | ❌ داده برنگشت |
| ۴ | OKX ZEC | ❌ داده برنگشت |
| ۵ | Coinbase BTC | ✅ ۱۳ کندل، آخرین: ۲۰۲۱-۰۵-۰۴ |
| ۶ | Bitstamp BTC | ✅ ۲۰۲۱-۰۶-۱۰ |

**⚠️ نکته مهم (TD کشف):** سناریو ۵ — Coinbase از **۲۰۲۱-۰۵-۰۴** شروع کرده، نه شروع واقعی. A1 امروز نشان داد Coinbase BTC-USD از **۲۰۱۵-۰۷-۲۰** داده دارد. این تست فقط از ۲۰۲۱ تست کرده.

**خطا:** OKX در هر ۲ سناریو داده نداد (پارامتر `bar` یا `after`).

**استفاده در:** Item_03، Item_09.

**وضعیت:** 📌 SUPERSEDED (برای Coinbase BTC).

---

### ۲.۴ — `tests/coverage/2026-10-28_okx_cc_test.txt` ✅ SUCCESS

**تست چه چیزی:** وجود ۵m در OKX و Crypto.com در بازه‌های مختلف.

**نتیجه OKX:**

| دارایی | قبل ۲۰۱۸ | قبل ۲۰۲۰ | قبل ۲۰۲۲ | قبل ۲۰۲۴ |
|---|---|---|---|---|
| BTC/ETH/XRP/LTC/BCH | NO | YES | YES | YES |
| SOL | NO | NO | YES | YES |
| ARB | NO | NO | NO | YES |

**نتیجه Crypto.com:** مشابه OKX (۲۰۱۹=NO، ۲۰۲۱=YES).

**استفاده در:** Item_03.

**وضعیت:** ✅ SUCCESS — مرجع OKX/Crypto.com (سازگار با A2.5a امروز).

---

### ۲.۵ — `tests/coverage/2026-10-30_1h_1d_coverage.txt` ⚠️ BUGGY

**تست چه چیزی:** قدیمی‌ترین timestamp ۱h و ۱d برای ۵ صرافی.

**نتیجه:**

| صرافی | 1h | 1d |
|---|---|---|
| Binance | ۲۰۱۷-۰۸-۱۷ ۰۴:۰۰ | ۲۰۱۷-۰۸-۱۷ ۰۰:۰۰ |
| OKX | **۲۰۲۶-۱۰-۲۸ (باگ)** | **۲۰۲۶-۱۰-۲۸ (باگ)** |
| Coinbase | ۲۰۱۷-۰۱-۰۱ | ۲۰۱۷-۰۱-۰۱ |
| Bitstamp | ۲۰۱۷-۰۱-۰۱ | ۲۰۱۷-۰۱-۰۱ |
| Crypto.com | None | None |

**باگ:** OKX داده امروز را برگرداند (پارامتر `bar` نادرست).

**⚠️ نکته حیاتی:** این فایل **فقط ۱h و ۱d** دارد — **۱۵m و ۳۰m هرگز تست نشده بودند** (A2 امروز اولین بار).

**استفاده در:** Item_03، Item_06.

**وضعیت:** 📌 SUPERSEDED (با A2 امروز که OKX را درست کرد).

---

## Section 3 — Rate Limit & HTTP

### ۳.۱ — `2026-10-29_header_check.txt` ✅ SUCCESS

**نتیجه:**

| صرافی | هدر Rate Limit |
|---|---|
| Binance | `x-mbx-used-weight-1m: 1`، `x-mbx-used-weight: 1` |
| OKX | ندارد |
| Bitstamp | ندارد |
| Coinbase | ندارد (فقط `access-control-expose-headers`) |
| Crypto.com | ندارد |

**استفاده در:** Item_09 (C-001)، Item_11.

---

### ۳.۲ — `2026-10-29_binance_klines_weight.txt` ✅ SUCCESS 💎

**نتیجه:** وزن هر درخواست کندل Binance = **۲** (delta=2 ثابت). **مستقل از limit و دارایی.**
**کشف:** در req 9 پنجره ۱ دقیقه‌ای ریست شد.

**استفاده در:** Item_09 (C-001)، Item_11 (Pacing).

---

### ۳.۳ — `2026-10-29_binance_limit1000.txt` ✅ SUCCESS 📌

**نتیجه:** ۳ درخواست، HTTP 200. weight: 2→4→6. ۱۰۰۰ کندل پذیرفته.

**وضعیت:** 📌 SUPERSEDED با A3 امروز (که دقیق‌تر است).

---

### ۳.۴ — `2026-10-29_binance_sol.txt` ✅ SUCCESS 📌

**نتیجه:** SOLUSDT هم وزن ۲ (مستقل از دارایی).

**وضعیت:** 📌 SUPERSEDED با A3 امروز (وزن = ۲ تأیید شد).

---

### ۳.۵ — `2026-10-29_okx_safe.txt` ✅ SUCCESS

**نتیجه:** ۳ درخواست OKX، HTTP 200، code=0، data_rows=1.

**استفاده در:** Item_09.

---

### ۳.۶ — `2026-10-30_bitstamp_coinbase_cryptocom_safe.txt` ✅ SUCCESS

**نتیجه:**
- Bitstamp: ۳× HTTP 200 (bytes=۱۷۲)
- Coinbase: ۳× HTTP 200 (bytes=۲۰۹۰۴)
- Crypto.com BTC_USDT: ۲۰۰، داده کامل
- Crypto.com BTC_USD: ۲۰۰، داده کامل
- **تعارض NOT_LISTED حل شد**

**استفاده در:** Item_03 (پوشش Crypto.com)، Item_09.

---

### ۳.۷ — `2026-10-30_okx_history_http.txt` ✅ SUCCESS

**نتیجه:** ۸۹ درخواست پی‌درپی OKX. صفر خطا. نرخ ۲.۰ req/s. زمان ۴۳.۸s.

**استفاده در:** Item_09 (C-003)، Item_13 (Bootstrap OKX).

---

## Section 4 — WebSocket

### ۴.۱ — `2026-10-30_okx_websocket_test.txt` ❌ FAILED

**نتیجه:** CONNECTED=True، اما همه ۳ اشتراک با **code 60018** رد شد.

**خطا:** `60018 — wrong URL or channel:candle5m`.
**استنتاج:** استفاده از `public` به‌جای `business` endpoint (از مقایسه با v2).

**استفاده در:** Item_11.

---

### ۴.۲ — `2026-10-30_okx_websocket_test_v2.txt` ✅ SUCCESS

**نتیجه:** business endpoint. ۳ جفت: BTC (۳۴ msg)، ETH (۲۷ msg)، SOL (۲۱ msg). صفر خطا.

---

### ۴.۳ — `2026-10-30_okx_websocket_all.txt` ✅ SUCCESS 💎

**نتیجه:** ۸۹ جفت در ۲ بچ. ۸۹/۸۹ مشترک. ۱۳۸۵ پیام در ۶۰s. صفر خطا. avg ۱۵.۶ msg/pair.

**استفاده در:** Item_11 (Live RAM)، Item_09 (C-019).

**تأیید امروز:** A2.5a همین نتیجه را تأیید کرد (تکراری).

---

### ۴.۴ — `2026-10-30_coinbase_websocket_all.txt` ✅ SUCCESS 💎

**نتیجه:** ۱۰۳ جفت در یک اتصال. ۱۰۳/۱۰۳ با پیام. ۹۶۵۹ پیام در ۶۰s. صفر خطا.
**استنتاج:** کشف ۸۴ دارایی جدید (۱۰۳−۱۹).

**استفاده در:** Item_11، Item_03.

---

## Section 5 — Supply/CMC Workflows (۹ فایل)

| # | Workflow | موضوع | Artifact |
|---|---|---|---|
| ۱ | final_supply_harvest.yml | Harvest نهایی ۱۲۵ (۱۲ checkpoint ۲۰۱۷-۲۰۲۶) | `final_125_supply.json` (۱۱۸ FILLED) |
| ۲ | verify_top125_supply.yml | تأیید پوشش (۸ checkpoint) | `verification_results.json` |
| ۳ | cmc_earliest_dates.yml | قدیمی‌ترین تاریخ ۱۲۵ (۸ checkpoint) | `earliest_dates.json` |
| ۴ | cmc_fill_40.yml | پر کردن ۴۰ UNAVAILABLE | `cmc_fill_40.json` |
| ۵ | cmc_aggressive_fill.yml | ۲۹ باقی‌مانده (۲۰۲۴-۲۰۲۵) | `aggressive_fill_29.json` |
| ۶ | cmc_internal_extended.yml | CMC internal + probe نرخ | — |
| ۷ | combined_supply_tests.yml | CMC + DefiLlama stablecoins | — |
| ۸ | fill_gaps.yml | پر کردن ۵۳ UNAVAILABLE | `fill_gaps_results.json` |
| ۹ | verify_and_fill.yml | تأیید ۱۲۵ + retry | `verify_125.json` + `coingecko_retry.json` |

**استفاده در:** Item_02، Item_15، Item_25، Item_27.

---

## Section 6 — Infrastructure Workflows (۷ فایل)

| # | Workflow | موضوع | وضعیت |
|---|---|---|---|
| ۱ | test_actions.yml | پایه GitHub Actions | ✅ |
| ۲ | test_external_api.yml | DNS + API Binance/Coinbase/Kraken | ✅ |
| ۳ | test_comprehensive_data.yml | جامع: Binance، ۴ صرافی، ۱۲ دارایی | ✅ |
| ۴ | test_cron_timing.yml | زمان‌بندی UTC (تأخیر ۳ ثانیه) | ✅ |
| ۵ | test_historical_supply.yml | RPC Ethereum (LINK/UNI/USDT/MATIC) | ✅ |
| ۶ | test_crypto2.yml | بسته R | ❌ FAILED (بدون خروجی خام) |
| ۷ | test_crypto2_v2.yml | تلاش رفع | ⚠️ PARTIAL (بدون خروجی خام) |

---

## Section 7 — TEST001/TEST003 (۵ فایل)

| # | فایل | مسیر | موضوع |
|---|---|---|---|
| ۱ | test001.py | scripts/ | CLI TEST001 |
| ۲ | test001_manual.yml | .github/workflows/ | اجرای دستی |
| ۳ | test003_origin.py | scripts/ | مبدأ ۲۰۱۷ (1d) |
| ۴ | test003_manual.yml | .github/workflows/ | اجرای دستی |
| ۵ | universe.json | data/test001/ | ۱۲۵ دارایی |

---

## Section 8 — Meta/Structural (۳ فایل)

| # | فایل | موضوع |
|---|---|---|
| ۱ | test_stage_a1_structure.py | تست ساختاری Stage A1 |
| ۲ | 2026-10-27_requirements.txt | فقط requests |
| ۳ | 2026-10-27_summary.txt | خلاصه **۱۷ مسیر / ۱۲ نوع یکتا** (۵ results.json + ۱۲ فایل دیگر، ۲ تکراری) |

---

## Section 9 — Failed & Buggy (خلاصه)

### ❌ FAILED (۲ مورد)
- `okx_websocket_test.txt` — code 60018 (کانال اشتباه)
- `test_crypto2.yml` — بدون خروجی خام

### ⚠️ BUGGY/PARTIAL (۵ مورد)
- `5m_since_2017.tsv` — OKX/CC=تاریخ امروز، Bitstamp BTC=ناقص
- `coverage_matrix.tsv` — Crypto.com=NOT_LISTED برای همه
- `test_real_check.txt` — OKX ۲/۲ خطا، Coinbase فقط از ۲۰۲۱
- `1h_1d_coverage.txt` — OKX باگ، ۱۵m/۳۰m ندارد
- `test_crypto2_v2.yml` — خروجی نامطمئن

---

## Section 10 — Golden Tests (مرجع اصلی)

| # | فایل | چرا طلایی |
|---|---|---|
| ۱ | `coverage_matrix.tsv` | ماتریس ۱۲۵×۵ (ولی Crypto.com bug دارد) |
| ۲ | `5m_since_2017.tsv` | ماتریس ۱۵×۵ (Binance مرجع) |
| ۳ | `binance_klines_weight.txt` | تنها اندازه‌گیری دقیق وزن=۲ |
| ۴ | `okx_websocket_all.txt` | تنها تست کامل WS OKX |
| ۵ | `coinbase_websocket_all.txt` | تنها تست کامل WS Coinbase |

---

## Section 11 — Duplicate & Superseded Map

| تست امروز | فایل قدیمی | نوع | تصمیم |
|---|---|---|---|
| A1 Binance | 5m_since_2017 + test_real_check | تکراری | هر دو CURRENT |
| A1 Bitstamp | 5m_since_2017 (۲۰۱۷) + coverage (۲۰۲۱) | تکمیلی | قدیمی 📌 SUPERSEDED، امروز CURRENT |
| A1 Coinbase | 5m_since_2017 (۲۰۱۷) + coverage (۲۰۲۱) + test_real (۲۰۲۱) | تکمیلی | قدیمی 📌 SUPERSEDED، امروز CURRENT |
| A1 Crypto.com | 5m_since_2017 (باگ) + okx_cc_test (۲۰۲۱) | تکمیلی | قدیمی 📌 SUPERSEDED، امروز CURRENT |
| A1 Bybit | هیچ | جدید | امروز CURRENT |
| A2 15m/30m | هیچ | جدید | امروز CURRENT |
| A2 1h/1d | 1h_1d_coverage (OKX باگ) | تکمیلی | قدیمی 📌 SUPERSEDED، امروز CURRENT |
| A2.5a OKX 1d | 1h_1d_coverage (باگ) | جدید | امروز CURRENT |
| A2.5a OKX 5m | coverage (۲۰۱۸-۰۱-۱۱) | تکمیلی | قدیمی 📌 SUPERSEDED، امروز CURRENT |
| A2.5a Crypto.com | okx_cc_test (۲۰۲۱) | تکمیلی | امروز CURRENT |
| A3 Binance ≥۱۰۰۰ | binance_limit1000 + binance_sol | تکراری | هر دو CURRENT |
| A3 OKX ۳۰۰ | هیچ | جدید | امروز CURRENT |
| A3 Bitstamp ≥۱۰۰۰ | هیچ | جدید | امروز CURRENT |
| A3 Crypto.com ۳۰۰ | هیچ | جدید | امروز CURRENT |
| A3 Bybit ≥۱۰۰۰ | هیچ | جدید | امروز CURRENT |
| A3 Coinbase ۳۰۰ | bitstamp_coinbase_cryptocom_safe | جدید (cap تست نشده بود) | امروز CURRENT |
| OKX WS ۸۹ جفت | okx_websocket_all | — | تست امروز نبود؛ فقط reference از TEST_MAP |

---

## Section 12 — ناسازگاری‌ها (اصلاح‌شده)

### ۱۲.۱ — Bitstamp BTC: ۲۰۱۷ vs ۲۰۱۵
- `5m_since_2017.tsv`: ۲۰۱۷-۰۱-۰۱ (فقط «از ۲۰۱۷» جستجو کرده)
- `coverage_matrix.tsv`: ۲۰۲۱-۰۶-۱۰ (pair متفاوت احتمالاً)
- `A1 امروز`: **۲۰۱۵-۰۱-۰۱** (۳ تست مستقل)
- **حل‌شده:** A1 امروز مرجع است.

### ۱۲.۲ — Coinbase pair
- **BTC-USD:** از **۲۰۱۵-۰۷-۲۰** (A1 امروز، ۹ تست مستقل)
- **BTC-USDT:** نامشخص (A4 امروز)
- `test_real_check.txt` (۲۰۲۱-۰۵-۰۴) فقط از ۲۰۲۱ تست کرده، نه کشف شروع.

### ۱۲.۳ — ۱۵m/۳۰m تاریخی
- ✅ هیچ تست قبلی نداشتند. A2 امروز اولین بار.

### ۱۲.۴ — OKX مبدأ دقیق
- **1d:** ۲۰۱۷-۱۰-۱۰ (TRUE START، count=۸۳)
- **1h:** ۲۰۱۸-۰۱-۱۱ (TRUE START، count=۸۵)
- **5m/15m/30m:** ~۲۰۱۸-۰۱-۱۵ (Custom، pagination-limited)

---

## Section 13 — Missing Files (۲۱ فایل غایب از TEST_MAP v1)

| # | نام | دسته |
|---|---|---|
| ۱-۹ | ۹ Workflow Supply/CMC | Supply (Section 5) |
| ۱۰-۱۶ | ۷ Workflow Infrastructure | Infra (Section 6) |
| ۱۷-۲۱ | TEST001/TEST003 + universe + requirements | TEST00x (Section 7) |

**همه در v2.1 اضافه شدند.** ✅

---

## Section 14 — Pending Tests (باقی‌مانده)

| # | تست | وضعیت |
|---|---|---|
| ۱ | A4 — فرمت OHLCV (۶ صرافی) | ❌ انجام نشده |
| ۲ | A5 — Supply تاریخی (بازبینی Workflowها) | ⏳ در Workflowها هست، ولی در TEST_MAP ثبت نشده |
| ۳ | A6 — Migration Map (FTM→S، MATIC→POL) | ❌ انجام نشده |
| ۴ | A7 — Delisted Assets (FTT، LUNA) | ❌ انجام نشده |
| ۵ | A8 — Bootstrap Plan | ❌ انجام نشده |
| ۶ | WebSocket بقیه صرافی‌ها (Binance، Bitstamp، Crypto.com، Bybit) | ❌ فقط OKX و Coinbase تست شده |
| ۷ | Coinbase BTC-USDT pair | ❌ فقط BTC-USD تست شده |
| ۸ | پوشش ۱۲۵ دارایی در هر صرافی | ⏳ فقط Binance عدد دقیق (۱۰۵) دارد |

---

## Section 15 — راهنمای استفاده (برای ایجنت‌ها)

### قبل از هر تست جدید:
۱. **Section 1** (تست‌های امروز) را ببین — آیا این تست امروز انجام شده؟
۲. **Section 10** (Golden Tests) را ببین — آیا مرجع موجود است؟
۳. **Section 11** (Duplicate Map) را ببین — آیا تکراری است؟
۴. اگر تست جدید بود → **انجام بده + این سند را آپدیت کن.**

### برای پیدا کردن تست مرتبط با آیتم:
- **Item_03 (Universe):** Sections 1، 2، 12
- **Item_09 (Rate Limit):** Section 3، 4
- **Item_11 (Cache/WS):** Section 4
- **Item_13 (Bootstrap):** Sections 1، 2
- **Item_15 (Supply):** Section 5

---

## Section 16 — OHLCV Format per Exchange

**تست A4 (۷ نوامبر ۲۰۲۶، سشن ۲)**

| صرافی | نوع | ترتیب فیلدها | timestamp | قیمت | جهت | یک call |
|---|---|---|---|---|---|---|
| Binance | list | [ts, o, h, l, c, v, ...] (۱۲ فیلد) | ms (int) | str | صعودی | ✅ |
| OKX | dict.data[] | [ts, o, h, l, c, v, ...] (۹ فیلد) | ms (str) | str | نزولی | ✅ |
| Coinbase | list | [ts, **l, h, o**, c, v] (۶ فیلد) | s (int) | **num** | نزولی | ✅ |
| Bitstamp | dict.data.ohlc[] | {timestamp, open, high, low, close, volume} | s (str) | str | صعودی | ✅ |
| Crypto.com | dict.result.data[] | {t, o, h, l, c, v} | ms (int) | str | صعودی | ✅ |
| Bybit | dict.result.list[] | [ts, o, h, l, c, v, turnover] (۷ فیلد) | ms (str) | str | نزولی | ✅ |

### ۵ ناسازگاری حیاتی (پیامد برای Item_16 و Item_07)

**۱. Coinbase ترتیب OHLC معکوس دارد:**
`[ts, low, high, open, close, volume]` — نه استاندارد.
اگر Item_16 استاندارد parse کند → کندل خراب.

**۲. timestamp سه فرمت:**
- ms+int: Binance, Crypto.com
- ms+str: OKX, Bybit
- s+int: Coinbase
- s+str: Bitstamp

**۳. Coinbase تنها صرافی با قیمت عددی (float):**
بقیه ۵ صرافی رشته می‌دهند. ریسک Decimal در Item_07.

**۴. جهت کندل — ۳ صعودی، ۳ نزولی:**
- صعودی: Binance, Bitstamp, Crypto.com
- نزولی: OKX, Coinbase, Bybit

**۵. فیلدهای اضافی متفاوت:**
Binance ۱۲، OKX ۹، Bybit ۷، بقیه ۶.

### جدول مرجع Item_16 — ExchangeCandleSchema

| صرافی | field_order | ts_unit | ts_type | price_type | direction |
|---|---|---|---|---|---|
| Binance | [ts,o,h,l,c,v,...] | ms | int | str | asc |
| OKX | [ts,o,h,l,c,v,...] | ms | str | str | desc |
| Coinbase | [ts,l,h,o,c,v] | s | int | num | desc |
| Bitstamp | {ts,o,h,l,c,v} | s | str | str | asc |
| Crypto.com | {t,o,h,l,c,v} | ms | int | str | asc |
| Bybit | [ts,o,h,l,c,v,tn] | ms | str | str | desc |

**این جدول، مرجع اجباری Item_16 است.**

**وضعیت:** ✅ CLOSED (A4)

---

## آمار نهایی

| دسته | تعداد |
|---|---|
| تست‌های امروز (Section 1) | ۵ |
| Coverage قدیمی | ۵ |
| Rate Limit & HTTP | ۷ |
| WebSocket | ۴ |
| Supply/CMC | ۹ |
| Infrastructure | ۷ |
| TEST001/TEST003 | ۵ |
| Meta/Structural | ۳ |
| OHLCV Format (Section 16) | ۱ |
| **جمع** | **۴۶** |
| Golden | ۵ |
| Failed | ۲ |
| Buggy/Partial | ۵ |
| Superseded | ۹ |
| Pending (Section 14) | ۸ |

**پوشش v2.1:** ۴۵ تست موجود + ۸ تست باقی‌مانده.

---

**پایان TEST_MAP v2.1**

---

### R-24 — پروتکل هماهنگی جلسات
- AM شروع جلسه را اعلام می‌کند
- شف پیام را به همه می‌رساند
- سؤالات به AM برمی‌گردد
- فقط AM دستور اجرا می‌دهد
