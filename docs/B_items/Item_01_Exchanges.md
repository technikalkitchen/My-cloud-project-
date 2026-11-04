Item_01_Exchanges.md — صرافی‌ها (Exchanges)

تاریخ: ۳ نوامبر ۲۰۲۶
نسخه: v1.0
وضعیت: NEEDS_OWNER_DECISION
اسناد مرجع: MAP.md v1.1 (LOCKED)، TEST_MAP.md (OBSERVED)، گزارش‌های تست مستقیم API و Checkpointهای جلسات ۲۸ تا ۳۰ اکتبر ۲۰۲۶.

نکته درباره Legacy: فایل B01_Master در مخزن فعلی Placeholder خالی است و Amendment B-01 نیز در سوابق موجود هنوز PROPOSED ثبت شده است. بنابراین این نسخه بر اساس MAP، شواهد تست و تصمیمات قابل بازیابی تنظیم شده است.

---

بخش ۰ — هدف و دامنه

این آیتم، فهرست صرافی‌های مجاز پروژه Kitchen Assistant Bot V4، Endpointهای ارتباطی و قواعد سطح معماری مربوط به منابع داده صرافی را تعریف می‌کند.

مسئولیت این آیتم شامل موارد زیر است:

- تعیین پنج صرافی مجاز.
- تعریف Endpointهای پایه ارتباطی.
- تعیین سیاست Dual-Binance.
- ثبت صرافی‌های خارج از محدوده پروژه.
- مشخص‌کردن مرز دریافت قیمت و OHLCV از منابع صرافی.

مرز مسئولیت:

- منابع Aggregator برای تأمین Supply در Item_02 تعریف می‌شوند.
- Canonical Pair و تبدیل جفت‌های Fiat در Item_05 تعریف می‌شوند.
- محدودیت نرخ در Item_09 ثبت می‌شود.
- Error Handling و Retry در Item_10 مدیریت می‌شوند.
- منطق Bootstrap در Item_13 قرار دارد.
- قرارداد OHLCV در Item_16 و داده قیمت صرافی در Item_18 مدیریت می‌شود.

این سند منطق داخلی این آیتم‌ها را دوباره تعریف نمی‌کند.

---

بخش ۱ — فهرست صرافی‌های مجاز

طبق MAP.md v1.1، پروژه فقط پنج صرافی منطقی مجاز دارد:

1. Binance
2. OKX
3. Bitstamp
4. Coinbase
5. Crypto.com

۱.۱ Endpointهای REST

صرافی| REST Base URL| وضعیت شواهد
Binance Global| "https://data-api.binance.vision"| OBSERVED
Binance US| "https://api.binance.us"| نیازمند اعتبارسنجی Dual-Binance
OKX| "https://www.okx.com"| OBSERVED
Bitstamp| "https://www.bitstamp.net"| OBSERVED
Coinbase| "https://api.exchange.coinbase.com"| OBSERVED
Crypto.com| "https://api.crypto.com/exchange/v1"| OBSERVED

Binance Global و Binance US در صورت تأیید نهایی Dual-Binance، یک صرافی منطقی محسوب می‌شوند؛ نه دو صرافی مستقل.

نکته: Endpointهای WebSocket از REST جدا هستند. تست‌های آرشیوی OKX از Business Channel و تست Coinbase از Advanced Trade WebSocket استفاده کرده‌اند. آدرس دقیق WebSocket تولیدی باید در پیکربندی Adapter مربوطه ثبت شود؛ شواهد فعلی برای ادعای تأیید تمام Endpointهای WebSocket کافی نیست.

۱.۲ شواهد تست

نتایج تست‌های واقعی ثبت‌شده در TEST_MAP:

- Binance، OKX، Bitstamp، Coinbase و Crypto.com در تست‌های مستقیم API بررسی شده‌اند.
- سه درخواست HTTP ایمن برای Bitstamp، Coinbase و Crypto.com با پاسخ موفق ثبت شده است.
- OKX در تست ۸۹ درخواست تاریخی متوالی، بدون خطای 429 پاسخ داده است.
- OKX در تست WebSocket تعداد ۸۹ جفت را روی یک اتصال پذیرفته و طی ۶۰ ثانیه ۱۳۸۵ پیام دریافت شده است.
- Coinbase در تست WebSocket تعداد ۱۰۳ جفت را پذیرفته و طی ۶۰ ثانیه ۹۶۵۹ پیام دریافت شده است.

این نتایج، شواهد تست‌های انجام‌شده در زمان ثبت آن‌ها هستند و تضمین دائمی دسترس‌پذیری Endpointها محسوب نمی‌شوند.

منبع نتایج: "tests/TEST_MAP.md" و فایل‌های تست مرتبط.

---

بخش ۲ — سیاست Dual-Binance

۲.۱ مدل معماری

در MAP.md، Binance به‌صورت Dual-Binance در فهرست صرافی‌های مجاز تعریف شده است.

مدل موردنظر شامل دو منبع است:

- Binance Global از طریق "data-api.binance.vision"
- Binance US از طریق "api.binance.us"

هدف معماری، تشکیل یک منبع منطقی واحد با نام Binance است.

در این مدل، Binance Global و Binance US نباید در محاسبات نهایی به‌عنوان دو صرافی مستقل شمرده شوند.

