# 🧠 نقشه راه مادر Scanner — Kitchen Assistant

## 0. هدف اصلی

این فایل مرجع اصلی و ثابت برای ساخت و تکمیل زیرسیستم **Scanner** در Kitchen Assistant است.

Scanner باید:
- داده‌های معتبر بازار را جمع‌آوری و اعتبارسنجی کند.
- جهت کلی بازار و جریان حرکت سرمایه را نمایش دهد.
- دارایی‌های برتر را به‌صورت پویا شناسایی کند.
- حرکات قوی و قابل‌اعتماد را از حرکات کاذب جدا کند.
- زمان جست‌وجوی معامله‌گر برای پیدا کردن گزینه‌های ارزشمند را کاهش دهد.
- **سیگنال ورود یا خروج تولید نکند.**
- **به‌تنهایی مبنای تصمیم معاملاتی نباشد.**

Scanner فقط یک زیرسیستم از Kitchen Assistant است.

ترتیب کلی توسعه محصول پس از تکمیل Scanner:
1. Scanner
2. Trade Management / سرمایه، ریسک و مدیریت خروج
3. Trading Journal
4. Order Book
5. سایر قابلیت‌های تعریف‌شده در Roadmap اصلی محصول

تا Scanner پایدار، تست‌شده و قابل‌اتکا نشده، توسعه زیرسیستم بعدی شروع نشود.

---

## 1. ساختار کلی Scanner

### A. Technical Foundation — مراحل 1 تا 6.5

این بخش زیرساخت فنی Scanner است و منطق موجود Notebook را در بر می‌گیرد:

- U01 Bootstrap
- U02 Flask Runtime
- U03 Data Foundation
- U04 Single-Symbol Real Capture
- U05 Multi-Symbol Capture
- U06 Quality Gate
- U06.5 Market Data Foundation

همراه با قراردادهای داده، اعتبارسنجی، کنترل کیفیت و Safety Gateها.

### B. Operational Scanner — مراحل بعد از 6.5

ترتیب عملیاتی:

1. Stage 7 — Total + USDT.D
2. Stage 8 — BTC + BTC.D
3. Stage 9 — Smart Market Participation
4. Dynamic Top 10
5. Strong Movers — انتخاب 5 دارایی قابل‌اعتماد از محدوده 11 تا 125
6. Top 3 Reliable Movers

**هر مرحله باید جداگانه پیاده‌سازی، تست و تأیید شود. تا مرحله فعلی تأیید نشده، مرحله بعدی شروع نشود.**

---

## 2. منابع اصلی پروژه

Kilo باید این منابع را قبل از تغییرات مهم مطالعه کند:

- `SCANNER_MASTER_ROADMAP.md` ← مرجع اصلی Scanner
- `Kitchen Assistant v3.1.4.ipynb` ← منبع منطق موجود
- `KILO_ANALYSIS.md` ← تحلیل Notebook
- `KILO_MIGRATION_AUDIT.md` ← ممیزی مهاجرت
- `README.md`

اگر چیزی در منابع تعریف نشده باشد، نباید خودسرانه به‌عنوان Requirement تاریخی فرض شود.

---

## 3. مسیر مهاجرت

مسیر رسمی:

**Notebook → استخراج Core Logic → Python Package مستقل → Tests → Scanner Bot**

Notebook فعلی یک Telegram Bot کامل نیست؛ یک pipeline تحلیل و اعتبارسنجی بازار است.

بنابراین:
- Notebook نباید کورکورانه به یک فایل Python بزرگ تبدیل شود.
- Colab-only code باید حذف یا جایگزین شود.
- وابستگی‌ها و تست‌ها باید مشخص و استخراج شوند.
- منطق U06.5 باید از نظر منطقی حفظ شود.
- سپس لایه‌های عملیاتی Scanner ساخته شوند.

---

## 4. قواعد داده و منابع

### Asset Data

اولویت:

**Binance → Coinbase fallback**

