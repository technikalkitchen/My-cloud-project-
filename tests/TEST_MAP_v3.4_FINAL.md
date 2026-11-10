۲ اصلاح پیدا کردم:

1. Section 3 line جمع — اشتباه بود: «۵ READY · ۱۲ READY_NEEDS_DOC» ولی جدول Section 3 و Section 7 می‌گوید ۶ READY · ۱۶ ردیف (۱۸ آیتم) READY_NEEDS_DOC.
2. A9 OKX v3.2 — commit v3.1 (edfa4c1) ثبت نشده بود، و «نیازمند اسکریپت» باید «نیازمند اجرای آمار» باشد (اسکریپت هست، فقط اجرا نشده).

متن کامل با اصلاحات:

---

TEST_MAP v3.4 FINAL — Purpose-Driven Registry

تاریخ: ۱۱ نوامبر ۲۰۲۶ | ساعت: ~۱۹:۲۵ تهران | سشن: ۱
منبع: ۸ چک‌پوینت + ۸ دسته بازبینی + TD-01 + audit_2026-11-11 + Coinbase Diagnostic (11 Nov)
وضعیت: FINAL — ۹ patch TD+Extractor اعمال‌شده

---

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
A9 OKX v3.2 Q6 ۰۵، ۱۸ 3cd2cf0 (v3.1=edfa4c1) EXISTS ✅ — BTC-pair: PENDING (نیازمند اجرای آمار)، USD: PENDING، USDT: ۱۰۵/۱۵۰. ETH BTC-pair=2018-01-10 (11 iter). BTC/USD=NOT_LISTED. effective_min changes=0
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

Reproduction note: A1-A3 اسکریپت در Repo ندارند (no_commit). خروجی‌ها در TEST_MAP v2.1 ثبت شده. برای بازتولید → TD باید بازنویسی کند (R-12b).

۲.۲ — A4: ۵ ناسازگاری (CLOSED)

# ناسازگاری
۱ Coinbase field order: [ts, low, high, open, close, vol]
۲ ۴ timestamp format: ms+int (Binance/CC) · ms+str (OKX/Bybit) · s+int (Coinbase) · s+str (Bitstamp)
۳ Coinbase price = float (بقیه string)
۴ Direction: asc (Binance/Bitstamp/CC) vs desc (OKX/Coinbase/Bybit)
۵ Field counts: ۱۲/۹/۷/۶

ExchangeCandleSchema = مرجع اجباری Item_16.

۲.۲.۵ — ۷ NO_DATA (A5، ۶ Nov — audit ۱۱ Nov)

Symbol CMC ID در final_125 CMC ID در A9 تفاوت
SPX 33203 28081 ⚠️ متناقض
XPL 37535 36645 ⚠️ متناقض
FF 39273 38482 ⚠️ متناقض
PIEVERSE 38543 38849 ⚠️ متناقض
KITE 39275 38828 ⚠️ متناقض
MON 38320 30495 ⚠️ متناقض
NFT 39003 9816 ⚠️ متناقض

کاوئات targeting (Extractor): این ۷ با cmc_id متناقض، احتمالاً دارایی اشتباه را در final_125_supply تست کرده‌اند. «NO_DATA» ≠ «عدم وجود داده در CMC» — بلکه «عدم داده برای این cmc_id». دارایی اصلی ممکن است داده داشته باشد.

اقدام P2: Extractor /search?keyword=X → تعیین cmc_id واقعی.

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

A10 = audit step ۱۰ (بررسی وجود app/market/test001/adapters.py) — نه تست جدا.

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

جمع: ۶ READY · ۱۶ READY_NEEDS_DOC (۱۸ آیتم) · ۵ PARTIAL · ۱ BLOCKED — ۳۰ آیتم

Section 4 — PENDING واقعی (۶)

# تست P مالک وضعیت دقیق
۱ Coinbase full scan P0 TD Script in TD hands (pending AM approval). JSON نه تولید شده.
۲ Bitstamp diagnostic P0 TD Script not yet written.
۳ Coinbase BTC-USDT pair date P1 TD (در full scan پوشش)
۴ WS Binance/Bybit P2 TD Script not written
۵ ۷ CMC ID P2 Extractor /search endpoint patch لازم
۶ USD1 DefiLlama P3 Extractor Script not written

Section 5 — تصمیم‌های Owner

R-29 — Universe نهایی

· متن: CMC Top 150 → حذف Wrapped → نمایش ۱۲۵ خالص
· اثر: Item_03 §۲.۱، Item_27 | تصمیم: Owner | تاریخ: ۹ Nov | وضعیت: APPROVED

