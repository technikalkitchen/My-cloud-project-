TEST_MAP v3.4 FINAL — Purpose-Driven Registry

تاریخ: ۱۱ نوامبر ۲۰۲۶ | ساعت: ~۱۹:۲۵ تهران | سشن: ۱
منبع: ۸ چک‌پوینت + ۸ دسته بازبینی + TD-01 + audit_2026-11-11 + Coinbase Diagnostic (11 Nov)
وضعیت: FINAL — ۹ patch TD+Extractor اعمال‌شده

این فایل TEST_MAP است. برای ساختار ۳۰ آیتم → docs/MAP.md v1.1. برای قوانین و CINها → docs/B_items/Cross_Item_Notes.md. برای محتوای هر آیتم → docs/B_items/Item_XX_*.md. برای شواهد تست → tests/evidence/.

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
A5 Supply timeseries Q7 ۱۵، ۱۹، ۲۵ d0fd6dd dict ۱۱۷ کلید (PROVISIONAL — pending 7 NO_DATA fix)، ۱۳.۱۷MB
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
audit_2026-11-11 همه همه commit 8998ecf پاسخ ۷ سؤال باز
Coinbase Diagnostic (11 Nov) Q1، Q6 ۰۱، ۰۳، ۰۵ commit 8998ecf ۹ تست — READY for full scan
Coinbase /products (11 Nov) Q1، Q6 ۰۱، ۰۵ uncommitted BTC-USD online · BTC-USDT online · USDT-USD online

تفاوت ۱۱۷ vs ۱۱۸: A5 = ۱۱۷ کلید (USD1 با ۵۰۲ error شکست خورد)؛ final_125_supply = ۱۱۸ FILLED. تفاوت فقط USD1 است.

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

منبع A9 cmc_ids: cmc_top150_2026-11-08.json (CMC listing، ۸ Nov) — authoritative. final_125_supply.json با cmc_idهای اشتباه ساخته شده.

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

Section 2.10 — File Paths Reference

فایل | مسیر
A5 Supply | results/supply_timeseries/supply_timeseries_2026-11-07.json
final_125_supply | results/final_supply_harvest/run_40351779336/final-125-supply-results/final_125_supply.json
asset_universe_master | tests/evidence/asset_universe_master_2026-11-08.json
cmc_top150 | tests/evidence/cmc_top150_2026-11-08.json
A6_A7 Discovery | tests/evidence/A6_A7_discovery_2026-11-08.json
A6_A7 OKX Correction | tests/evidence/A6_A7_okx_correction_2026-11-09.json
A9 Binance v2 | tests/evidence/a9_binance_2026-11-08.json (commit b45bce0)
A9 Bybit v2 | tests/evidence/a9_bybit_2026-11-08.json (commit b45bce0)
A9 Bitstamp v2 | tests/evidence/a9_bitstamp_2026-11-08.json (commit b45bce0)
a9_asset_start_dates | tests/evidence/a9_asset_start_dates_2026-11-08.json
A9 OKX | tests/evidence/a9_okx_2026-11-09.json
A9 OKX v3.2 | tests/evidence/a9_okx_v3_2026-11-09.json
A9 OKX USDC retry | tests/evidence/a9_okx_usdc_retry_2026-11-09.json
POL Bybit Test | tests/evidence/pol_bybit_test_2026-11-08.json
A4 OHLCV Format | tests/evidence/2026-11-07_A4_OHLCV_Format.md
audit_2026-11-11 | tests/evidence/audit_2026-11-11.json + .md
Coinbase Diagnostic | tests/evidence/scripts/coinbase_btc_diagnostic.py
Cross_Item_Notes | docs/B_items/Cross_Item_Notes.md
MAP | docs/MAP.md
TEST_MAP v2.1 | tests/TEST_MAP.md — SUPERSEDED با v3.4

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
۳ Coinbase BTC-USDT pair date P1 TD تاریخ دقیق نامشخص (قطعاً بعد از June 2020، شاهد: t4=0)
۴ WS Binance/Bybit P2 TD Script not written
۵ ۷ CMC ID P2 Extractor /search endpoint patch لازم
۶ USD1 DefiLlama P3 Extractor Script not written

Section 5 — تصمیم‌های Owner

R-29 — Universe نهایی

· متن: CMC Top 150 → حذف Wrapped → نمایش ۱۲۵ خالص
· اثر: Item_03 §۲.۱، Item_27 | تصمیم: Owner | تاریخ: ۹ Nov | وضعیت: APPROVED
- **لیست ۲۵ دارایی حذف‌شده (Wrapped):** PENDING (Extractor در سشن بعد لیست ۲۵تایی را استخراج و ثبت می‌کند).

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

R-12a، R-12b، R-26، R-27، R-28 — Protocol rules (Patcher HOLD)

توجه: این ۵ R در Cross_Item_Notes v1.0 (R-01..R-25) نیستند. در TEST_MAP ثبت موقت می‌شوند تا Patcher در Cross_Item_Notes ثبت کند.

