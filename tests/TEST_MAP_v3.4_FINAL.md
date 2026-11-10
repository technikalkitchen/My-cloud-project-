🧭 ایجنت منیجر ۰۲ — پیام #۷۴
تاریخ: ۱۱ نوامبر ۲۰۲۶ | ساعت: طبق قانون ۲ — ساعت تهران؟ (ولی چون TD در حال آماده‌سازی است، با ~۱۹:۲۵ نوشتم؛ اگر متفاوت است بگو patch کنم)

حق داری. همه یافته‌های جدید باید همین الان قفل شوند — نه در پیام‌های چت (که با ریست context پاک می‌شوند).

---

```
═══════════════════════════════════════════════════════════════
TEST_MAP v3.4 FINAL — Purpose-Driven Registry
تاریخ: ۱۱ نوامبر ۲۰۲۶ | ساعت: ~۱۹:۲۵ تهران | سشن: ۱
منبع: ۸ چک‌پوینت + ۸ دسته بازبینی + TD-01 + audit_2026-11-11 + Coinbase Diagnostic (11 Nov)
وضعیت: FINAL — همه یافته‌ها ثبت‌شده
═══════════════════════════════════════════════════════════════
```

Section 0 — Timeline

دوره بازه Cutoff اعتبار
آماتور ۲۸–۳۰ اکتبر ۲۰۲۶ ۳۰ Oct ۲۳:۵۹ UTC نگه‌داری، نه مرجع
حرفه‌ای ۶–۱۱ نوامبر ۲۰۲۶ — مرجع قطعی

Section 1 — ۸ سؤال پایه

# سؤال آیتم‌ها
Q1 هر صرافی چند کوین و از چه تاریخی؟ ۰۱، ۰۳، ۱۳
Q2 چه TFها و از چه تاریخی؟ ۰۶، ۱۱، ۱۶
Q3 محدودیت نرخ هر صرافی؟ ۰۹، ۱۱، ۱۳
Q4 فرمت OHLCV هر صرافی؟ ۰۷، ۱۶
Q5 مهاجرت/حذف در یونیورس؟ ۰۳، ۰۴
Q6 pair BTC و USD؟ ۰۵، ۱۸
Q7 ساپلای از کجا و چقدر؟ ۱۵، ۱۹، ۲۵
Q8 ظرفیت ذخیره و WS؟ ۱۱، ۱۲، ۱۳

Section 2 — نگاشت تست → آیتم

۲.۱ — فعال (مرجع قطعی، ۳۰ تست)