هر Asset نمایش‌داده‌شده باید Source/Exchange خود را مشخص کند.

نمونه:

```text
ETHUSDT +N%
ETHBTC +N%
Volume (ETHUSDT): ...
Exchange: Binance
```

### Index / Market-Structure Data

داده‌های Index و Market Structure باید از Data Foundation تعریف‌شده در Stage 6.5 بیایند و با Asset Data قاطی نشوند.

---

## 5. قانون BTC Pair

برای هر Asset:

1. ابتدا Pair واقعی در Binance بررسی شود.
2. اگر Binance در دسترس نبود، Coinbase بررسی شود.
3. اگر Pair واقعی BTC وجود نداشت:
   - Pair جعلی ساخته نشود.
   - وانمود نشود که Asset واقعاً با BTC معامله شده است.
   - در صورت نیاز، فقط از BTC proxy/calculation معتبر و تعریف‌شده بر پایه داده تأییدشده Stage 6.5 استفاده شود.

برای BTC:
- `BTCUSDT` نمایش داده شود.
- `BTCBTC` نمایش داده نشود.

---

## 6. قانون Volume

برای Assetها:

- فقط Volume مربوط به **USDT pair همان Asset** نمایش داده شود.
- Volume مربوط به BTC pair نمایش داده نشود.
- Volume باید مربوط به **همان Time Window درخواست‌شده توسط کاربر** باشد.
- نباید یک 24h Volume عمومی جایگزین Window درخواست‌شده شود.

برای Index / Dominance:

**Volume نمایش داده نشود.**

---

## 7. Price Change در برابر Dominance Change

برای قیمت:

**Price Change (%)** به‌صورت درصد معمول نمایش داده شود.

برای Dominance:

تغییر به‌صورت **percentage points / واحد درصد** محاسبه شود، نه رشد نسبی.

مثال:

`11.50% → 11.60%`

خروجی:

`+0.10 percentage points`

نه `+0.87%`.

---

# 8. Technical Foundation — Stages 1 تا 6.5

این مراحل زیرساخت Scanner هستند و باید از Notebook به ساختار مستقل منتقل شوند.

U06.5 مهم‌ترین بخش Market Data Foundation است.

### اصل حیاتی

**منطق U06.5 نباید صرفاً برای ساده شدن مهاجرت حذف یا تضعیف شود.**

Quality Gateها، Safety Lockها، اعتبارسنجی و قراردادهای داده آن باید حفظ شوند.

---

# 9. Stage 7 — Total + USDT.D

Stage 7 از داده معتبر Stage 6.5 استفاده می‌کند.

هدف:
- تحلیل Total Market
- تحلیل USDT Dominance
- نمایش جهت کلی بازار
- استفاده از Scenario Matrix
- استفاده از Intelligence تعریف‌شده برای همین مرحله

برای Scenarioها، Narrativeهای فارسی از پیش طراحی‌شده وجود دارند.

### قانون Narrative

Narrativeهای رسمی:
- باید دقیقاً همان متن تعریف‌شده پروژه باشند.
- حتی یک کلمه تغییر نکنند.
- برای جلوگیری از تکرار، چند Pattern برای هر Scenario داشته باشند.
- متن جدید نباید جایگزین Narrative رسمی شود مگر اینکه بعداً صراحتاً تعریف شود.

---

# 10. Stage 8 — BTC + BTC.D

Stage 8 از Market Data Foundation استفاده می‌کند.

هدف:
- تحلیل BTC
- تحلیل BTC Dominance
- بررسی رابطه BTC و BTC.D
- استفاده از Scenario Matrix اختصاصی Stage 8
- استفاده از Narrativeهای رسمی Stage 8

Matrix این مرحله مستقل است و نباید بدون دلیل با Matrix مرحله دیگر ادغام شود.

Narrativeهای رسمی نیز بدون تغییر استفاده شوند.

---

# 11. Stage 9 — Smart Market Participation