R-12a — شواهد بزرگ | متن: فایل‌های >۱۰MB در results/ با git add -f؛ <۱۰MB در tests/evidence/ | دلیل: A5 (۱۳MB) نیازمند -f بود | وضعیت: RESOLVED

R-12b — اسکریپت‌ها در repo | متن: اسکریپت‌های تست در tests/evidence/scripts/ — نه /tmp | دلیل: /tmp سه بار پاک شد | وضعیت: RESOLVED

R-26 — Diagnostic First | متن: قبل از هر اجرای multi-exchange، ۵-۱۰ تست BTC per-exchange | دلیل: A9 v2 (بدون diagnostic) → ۰/۱۵۰ → ۴۰ دقیقه اتلاف | وضعیت: RESOLVED

R-27 — Save تدریجی | متن: اسکریپت‌های >۵ دقیقه، save per-10-asset | دلیل: A9 v2 (۴۰ دقیقه) — ریسک از دست دادن با قطع VPN | وضعیت: RESOLVED

R-28 — Return-type sync | متن: تغییر return type تابع → همه callerها آپدیت | دلیل: A9 OKX v3.1 (walk_back_quote tuple→dict) → diagnostic خطا | وضعیت: RESOLVED

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
۲ §3.6 «... منابع جایگزین (مانند Binance)» «Coinbase USDT-USD آنلاین (۱۱ Nov) → same-exchange rate. Binance fallback فقط اگر USDT-USD در صرافی مبدأ نبود» Coinbase Diagnostic t8، ۱۱ Nov
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
---

## Appendix — Self-Sufficiency Lists (v3.4.2)

**تاریخ:** ۱۱ نوامبر ۲۰۲۶
**منبع:** JSONهای repo (نه از حافظه)
**هدف:** دستیار جدید بدون باز کردن فایل‌های تست به آیتم‌های ۰۱، ۰۳، ۱۵، ۱۹، ۲۵ دسترسی دارد.

### Appendix A — A9 Per-Exchange Coverage

**منبع:** `a9_okx_2026-11-09.json` (OKX — 105/150 TESTED، USDT+USD+USDC) + `a9_asset_start_dates_2026-11-08.json` (Binance/Bybit/Bitstamp)

**کاوئات‌ها:**

- **OKX:** ۱۰۵/۱۵۰ TESTED (نسخه a9_okx، جایگزین باگ a9_asset_start_dates). ۴۵ NOT_LISTED با USDT+USD+USDC هر سه تأیید شد.
- **Bitstamp:** ۸۵/۱۵۰ TESTED (پس از اجرای A9 Bitstamp full در ۱۱ Nov). ۶۵ NOT_LISTED واقعی (در USDT/USD/BTC چک شد).
- **Binance/Bybit:** ۱۱۴/۱۵۰ و ۱۲۱/۱۵۰ TESTED. مقادیر NOT_FOUND با کوئوت‌های محدود (USDT/USD) تست شده‌اند.
- **Coinbase:** ۹۹/۱۵۰ TESTED (22 Direct USDT, 77 Converted USD از USDT-USD 2021-05-04). ۵۱ NOT_LISTED.

- **TESTED:** داده تأیید شد.
- **NOT_LISTED:** صرافی ندارد (همه quoteها تست شدند).
- **NOT_FOUND:** تست شد با quote محدود (USDT/USD) — A9 v3 (BTC/USD) pending.
- **PENDING_RETEST:** pair bug (Bitstamp) — P0.

