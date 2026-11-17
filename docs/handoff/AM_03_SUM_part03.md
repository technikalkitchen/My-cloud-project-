خلاصه‌ی بخش ۰۳ از ۱۲

محدوده: پیام #9 تا #10 | تاریخ: ۱۳ نوامبر ۲۰۲۶ | سشن: ۲ | ساعت: ۰۱:۴۸ تا ۰۲:۱۰
حجم اصلی: ۲۲,۶۱۲ کاراکتر

---

پیام #9 — ۰۱:۴۸ | بررسی Item_05 (v1.0 + Pending Amendments)

درخواست کاربر (پیش‌درآمد): ارسال Item_05 — دو نسخه دارد. AM-03 باید مو‌به‌مو بررسی کند.

پاسخ AM-03 — حکم کلی: پیچیده‌ترین آیتم تا اینجا چون دو نسخه دارد:

· Item_05_Canonical_Pairs.md v1.0 — ۲۷ اکتبر، LOCKED
· Item_05_Pending_Amendments.md — ۳۰ اکتبر، PENDING (۴ تغییر: دسته‌بندی ۴گانه، اولویت، دامنه crypto-only، MC به USDT)

⚠️ تناقض کلیدی: TEST_MAP §11 (۱۱ نوامبر) لیست چهار Amendment متفاوت را ثبت کرده:

# TEST_MAP §11 منبع در Pending هست؟
۱ ۱۲۵ → ۱۵۰ CMC R-29 (۹ Nov) ❌ نیست
۲ §3.6 Coinbase USDT-USD online Coinbase Diagnostic t8 (۱۱ Nov) ❌ نیست
۳ converted_fiat → Direct_USD_Converted (۴ دسته) Pending #1 (۳۰ Oct) ✅ هست
۴ Stage B → LOCKED در همین سند تصمیم جدید ❌ نیست

نتیجه: Pending (۳۰ Oct) با TEST_MAP §11 (۱۱ Nov) یکسان نیست — TEST_MAP روایت جدیدتر و بازنویسی‌کننده است. مجموع تغییرات لازم: ۶–۷ مورد با یک هم‌پوشانی.

وضعیت LOCKED/CLOSED باطل — چون هر دو نسخه قبل از دوره حرفه‌ای (۶–۱۱ Nov) نوشته شده‌اند. TEST_MAP §3 خودش Item_05 = PARTIAL با PENDING «Coinbase BTC-USDT full scan» + «۴ باگ Amendment».

🔴 P0 — بلوک‌کننده (۷ مورد)

# مسئله جزئیات
۱ §2.1 هنوز ۱۲۵ باید ۱۵۰ CMC (۱۲۵ خالص بعد از Wrapped). شاهد: R-29 APPROVED + Appendix C (۱۵۰ ردیف)
۲ §1.3 تک‌دسته (converted_fiat) مدل ۴دسته (Direct_USDT / Direct_BTC / Direct_USD_Converted / Implied) در main doc نیست. Pending #1 = TEST_MAP #3 ولی اعمال نشده
۳ §3.6 fallback به Binance Coinbase USDT-USD از ۱۱ Nov online تأیید شد. باید same-exchange rate اول، Binance fallback ثانویه
۴ Coinbase scope change غایب BTC-USDC delisted + USDC-USD NOT_FOUND (۱۱ Nov) کاملاً غایب. USDC فقط tier 4 fallback برای آلت‌کوین‌ها، نه BTC
۵ BTC-USDT Coinbase online main doc فقط از «نبود BTC/USDT» صحبت می‌کند، نه حضورش. باید Direct_USDT اولویت ۱ برای BTC
۶ §4 «۵ پارامتر در Stage B» TEST_MAP §11 #4: «۵ پارامتر در همین سند (LOCKED، نه Stage B)». تصمیم جدیدی که Pending هم پوشش نمی‌دهد. شکاف محتوایی: TD باید الان بنویسد، کسی ننوشته
۷ وضعیت LOCKED باطل → NEEDS_REWORK

🟡 P1 — تأخیردهنده (۸ مورد)