هدف این مرحله ارائه تصویر شفاف‌تر از مشارکت و حرکت سرمایه، به‌جای اتکا به Aggregateهای سنتی مانند TOTAL2، TOTAL3 و OTHERS.D است.

Segmentation:

1. BTC
2. ETH
3. TOP10_ALT
4. BROAD_ALT_11_125

### خروجی BTC
- BTC Market Cap + movement
- BTC.D + movement

### خروجی ETH
- ETH Market Cap + movement
- ETH.D + movement

### خروجی Top 10 Alt
- Top 10 Alt Market Cap + movement
- Top 10 Alt Dominance + movement

### خروجی Alt 11–125
- Alt 11–125 Market Cap + movement
- Alt 11–125 Dominance + movement

### اصل Stage 9

این مرحله:
- Scenario ندارد.
- Matrix ندارد.
- Label تحلیلی ندارد.
- Conclusion ندارد.

هدف، نمایش مستقیم و قابل‌فهم داده است.

---

# 12. Dynamic Top 10

پس از Stage 9، Scanner باید Top 10 دارایی بر اساس Market Cap را **Dynamic** مشخص کند.

- لیست نباید ثابت باشد.
- در هر درخواست، Ranking تا حد امکان تازه شود.
- اگر CoinMarketCap در دسترس نبود، از منبع معتبر جایگزین Market Cap استفاده شود.
- Scanner نباید بی‌دلیل به یک Provider وابسته باشد.

### خروجی

BTC:

```text
BTCUSDT +N%
```

ETH:

```text
ETHUSDT +N%
ETHBTC +N%
```

XRP:

```text
XRPUSDT +N%
XRPBTC +N%
```

و به همین شکل برای Top 10.

هر Asset باید:
- Source/Exchange داشته باشد.
- USDT Volume همان Time Window را داشته باشد.

این مرحله Scenario یا Matrix ندارد.

---

# 13. انتخاب 5 Strong Movers از رتبه‌های 11 تا 125

Scanner باید از محدوده **Alt 11–125** پنج دارایی قوی و قابل‌اعتماد انتخاب کند.

این انتخاب نباید صرفاً `Top 5 percentage gainers` باشد.

عوامل ارزیابی، تا جایی که داده معتبر اجازه دهد، می‌توانند شامل این موارد باشند:

- Price Movement در Window درخواست‌شده
- USDT Trading Volume در همان Window
- Volume Consistency
- Liquidity در صورت وجود داده معتبر
- Persistence حرکت
- تشخیص spike یا حرکت غیرعادی
- Relative Strength در صورت وجود BTC pair معتبر
- Reliability داده و Source

### اصل مهم

حرکت بزرگ نباید فقط به دلیل بزرگ بودن حذف شود.

مثلاً +18% با Volume قوی و پایدار می‌تواند بسیار معتبر باشد؛ اما +18% با Volume ناچیز، نقدشوندگی ضعیف یا spike غیرعادی باید امتیاز اعتماد پایین‌تری بگیرد.

### محدودیت

Order Book در این مرحله dependency اجباری نیست، چون بعداً به‌عنوان زیرسیستم مستقل توسعه خواهد یافت.

### خروجی

```text
ATOMUSDT +N%
ATOMBTC +N%
Volume (ATOMUSDT): ...
Exchange: Binance
```

BTC pair فقط طبق قانون BTC Pair نمایش داده شود.

---

# 14. Top 3 Reliable Movers

این مرحله جایگزین یک Generic Final Intelligence یا Mega Summary غیرضروری است.

از بین:
- Dynamic Top 10
- پنج Strong Movers

سه Asset که ارزش بررسی بیشتر دارند انتخاب شوند.

معیار اصلی:

**Strong Movement + Reliability**

این مرحله نباید صرفاً بزرگ‌ترین درصد رشد را انتخاب کند.