| Symbol | OKX | Binance | Bybit | Bitstamp | Coinbase |
|---|---|---|---|---|---|
| AAVE | TESTED | TESTED | TESTED | TESTED | TESTED |
| ADA | TESTED | TESTED | TESTED | TESTED | TESTED |
| AERO | NOT_LISTED | TESTED | TESTED | TESTED | TESTED |
| AKT | NOT_LISTED | NOT_FOUND | NOT_FOUND | NOT_LISTED | TESTED |
| ALGO | TESTED | TESTED | TESTED | TESTED | TESTED |
| APT | TESTED | TESTED | TESTED | TESTED | TESTED |
| AR | TESTED | TESTED | TESTED | NOT_LISTED | NOT_LISTED |
| ARB | TESTED | TESTED | TESTED | TESTED | TESTED |
| ASTER | TESTED | TESTED | TESTED | TESTED | TESTED |
| ATOM | TESTED | TESTED | TESTED | TESTED | TESTED |
| AVAX | TESTED | TESTED | TESTED | TESTED | TESTED |
| AXS | TESTED | TESTED | TESTED | TESTED | TESTED |
| BAT | TESTED | TESTED | TESTED | TESTED | TESTED |
| BCH | TESTED | TESTED | TESTED | TESTED | TESTED |
| BEAM | NOT_LISTED | TESTED | TESTED | NOT_LISTED | TESTED |
| BGB | NOT_LISTED | NOT_FOUND | NOT_FOUND | NOT_LISTED | NOT_LISTED |
| BNB | TESTED | TESTED | TESTED | TESTED | TESTED |
| BONK | TESTED | TESTED | TESTED | TESTED | TESTED |
| BSV | NOT_LISTED | NOT_FOUND | NOT_FOUND | NOT_LISTED | NOT_LISTED |
| BTC | TESTED | TESTED | TESTED | TESTED | TESTED |
| BTT | NOT_LISTED | TESTED | TESTED | NOT_LISTED | NOT_LISTED |
| CAKE | NOT_LISTED | TESTED | TESTED | NOT_LISTED | TESTED |
| CAP | NOT_LISTED | NOT_FOUND | TESTED | NOT_LISTED | TESTED |
| CC | TESTED | NOT_FOUND | TESTED | TESTED | NOT_LISTED |
| CFX | TESTED | TESTED | NOT_FOUND | NOT_LISTED | NOT_LISTED |
| COMP | TESTED | TESTED | TESTED | TESTED | TESTED |
| CRO | TESTED | NOT_FOUND | NOT_FOUND | NOT_LISTED | TESTED |
| CRV | TESTED | TESTED | TESTED | TESTED | TESTED |
| CVX | TESTED | TESTED | NOT_FOUND | NOT_LISTED | TESTED |
| DAI | NOT_LISTED | TESTED | TESTED | NOT_LISTED | NOT_LISTED |
| DASH | TESTED | TESTED | TESTED | NOT_LISTED | TESTED |
| DCR | NOT_LISTED | TESTED | TESTED | NOT_LISTED | NOT_LISTED |
| DOGE | TESTED | TESTED | TESTED | TESTED | TESTED |
| DOT | TESTED | TESTED | TESTED | TESTED | TESTED |
| EIGEN | TESTED | TESTED | TESTED | TESTED | TESTED |
| ENA | TESTED | TESTED | TESTED | TESTED | TESTED |
| ENS | TESTED | TESTED | TESTED | NOT_LISTED | TESTED |
| ETC | TESTED | TESTED | TESTED | TESTED | TESTED |
| ETH | TESTED | TESTED | TESTED | TESTED | TESTED |
| ETHFI | TESTED | TESTED | TESTED | NOT_LISTED | TESTED |
| EURC | NOT_LISTED | NOT_FOUND | NOT_FOUND | NOT_LISTED | NOT_LISTED |
| FDUSD | NOT_LISTED | TESTED | NOT_FOUND | NOT_LISTED | NOT_LISTED |
| FET | TESTED | TESTED | TESTED | TESTED | TESTED |
| FF | NOT_LISTED | TESTED | TESTED | NOT_LISTED | NOT_LISTED |
| FIL | TESTED | TESTED | TESTED | NOT_LISTED | TESTED |
| FLOKI | TESTED | TESTED | TESTED | TESTED | TESTED |
| FLR | TESTED | NOT_FOUND | TESTED | TESTED | TESTED |
| FLUID | TESTED | NOT_FOUND | TESTED | NOT_LISTED | TESTED |
| GNO | NOT_LISTED | TESTED | NOT_FOUND | NOT_LISTED | TESTED |
| GOMINING | NOT_LISTED | NOT_FOUND | NOT_FOUND | NOT_LISTED | NOT_LISTED |
| GRAM | TESTED | TESTED | TESTED | TESTED | NOT_LISTED |
| GRT | TESTED | TESTED | TESTED | TESTED | TESTED |
| GT | NOT_LISTED | NOT_FOUND | NOT_FOUND | NOT_LISTED | NOT_LISTED |
| HBAR | TESTED | TESTED | TESTED | TESTED | TESTED |
| HYPE | TESTED | TESTED | TESTED | TESTED | TESTED |
| ICP | TESTED | TESTED | TESTED | TESTED | TESTED |
| IMX | TESTED | TESTED | TESTED | TESTED | TESTED |
| INJ | TESTED | TESTED | TESTED | TESTED | TESTED |
| IOTA | TESTED | TESTED | NOT_FOUND | NOT_LISTED | NOT_LISTED |
| JASMY | NOT_LISTED | TESTED | TESTED | NOT_LISTED | TESTED |
| JST | NOT_LISTED | TESTED | TESTED | NOT_LISTED | NOT_LISTED |
| JTO | TESTED | TESTED | TESTED | TESTED | TESTED |
| JUP | TESTED | TESTED | TESTED | TESTED | NOT_LISTED |
| KAIA | TESTED | TESTED | TESTED | NOT_LISTED | NOT_LISTED |
| KAS | NOT_LISTED | NOT_FOUND | TESTED | NOT_LISTED | NOT_LISTED |
| KCS | NOT_LISTED | NOT_FOUND | TESTED | NOT_LISTED | NOT_LISTED |
| KITE | TESTED | TESTED | NOT_FOUND | NOT_LISTED | TESTED |
| KMNO | TESTED | TESTED | TESTED | NOT_LISTED | TESTED |
| LDO | TESTED | TESTED | TESTED | TESTED | TESTED |
| LEO | TESTED | NOT_FOUND | NOT_FOUND | NOT_LISTED | NOT_LISTED |
| LINK | TESTED | TESTED | TESTED | TESTED | TESTED |
| LIT | TESTED | TESTED | TESTED | TESTED | NOT_LISTED |
| LTC | TESTED | TESTED | TESTED | TESTED | TESTED |
| LUNC | NOT_LISTED | TESTED | TESTED | NOT_LISTED | NOT_LISTED |
| M | NOT_LISTED | NOT_FOUND | NOT_FOUND | NOT_LISTED | NOT_LISTED |
| MANA | TESTED | TESTED | TESTED | TESTED | TESTED |
| MET | TESTED | TESTED | TESTED | NOT_LISTED | TESTED |
| MNT | NOT_LISTED | NOT_FOUND | TESTED | TESTED | NOT_LISTED |
| MON | TESTED | NOT_FOUND | TESTED | TESTED | TESTED |
| MORPHO | TESTED | TESTED | TESTED | TESTED | TESTED |
| NEAR | TESTED | TESTED | TESTED | TESTED | TESTED |
| NEXO | NOT_LISTED | TESTED | TESTED | NOT_LISTED | NOT_LISTED |
| NFT | TESTED | NOT_FOUND | TESTED | NOT_LISTED | NOT_LISTED |
| NIGHT | TESTED | TESTED | TESTED | NOT_LISTED | NOT_LISTED |
| OKB | TESTED | NOT_FOUND | NOT_FOUND | NOT_LISTED | NOT_LISTED |
| ONDO | TESTED | TESTED | TESTED | TESTED | TESTED |
| OP | TESTED | TESTED | TESTED | TESTED | TESTED |
| PAXG | TESTED | TESTED | TESTED | TESTED | TESTED |
| PENDLE | TESTED | TESTED | TESTED | NOT_LISTED | TESTED |
| PENGU | TESTED | TESTED | TESTED | TESTED | TESTED |
| PEPE | TESTED | TESTED | TESTED | TESTED | TESTED |
| PI | TESTED | NOT_FOUND | NOT_FOUND | NOT_LISTED | NOT_LISTED |
| PIEVERSE | NOT_LISTED | NOT_FOUND | TESTED | NOT_LISTED | NOT_LISTED |
| POL | TESTED | TESTED | TESTED | TESTED | TESTED |
| PUMP | TESTED | TESTED | TESTED | NOT_LISTED | TESTED |
| PYTH | TESTED | TESTED | TESTED | TESTED | TESTED |
| PYUSD | TESTED | NOT_FOUND | TESTED | TESTED | NOT_LISTED |
| QNT | NOT_LISTED | TESTED | TESTED | TESTED | TESTED |
| RAY | TESTED | TESTED | NOT_FOUND | TESTED | TESTED |
| RENDER | TESTED | TESTED | TESTED | TESTED | TESTED |
| RLUSD | TESTED | TESTED | TESTED | TESTED | NOT_LISTED |
| RUNE | NOT_LISTED | TESTED | TESTED | NOT_LISTED | NOT_LISTED |
| SEI | TESTED | TESTED | TESTED | TESTED | TESTED |
| SHIB | TESTED | TESTED | TESTED | TESTED | TESTED |
| SKY | TESTED | TESTED | TESTED | TESTED | TESTED |
| SOL | TESTED | TESTED | TESTED | TESTED | TESTED |
| SOON | NOT_LISTED | NOT_FOUND | NOT_FOUND | NOT_LISTED | NOT_LISTED |
| SPX | NOT_LISTED | NOT_FOUND | TESTED | NOT_LISTED | TESTED |
| STABLE | NOT_LISTED | NOT_FOUND | TESTED | NOT_LISTED | TESTED |
| STRK | TESTED | TESTED | TESTED | TESTED | TESTED |
| STX | TESTED | TESTED | TESTED | NOT_LISTED | TESTED |
| SUI | TESTED | TESTED | TESTED | TESTED | TESTED |
| SUN | NOT_LISTED | TESTED | TESTED | NOT_LISTED | NOT_LISTED |
| SYRUP | NOT_LISTED | TESTED | NOT_FOUND | TESTED | TESTED |
| TAO | TESTED | TESTED | NOT_FOUND | TESTED | TESTED |
| TEL | NOT_LISTED | NOT_FOUND | TESTED | NOT_LISTED | NOT_LISTED |
| THETA | TESTED | TESTED | TESTED | NOT_LISTED | NOT_LISTED |
| TIA | TESTED | TESTED | TESTED | NOT_LISTED | TESTED |
| TRAC | NOT_LISTED | NOT_FOUND | NOT_FOUND | TESTED | TESTED |
| TRUMP | TESTED | TESTED | TESTED | TESTED | TESTED |
| TRX | TESTED | TESTED | TESTED | TESTED | NOT_LISTED |
| TUSD | NOT_LISTED | TESTED | TESTED | NOT_LISTED | NOT_LISTED |
| TWT | NOT_LISTED | TESTED | TESTED | NOT_LISTED | NOT_LISTED |
| U | NOT_LISTED | TESTED | TESTED | NOT_LISTED | NOT_LISTED |
| UNI | TESTED | TESTED | TESTED | TESTED | TESTED |
| USD1 | TESTED | TESTED | TESTED | NOT_LISTED | TESTED |
| USDC | TESTED | TESTED | TESTED | TESTED | NOT_LISTED |
| USDD | NOT_LISTED | NOT_FOUND | TESTED | NOT_LISTED | NOT_LISTED |
| USDG | TESTED | NOT_FOUND | NOT_FOUND | TESTED | NOT_LISTED |
| USDT | TESTED | TESTED | TESTED | TESTED | TESTED |
| USDe | NOT_LISTED | NOT_FOUND | NOT_FOUND | NOT_LISTED | NOT_LISTED |
| VET | NOT_LISTED | TESTED | TESTED | NOT_LISTED | TESTED |
| VIRTUAL | TESTED | TESTED | TESTED | TESTED | TESTED |
| VVV | TESTED | NOT_FOUND | TESTED | TESTED | TESTED |
| WIF | TESTED | TESTED | TESTED | TESTED | TESTED |
| WLD | TESTED | TESTED | TESTED | TESTED | TESTED |
| WLFI | TESTED | TESTED | TESTED | TESTED | TESTED |
| XAUt | NOT_LISTED | NOT_FOUND | NOT_FOUND | NOT_LISTED | NOT_LISTED |
| XCN | NOT_LISTED | NOT_FOUND | NOT_FOUND | TESTED | TESTED |
| XDC | NOT_LISTED | NOT_FOUND | TESTED | TESTED | NOT_LISTED |
| XLM | TESTED | TESTED | TESTED | TESTED | TESTED |
| XMR | NOT_LISTED | TESTED | NOT_FOUND | NOT_LISTED | NOT_LISTED |
| XPL | TESTED | TESTED | TESTED | TESTED | TESTED |
| XRP | TESTED | TESTED | TESTED | TESTED | TESTED |
| XTZ | TESTED | TESTED | TESTED | TESTED | TESTED |
| ZAMA | TESTED | TESTED | TESTED | NOT_LISTED | TESTED |
| ZBCN | TESTED | NOT_FOUND | NOT_FOUND | NOT_LISTED | NOT_LISTED |
| ZEC | TESTED | TESTED | TESTED | TESTED | TESTED |
| ZRO | TESTED | TESTED | TESTED | TESTED | TESTED |
| 币安人生 | NOT_LISTED | NOT_FOUND | NOT_FOUND | NOT_LISTED | NOT_LISTED |

