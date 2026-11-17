خلاصه‌ی بخش ۰۵ از ۱۲

محدوده: پیام #12 | تاریخ: ۱۳ نوامبر ۲۰۲۶ | سشن: ۲ | ساعت: ۰۳:۰۰
حجم اصلی: ۱۴,۰۵۰ کاراکتر

---

پیام #12 — ۰۳:۰۰ | بررسی مو‌به‌مو Item_10_Error.md

درخواست کاربر (پیش‌درآمد و پس‌درآمد):

· ارسال Item_10 — مهم‌ترین آیتم ماه
· نکته کلیدی کاربر: «یک جدول Registry از کل محدودیت‌هایی که هر آیتم می‌تواند داشته باشد — جزئیات کامل در آیتم مختص خودش. هر آیتمی که نیاز دارد، یک بخش جداگانه به نام «محدودیت‌ها (Limits)» دارد.»

پاسخ AM-03 — حکم کلی: مثل Item_08 بعد از TEST_MAP نوشته شده (ارجاعات A3, A9, A4, Coinbase Diagnostic دارد). ساختار تمیز، Scope شفاف، Boundaries دقیق، MVP-First صریح. ولی بیشتر از Item_08 در معرض نقض R-16 است — چند ارجاع به تست اشتباه یا ناموجود. حکم: NEEDS_REWORK (اصلاح هدفمند، نه بازنویسی کامل).

ثبت مجدد دو نکته: MAP v1.1 = تنها مرجع | Item_06 Parts 2/3 نوشته نشده (نیاز به B05_Master + B75 + حل R-30).

---

🔴 P0 — بلوک‌کننده (۴ مورد)

# مسئله جزئیات
۱ فرمول Backoff خودمتناقض §2.2: delay = base × 2^attempt + jitter با attempt ∈ {0,1} — ولی مثال تا attempt 2 می‌رود. §2.1: «۳ تلاش (۱ + ۲ retry)» = attempt ∈ {0,1,2}. اصلاح: delay = base × 2^(attempt-1) + jitter برای attempt ∈ {1,2}، delay(0) = 0
۲ ۴۱۸ Backoff با cap ۴۸h ناسازگار §3.1: [1h, 2h, 4h, 8h, 16h, 32h] — ۵ انتظار = ۳۱h ✓، ۶ انتظار = ۶۳h ✗ (> 48h). اصلاح: یا ۵ انتظار max، یا ۶th = min(32h, 48h − sum) = 17h
۳ ارجاع A2 اشتباه §8 #1 و §2.3 Patch 2 → «A2: OKX هدر ندارد». ولی A2 = Timeframes، نه Rate Limit. شاهد صحیح: Binance header Q3 ۰۹ (29 Oct) — فقط Binance هدر RL دارد. OKX history rate Q3 ۰۹، ۱۳ (30 Oct) = ۲ req/s. Bybit هم در Patch 2 جا افتاده (باید ۵ صرافی باشد)
۴ WebSocket error handling غایب Taxonomy (§1) فقط HTTP errors دارد. R-03: WS فقط Live Edge. TEST_MAP: OKX 89 pairs / Coinbase 103 pairs. شکاف بزرگ: disconnect، reconnect، ping timeout، subscription failure، stale feed هیچ‌کدام نیست. دقیقاً یکی از Item_10 یا Item_11 باید مسئول باشد — الان هیچ‌کدام نیست

---

🟡 P1 — تأخیردهنده (۱۰ مورد)

