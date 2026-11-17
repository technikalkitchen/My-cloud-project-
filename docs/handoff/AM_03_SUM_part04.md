خلاصه‌ی بخش ۰۴ از ۱۲

محدوده: پیام #11 | تاریخ: ۱۳ نوامبر ۲۰۲۶ | سشن: ۲ | ساعت: ۰۲:۳۵
حجم اصلی: ۱۱,۷۴۸ کاراکتر

---

پیام #11 — ۰۲:۳۵ | بررسی Item_08_Data_Contract.md

درخواست کاربر (پیش‌درآمد): ارسال Item_08 — نوشته‌شده بعد از TEST_MAP، ولی احتمالاً نیاز بازنویسی دارد.

پاسخ AM-03 — حکم کلی: بهترین فایل تا اینجا — چون:

· بعد از TEST_MAP نوشته شده
· Appendix A–E را cite می‌کند
· ساختار تمیز، Scope شفاف، Boundaries روشن

ولی ۳ مشکل جدی دارد که از APPROVED به NEEDS_REWORK می‌برد:

1. NO_DATA vocabulary ناسازگار با TEST_MAP
2. Section 9 #1 ادعای RESOLVED غلط — فقط ۳ از ۷ ID، ادعای «۲۰۱۷ supply ندارند» دقیقاً نقض TEST_MAP
3. ohlcv.json شامل "15m" — وابسته به R-30 حل‌نشده

ثبت دو نکته‌ی کاربر (در ابتدای پیام)

· MAP v1.2 کنار گذاشته شد — تنها مرجع = MAP.md v1.1 ارسالی
· Item_06 Parts 2/3 نوشته نشده‌اند — اطلاعات در B05_Master و B75 (legacy). برای بریف آیتم ۶، دریافت این دو لازم است

---

🔴 P0 — بلوک‌کننده (۳ مورد)

# مسئله جزئیات
۱ NO_DATA تعریف ناسازگار Item_08 vocab = FULL/PARTIAL/UNAVAILABLE/N_A/PENDING. NO_DATA وجود ندارد. TEST_MAP §2.2.5 (commit 8998ecf): NO_DATA ≠ «عدم وجود داده»، بلکه «cmc_id اشتباه — نیاز retry». اثر: Package C نمی‌داند map کند به کدام state
۲ Section 9 #1 ادعای RESOLVED غلط فقط ۳ از ۷ ID (SPX=28081, NFT=9816, MON=30495). جا افتاده: XPL=36645، FF=38482، PIEVERSE=38849، KITE=38828. ادعای «۲۰۱۷ supply ندارند» مستقیماً نقض TEST_MAP. TEST_MAP §3 (PENDING #5) + Appendix B: A5 retry انجام نشده → باید PENDING باشد، نه RESOLVED
۳ ohlcv.json "15m" Item_08 §7.4: {BTC: {Binance: {"15m": [], "1h": [], "1d": []}}}. MAP+Item_06: پایه = 5m/1h/1d (بدون 15m). Item_Registry: 15m پایه. TEST_MAP: 30m on-demand PROPOSED. تا R-30 حل نشود، نمی‌شود گفت 15m یا 5m — اثر روی Item_11 و Item_16

---

🟡 P1 — تأخیردهنده (۷ مورد)

# مسئله
۱ ارجاع TEST_MAP v3.4.5 اشتباه — نسخه واقعی: v3.4 FINAL
۲ Provenance naming ناسازگار با Item_05 §3.7: source_pair ↔ input_pair / source_exchange ↔ input_exchange / rate_registration_time کاملاً غایب. Item_05 §1.6 می‌گوید «باید با آیتم ۸ هماهنگ شود»
۳ Section 9 #3 Coinbase BTC-USDT RESOLVED — شاهد 2021-05-04 در TEST_MAP نیست. TEST_MAP §13 #4: P1 OPEN. Coinbase Diagnostic t4: «بعد از 2020». نیاز commit شاهد یا PENDING
۴ Section 9 #4 R-32 RESOLVED — TEST_MAP §5: R-32 OPEN (Owner). Item_08 مدل داده را حل کرده، ولی R-32 صریحاً درباره UI است. باید: «Data Model resolved؛ UI decision OPEN»
۵ Custom Range Metadata غایب — Item_Registry زیر Item_08 (Legacy B75 §13): range_type, start_requested, start_actual, offset_minutes, coverage_ratio, historical_context. Item_08 فقط coverage_ratio و missing_ranges دارد. یا تعریف شود یا حواله صریح به Item_06 Part 3
۶ Section 4.3 قواعد بدون شاهد — imprecise: true اگر walk-back به max_iter یا count_at_start >= 182. max_iter کجا تعریف شده؟ 182 از کجا آمده؟ هیچ‌کدام در TEST_MAP/Item_Registry/Legacy نیست. R-16 نقض
۷ asset_id مدل ناسازگار — Item_08 §2: asset_id="BTC" (symbol)، coingecko_id="bitcoin"، cmc_id=1. Item_03 v1.0: «asset_id = CoinGecko ID». → نیاز تصمیم Owner که کدام canonical است

---

🟢 P2 — قابل تعویق (۸ مورد)

· Section 5: price در supply.json مبهم — همان price در prices.json است یا CMC price برای MC؟
· Section 7.2: prices.json schema ناقص — فقط {...provenance} (برای Package C کافی نیست)
· Migration object ساده‌شده: Item_08 نسخه ۳-فیلدی (from/to/effective_at)، Item_04 نسخه ۸-فیلدی → باید صریح: «B→C subset است»
· Volume string aggregation — چطور دو string جمع کنیم؟ Decimal(str)? Item_07/16
· Section 4.3 quote مبهم — برای هر asset-exchange-quote یک رکورد یا فقط تبدیل USDT؟
· direction:"asc" در canonical candle — بعد از normalization همه asc هستند، نگه‌داشتن = ابهام
· «۲۰۱۷ supply ندارند» گمراه‌کننده — TEST_MAP می‌گوید ممکن است داده داشته باشند
· Section 1 PENDING «در یک سشن تبدیل می‌شود» — کدام سشن؟ چه کسی مسئول؟