**جمع:** 150 asset

### Appendix B — A5 Supply Dates (۱۱۷ asset)

**منبع:** `results/supply_timeseries/supply_timeseries_2026-11-07.json`

**کاوئات:**
- `available_from` = اولین تاریخ داده در CMC است (NOT actual launch date). مثال: SOL=2021-01-01 (CMC)، ولی listing بایننس=2020-08.
- **تفکیک مسئولیت:** Item_15 (Supply Engine) از این مقادیر استفاده می‌کند. Item_03 (Universe) باید از `listing_date` در Item_04 استفاده کند.
- **ریاضی ۱۱۷:** `۱۱۷ = ۱۲۵ - ۷ (NO_DATA با cmc_id اشتباه) - ۱ (USD1 با خطای 502 در A5)`.
- ۷ NO_DATA در این لیست نیستند. Fix: A5 retry با Appendix C cmc_ids.

**کاوئات:** `available_from` = اولین date سری روزانه (دقت ۱ روز).

| Symbol | available_from |
|---|---|
| AAVE | 2021-01-01 |
| ADA | 2018-01-01 |
| AERO | 2024-01-01 |
| ALGO | 2020-01-01 |
| APT | 2023-01-01 |
| AR | 2021-01-01 |
| ARB | 2024-01-01 |
| ASTER | 2026-01-01 |
| ATOM | 2020-01-01 |
| AVAX | 2021-01-01 |
| BCH | 2018-01-01 |
| BGB | 2023-01-01 |
| BNB | 2018-01-01 |
| BONK | 2024-01-01 |
| BSV | 2019-01-01 |
| BTC | 2017-01-01 |
| BTT | 2023-01-01 |
| CAKE | 2021-01-01 |
| CC | 2026-01-01 |
| CFX | 2022-01-01 |
| CRO | 2019-01-01 |
| CRV | 2021-01-01 |
| CVX | 2022-01-01 |
| DAI | 2021-01-01 |
| DASH | 2017-01-01 |
| DCR | 2017-01-01 |
| DOGE | 2017-01-01 |
| DOT | 2021-01-01 |
| ENA | 2024-07-01 |
| ENS | 2022-01-01 |
| ETC | 2017-01-01 |
| ETH | 2017-01-01 |
| ETHFI | 2024-07-01 |
| EURC | 2023-01-01 |
| FDUSD | 2024-01-01 |
| FET | 2020-01-01 |
| FIL | 2021-01-01 |
| FLR | 2024-01-01 |
| GNO | 2018-01-01 |
| GRAM | 2022-01-01 |
| GRT | 2021-01-01 |
| GT | 2020-01-01 |
| HBAR | 2020-01-01 |
| HYPE | 2025-01-01 |
| ICP | 2022-01-01 |
| IMX | 2022-01-01 |
| INJ | 2021-01-01 |
| JST | 2021-01-01 |
| JTO | 2024-01-01 |
| JUP | 2024-07-01 |
| KAIA | 2024-01-01 |
| KAS | 2023-01-01 |
| KCS | 2018-01-01 |
| KMNO | 2025-01-01 |
| LDO | 2022-01-01 |
| LEO | 2020-01-01 |
| LINK | 2018-01-01 |
| LIT | 2026-01-01 |
| LTC | 2017-01-01 |
| LUNC | 2020-01-01 |
| M | 2026-01-01 |
| MNT | 2024-01-01 |
| MORPHO | 2025-01-01 |
| NEAR | 2021-01-01 |
| NEXO | 2019-01-01 |
| NIGHT | 2026-01-01 |
| OKB | 2020-01-01 |
| ONDO | 2024-07-01 |
| OP | 2023-01-01 |
| PAXG | 2020-01-01 |
| PENDLE | 2022-01-01 |
| PENGU | 2025-01-01 |
| PEPE | 2024-01-01 |
| PI | 2025-07-01 |
| POL | 2024-01-01 |
| PUMP | 2026-01-01 |
| PYTH | 2024-01-01 |
| PYUSD | 2024-01-01 |
| QNT | 2019-01-01 |
| RAY | 2022-01-01 |
| RENDER | 2021-01-01 |
| RLUSD | 2025-07-01 |
| SEI | 2024-01-01 |
| SHIB | 2022-01-01 |
| SKY | 2025-07-01 |
| SOL | 2021-01-01 |
| STABLE | 2026-01-01 |
| STRK | 2024-07-01 |
| STX | 2021-01-01 |
| SUI | 2024-01-01 |
| SUN | 2022-01-01 |
| TAO | 2024-01-01 |
| TIA | 2024-01-01 |
| TRUMP | 2025-07-01 |
| TRX | 2018-01-01 |
| TUSD | 2019-01-01 |
| U | 2026-01-01 |
| UNI | 2021-01-01 |
| USDC | 2019-01-01 |
| USDD | 2023-01-01 |
| USDG | 2025-01-01 |
| USDT | 2017-01-01 |
| USDe | 2024-01-01 |
| VET | 2019-01-01 |
| VIRTUAL | 2024-01-01 |
| VVV | 2025-07-01 |
| WLD | 2024-01-01 |
| WLFI | 2026-01-01 |
| XAUT | 2022-01-01 |
| XDC | 2019-01-01 |
| XLM | 2017-01-01 |
| XMR | 2017-01-01 |
| XRP | 2017-01-01 |
| XTZ | 2019-01-01 |
| ZEC | 2017-01-01 |
| ZRO | 2024-07-01 |
| 币安人生 | 2026-01-01 |