تست Q آیتم commit نکته
A1 مبدأ ۵m Q1 ۰۱، ۰۳، ۱۳ no_commit (chat_session) professional ۷ Nov، ۶ صرافی
A2 TF Q2 ۰۶، ۱۶ no_commit professional ۷ Nov
A2.5a OKX/CC Q2 ۰۶ no_commit OKX 1d=2017-10-10
A3 سقف کندل Q3 ۰۹، ۱۳ no_commit Binance≥1000، OKX/CC/Coinbase=300
A4 OHLCV Q4 ۰۷، ۱۶ 8c1f4d5 + 6320395 ۵ ناسازگاری — CLOSED
A5 Supply timeseries Q7 ۱۵، ۱۹، ۲۵ d0fd6dd dict ۱۱۷ کلید، ۱۳.۱۷MB
final_125_supply (data) Q7 ۰۳، ۱۵ data_source ۱۱۸ tag FILLED، نقطهٔ اول
A6_A7 Discovery v4 Q5 ۰۳، ۰۴ 93bfa04 ۳ migration + ۳ delisted + survivor + KMNO
A6_A7 OKX Correction Q5 ۰۴ 15fccca POL=2024-09-03، RENDER=2024-07-14، S=2025-01-20 — همه CONFIRMED ✅
POL Bybit Test Q5 ۰۴ fe8a1d2 same_asset (close diff ۰.۱۴٪)، launchTime=null، test_date=2023-10-25
A9 OKX walk-back Q1، Q6 ۰۱، ۰۳ 8e823f2 ۱۰۵/۱۵۰
A9 OKX USDC retry Q6 ۰۱ 5436bd5 + ab5598b +۱ (EURC) = ۱۰۶/۱۵۰ — PARTIAL (۶۰۰ روز)
A9 OKX v3.2 Q6 ۰۵، ۱۸ 3cd2cf0 EXISTS ✅ — ETH BTC-pair=2018-01-10 (11 iter)، BTC/USD=NOT_LISTED، effective_min تغییر نکرد
A9 Binance v2 Q1 ۰۱، ۰۳ b45bce0 ۱۱۴/۱۵۰ — فقط USDT/USD
A9 Bybit v2 Q1 ۰۱، ۰۳ b45bce0 ۱۲۱/۱۵۰
A9 Bitstamp v2 Q1 ۰۱ b45bce0 ۱/۱۵۰ — ناقص
Binance weight=2 Q3 ۰۹، ۱۱ (29 Oct) ریست در مرز دقیقه
Binance header Q3 ۰۹ (29 Oct) فقط Binance هدر RL
OKX history rate Q3 ۰۹، ۱۳ (30 Oct) مؤثر ۲ req/s
OKX WS ۸۹ جفت Q8 ۱۱ (30 Oct) ۱۳۸۵ msg/60s، confirm=0
OKX WS v2 (۳ جفت) Q8 ۱۱ (30 Oct) BTC ۳۴، ETH ۲۷، SOL ۲۱
Coinbase WS ۱۰۳ جفت Q8 ۱۱ (30 Oct) ۹۶۵۹ msg/60s
Bitstamp/Coinbase/CC safe Q1 ۰۱، ۰۳ (30 Oct) CC NOT_LISTED رد شد
CMC cap=732 Q7 ۱۵ (7 Nov) pagination قاعده
CMC IDs internal_extended Q5 ۰۳، ۰۴ (6 Nov) MATIC=3890، POL=28321
cmc_top150 fetch Q1 ۰۳ b45bce0 ۱۵۰ CMC authoritative
asset_universe_master Q1 ۰۳ fe8a1d2 + 64e3540 ۱۹۵ union
audit_2026-11-11 همه همه uncommitted پاسخ ۷ سؤال باز
Coinbase Diagnostic (11 Nov) Q1، Q6 ۰۱، ۰۳، ۰۵ uncommitted ۹ تست — READY for full scan
Coinbase /products (11 Nov) Q1، Q6 ۰۱، ۰۵ uncommitted BTC-USD online · BTC-USDT online · USDT-USD online

۲.۲ — A4: ۵ ناسازگاری (CLOSED)

# ناسازگاری
۱ Coinbase field order: [ts, low, high, open, close, vol]
۲ ۴ timestamp format: ms+int (Binance/CC) · ms+str (OKX/Bybit) · s+int (Coinbase) · s+str (Bitstamp)
۳ Coinbase price = float (بقیه string)
۴ Direction: asc (Binance/Bitstamp/CC) vs desc (OKX/Coinbase/Bybit)
۵ Field counts: ۱۲/۹/۷/۶

ExchangeCandleSchema = مرجع اجباری Item_16.

۲.۳ — دورهٔ آماتور (نگه‌داری، ۱۰ تست)

coverage_matrix.tsv · 5m_since_2017.tsv · test_real_check.txt · 1h_1d_coverage.txt · okx_cc_test.txt · binance_limit1000.txt · binance_sol.txt · okx_websocket_test.txt · requirements.txt · universe.json (قدیمی)

۲.۴ — منسوخ (۱۶ + ۱ data_source)

fill_gaps.yml · cmc_fill_40.yml · aggressive_fill_29.yml · coingecko_retry · verify_and_fill.yml · verify_top125_supply.yml · cmc_earliest_dates.yml · test_crypto2.yml/v2 · test_cron_timing.yml · test_comprehensive_data.yml · combined_supply_tests.yml · test_historical_supply.yml · test_external_api.yml · test_actions.yml · test_stage_a1_structure.py · test003_origin.py