🔵 P3 — Nice-to-have (۵ مورد)

· ISO 8601 Z (Section 10) vs timestamp_ms (Section 3.2) — کدام کجا؟
· Bybit صرافی ششم صریح نیست (R-11 ارجاع)
· direction:"asc" (تکرار P2-6)
· Section 9 #5 (币安人生) OPEN — درست ثبت شده ✓
· fetched_at vs timestamp_ms تمایز ممکن است گم شود

---

تناقض‌های بین‌فایلی اثرگذار بر Item_08 (۷ محور)

محور اثر
R-30 (P0-3) ohlcv.json "15m" وابسته
R-32 (P1-4) Section 9 #4 — TEST_MAP OPEN vs Item_08 RESOLVED
Coinbase BTC-USDT date (P1-3) Section 9 #3 — بدون شاهد
asset_id model (P1-7) Item_03 (CoinGecko) vs Item_08 (symbol) vs TEST_MAP (cmc_id)
Item_05 Provenance naming (P1-2) source_pair vs input_pair، rate_registration_time missing
NO_DATA state (P0-1) vocabulary gap — اثر روی Package C
Custom Range metadata (P1-5) Legacy B75 §13 missing → حواله به Item_06 Part 3

---

⭐ نقاط قوت (که نباید در بازنویسی از دست بروند)

· Appendix E citation — raw formats دقیق از A4
· Data State vocabulary — تمیز (FULL/PARTIAL/UNAVAILABLE/N_A/PENDING)، فقط NO_DATA جا افتاده
· Section 8 (Boundaries) — جدول تقسیم مسئولیت عالی
· Section 10 (MVP-First) — صریح و درست
· Price Path Taxonomy — هماهنگ با Item_05 Pending Amendment #1
· Effective Start / Imprecise — مدل خوب برای walk-back (فقط citation کم دارد)

---

پیشنهاد ساختاری برای بازنویسی (فشرده)

بخش تغییر
§1 افزودن NO_DATA (یا معادل PENDING صریح) + custom_range_meta یا حواله Item_06 Part 3
§2 asset_id: «symbol-based internal؛ cmc_id و coingecko_id به عنوان source IDs» + تصمیم Owner درباره Item_03
§3.2 حذف direction یا برچسب «source_direction»
§4.2 هماهنگ‌سازی نام‌ها با Item_05 §3.7
§4.3 citation برای max_iter و 182 — یا PENDING با ارجاع
§5 تعیین تکلیف price در supply.json
§7.2 schema کامل prices.json
§7.4 15m → 5m (اگر R-30 = MAP) یا هر دو (اگر Item_Registry)
§9 #1 → PENDING با ۷ ID کامل / #3 → PENDING با ارجاع Diagnostic t4 / #4 → «Data Model resolved، UI decision OPEN»
وضعیت NEEDS_REWORK

---

📋 وضعیت و تصمیمات این بخش

تصمیمات جدید کاربر (پیش‌درآمد)

1. MAP v1.2 کنار گذاشته شد — MAP.md v1.1 تنها مرجع
2. Item_06 Parts 2/3 نوشته نشده‌اند — برای نوشتن، B05_Master و B75 (legacy) لازم است

وضعیت آیتم بررسی‌شده

آیتم وضعیت اعلام‌شده حکم AM-03
Item_08 APPROVED (نوشته‌شده بعد از TEST_MAP) NEEDS_REWORK (۳ P0 — NO_DATA، Section 9 #1، ohlcv 15m)

فایل‌های دریافت‌شده تا پایان part04

TEAM_PROTOCOL · MAP v1.1 · TEST_MAP v3.4 · Item_Registry · Item_01 · Item_03 · Item_04 · Item_05 (v1.0+Pending) · Item_06 Part 1 · Item_08

فایل‌های دریافت‌نشده

· Item_06 Parts 2 و 3 — تأیید شد نوشته نشده‌اند (نیاز به B05_Master و B75)
· Item_07 (فاز ۱، APPROVED)
· Item_10 (فاز ۱، APPROVED)
· B05_Master + B75 (legacy — برای Parts 2/3 آیتم ۶)

P0های باز (مانع شروع بازنویسی)

1. R-30 چهارگانه — مانع Item_06 + Item_08 §7.4 + Item_11 + Item_12 + Item_16
2. NO_DATA vocabulary — Item_08 §1
3. ۷ NO_DATA status — Item_08 §9 #1
4. asset_id model — Item_03 vs Item_04 vs Item_08 vs TEST_MAP

پیشنهاد عملی AM-03

اگر Owner تصمیم R-30 را شفاهی هم بگیرد → AM-03 می‌تواند بریف Item_06 را کامل کند و هم‌زمان Item_08 §7.4 را در بریف Item_08 اصلاح کند. بدون این تصمیم، هر دو بازنویسی معلق می‌مانند.

---

پایان خلاصه‌ی بخش ۰۴. فایل بعدی: part05 (پیام #12 به بعد — Item_08 ادامه یا Item_07/Item_10).

مسیر: docs/handoff/AM_03_SUM_part04.md
کامیت: docs(handoff): add summary part04 — Item_08 review (3 P0: NO_DATA, §9#1, 15m)