**جمع:** 117 asset

### Appendix C — CMC Top 150

**منبع:** `tests/evidence/cmc_top150_2026-11-08.json` (CMC listing، ۸ Nov) — authoritative.
**کاوئات:** CMC IDs از A9 (authoritative) هستند، نه از `final_125_supply`. تفاوت ۷ مورد در Section 2.2.5.
⚠️ Rank 82 (币安人生، CMC 38590): نیازمند تأیید. اگر meme coin واقعی نیست، حذف شود.

| Rank | Symbol | CMC ID |
|---|---|---|
| 1 | BTC | 1 |
| 2 | ETH | 1027 |
| 3 | USDT | 825 |
| 4 | BNB | 1839 |
| 5 | XRP | 52 |
| 6 | USDC | 3408 |
| 7 | SOL | 5426 |
| 8 | TRX | 1958 |
| 9 | ZEC | 1437 |
| 10 | HYPE | 32196 |
| 11 | XMR | 328 |
| 12 | DOGE | 74 |
| 13 | LEO | 3957 |
| 14 | LINK | 1975 |
| 15 | ADA | 2010 |
| 16 | XLM | 512 |
| 17 | USDe | 29470 |
| 18 | BCH | 1831 |
| 19 | NEAR | 6535 |
| 20 | DAI | 4943 |
| 21 | UNI | 7083 |
| 22 | LTC | 2 |
| 23 | CC | 37263 |
| 24 | AVAX | 5805 |
| 25 | SUI | 20947 |
| 26 | USD1 | 36148 |
| 27 | XAUt | 5176 |
| 28 | GRAM | 11419 |
| 29 | HBAR | 4642 |
| 30 | PYUSD | 27772 |
| 31 | USDG | 33793 |
| 32 | RLUSD | 34387 |
| 33 | TAO | 22974 |
| 34 | SHIB | 5994 |
| 35 | CRO | 3635 |
| 36 | QNT | 3155 |
| 37 | OKB | 3897 |
| 38 | PEPE | 24478 |
| 39 | ENA | 30171 |
| 40 | AAVE | 7278 |
| 41 | ASTER | 36341 |
| 42 | M | 35491 |
| 43 | PAXG | 4705 |
| 44 | ONDO | 21159 |
| 45 | PUMP | 36507 |
| 46 | U | 39120 |
| 47 | DOT | 6636 |
| 48 | USDD | 19891 |
| 49 | SKY | 33038 |
| 50 | MNT | 27075 |
| 51 | WLFI | 33251 |
| 52 | ICP | 8916 |
| 53 | BGB | 11092 |
| 54 | WLD | 13502 |
| 55 | ARB | 11841 |
| 56 | JST | 5488 |
| 57 | MORPHO | 34104 |
| 58 | ETC | 1321 |
| 59 | GT | 4269 |
| 60 | VVV | 35509 |
| 61 | KCS | 2087 |
| 62 | POL | 28321 |
| 63 | ALGO | 4030 |
| 64 | PI | 35697 |
| 65 | KAS | 20396 |
| 66 | INJ | 7226 |
| 67 | RENDER | 5690 |
| 68 | LIT | 39125 |
| 69 | JUP | 29210 |
| 70 | ATOM | 3794 |
| 71 | NIGHT | 39064 |
| 72 | XDC | 2634 |
| 73 | FIL | 2280 |
| 74 | ZRO | 26997 |
| 75 | AERO | 29270 |
| 76 | STX | 4847 |
| 77 | CAKE | 7186 |
| 78 | DASH | 131 |
| 79 | ETHFI | 29814 |
| 80 | APT | 21794 |
| 81 | FLR | 7950 |
| 82 | 币安人生 | 38590 |
| 83 | PYTH | 28177 |
| 84 | TUSD | 2563 |
| 85 | RAY | 8526 |
| 86 | NEXO | 2694 |
| 87 | STABLE | 38892 |
| 88 | EURC | 20641 |
| 89 | PIEVERSE | 38849 |
| 90 | VET | 3077 |
| 91 | TIA | 22861 |
| 92 | CRV | 6538 |
| 93 | PENGU | 34466 |
| 94 | VIRTUAL | 29420 |
| 95 | BTT | 16086 |
| 96 | SEI | 23149 |
| 97 | FET | 3773 |
| 98 | TRUMP | 35336 |
| 99 | SPX | 28081 |
| 100 | BSV | 3602 |
| 101 | KITE | 38828 |
| 102 | FF | 38482 |
| 103 | STRK | 22691 |
| 104 | SUN | 10529 |
| 105 | GNO | 1659 |
| 106 | FDUSD | 26081 |
| 107 | XTZ | 2011 |
| 108 | PENDLE | 9481 |
| 109 | LDO | 8000 |
| 110 | XPL | 36645 |
| 111 | BONK | 23095 |
| 112 | IMX | 10603 |
| 113 | OP | 11840 |
| 114 | LUNC | 4172 |
| 115 | DCR | 1168 |
| 116 | CFX | 7334 |
| 117 | BEAM | 28298 |
| 118 | GRT | 6719 |
| 119 | AR | 5632 |
| 120 | FLOKI | 10804 |
| 121 | KAIA | 32880 |
| 122 | COMP | 5692 |
| 123 | KMNO | 30986 |
| 124 | MON | 30495 |
| 125 | NFT | 9816 |
| 126 | ENS | 13855 |
| 127 | RUNE | 4157 |
| 128 | AKT | 7431 |
| 129 | BAT | 1697 |
| 130 | FLUID | 10508 |
| 131 | ZBCN | 30636 |
| 132 | CVX | 9903 |
| 133 | JTO | 28541 |
| 134 | JASMY | 8425 |
| 135 | TWT | 5964 |
| 136 | TRAC | 2467 |
| 137 | MET | 38353 |
| 138 | ZAMA | 39332 |
| 139 | EIGEN | 30494 |
| 140 | IOTA | 1720 |
| 141 | SYRUP | 33824 |
| 142 | CAP | 40531 |
| 143 | WIF | 28752 |
| 144 | SOON | 36542 |
| 145 | GOMINING | 10180 |
| 146 | TEL | 2394 |
| 147 | AXS | 6783 |
| 148 | MANA | 1966 |
| 149 | THETA | 2416 |
| 150 | XCN | 18679 |

