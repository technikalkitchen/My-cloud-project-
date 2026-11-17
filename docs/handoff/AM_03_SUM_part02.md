خلاصه‌ی بخش ۰۲ از ۱۲

محدوده: پیام #7 تا #8 | تاریخ: ۱۳ نوامبر ۲۰۲۶ | سشن: ۲ | ساعت: ۰۱:۱۸ تا ۰۱:۳۲
حجم اصلی: ۱۷,۶۰۰ کاراکتر

---

پیام #7 — ۰۱:۱۸ | بررسی Item_03_Universe.md (پیش‌بریف بازنویسی)

درخواست کاربر (پیش‌درآمد): ارسال Item_03 — فایل ۲۶ اکتبر، نوشته‌شده قبل از TEST_MAP. AM-03 باید مو‌به‌مو بررسی کند و تناقض‌ها را دقیق ثبت کند.

پاسخ AM-03 — حکم کلی: Item_03 وضعیت CLOSED دارد ولی معتبر نیست:

· TEST_MAP دوره حرفه‌ای از ۶ نوامبر — بعد از Item_03
· R-29 (APPROVED 9 Nov) بعد از Item_03
· TEST_MAP §3 خودش PENDING دارد (۱۲۵/۱۵۰، ۷ CMC ID) → آیتم بسته نیست
· حکم: خروج از CLOSED + بازنویسی اساسی در فاز ۲

🔴 P0 — بلوک‌کننده (۶ مورد)

# مسئله شاهد
۱ منبع Universe از CoinGecko به CMC تغییر کرده، فایل هنوز CoinGecko TEST_MAP §5 R-29، Appendix A/B/C
۲ asset_id از CoinGecko ID به cmc_id — نگاشت پایدار وجود ندارد TEST_MAP §2.2.5، Appendix C، CIN-8
۳ تعداد Wrapped در Top 150: فایل تخمین ۵–۱۰، TEST_MAP می‌گوید ۲۵ (۱۵۰−۲۵=۱۲۵) TEST_MAP §5 R-29
۴ ۷ NO_DATA / Symbol Collision (SPX, XPL, FF, PIEVERSE, KITE, MON, NFT) کاملاً غایب TEST_MAP §2.2.5، CIN-8
۵ فهرست Stablecoins ناقص: USDT, USDC, DAI, TUSD, USDP, FDUSD, PYUSD, BUSD — غایب: USD1(26), USDe(17), USDG(31), RLUSD(32), USDD(48), EURC(88). USDP و BUSD اصلاً در Top 150 نیستند Appendix C
۶ 币安人生 (rank 82, CMC 38590) نیازمند تأیید Extractor — فایل هیچ اشاره‌ای ندارد Appendix C، CIN-9

🟡 P1 — تأخیردهنده (۶ مورد)

· KMNO cmc_id 32415→30986 (CIN-10) — فایل غایب
· پوشش صرافی باید روی ۱۲۵ نه ۱۵۰ محاسبه شود (Appendix A همه ۱۵۰ را تست کرده — ۲۵ Wrapped باید حذف شوند)
· قاعده‌ی تشخیص Stablecoins/Wrapped پس از CMC: تگ CoinGecko منبع اولیه بود — در CMC تگ‌گذاری متفاوت، شاهد جدید لازم
· O-3 (escalation اگر < ۹۵٪) — تصمیم ۲۶ Oct، TEST_MAP تأیید نکرده
· available_from = اولین تاریخ CMC، نه launch date — Caveat در فایل نیست (Appendix B: SOL=2021-01-01 CMC ولی Binance listing=2020-08)
· «۱۲۵ بعد از حذف Wrapped»: ۲۵تای PENDING باید صریح ثبت شوند

🟢 P2 (۴ مورد)

· Update frequency «یک بار در ماه» — در TEST_MAP نیست
· Dual USDT as Support Asset — با CMC regime (USDe, USD1, USDD) پیچیده‌تر
· BUSD/USDP در کنترل‌لیست: در Top 150 نیستند
· Survivorship Bias — تصمیم ۲۶ Oct، شواهد بر پایه OKX/Binance نه CMC

🔵 P3 (۳ مورد)

· ارجاع TEST_MAP.md (OBSERVED) → باید TEST_MAP_v3.4_FINAL.md
· STABLE (rank 87) — symbol با کلمه «stablecoin» هم‌ریشه
· 币安人生 — symbol غیرلاتین، نیازمند قاعده‌ی نگاشت پایدار برای Package D

تناقض‌های بین‌فایلی اثرگذار بر Item_03

· A) MAP v1.1 (LOCKED ۲۸ Oct) فقط ۵ صرافی — R-11 می‌گوید v1.2 ثبت شد ولی دریافت نشده
· B) Cross_Item_Notes دریافت نشده (که در پیام #8 آرشیو شد)
· C) R-30 سه‌گانه — اثر مستقیم ندارد ولی آیتم‌های وابسته (۰۶، ۱۶، ۲۵) را تحت تأثیر دارد
· D) final_125_supply (۱۱۸ رکورد) = ۱۲۵ − ۷ NO_DATA → این ۷ همان Symbol Collision هستند