یک معیار سوم ممکن است در آینده تعریف شود، اما تا زمانی که رسماً مشخص نشده، نباید به‌عنوان Requirement قطعی اختراع شود.

### خروجی نمونه

```text
1. SOLUSDT +8.4%
   Volume: ...
   Exchange: Binance

2. XRPUSDT +6.9%
   Volume: ...
   Exchange: Binance

3. LINKUSDT +5.8%
   Volume: ...
   Exchange: Coinbase
```

این مرحله:
- Scenario ندارد.
- Matrix ندارد.
- Narrative ندارد.
- Entry Signal ندارد.
- Exit Signal ندارد.
- Long/Short Signal ندارد.
- Trade Recommendation ندارد.

هدف فقط مشخص کردن Assetهایی است که ارزش بررسی عمیق‌تر دارند.

---

# 15. چیزهایی که عمداً نباید ساخته شوند

## Mega Matrix

نباید تمام Matrixهای قبلی در یک Mega Matrix ادغام شوند.

## Generic Intelligence

نباید یک لایه Generic Intelligence فقط برای ایجاد ظاهر «هوشمند» ساخته شود که:
- نتیجه بدون پشتوانه بدهد.
- خروجی قبلی را تکرار کند.
- Narrative تکراری تولید کند.
- چیزی را که داده‌ها ثابت نمی‌کنند به‌عنوان واقعیت بیان کند.

هر لایه جدید باید ارزش واقعی و قابل‌توضیح داشته باشد.

اگر لایه‌ای اطلاعات مفید جدیدی اضافه نمی‌کند، ساخته نشود.

---

# 16. خروجی‌های قبلی نباید گم شوند

Stage بعدی نباید خروجی مهم Stageهای قبلی را حذف یا پنهان کند.

Scanner باید بتواند این بخش‌ها را در اختیار کاربر قرار دهد:

- Total + USDT.D
- BTC + BTC.D
- Smart Market Participation
- Dynamic Top 10
- 5 Strong Movers
- Top 3 Reliable Movers

---

# 17. فلسفه Scanner

Scanner برای تصمیم‌گیری به‌جای معامله‌گر ساخته نمی‌شود.

هدف:
- صرفه‌جویی در زمان
- پیدا کردن Assetهای مهم
- نمایش حرکت بازار
- نمایش جریان مشارکت/سرمایه
- محدود کردن فضای جست‌وجو
- مشخص کردن Assetهایی که ارزش بررسی بیشتر دارند

بنابراین:

**Scanner = انتخاب و تحلیل اولیه**

نه:

**Scanner = تصمیم نهایی معامله**

---

# 18. هشدار اجباری Scanner

در خروجی Scanner باید هشدار واضحی وجود داشته باشد با این مفهوم:

> ⚠️ **توجه:** اطلاعات و انتخاب‌های ارائه‌شده توسط Scanner به‌هیچ‌وجه سیگنال ورود یا خروج از معامله نیستند و نباید به‌تنهایی مبنای تصمیم معاملاتی قرار گیرند. هدف Scanner، صرفه‌جویی در زمان و مشخص‌کردن دارایی‌های برتر، جریان حرکت سرمایه و جهت کلی بازار است تا بتوانید روی گزینه‌هایی که ارزش بررسی بیشتری دارند تمرکز کنید. تصمیم نهایی برای معامله، از جمله تشخیص Setup، Entry و Trigger، بر عهده خود شماست.

---

# 19. قواعد فارسی و English / RTL-LTR

به‌دلیل ترکیب فارسی و Tickerها:

- پیام فارسی نباید با یک کلمه انگلیسی شروع شود.
- Tickerها ترجیحاً در خط یا Field مستقل باشند.
- اصطلاحات انگلیسی لازم کنترل‌شده استفاده شوند.
- Narrativeهای رسمی حتی یک کلمه تغییر نکنند.
- متن جدید باید برای خوانایی RTL/LTR طراحی شود.

---

# 20. چرخه تست هر Stage