**جمع:** 150 asset

---

### Appendix D — A6 Migration/Delisted Per-Item

**منبع:** `A6_A7_discovery_2026-11-08.json` + `A6_A7_okx_correction_2026-11-09.json` + `a9_asset_start_dates_2026-11-08.json`

**کاوئات:**
- **FTT/LUNA/UST:** در Binance/Bybit از Top 125 خارج شده‌اند ولی هنوز active هستند (A6 discovery).
- **MATIC/RNDR/FTM (source):** OKX pair را rename کرده — sourceها NOT_LISTED، فقط target
- **Binance/Bybit:** هر دو source و target (dual-listing)
- **POL Bybit:** از 2023-10-25 (test_date)، launchTime=null — pre-migration alias

| Asset | Role | OKX | Binance | Bybit | Bitstamp | Coinbase |
|---|---|---|---|---|---|---|
| MATIC | migration_source (→POL) | NOT_LISTED | - | - | - | - |
| POL | migration_target (MATIC→) | TESTED 2024-09-03 | TESTED 2024-09-13 | TESTED 2023-10-25 | NOT_FOUND | NOT_FOUND |
| RNDR | migration_source (→RENDER، rename) | NOT_LISTED | - | - | - | - |
| RENDER | migration_target (RNDR→، rename) | TESTED 2024-07-14 | TESTED 2024-07-26 | TESTED 2024-07-31 | NOT_FOUND | NOT_FOUND |
| FTM | migration_source (→S) | NOT_LISTED | - | - | - | - |
| S | migration_target (FTM→) | TESTED 2025-01-20 | - | - | - | - |
| FTT | delisted | - | - | - | - | - |
| LUNA | delisted | - | - | - | - | - |
| UST | delisted | - | - | - | - | - |
| LUNC | survivor | NOT_FOUND | TESTED 2022-09-09 | TESTED 2021-10-27 | NOT_FOUND | NOT_FOUND |

