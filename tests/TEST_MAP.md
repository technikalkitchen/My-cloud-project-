فهرست جامع تست‌ها — سه پارت

بررسی TEST_MAP: تست‌مپ فقط ۱۳ فایل از ~۴۰ فایل را پوشش می‌دهد. کل دستهٔ Supply/CMC (۹ فایل + نتایج) در تست‌مپ غایب است. کل دستهٔ زیرساخت/اتصال (۷ فایل) هم غایب. کل دستهٔ TEST001/TEST003 (۶ فایل) هم غایب. پس جواب کوتاه: نه، تست‌مپ به‌روز و کامل نیست. فهرست زیر کار کامل و تمیز است.

---

A. تست‌های پوشش داده (Coverage)

نام مسیر وضعیت توضیح
2026-10-28_coverage_matrix.tsv tests/coverage/ ✅💎 ماتریس ۱۲۵×۵ با وضعیت LISTED/NOT_LISTED + ۴ timestamp (Binance, OKX, Bitstamp, Coinbase). ستون Crypto.com همیشه NOT_LISTED (باگ).
2026-10-28_5m_since_2017.tsv tests/coverage/ ✅💎 ماتریس ۱۵ دارایی × ۵ صرافی با تاریخ شروع 5m. Binance 2017-08-17، OKX 2026-10-28 (!)، Bitstamp/Coinbase 2017-01-01.
2026-10-28_test_real_check.txt tests/coverage/ ⚠️ ۶ سناریو تست تاریخ شروع. Binance ✅، Coinbase ✅، Bitstamp ✅، اما OKX در هر دو تست ❌ (داده برنگشت).
2026-10-28_okx_cc_test.txt tests/coverage/ ✅ تست وجود 5m در OKX و Crypto.com در بازه‌های ۲۰۱۸/۲۰۲۰/۲۰۲۲/۲۰۲۴ برای ۷ دارایی. OKX BTC: قبل ۲۰۱۸ = NO، قبل ۲۰۲۰ = YES.
2026-10-30_1h_1d_coverage.txt tests/coverage/ ⚠️ قدیمی‌ترین timestamp 1h و 1d در ۵ صرافی. OKX باگ پارامتر داشت و داده امروز (1793376000000) را برگرداند.

B. تست‌های Rate Limit و HTTP

نام مسیر وضعیت توضیح
2026-10-29_header_check.txt tests/rate_limit/ ✅ بررسی هدرها. فقط Binance هدر x-mbx-used-weight-1m دارد. بقیه هیچ هدر Rate Limit ندارند.
2026-10-29_binance_klines_weight.txt tests/rate_limit/ ✅💎 وزن endpoint کندل Binance با limit=1 (۱۰ درخواست). نتیجه قطعی: وزن هر درخواست = ۲، مستقل از limit و دارایی.
2026-10-29_binance_limit1000.txt tests/rate_limit/ ✅ تأیید: limit=1000 هم وزن ۲ دارد.
2026-10-29_binance_sol.txt tests/rate_limit/ ✅ تأیید: SOLUSDT هم وزن ۲ دارد. دارایی مهم نیست.
2026-10-29_okx_safe.txt tests/rate_limit/ ✅ ۳ درخواست ایمن به OKX (limit=1). همه HTTP 200 و okx_code=0.
2026-10-30_bitstamp_coinbase_cryptocom_safe.txt tests/rate_limit/ ✅ ۳ درخواست ایمن به Bitstamp/Coinbase/Crypto.com. Crypto.com هم BTC_USDT و هم BTC_USD را برگرداند (تعارض NOT_LISTED حل شد).
2026-10-30_okx_history_http.txt tests/rate_limit/ ✅ ۸۹ درخواست پی‌درپی OKX. صفر خطا. نرخ مؤثر 2.0 req/s.

C. تست‌های WebSocket