۲.۲ وضعیت اعتبارسنجی

در Checkpoint مورخ ۲۸ اکتبر، مکانیزم Dual-Binance با شناسه O-5 باز ثبت شده بود.

همچنین تست T-03 برای بررسی تفاوت دو Endpoint مطرح شده بود.

در کد فعلی TEST001 فقط Endpoint مربوط به Binance Global استفاده شده است؛ بنابراین ترکیب عملیاتی دو Endpoint هنوز با این تست اثبات نشده است.

۲.۳ پوشش بازار

عدد تقریبی ۷۰٪ پوشش Binance در سوابق پروژه ثبت شده است، اما تا زمانی که روش محاسبه، داده ورودی و نتیجه قابل بازتولید مشخص نشود، این عدد نباید به‌عنوان مقدار قطعی یا تضمین‌شده در محاسبات پروژه استفاده شود.

وضعیت: مکانیزم Dual-Binance و مقدار پوشش بازار نیازمند تعیین تکلیف نهایی Owner هستند.

جزئیات پیاده‌سازی Bootstrap در Item_13 و جزئیات پردازش قیمت و OHLCV در آیتم‌های مربوطه باقی می‌مانند. تعریف منبع منطقی Binance و سیاست Dual آن همچنان در محدوده Item_01 است.

---

بخش ۳ — صرافی‌های خارج از محدوده پروژه

فهرست مجاز پروژه محدود به پنج صرافی بخش ۱ است.

موارد زیر در محدوده منابع مجاز فعلی قرار ندارند:

صرافی‌های خارج از Allowlist:

- Kraken
- Bitfinex
- CEX.io
- Gemini
- Bybit
- MEXC
- Gate.io
- KuCoin
- Bitget
- HTX
- LBank
- Bitunix

این فهرست به معنای ثبت‌نشدن آن‌ها در Allowlist پروژه است و نباید به‌عنوان منبع جایگزین در محاسبات یا دریافت داده استفاده شوند.

دلایل تاریخی حذف این صرافی‌ها باید به‌عنوان تصمیم یا نتیجه تست مستقل ثبت شوند؛ این نسخه برای آن‌ها ادعای تستی جدید ایجاد نمی‌کند.

DEXها:

منابع DEX در محدوده منابع مجاز این آیتم قرار ندارند و Cross-Check مبتنی بر DEX در معماری فعلی پروژه استفاده نمی‌شود.

---

بخش ۴ — قواعد عملیاتی و مرز منابع داده

- تمام قیمت‌های صرافی و داده‌های OHLCV پروژه از پنج صرافی مجاز بخش ۱ تأمین می‌شوند.
- Aggregatorها مجاز به تأمین قیمت صرافی یا OHLCV نیستند.
- Aggregatorها فقط در مسیر Supply و مطابق Item_02 استفاده می‌شوند.
- CMC Internal API منبع اصلی Supply است.
- CoinGecko منبع جایگزین Supply است.
- DefiLlama برای استیبل‌کوین‌ها و CoinMetrics برای دارایی‌های بومی در Item_02 تعریف می‌شوند.
- تشخیص وجود یا عدم وجود Pair باید از Metadata معتبر همان صرافی انجام شود.
- تبدیل Pairهای USD به Canonical Pairهای پروژه طبق Item_05 انجام می‌شود.
- هیچ صرافی خارج از Allowlist نباید به‌عنوان منبع جایگزین خودکار وارد سیستم شود.

مرز با Item_10

Item_10 مسئول مدیریت خطا، Retry و Backoff است.

سیاست Retry نباید باعث انتخاب خودکار یک صرافی خارج از منبع انتخاب‌شده یا اضافه‌شدن صرافی ششم شود.

---

بخش ۵ — مرز مسئولیت‌ها

موضوع| مسئول
فهرست صرافی‌های مجاز| Item_01
Endpointهای پایه و سیاست Dual-Binance| Item_01
منابع Supply و Aggregatorها| Item_02
Canonical Pair و Fiat Conversion| Item_05
Rate Limit و محدودیت‌های منابع| Item_09
Error Handling و Retry| Item_10
Bootstrap و دریافت اولیه داده| Item_13
قرارداد OHLCV| Item_16
قیمت هر صرافی| Item_18

---

بخش ۶ — موارد باز

- O-5: تأیید نهایی مکانیزم Dual-Binance.
- C-06: تعریف و اعتبارسنجی عدد ۷۰٪ پوشش Binance.
- اعتبارسنجی Endpoint مربوط به Binance US در محیط اجرایی پروژه.
- ثبت دقیق Endpointهای WebSocket تولیدی در Adapterها.
- تأیید نهایی سیاست عدم استفاده از Backup Exchange.
- تعیین وضعیت مستند دلایل حذف صرافی‌های خارج از Allowlist.

---

پایان Item_01_Exchanges.md

Status: NEEDS_OWNER_DECISION
Next action: AM برای تعیین تکلیف O-5 و موارد باز قبل از LOCK.
Open items: O-5_DUAL_BINANCE، C-06_BINANCE_COVERAGE، BINANCE_US_VALIDATION، WEBSOCKET_ENDPOINTS، NO_BACKUP_POLICY، EXCHANGE_EXCLUSION_EVIDENCE