final_supply_harvest.yml = data_source_only (workflow obsolete، داده معتبر — ۱۱۸ رکورد)

۲.۵ — Coinbase Diagnostic (11 Nov) — نتایج تفصیلی

Test Range Result Interpretation
t1 BTC-USD 2015-06 count=0 پیش از boundary ✅
t2 BTC-USD 2015-08 count=31 boundary 2015-07-20 تأیید ✅
t3 BTC-USD 2020-06 count=30 mid-history ✅
t4 BTC-USDT 2020-06 count=0 pair online ولی تاریخ بعد از 2020
t5 BTC-USDC 2024-06 count=0 delisted (confirmed via /products)
t6 BTC-USD 1-year HTTP 400 سقف ۳۰۰ تأیید ✅
t7 BTC-USD 6-month count=182 pagination روش صحیح ✅
t8 USDT-USD 2020-06 count=0 pair online
t9 USDC-USD 2020-06 HTTP 404 NOT_FOUND

Critical (t2+t3): PASS. Full scan Ready: YES.

۲.۶ — Coinbase /products (11 Nov) — نتیجهٔ قطعی

Pair Status Item_05 Action
BTC-USD online ✅ Direct_USD
BTC-USDT online ✅ Direct_USDT — اولویت ۱
BTC-USDC delisted ⚠️ حذف از scope (شف تأیید)
USDT-USD online ✅ §۳.۶ same-exchange rate ✅
USDC-USD NOT_FOUND ❌ حذف از scope (شف تأیید)

تصمیم Owner (۱۱ Nov): BTC-USDC و USDC-USD از scope Coinbase حذف — برای BTC همیشه Direct path (USDT یا USD) فعال است. USDC فقط tier 4 fallback برای آلت‌کوین‌ها، نه BTC.

۲.۷ — TEST001 Framework (زمینه، نه پایه — ۵ فایل)

فایل وضعیت
test001.py ✅ CLI wrapper
test001_manual.yml ✅ timeout 360min
config.py ✅ ۵ صرافی (بدون Bybit) + ۲ TF (5m،1h) — پیش از R-11/A2
runner.py ✅ first/last only، نه OHLCV
adapters.py ✅ سالم — market_id per-exchange: Binance BTCUSDT · OKX BTC-USDT · Bitstamp btcusdt · Coinbase BTC-USD · CC BTC_USDT؛ باگ در a6_a7_discovery.py بود

قانون: TEST001 پیش از R-11 و A2 است. Item_01/06/16 نباید از TEST001 مشتق شوند.

Section 3 — وضعیت هر آیتم

# آیتم status PENDING
۰۱ Exchanges PARTIAL Bitstamp retest (P0)، Bybit در config، Coinbase full scan
۰۲ Aggregators READY فقط CMC
۰۳ Universe READY ۱۲۵/۱۵۰ تصمیم، ۷ CMC ID (P2)
۰۴ Migration READY RNDR دو تاریخ (R-32)، KMNO patch
۰۵ Canonical Pairs PARTIAL Coinbase BTC-USDT full scan، Item_05 Amendment (۴ باگ)
۰۶ Timeframes READY_NEEDS_DOC ۳۰m تصمیم (R-30)
۰۷ Precision READY —
۰۸ Data Contract READY_NEEDS_DOC —
۰۹ Rate Limit PARTIAL Coinbase/Bitstamp/CC/Bybit rate
۱۰ Error READY_NEEDS_DOC —
۱۱ Cache PARTIAL WS Binance/Bybit (P2)
۱۲ Storage READY_NEEDS_DOC —
۱۳ Bootstrap BLOCKED Item_13 نوشته نشده (TD1)
۱۴ Collector READY_NEEDS_DOC —
۱۵ Supply READY دو منبع، USD1 (P3)
۱۶ OHLCV READY CLOSED
۱۷ Exchange Volume READY_NEEDS_DOC (A4 v field)
۱۸ Exchange Price PARTIAL A9 v3 BTC partial
۱۹ Exchange MC READY_NEEDS_DOC از upstream
۲۰/۲۱ Reliability READY_NEEDS_DOC تعریف formal
۲۲ Dominance READY_NEEDS_DOC —
۲۳/۲۴ Kitchen READY_NEEDS_DOC وزن‌دهی
۲۵ Kitchen MC READY_NEEDS_DOC از upstream
۲۶ Coverage READY_NEEDS_DOC فرمول
۲۷ Ranking READY_NEEDS_DOC —
۲۸ Grouping READY_NEEDS_DOC —
۲۹ Dominance READY_NEEDS_DOC —
۳۰ Snapshot READY_NEEDS_DOC —