**جمع:** ۱۰ asset (۶ migration + ۳ delisted + ۱ survivor)

### Appendix E — ExchangeCandleSchema (A4 CLOSED)

**منبع:** `tests/evidence/2026-11-07_A4_OHLCV_Format.md` (A4، ۷ Nov، commit 8c1f4d5 + 6320395)

**۵ ناسازگاری حیاتی:**
1. **Field order:** Coinbase `[ts, low, high, open, close, vol]` — معکوس
2. **۴ timestamp format:** ms+int / ms+str / s+int / s+str
3. **Coinbase price = float** (بقیه str)
4. **Direction:** asc (Binance/Bitstamp/CC) vs desc (OKX/Coinbase/Bybit)
5. **Field counts:** ۱۲/۹/۷/۶

**جدول کامل:**

| Exchange | field_order | ts_unit | ts_type | price_type | direction | field_count |
|---|---|---|---|---|---|---|
| Binance | [ts,o,h,l,c,v,...] | ms | int | str | asc | 12 |
| OKX | [ts,o,h,l,c,v,...] | ms | str | str | desc | 9 |
| Coinbase | [ts,**l**,**h**,**o**,c,v] | s | int | **num** | desc | 6 |
| Bitstamp | {timestamp,open,high,low,close,volume} | s | str | str | asc | 6 |
| Crypto.com | {t,o,h,l,c,v} | ms | int | str | asc | 6 |
| Bybit | [ts,o,h,l,c,v,turnover] | ms | str | str | desc | 7 |