R-30 — ۳۰m ذخیره یا on-demand

· متن: on-demand (نه ذخیره) | اثر: Item_06، Item_12، Item_16 | تاریخ: ۱۱ Nov | وضعیت: PROPOSED

R-31a — DefiLlama برای USD1

· متن: تست (تنها stablecoin بدون داده) | اثر: Item_15 | تاریخ: ۱۱ Nov | وضعیت: PROPOSED

R-31b — DefiLlama برای ۷ NO_DATA

· متن: حذف (این ۷ stablecoin نیستند) | اثر: Item_15 | تاریخ: ۱۱ Nov | وضعیت: PROPOSED

R-32 — RNDR UI: دو تاریخ یا effective_at تنها؟

· متن: Item_04 effective_at=2023-11-02 + listing_dates={binance:2024-07-22, okx:2024-07-14}. UI کدام؟
· اثر: Item_04، Item_27، Package D | تاریخ: ۱۱ Nov | وضعیت: OPEN (Owner)

تأییدهای ۱۱ Nov (بدون R جدید)

· BTC-USDC از Coinbase scope حذف (delisted)
· USDC-USD از Coinbase scope حذف (NOT_FOUND)
· Coinbase quotes = USD + USDT فقط
· POL/Bybit Policy A (strict 2024-09-04) + ثبت test_date=2023-10-25

Section 6 — فایل‌های منتظر

# فایل مالک
۱ ۳ لاگ GitHub Actions (combined/comprehensive/crypto2) Patcher grep
۲ Item_13_Bootstrap.md ❌ placeholder — A8 BLOCKED
۳ cmc_fill_40.json (کامل) Extractor

Section 7 — شمارش نهایی (۳۰ آیتم)

دسته ردیف آیتم
READY ۶ ۶
READY_NEEDS_DOC ۱۶ ۱۸
PARTIAL ۵ ۵
BLOCKED ۱ ۱
جمع ۲۸ ردیف ۳۰ آیتم

READY (۶): ۰۲، ۰۳، ۰۴، ۰۷، ۱۵، ۱۶
READY_NEEDS_DOC (۱۶ ردیف / ۱۸ آیتم): ۰۶، ۰۸، ۱۰، ۱۲، ۱۴، ۱۷، ۱۹، ۲۰، ۲۱، ۲۲، ۲۳، ۲۴، ۲۵، ۲۶، ۲۷، ۲۸، ۲۹، ۳۰
PARTIAL (۵): ۰۱، ۰۵، ۰۹، ۱۱، ۱۸
BLOCKED (۱): ۱۳

آمار تست‌ها

دسته تعداد
فعال ۳۰
آماتور ۱۰
منسوخ ۱۶ + ۱ data_source
PENDING واقعی ۶
تصمیم Owner ۹

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

KMNO cmc_id: 32415 → 30986

· تاریخ: نامعلوم | دلیل: نامعلوم — احتمالاً CMC re-listing یا symbol collision
· اقدام: Extractor تأیید (P2، در batch /search)
· patch (۵ فایل): asset_universe_master، final_125_supply ×۲، supply_timeseries، Item_15
· نگه‌داری (نه patch): A6_discovery (cmc_id_changes جدا)، checkpoint ۸ Nov

Section 11 — Item_05: ۴ باگ Amendment (LOCKED v1.0 → amendment)

# بخش قبل (v1.0) بعد (Amendment) مرجع
۱ §2.1 «USDT واحد مظنه استاندارد اصلی برای تمام ۱۲۵ دارایی Universe است» «برای ۱۵۰ دارایی CMC (نمایش ۱۲۵ خالص پس از حذف Wrapped)» R-29، ۹ Nov
۲ §3.6 «... منابع جایگزین (مانند Binance)» «Binance BTC-pair دارد (A9 v3.2، 3cd2cf0)، OKX ندارد. Binance به‌عنوان rate source جایگزین معتبر است، مشروط به ثبت rate_source» A9 v3.2
۳ §1.3 converted_fiat Direct_USD_Converted — ۴ دسته: Direct_USDT / Direct_BTC / Direct_USD_Converted / Implied Amendment ۳۰ Oct
۴ §4 «۵ پارامتر معلق Stage B» «۵ پارامتر در همین سند (LOCKED، نه Stage B)» LOCKED

مرجع: Item_05_Pending_Amendments.md (۳۰ Oct) — ۴ تغییر پوشش داده ولی اعمال نشده.

Section 12 — یافته‌های کلیدی audit (خلاصه)

# یافته شاهد
۱ A9 OKX v3.2 exists commit 3cd2cf0 (v3.1=edfa4c1)
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