· BTC-pair PENDING در OKX — مدل Implied §1.2 را مبهم می‌کند
· USD PENDING در OKX (BTC/USD=NOT_LISTED) — §2.4 fallback برای OKX عملاً ممکن نیست
· آمار coverage Appendix A غایب — Coinbase: ۲۲ Direct USDT، ۷۷ Converted USD (از 2021-05-04)، ۵۱ NOT_LISTED
· ETH BTC-pair=2018-01-10 در OKX — شاهد مثبت Implied، غایب
· Coinbase BTC-USDT full scan (P0) — هنوز انجام نشده، Item_05 نمی‌تواند بسته شود
· Pending #2 (اولویت ۱→۵) و #4 (MC به USDT) — در TEST_MAP §11 نیامده‌اند. تصمیم Owner: معتبر یا کنسل؟
· converted_fiat ناسازگاری — §1.3 جدید، ولی §3.6/§3.7 نام قدیمی/جدید هم‌زمان
· Coinbase USDC-USDT برای BTC — نیاز به P2 (priority) نیست، باید در §2.4 صریح شود

🟢 P2 (۵ مورد)

· تناقض Pending (۳۰ Oct) vs TEST_MAP §11 (۱۱ Nov) درباره Stage B — تصمیم مستندنشده بین این دو تاریخ
· Item_03 §4 → Item_05 «جفت BTC برای Stablecoins» — Item_05 هیچ بخشی برای این ندارد
· Item_04 §1.5 مرز زمانی — Item_05 §1.5 فقط «قیمت‌های تاریخی»، بدون ارجاع به effective_at
· Pending #3 (crypto-only scope) — §3.1 فقط فیات‌ها را حذف می‌کند، صریح نمی‌گوید «فیات-به-فیات در دامنه نیست»
· MC به USDT — مرز Package D روشن نیست

🔵 P3 (۴ مورد)

· ارجاع TEST_MAP.md → باید TEST_MAP_v3.4_FINAL.md
· DEX cross-check — Item_01 خارج کرده، Item_05 §1.4 ساکت. ارجاع صریح لازم
· asset_id model ناسازگار — Item_03 (CoinGecko) vs Item_04 (symbol)، Item_05 §5 صریح نیست
· تاریخ فایل ۲۷ Oct — بافت تاریخی، نه مشکل

تناقض‌های بین‌فایلی (A–E)

· A) MAP v1.2 دریافت نشده — کاربر پاسخ داد: بیخیال نسخه، همان MAP.md ارسالی معتبر است
· B) R-30 سه‌گانه حل نشده
· C) asset_id model ناسازگار
· D) KMNO patch — Item_05 در ۵ فایل TEST_MAP §10 نیست، اثر احتمالاً صفر
· E) Coinbase full scan P0 — Item_05 به آن ارجاع نداده

پیشنهاد ساختاری

· ادغام main + Pending در یک سند واحد
· §2.1: ۱۲۵ → ۱۵۰ CMC (R-29)
· §1.3: مدل ۴دسته کامل + نام‌گذاری یکسان (Direct_USD_Converted، Implied)

---

پیام #10 — ۰۲:۱۰ | بررسی Item_06_Part1_Timeframes.md + رفع ابهام R-30

درخواست کاربر (پیش‌درآمد): ارسال Item_06 Part 1 — آخرین آیتم فاز ۲.

پاسخ AM-03 — حکم کلی: فایل ۲۸ Oct نوشته شده. وضعیت PROPOSED — TD CHANGES APPLIED (دقیق‌تر از بقیه که CLOSED/LOCKED باطل داشتند). ولی TEST_MAP §3: Item_06 = READY_NEEDS_DOC با PENDING «۳۰m تصمیم (R-30)». نیازمند کار + P0 مستقل.

🔴 P0 — بلوک‌کننده (۳ مورد)

۱) تناقض R-30 — چهار روایت ناسازگار

منبع 5m 15m 30m 1h 1d وضعیت
MAP v1.1 ✅ پایه ❌ ❌ ✅ پایه ✅ پایه LOCKED
Item_06 (28 Oct) ✅ پایه (۳۰ روز شناور) ❌ (خروجی) ❌ (خروجی) ✅ پایه ✅ پایه PROPOSED
TEST_MAP (11 Nov) سکوت سکوت on-demand، PROPOSED سکوت سکوت FINAL
Item_Registry (12 Nov) شناور (Live Edge) پایه (ذخیره) on-demand سکوت سکوت WORKING

پیامدهای معماری اگر Item_Registry درست باشد:

· Cache (Item_11) → ذخیره 15m نه 5m
· Storage (Item_12) → محاسبه حجم 15m نه 5m
· جدول ۴۱ ردیفی (row 12: 2d→15m→192) بدون on-demand درست کار می‌کند (مزیت بزرگ)