جمع: ۵ READY · ۱۲ READY_NEEDS_DOC · ۵ PARTIAL · ۱ BLOCKED · ۵ نیازمند تست مستقل.

Section 4 — PENDING واقعی (۵ — Coinbase P0 حل شد)

# تست P مالک وضعیت
۱ Coinbase full scan (۱۵۰ asset، ۶ ماهه، USD+USDT) P0 TD ⏳ در حال نوشتن
۲ Bitstamp pair mapping retest (۵ diag) P0 TD ⏳ موازی
۳ Coinbase BTC-USDT pair (تاریخ شروع) P1 TD — (در full scan پوشش)
۴ WS Binance/Bybit P2 TD —
۵ ۷ CMC ID (/search — endpoint patch) P2 Extractor —
۶ USD1 DefiLlama P3 Extractor —

Section 5 — تصمیم‌های Owner

# تصمیم پیشنهاد تأیید شف
R-29 Universe نهایی CMC Top 150 → نمایش ۱۲۵ —
R-30 ۳۰m ذخیره یا on-demand on-demand —
R-31a DefiLlama/USD1 تست —
R-31b DefiLlama/۷ NO_DATA حذف —
R-32 RNDR UI: دو تاریخ یا effective_at تنها؟ Owner —
POL/Bybit Policy A (strict 2024-09-04) + ثبت test_date — —
BTC-USDC Coinbase حذف از scope — ✅ ۱۱ Nov
USDC-USD Coinbase حذف از scope — ✅ ۱۱ Nov
Coinbase quotes USD + USDT فقط — ✅ ۱۱ Nov

Section 6 — فایل‌های منتظر

# فایل مالک
۱ ۳ لاگ GitHub Actions (combined/comprehensive/crypto2) Patcher grep
۲ Item_13_Bootstrap.md ❌ placeholder — A8 BLOCKED
۳ cmc_fill_40.json (کامل) Extractor

Section 7 — شمارش نهایی

دسته تعداد
فعال (مرجع) ۳۰
آماتور (نگه‌داری) ۱۰
منسوخ ۱۶ + ۱ data_source
HOLD/PENDING/BLOCKED ۱۰
PENDING واقعی (تست) ۵ (۲ P0، ۱ P1، ۲ P2)
تصمیم Owner ۹ (۶ قبلی + ۳ جدید)

Section 8 — ۷ سؤال TD — پاسخ قطعی

# پاسخ شاهد
TD1 A8 وجود ندارد → BLOCKED Item_13 placeholder
TD2 A1/A2/A3 = professional_period چک‌پوینت ۷ Nov
TD3 Supply = دو منبع مکمل final_125 (۱۱۸) + A5 dict (۱۱۷)
TD4 POL/RENDER/S = CONFIRMED JSON oldest_ms + imprecise=false
TD5 RNDR = دو فیلد (effective_at + listing_dates) TD5
TD6 TEST001 = یک نسخه (app/market/test001/) A10 + adapters.py
TD7 ۷ NO_DATA = تأیید A7 JSON + final_125
TD8 Coinbase diagnostic = PASS ✅ 11 Nov

Section 9 — UNVERIFIED (صفر)

مورد قبلاً اکنون
S=2025-01-20 UNVERIFIED ✅ CONFIRMED
POL/RENDER UNVERIFIED ✅ CONFIRMED
A9 v3.2 UNVERIFIED ✅ EXISTS (3cd2cf0)
A1-A3 commits no_commit ✅ professional_period
A8 Bootstrap UNVERIFIED ✅ BLOCKED