نام مسیر وضعیت توضیح
2026-10-30_okx_websocket_test.txt tests/rate_limit/ ❌ ناموفق. خطای 60018 برای کانال candle5m (استفاده از public به‌جای business endpoint).
2026-10-30_okx_websocket_test_v2.txt tests/rate_limit/ ✅ نسخه ۲ موفق. business endpoint. ۳ جفت: ۳۴/۲۷/۲۱ پیام در ۳۰ ثانیه.
2026-10-30_okx_websocket_all.txt tests/rate_limit/ ✅💎 ۸۹ جفت در ۲ بچ (۵۰+۳۹). ۸۹/۸۹ اشتراک. ۱۳۸۵ پیام در ۶۰ ثانیه. صفر خطا.
2026-10-30_coinbase_websocket_all.txt tests/rate_limit/ ✅💎 ۱۰۳ جفت در یک اتصال. ۱۰۳/۱۰۳ اشتراک. ۹۶۵۹ پیام در ۶۰ ثانیه. صفر خطا. کشف ۸۴ دارایی جدید.

D. تست‌های Supply / CMC (کاملاً غایب از TEST_MAP)

نام مسیر وضعیت توضیح
final_supply_harvest.yml .github/workflows/ ✅💎 harvest نهایی ۱۲۵ دارایی با CMC ID ثابت و ۱۲ checkpoint (۲۰۱۷–۲۰۲۶). خروجی: final_125_supply.json → ۱۱۸ FILLED / ۱۲۵.
verify_top125_supply.yml .github/workflows/ ✅💎 تأیید پوشش با ۸ checkpoint. خروجی: verification_results.json + top125_mapped.json. دسته‌بندی FULL/PARTIAL/UNAVAILABLE.
cmc_earliest_dates.yml .github/workflows/ ✅ قدیمی‌ترین تاریخ ۱۲۵ دارایی با ۸ checkpoint. خروجی: earliest_dates.json + cmc_ids.json.
cmc_fill_40.yml .github/workflows/ ✅ پر کردن ۴۰ UNAVAILABLE با CMC Top 500 mapping، ۶ checkpoint (۲۰۲۰–۲۰۲۵). خروجی: cmc_fill_40.json.
cmc_aggressive_fill.yml .github/workflows/ ✅ ۲۹ دارایی باقی‌مانده، checkpoint اضافی برای توکن‌های جدید (۲۰۲۴–۲۰۲۵). خروجی: aggressive_fill_29.json.
cmc_internal_extended.yml .github/workflows/ ✅ بررسی ساختار کامل CMC internal + ۱۵ دارایی × ۳ تاریخ + probe نرخ ۱۰ درخواست.
combined_supply_tests.yml .github/workflows/ ✅ ۳ job: CMC internal (v3 + v3.1)، پکیج coinmarketcap-scraper، DefiLlama stablecoins.
fill_gaps.yml .github/workflows/ ✅ پر کردن ۵۳ UNAVAILABLE از CoinGecko + DefiLlama. خروجی: fill_gaps_results.json.
verify_and_fill.yml .github/workflows/ ✅ تأیید ۱۲۵ + flag suspicious + retry CoinGecko برای ۴۰. خروجی: verify_125.json + coingecko_retry.json.

E. تست‌های زیرساخت، اتصال و RPC (غایب از TEST_MAP)

نام مسیر وضعیت توضیح
test_actions.yml .github/workflows/ ✅ پایه: تست GitHub Actions با echo.
test_external_api.yml .github/workflows/ ✅ DNS + دسترسی به Binance/Coinbase/Kraken.
test_comprehensive_data.yml .github/workflows/ ✅ جامع: Binance Global، عمق 1m/1h/1d، ۱۲ دارایی، مقایسه ۴ صرافی، اگریگیتورها، Gemini/Bitstamp.
test_cron_timing.yml .github/workflows/ ✅ ثبت UTC + run_id + actor. طبق TEST_MAP: تأخیر ۳ ثانیه.
test_historical_supply.yml .github/workflows/ ✅ totalSupply از RPC عمومی Ethereum (LINK/UNI/USDT/MATIC) در ۳ بلاک.
test_crypto2.yml .github/workflows/ ❌ تست بسته R crypto2. ناموفق (نسخه v2 برای رفع آن ساخته شد).
test_crypto2_v2.yml .github/workflows/ ⚠️ تلاش برای رفع با dplyr 1.0.10. خروجی برای BTC/LINK/USDT.