پیامد اگر MAP+Item_06 درست باشند:

· جدول rows 12–16 (بازه‌های تاریخی 2d–6d) → نیازمند on-demand 5m که در ۵m «۳۰ روز اخیر» عملاً نمی‌شود ساخت (coarser→finer ممکن نیست)

درخواست رسمی از Owner:

1. کدام R-30: (الف) فقط 30m on-demand / (ب) 15m پایه + 5m شناور + 30m on-demand / (ج) 5m/1h/1d پایه بدون 15m
2. اگر (ب): شاهد/تست کجاست؟ باید در TEST_MAP ثبت شود
3. اگر (ج): Item_Registry باید پچ شود (15m → 5m)

۲) جدول ۴۱ ردیفی — شکاف پنهان برای بازه‌های تاریخی

· ۵m فقط ۳۰ روز → برای 2d–6d تاریخی (مثلاً از ۲ سال پیش) در دسترس نیست
· 1h هست، ولی coarser→finer ممکن نیست
· سؤال بلوکه: آیا on-demand 5m برای 2d–6d تاریخی مجاز است؟ محدودیت نرخ (Item_09)؟ زمان پاسخ؟ فایل ساکت است

۳) ارجاع TEST_MAP.md (OBSERVED) — باید TEST_MAP_v3.4_FINAL.md

🟡 P1 — تأخیردهنده (۱۰ مورد)

· هیچ ارجاعی به A2 یا A2.5a نیست — OKX 1d=2017-10-10 غایب
· CIN-6 (Crypto.com ۲ ماهه Default vs Custom) — کاملاً غایب
· CIN-2 (TF > 1h On-the-Fly) و CIN-3 (Edge Filling) — صریح cite نشده
· R-03 (WebSocket فقط Live Edge) — کاملاً غایب. باید صریح: «5m از دو منبع: WebSocket (لبه زنده) + HTTP (تاریخچه ۳۰ روز)»
· «کندل تقریبی» گمراه‌کننده — اکثر اعداد دقیق‌اند (فقط row 41 برآورد)
· O-1 (From beginning) وضعیت OPEN — ولی الگوریتم در §2 نوشته شده. صریح شود: «متن §2 پیش‌نویس، تأیید نهایی Stage B»
· مرز با Item_09 (Rate Limit) غایب
· مرز با Item_10 (Error) غایب
· مرز با Item_11 (Cache) و Item_12 (Storage) غایب
· مرز با Item_08 (Data Contract) — data_status: PARTIAL از Item_08 می‌آید، صریح نیست
· مرز با Item_25 (Kitchen Coverage) — row 41 محاسبه تعداد کندل معتبر، مرتبط

🟢 P2 (۱۰ مورد)

· رفتار کندل باز (open) در مرز تجمیع — §3 فقط «missing» می‌گوید، نه «open»
· مثال From beginning برای BTC — ۳۲۸۵ روز با 15d = ۲۱۹ کندل (در محدوده)، UX؟
· راهبرد کش برای 15m/30m/45m خروجی — ساکت
· دقت تلورانس مرز UTC — 1w از دوشنبه؟ 1M ۳۰ روزه یا اول ماه؟
· 4h = 4×1h vs 48×5m — §1 و §2 row 7 با هم سازگار ولی صریح نیست
· Volume «هم‌واحد» — Coinbase float vs بقیه str. Item_07/16 حل کنند
· «اولین داده معتبر» — تعریف نشده
· مرز Item_14 (Collector) — 5m 30-day rolling هم؟
· «کندل تقریبی» → «کندل خروجی» (پیشنهاد rename)
· اعداد فارسی/انگلیسی مخلوط — یکسان‌سازی

🔵 P3 (۵ مورد)

· جدول‌های به‌هم‌ریخته در چت (تله nano)
· B05_Master در دست نیست — درخواست ارسال
· «حدود ۱۵۰ تا ۳۰۰» → «هدف: 150 ≤ کندل ≤ 300»
· تیتر «کندل تقریبی» → «کندل خروجی»
· اعداد فارسی/انگلیسی مخلوط

تناقض‌های بین‌فایلی (A–E)