# مسئله
۱ TEST_MAP v3.4.5 اشتباه — باید v3.4 FINAL
۲ Diagnostic t6/t7 استناد نشده‌اند — t6: 1-year HTTP 400 (سقف ۳۰۰ تأیید)، t7: 6-month count=182 (pagination)
۳ Patch 1 فقط Coinbase — A3: Binance ≥1000، OKX/CC/Coinbase=300. Patch باید per-exchange cap + split strategy شود، نه فقط Coinbase
۴ ۷ NO_DATA در §4 غایب — NO_DATA → PENDING (نه UNAVAILABLE/N_A). هماهنگ با Item_08 P0-1
۵ §8 #2 Coinbase 400 pattern RESOLVED نیست ولی t6 حل کرده — تناقض داخلی
۶ R-15 (ثبت مصرف منابع) غایب — Item_Registry (Item_09): RESOLVED. Item_10 از Item_09 استفاده می‌کند (429، Reset weight)، باید ارجاع دهد
۷ R-26 (Diagnostic First) غایب — TEST_MAP §5 RESOLVED. دلیل: A9 v2 بدون diagnostic → ۰/۱۵۰ → ۴۰ دقیقه اتلاف
۸ R-27 (Save تدریجی) غایب — TEST_MAP §5 RESOLVED. scriptهای >۵ دقیقه، save per-10-asset. §6 فقط logging، نه recovery
۹ Cooldown/Alarm — §3.3 کانال Telegram/Email، §7 Boundaries خوب. ولی CIN-7 (کیبورد Default داینامیک) و CIN-14 (متن نمایش نهایی Package D) غایب
۱۰ Bybit rate limit در Patch 2 — همان P0-3، جا افتاده

---

🟢 P2 — قابل تعویق (۱۰ مورد)