**پیامد Item_16:** Adapter باید per-exchange parse کند. ExchangeCandleSchema مرجع اجباری است.


## Section 13 — Known Issues & Data Quality

| # | Issue | Status | Owner | Impacted Items |
|---|---|---|---|---|
| 1 | 7 NO_DATA wrong cmc_id | P2 | Extractor | ۰۳، ۱۵ |
| 2 | KMNO 32415 vs 30986 | P2 | patch | ۰۳، ۱۵ |
| 3 | Bitstamp pair bug (A9 v2) | ✅ RESOLVED | TD | ۰۱، ۰۳ |
| 4 | Coinbase BTC-USDT date unknown (قطعاً بعد از 2020) | P1 | TD | ۰۵ |
| 5 | RNDR two dates (policy vs listing) | Owner | — | ۰۴ |
| 6 | POL Bybit 11-month gap | Owner | — | ۰۴ |
| 7 | A1-A3 no_commit | R-12b | — | ۰۱، ۰۳، ۱۳ |
| 8 | 币安人生 (rank 82) verification needed | Extractor | — | ۰۳ |
| 9 | Coinbase column pending (Appendix A) | ✅ RESOLVED | TD | ۰۱، ۰۳ |
| 10 | Appendix B CMC limit caveat | Recorded | — | ۱۵ |
| 11 | 7 assets missing from Appendix B | P2 | Extractor | ۱۵ |
| 12 | Bitstamp only BTC verified | ✅ RESOLVED | TD | ۰۱ |
| 13 | 25 Wrapped assets for 150→125 filter | P2 | Extractor | ۰۳ |

**Note:** Issues 1, 2, 4, 5, 6, 7, 8, 11, 13 are DATA/DESIGN gaps (mostly P2/Owner), NOT test failures. They do not block Phase 1 (writing items).


## Section 14 — Verification Commands

**A9 OKX:**
```bash
git show 8e823f2 --stat
cat tests/evidence/a9_okx_2026-11-09.json | jq 'keys | length'  # expect: 150
```

**CMC Top 150:**
```bash
cat tests/evidence/cmc_top150_2026-11-08.json | jq '.assets | length'  # expect: 150
```

**Supply (A5):**
```bash
cat results/supply_timeseries/supply_timeseries_2026-11-07.json | jq 'keys | length'  # expect: 117
```