· A) R-30 (P0 موجود) — تنها تناقض مستقیم بر دامنه Item_06. بقیه (R-32، R-29، KMNO) به ۰۳/۰۴/۰۵/۱۵
· B) MAP v1.2 — کاربر پاسخ داد: بیخیال نسخه، همان MAP.md معتبر است
· C) Cross_Item_Notes → Item_Registry — تأیید شد
· D) Parts 2 و 3 Item_06 وجود دارند — کاربر پاسخ داد: هنوز نوشته نشده‌اند. اطلاعات در B75 و B05_Master legacy است، باید بر اساس TEST_MAP ساخته شوند
· E) B-05_Master — در دست نیست، برای بازنویسی لازم

پیشنهاد ساختاری برای بازنویسی

· بخش ۰ جدید: دامنه و ارتباط با Parts 2/3
· بخش ۱ (Base TFs): پس از حل R-30 — 5m (WebSocket+HTTP 30d)، 1h (HTTP دائم)، 1d (HTTP دائم)، + 15m اگر (ب)
· بخش ۱ (Origin): ارجاع A2.5a + «اولین داده معتبر per-exchange per-pair»
· بخش ۲ (جدول ۴۱): بازبینی با حل R-30
· بخش ۳ (Aggregation): رفتار کندل باز + ارجاع Item_08
· بخش جدید ۳.۵: on-demand fetch برای 2d–6d تاریخی
· بخش ۴ (مرزها): + Item_08، ۰۹، ۱۰، ۱۱، ۱۲، ۲۵
· بخش جدید: ارجاعات شواهد (A2, A2.5a, R-03, R-30, CIN-2/3/6)
· وضعیت نهایی: NEEDS_REWORK با P0 معلق روی R-30

---

📋 وضعیت و تصمیمات این بخش

تصمیمات جدید کاربر (در پیش‌درآمد پایان بخش)

1. Parts 2 و 3 Item_06 نوشته نشده‌اند — اطلاعات در B75 و B05_Master legacy است، باید بر اساس TEST_MAP ساخته شوند
2. نسخه MAP بی‌اهمیت — همان MAP.md ارسالی معتبر است. نیازی به MAP_Amendment_v1.2 نیست
3. Item_08 در پیام بعدی — کاربر می‌گوید فرستاده ولی محتوا در این پیام نیست (احتمالاً در part04)

وضعیت آیتم‌های بررسی‌شده در این بخش

آیتم وضعیت اعلام‌شده حکم AM-03
Item_05 LOCKED (v1.0) + PENDING (Amendments) NEEDS_REWORK (۷ P0 — منبع ۱۲۵/۱۵۰، §1.3، §3.6، Coinbase scope، BTC-USDT، §4 پارامترها، LOCKED باطل)
Item_06 Part 1 PROPOSED (TD APPLIED) NEEDS_REWORK (۳ P0 — R-30، on-demand gap، TEST_MAP version)

فایل‌های دریافت‌شده تا پایان part03

TEAM_PROTOCOL · MAP v1.1 · TEST_MAP v3.4 · Item_Registry · Item_01 · Item_03 · Item_04 · Item_05 (v1.0+Pending) · Item_06 Part 1

فایل‌های دریافت‌نشده (باقی‌مانده)

· Item_06 Parts 2 و 3 — کاربر تأیید کرد: نوشته نشده‌اند، باید از B75/B05 ساخته شوند
· Item_07 · Item_08 · Item_10
· B05_Master (legacy)
· ~~MAP_Amendment_v1.2~~ — کاربر: نیازی نیست

مسائل باز مهم

1. R-30 چهارگانه — بزرگ‌ترین P0 باز. اثر: ۰۶، ۱۱، ۱۲، ۱۶
2. on-demand 5m برای بازه‌های تاریخی 2d–6d — فایل ساکت، نیاز تصمیم
3. asset_id model — CoinGecko vs symbol vs cmc_id → نیاز تصمیم Owner
4. R-32 status — TEST_MAP=OPEN / Item_Registry=Resolution → تأیید Owner
5. §4 «۵ پارامتر» — TD باید بنویسد، کسی ننوشته. شکاف محتوایی در Item_05

---

پایان خلاصه‌ی بخش ۰۳. فایل بعدی: part04 (شامل بررسی Item_08 — پیام #11 به بعد).

راه‌حل مسیر ذخیره: docs/handoff/AM_03_SUM_part03.md
کامیت: docs(handoff): add summary part03 — Item_05/Item_06 reviews + R-30 four-way conflict

بعد cat docs/handoff/AM_03_RAW_part04.md را بفرست. 👌