· Binance weight=2 / reset در مرز دقیقه — §3.2 (429) این را ذکر نکرده
· Safe Probe endpoint — §3.1 مثال OKX داده، §8 #5 می‌گوید P2 (Item_01 adapter). endpointهای دیگر فرق دارند
· Invalid data → UNAVAILABLE vs INVALID — §4 UNAVAILABLE، §5.2 INVALID. INVALID = Validation Status (Provenance)، نه Data State
· Coinbase BTC-USDC delisted + USDC-USD NOT_FOUND — Owner 11 Nov خارج از scope. باید نمونه صریح در Taxonomy 404 یا §4
· Item_05 §3.6 (same-exchange rate) failure — Item_10 §4 فرقی بین failure rate و failure price نمی‌گذارد
· A9 OKX BTC-pair PENDING — IMPLICIT BTC-pair partial، case در taxonomy نیست
· «۶ صرافی» صریح نیست (R-11 ارجاع)
· Logging retention — §6 «Item_12»، ولی R-07 (۱۶ فیلد NOT NULL در SQLite) در Item_10 ذکر نشده
· A4 «۵ ناسازگاری» — Patch 3 فقط Coinbase reorder (#1). ۴ مورد دیگر (ts format، price float، direction، field counts) در Item_08 §3.1
· A2.5a OKX/CC 1d=2017-10-10 — behavior پیش از این تاریخ = UNAVAILABLE (نه Retry)

🔵 P3 — Nice-to-have (۶ مورد)

· «❌ Circuit breaker پیشرفته» — «پیشرفته» یعنی چه؟
· Test 7 برای WS error (اگر P0-4 اضافه شود)
· «End of Item_10 v1.0 APPROVED» — همان خطای Item_08
· «Invalid data retry: ۲ تلاش» بدون شاهد (B15 §6.1)
· A2 misattribution در §8 #1 (همان P0-3)
· §8 #3 «418 Backoff cap 48h ✅ RESOLVED» — با محاسبات P0-2 ناسازگار

---

تناقض‌های بین‌فایلی اثرگذار بر Item_10

محور اثر
NO_DATA vocabulary (P1-4) با Item_08 P0-1 هم‌زمان باید حل شوند
R-30 اثر مستقیم ندارد، ولی بر WS error handling اثر دارد (WS منبع 5m/15m)
Item_05 §3.6 same-exchange rate failure Item_10 باید فرض کند UNAVAILABLE (P2-5)
Item_03 (۷ NO_DATA) §4 باید NO_DATA → PENDING را reflect کند
Coinbase BTC-USDC/USDC-USD (Owner 11 Nov) در Taxonomy 404 به‌عنوان نمونه صریح ذکر نشده (P2-4)
R-26/R-27 در Item_Registry نیستند، در TEST_MAP §5 هستند — ارجاع لازم (P1-7، P1-8)

---

⭐ نقاط قوت (حفظ شوند)

· Patch 3 (Parse قبل از Validation) — دقیقاً A4 را حل می‌کند
· §1 Taxonomy ۱۰ دسته — ساختارمند و کامل (به‌جز WS)
· §2.3 «Retry نباید Rate Limiter را دور بزند» — قانون طلایی
· §3 Adaptive Backoff — ایده خوب، فقط محاسبات P0-2
· §4 Error → Data State Mapping — جدول ارزشمند
· §7 Boundaries — تقسیم‌بندی دقیق
· §9 MVP-First — صریح

---

پیشنهاد ساختاری برای بازنویسی (فشرده)

بخش تغییر
§2.2 فرمول: delay = base × 2^(attempt-1) + jitter برای {1,2}، delay(0)=0
§3.1 418 با cap 48h: ۵ waits max یا ۶th = 17h
§1 Patch 1 Generalize per-exchange cap: Binance 1000+ / OKX 300 / Coinbase 300 / CC 300 + split strategy
§1 افزودن دسته ۱۱ WebSocket Errors یا حواله صریح به Item_11
§2.3 Patch 2 حذف A2، افزودن Binance header Q3 + OKX history rate Q3 + Bybit
§4 افزودن NO_DATA → PENDING + ستون validation_status جدا از Data State
§8 حذف #1، به‌روزرسانی #2 (t6)، افزودن #7 (WS)، #8 (per-exchange split)
جدید بخش «R-15 / R-26 / R-27» — ارجاع صریح
§6 retention policy → Item_12 R-07
§7 افزودن WS boundary (Item_11 یا Item_10)
ارجاعات Diagnostic t6, t7, t9 در §1 Patch 1 + §3.2 + §8
وضعیت NEEDS_REWORK

---

📋 وضعیت و تصمیمات این بخش

تصمیم/نکته‌ی مهم کاربر (پس‌درآمد)

قاعده‌ی جدید: «جدول Registry از کل محدودیت‌های هر آیتم — جزئیات کامل در آیتم مختص خودش. هر آیتمی که نیاز دارد، یک بخش جداگانه به نام «محدودیت‌ها (Limits)» دارد.»

→ این قاعده باید در TEAM_PROTOCOL.md یا Item_Registry ثبت شود (مثلاً به‌عنوان R-34 یا بخش ساختاری جدید).

وضعیت آیتم بررسی‌شده

آیتم وضعیت اعلام‌شده حکم AM-03
Item_10 APPROVED (پس از TEST_MAP) NEEDS_REWORK (۴ P0 — Backoff formula، 418 math، A2 misattribution، WS gap)

فایل‌های دریافت‌شده تا پایان part05

TEAM_PROTOCOL · MAP v1.1 · TEST_MAP v3.4 · Item_Registry · Item_01 · Item_03 · Item_04 · Item_05 (v1.0+Pending) · Item_06 Part 1 · Item_08 · Item_10

فایل‌های دریافت‌نشده

· Item_06 Parts 2 و 3 (نوشته نشده — نیاز به B05_Master + B75)
· Item_07 (فاز ۱، APPROVED)
· B05_Master + B75 (legacy)

P0های باز (مانع شروع بازنویسی)

1. R-30 چهارگانه — مانع Item_06 + Item_08 §7.4 + Item_10 WS
2. NO_DATA vocabulary + ۷ NO_DATA status — مانع Item_08 + Item_10
3. Item_10 P0-1 (Backoff)، P0-2 (418)، P0-3 (A2)، P0-4 (WS)

پیشنهاد عملی AM-03

بریف Item_08 می‌تواند مستقل آغاز شود (به‌جز §7.4 که وابسته R-30 است) — اگر اجازه دهید. آیتم ۰۶ و ۱۰ بعد از حل R-30 + دریافت B05/B75 آماده بریف می‌شوند.

---

پایان خلاصه‌ی بخش ۰۵. فایل بعدی: part06 (پیام #13 به بعد — Item_04 ادامه یا Item_05 بازگشت یا آیتم بعدی).

مسیر: docs/handoff/AM_03_SUM_part05.md
کامیت: docs(handoff): add summary part05 — Item_10 review (4 P0: backoff, 418, A2, WS) + Limits section rule