UNVERIFIED باقی‌مانده: صفر. ✅

Section 10 — KMNO Patch Scope

cmc_id=32415 (قدیمی) در ۹ فایل:

1. tests/evidence/A6_A7_discovery_2026-11-08.json (بخش cmc_id_changes — اینجا درست 30986 در بخش جدا)
2. tests/evidence/asset_universe_master_2026-11-08.json → patch 32415→30986
3. tests/evidence/A6_A7_discovery_2026-11-08_summary.md → patch اگر ذکر شده
4. results/run_40351779336/final-125-supply-results/final_125_supply.json → patch
5. results/supply_timeseries/supply_timeseries_2026-11-07.json → patch
6. results/final_supply_harvest/run_40351779336/final-125-supply-results/final_125_supply.json → patch
7. docs/B_items/Item_15_Supply.md → patch
8. docs/check_points/2026-11-08_session1.md → تاریخی، نگه‌داری
9. tests/evidence/scripts/audit_2026-11-11.py → فقط در text (نه patch)

patch مورد نیاز: ۵ فایل (۲، ۴، ۵، ۶، ۷) + ۱ نگه‌داری (۸).

Section 11 — Item_05 Amendment Required (۴ باگ)

از دیدن Item_05_Canonical_Pairs.md v1.0:

# بند مشکل
۱ §۲.۱ «۱۲۵ دارایی Universe» — باید ۱۵۰ CMC شود (تصمیم ۹ Nov)
۲ §۳.۶ «Binance به‌عنوان rate source جایگزین» — باید با A9 v3.2 هم‌خوان شود (Binance BTC-pair دارد، OKX ندارد)
۳ §۱.۳ «Converted_fiat» نام قدیمی — باید به Direct_USD_Converted (۴ دسته) تغییر کند
۴ §۴ «۵ پارامتر معلق Stage B» — چون Item_05 LOCKED است، باید در همین سند بمانند، نه Stage B

Item_05_Pending_Amendments.md (۳۰ اکتبر) این ۴ باگ را در ۴ تغییر پوشش داده — ولی Amendment اعمال نشده (v1.0 LOCKED هنوز فعال است).

Section 12 — یافته‌های کلیدی audit (خلاصه)

# یافته شاهد
۱ A9 OKX v3.2 exists commit 3cd2cf0
۲ POL/RENDER/S CONFIRMED JSON oldest_ms + imprecise=false
۳ A6_A7 OKX Correction exists JSON کامل
۴ A8 Bootstrap BLOCKED Item_13 placeholder
۵ ۷ NO_DATA تأیید A7 JSON + final_125
۶ KMNO = 32415 (۹ فایل) A6 grep
۷ A5 timeseries dict ۱۱۷ کلید A4 audit
۸ pol_bybit launchTime=null، close=0.6314 (diff ۰.۱۴٪) A9 audit
۹ TEST001 در app/market/test001/ A10 audit
۱۰ Coinbase ۹ تست PASS + BTC-USDT online 11 Nov diagnostic
۱۱ BTC-USDC delisted + USDC-USD NOT_FOUND /products 11 Nov
۱۲ USDT-USD online → §۳.۶ قابل اجرا /products 11 Nov

---

پایان TEST_MAP v3.4 FINAL — همه یافته‌ها ثبت شد.

---

ذخیره (۲ گام)

گام ۱ — ذخیره در repo:

```bash
nano tests/TEST_MAP_v3.4_FINAL.md
```

کل سند بالا را پیست کن → Ctrl+O → Enter → Ctrl+X

گام ۲ — کامیت:

```bash
git add tests/TEST_MAP_v3.4_FINAL.md && git commit -m "docs(TEST_MAP): v3.4 FINAL — 12 Nov 2026, all findings registered (audit + Coinbase diagnostic)" && git push
```

---

بعد از این: هر تست جدید (Coinbase full scan، Bitstamp diagnostic) → فقط patch به همین فایل → نه بازنویسی. طبق دستور شف.