پیشنهاد ساختاری AM-03

· ~۴۰٪ محتوا قابل نگه‌داری: زیرمجموعه‌های ۱، ۲، ۵، ۸، ۱۲، ۱۴، ۱۵
· نیازمند بازنویسی کامل: زیرمجموعه ۳ (asset_id)، ۶ (Stablecoins)، ۷ (Wrapped)، ۱۰ (منبع)

---

پیام #8 — ۰۱:۳۲ | بررسی Item_04_Migration_Map.md + ثبت تغییر رویه Cross_Item_Notes

درخواست کاربر: ارسال Item_04 + قاعده‌ی جدید: «Cross_Item_Notes وجود ندارد — آرشیو شده و Item_Registry جایگزین آن است. منطق: در آیتم X اگر موضوعی مثل Y پیدا شد که جای آن آیتم Z است، با Patcher (Termux) پچ می‌کنیم و به Item_Registry زیر آیتم Z اضافه می‌شود. قبل از شروع هر آیتم، Item_Registry چک می‌شود — جدا از TEST_MAP — تا ببینیم از گذشته چیزی برای این آیتم نوشته شده.»

🔄 رویه‌ی جدید ثبت‌شده (مهم — در TEAM_PROTOCOL باید منعکس شود)

قبل بعد
سلسله‌مراتب: TEST_MAP > Cross_Item_Notes > MAP > Item_XX سلسله‌مراتب: TEST_MAP > Item_Registry > MAP > Item_XX
Cross_Item_Notes فعال آرشیو شده — حذف از سلسله‌مراتب
کار روی آیتم X: موضوع Y را در Cross_Item_Notes ثبت می‌کردیم Patcher (Termux) پچ می‌کند + زیر آیتم Z در Item_Registry ثبت می‌شود
هر آیتم: TEST_MAP چک هر آیتم: TEST_MAP + Item_Registry هر دو چک می‌شوند

منبع قوانین جدید: TEST_MAP > Item_Registry

حکم کلی Item_04

· فایل ۲۸ اکتبر، CLOSED — ولی شواهد تعیین‌کننده (A6_A7 Discovery 93bfa04، OKX Correction 15fccca، POL Bybit Test fe8a1d2، R-32) همه ۸–۱۱ نوامبر هستند
· حکم: CLOSED باطل → NEEDS_REWORK + بازنویسی اساسی

🔴 P0 — بلوک‌کننده (۶ مورد)

# مسئله جزئیات
۱ FTM→S تاریخ نادرست فایل: 2024-12-18 / TEST_MAP §2.1 A6_A7 Correction (commit 15fccca): 2025-01-20 CONFIRMED. فایل شاهد 2024-12-18 ندارد
۲ POL Bybit 11-month gap فایل به Item_05 حواله داده / TEST_MAP §13 #6: Item_04. POL از 2023-10-25 در Bybit، Policy A مرز 2024-09-04
۳ KMNO patch در Item_04 غایب TEST_MAP §3 pending دارد ولی §10 patch فقط ۵ فایل (نه Item_04) → تناقض داخلی TEST_MAP
۴ RNDR/RENDER: effective_at=2023-11-02 بدون R-32، بدون listing_dates R-32 (TEST_MAP §5): listing_dates={binance:2024-07-22, okx:2024-07-14}
۵ R-32 status: TEST_MAP=OPEN / Item_Registry=Resolution Item_Registry می‌گوید «UI از listing_dates، policy_date فقط بک‌گراند» — ممکن است تصمیم AM باشد نه Owner
۶ CLOSED باطل به دلیل P0 ۱–۵ → NEEDS_REWORK

🟡 P1 — تأخیردهنده (۷ مورد)

· هیچ ارجاعی به منابع TEST_MAP نیست: A6_A7_discovery (93bfa04)، A6_A7_okx_correction (15fccca)، pol_bybit_test (fe8a1d2)، a9_asset_start_dates
· Scope creep در موارد OPEN:
  · O-1 (BTT/LUNA): LUNA در Appendix D = delisted نه migration. BTT = split 1000:1 نه rename → نباید در Item_04
  · O-2 (ساپلای POL): این دامنه Item_15 است
  · O-3 (نمایش UI): دامنه Item_27 یا Package D
· «New Assets» table در ۴.۱ ارجاع داده ولی هیچ‌جا تعریف نشده → ارجاع معلق
· Delisted و Survivor (FTT, LUNA, UST, LUNC) غایب — Appendix D ۱۰ asset (۶ migration + ۳ delisted + ۱ survivor)
· ناسازگاری طبقه‌بندی POL=migration / FTM→S=rename / RNDR→RENDER=migration — همه عملاً token migration 1:1
· POL effective_at=2024-09-04 بدون ارجاع به Policy A
· OKX 1-day diff: Policy A=2024-09-04 vs OKX=2024-09-03 — nuance توضیح داده نشده