هر Stage باید این چرخه را طی کند:

```text
Implement
→ Test
→ Inspect
→ Fix
→ Re-test
→ Verify
→ Backup/Commit
→ Next Stage
```

صرف اجرا شدن کد به معنی تکمیل Stage نیست.

باید بررسی شود:
- داده واقعی دریافت می‌شود.
- Source صحیح است.
- Volume صحیح است.
- Time Window صحیح است.
- BTC Pair Rule رعایت شده.
- Quality Gateها کار می‌کنند.
- خروجی مورد انتظار تولید می‌شود.
- داده جعلی وارد خروجی نمی‌شود.

---

# 21. ترتیب رسمی اجرای Scanner

## Phase A — Preparation

1. مطالعه کامل Roadmap
2. مطالعه Notebook
3. مطالعه Analysis
4. مطالعه Migration Audit
5. طراحی Migration Plan
6. بدون تغییر ناخواسته در پروژه

## Phase B — Technical Foundation

1. Migration Stage 1 → Test / Verify
2. Migration Stage 2 → Test / Verify
3. Migration Stage 3 → Test / Verify
4. Migration Stage 4 → Test / Verify
5. Migration Stage 5 → Test / Verify
6. Migration Stage 6 → Test / Verify
7. Migration / Preservation Stage 6.5 → Full Foundation Test

## Phase C — Operational Scanner

1. Stage 7 — Total + USDT.D → Test / Verify
2. Stage 8 — BTC + BTC.D → Test / Verify
3. Stage 9 — Smart Market Participation → Test / Verify
4. Dynamic Top 10 → Test / Verify
5. Strong Movers — 5 assets from 11–125 → Test / Verify
6. Top 3 Reliable Movers → Test / Verify

## Phase D — Scanner Final Verification

در پایان:
- Scanner از ابتدا تا انتها اجرا شود.
- تمام Stageها بررسی شوند.
- Sourceها بررسی شوند.
- Volumeها بررسی شوند.
- Time Windowها بررسی شوند.
- BTC Pair Rules بررسی شوند.
- RTL/LTR بررسی شود.
- Warning بررسی شود.
- Regression Test اجرا شود.
- خطاهای واقعی رفع شوند.
- Scanner به‌عنوان یک زیرسیستم پایدار تحویل شود.

---

# 22. معیار پایان Scanner

Scanner زمانی Complete محسوب می‌شود که:

- Technical Foundation پایدار باشد.
- منطق U06.5 حفظ شده باشد.
- Stage 7 پایدار باشد.
- Stage 8 پایدار باشد.
- Stage 9 پایدار باشد.
- Dynamic Top 10 کار کند.
- Strong Movers کار کند.
- Top 3 Reliable Movers کار کند.
- خروجی‌های ضروری حفظ شوند.
- Source هر Asset مشخص باشد.
- Volume صحیح و مطابق Window باشد.
- BTC Pair Rules رعایت شوند.
- Pair جعلی وجود نداشته باشد.
- Warning معاملاتی وجود داشته باشد.
- تست کامل Scanner موفق باشد.

پس از آن، توسعه Scanner متوقف می‌شود و پروژه طبق Roadmap اصلی وارد زیرسیستم بعدی می‌شود.

---

# 23. اصل نهایی برای Kilo

Kilo نباید کل Scanner را یک‌باره پیاده‌سازی کند.

روش رسمی:

**Stage-by-Stage**

برای هر Stage:

1. Study
2. Plan
3. Implement
4. Test
5. Fix
6. Verify
7. Backup/Commit
8. سپس Stage بعدی

اگر Requirement یا منطق مرحله‌ای مبهم است، Kilo نباید با حدس آن را پر کند.

---

## وضعیت فایل

این فایل **Master Roadmap زیرسیستم Scanner** است.

هر تغییر آینده باید کنترل‌شده باشد تا هیچ Requirement، Rule، Stage یا Safety Constraint از بین نرود.