F. تست‌های TEST001 و TEST003 (غایب از TEST_MAP)

نام مسیر وضعیت توضیح
test001.py scripts/ ✅ CLI entry TEST001. بررسی موجود بودن جفت‌ها + اولین/آخرین کندل.
test001_manual.yml .github/workflows/ ✅ اجرای دستی TEST001 (۵ صرافی، TF 5m,1h).
test003_origin.py scripts/ ✅ تست مبدأ ۲۰۱۷ برای Binance/Bitstamp/Coinbase (1d).
test003_manual.yml .github/workflows/ ✅ اجرای دستی TEST003.
universe.json data/test001/ ✅ ۱۲۵ دارایی (فقط symbol). همان universe تست‌ها.
README_TEST001_stage2_2.md root 📖 راهنمای TEST001 MVP Stage 2.2.

G. ساختاری و متا

نام مسیر وضعیت توضیح
test_stage_a1_structure.py tests/ ✅ تست ساختاری Stage A1: پوشه‌ها، init، importهای ممنوع، runtime tokens.
2026-10-27_requirements.txt root ✅ فقط requests.
2026-10-27_summary.txt results/ (احتمالی) 📖 خلاصه ۱۳ فایل JSON نتایج تست‌ها با نوع و کلیدها.
TEST_MAP.md tests/ 📖 سند مرجع تست‌های واقعی ۲۸–۳۰ اکتبر. ناقص (فقط ۱۳ فایل).

H. نتایج تست‌ها (Artifacts — از summary.txt)

نام مسیر توضیح
final_125_supply.json results/run_40351779336/final-125-supply-results/ ۱۲۵ ردیف، ۱۱۸ FILLED. BTC از ۲۰۱۷-۰۱-۰۱ (16077337).
verification_results.json results/verify_top125_supply/run_40239205961/top125-verification/ ۱۲۵ ردیف با checkpoints و coverage.
top125.json + top125_mapped.json همان mapping CoinGecko → CMC.
earliest_dates.json + cmc_ids.json results/cmc_earliest_dates/run_40238238190/earliest-dates/ ۱۲۵ دارایی، قدیمی‌ترین تاریخ + cmc_id.
cmc_fill_40.json results/cmc_fill_40/run_40347826878/cmc-fill-40-results/ ۴۰ هدف.
aggressive_fill_29.json results/cmc_aggressive_fill/run_40350363383/aggressive-fill-results/ ۲۹ هدف باقی‌مانده.
fill_gaps_results.json results/fill_gaps/run_40332035054/fill-gaps-results/ ۵۳ دارایی با cg_id، dl_id، best_earliest.
verify_125.json + coingecko_retry.json results/verify_and_fill/run_40335328998/verify-125-results/ ۱۲۵ + ۴۰ retry.
results.json (TEST001) results/test001_manual/run_*/test001-results/ ۵ فایل از ۵ run مختلف TEST001.

---

جمع‌بندی: TEST_MAP چه چیزهایی را ندارد

دسته تعداد فایل غایب
Supply/CMC (D) ۹ فایل + ۸ artifact
زیرساخت/اتصال/RPC (E) ۷ فایل
TEST001/TEST003 (F) ۶ فایل
ساختاری و متا (G) ۴ فایل (به‌جز خود TEST_MAP)
کل غایب ~۲۶ فایل

جمع‌بندی: تست‌های ناموفق (❌)

نام دلیل
2026-10-30_okx_websocket_test.txt خطای 60018 (کانال candle5m روی public)
test_crypto2.yml احتمالاً ناموفق (v2 برای رفع ساخته شد)

تست‌های باگ‌دار / جزئی (⚠️)

نام مشکل
2026-10-28_test_real_check.txt OKX در هر ۲ سناریو داده نداد
2026-10-30_1h_1d_coverage.txt OKX باگ پارامتر (داده امروز را برگرداند)
test_crypto2_v2.yml تلاش رفع، خروجی نامطمئن

طلایی‌ها (💎)

coverage_matrix.tsv · 5m_since_2017.tsv · binance_klines_weight.txt · okx_websocket_all.txt · coinbase_websocket_all.txt · final_supply_harvest.yml · verify_top125_supply.yml