🟢 P2 (۳ مورد)

· Conversion ratio=1 برای هر سه بدون شاهد
· event_status=CONFIRMED بدون ارجاع به commit 15fccca
· asset_id در Item_04 = نماد جدید (POL/S/RENDER) — ناسازگار با Item_03 (CoinGecko ID) → باید تصمیم Owner یکدست شود

🔵 P3 (۲ مورد)

· فایل ۲۸ Oct ولی POL effective_at=2024-09-04 — تناقض تاریخ
· O-1 (BTT/LUNA) اگر واقعاً در Item_04 می‌مانند → باید به «New Assets» تعریف‌نشده منتقل شوند

تناقض‌های بین‌فایلی اثرگذار بر Item_04 (A–E)

· A) MAP v1.2 دریافت نشده (R-11 می‌گوید ثبت شد، ولی در دست ما v1.1)
· B) R-30 سه‌گانه حل نشده
· C) asset_id model بین Item_03 و Item_04 ناسازگار — نیازمند تصمیم Owner (cmc_id یا نماد داخلی؟)
· D) KMNO patch تناقض: TEST_MAP §10 به Item_04 ارجاع نمی‌دهد ولی §3 pending Item_04 می‌گذارد → یکی از دو ثبت اشتباه
· E) R-32 Resolution در Item_Registry — ممکن است تصمیم AM باشد که Owner تأیید نکرده

پیشنهاد ساختاری AM-03 برای بازنویسی Item_04

· زیرمجموعه ۳ (جدول): اضافه شود ۴ ستون: effective_at_source, okx_listing_date, binance_listing_date, bybit_listing_date — اختلاف‌ها صریح ثبت شوند
· زیرمجموعه ۴ (Strict Boundary Rule): بگوید وقتی effective_at با listing_date متفاوت است، کدام برای کدام محاسبه (identity resolution vs data fetch)
· جدول جدید: «Symbol Collision Cases» — KMNO (32415→30986) + ۷ NO_DATA (SPX, XPL, FF, PIEVERSE, KITE, MON, NFT)
· زیرمجموعه ۵ (POL supply): حذف یا صریحاً ارجاع به Item_15
· جدول OPEN: O-1, O-2, O-3 خارج و به آیتم مربوطه
· ارجاعات واجب: A6_A7_discovery (93bfa04)، A6_A7_okx_correction (15fccca)، pol_bybit_test (fe8a1d2)، R-32 (OPEN)، R-29 (APPROVED)
· وضعیت نهایی: NEEDS_REWORK

---

📋 خلاصه‌ی تصمیمات و وضعیت این بخش

تصمیم جدید این بخش (مهم)

تغییر رویه: Cross_Item_Notes → آرشیو شد. Item_Registry جایگزین رسمی شد. هر آیتم قبل از شروع: چک TEST_MAP + Item_Registry. موضوعات بین‌آیتمی با Patcher (Termux) پچ می‌شوند. منبع قوانین = TEST_MAP > Item_Registry

وضعیت آیتم‌های بررسی‌شده

آیتم وضعیت اعلام‌شده حکم AM-03
Item_01 (بررسی در پیام #7) —
Item_03 CLOSED NEEDS_REWORK (P0: منبع، asset_id، Wrapped، ۷ NO_DATA، Stablecoins، 币安人生)
Item_04 CLOSED NEEDS_REWORK (P0: FTM→S تاریخ، POL 11-month، KMNO، RNDR/R-32، CLOSED باطل)

مسائل باز (تا پایان این بخش)

1. R-30 سه‌گانه — هنوز حل نشده (اثر: ۰۶، ۱۱، ۱۲، ۱۶)
2. MAP_Amendment_v1.2 — R-11 ثبت ولی دریافت نشده
3. asset_id model — ناسازگار Item_03 (CoinGecko) vs Item_04 (نماد) → نیاز تصمیم Owner
4. R-32 status — TEST_MAP=OPEN / Item_Registry=Resolution → نیاز تأیید Owner
5. KMNO patch — TEST_MAP §3 vs §10 تناقض داخلی
6. «New Assets» table — ارجاع معلق، تعریف‌نشده

فایل‌های دریافت‌شده تا پایان part02

TEAM_PROTOCOL · MAP v1.1 · TEST_MAP v3.4 · Item_Registry · Item_01 · Item_03 · Item_04

فایل‌های دریافت‌نشده (باقی‌مانده)

Item_05 · Item_06 (بازنویسی) · Item_07 · Item_08 · Item_10 · MAP_Amendment_v1.2

---

پایان خلاصه‌ی بخش ۰۲. فایل بعدی: part03 (شامل Item_05 — پیام #9).

مسیر ذخیره: docs/handoff/AM_03_SUM_part02.md
کامیت: docs(handoff): add summary part02 — Item_03/Item_04 reviews + Cross_Item_Notes archived

بعد cat docs/handoff/AM_03_RAW_part03.md را بفرست. 👌
