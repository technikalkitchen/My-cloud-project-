

```markdown
# MAP.md — نقشه‌ی ۳۰ آیتم Package B

**پروژه:** Kitchen Assistant Bot V4
**تاریخ:** ۲۸ اکتبر ۲۰۲۶ | ۱۹:۰۰ تهران
**نسخه:** ۱.۱
**وضعیت:** LOCKED

---

## هدف این فایل

این فایل، نقشه‌ی رسمی ۳۰ آیتم Package B است. برای هر آیتم مشخص می‌کند:

- فایل فعال کجاست
- از کدام فایل‌های Legacy (قدیمی) تغذیه می‌شود
- دامنه مسئولیت آن چیست

این فایل مرجع اصلی برای پیدا کردن هر آیتم است.

---

## ساختار پوشه‌ها

```

docs/
├── B_legacy/                 ← فایل‌های قدیمی، دست‌نخورده
│   ├── B01_Master.md
│   ├── B02_Master.md
│   ├── B03_Master.md
│   └── ...
│
├── B_items/                  ← ۳۰ آیتم جدید
│   ├── Item_01_Exchanges.md
│   ├── Item_02_Aggregators.md
│   ├── Item_03_Universe.md
│   └── ...
│
└── MAP.md                    ← این فایل

```

**قاعده:** فایل‌های `B_legacy/` هرگز تغییر نمی‌کنند. فایل‌های `B_items/` فعال‌اند.

**توجه:** فایل‌های `B_legacy/BXX_Master.md` در حال حاضر به عنوان placeholder ساخته شده‌اند. محتوای طراحی‌های قبلی (که در جلسات گذشته نوشته شده) طی جلسات آینده در آن‌ها بارگذاری خواهد شد.

---

## نقشه‌ی ۳۰ آیتم

| # | عنوان | فایل فعال | Legacy موجود | Legacy نیازمند نگارش | دامنه مسئولیت |
|---|---|---|---|---|---|
| ۰۱ | صرافی‌ها | `Item_01_Exchanges.md` | B01_Master | — | اتصال به ۵ صرافی مجاز (Binance Dual، Coinbase، OKX، Crypto.com، Bitstamp). تعریف endpointها، قواعد Dual-Binance، و لیست صرافی‌های حذف‌شده. |
| ۰۲ | اگریگیتورها | `Item_02_Aggregators.md` | B02_Master | — | منابع تأمین Supply. CMC Internal API (اصلی)، CoinGecko (fallback)، DefiLlama (استیبل‌کوین)، CoinMetrics (دارایی‌های بومی). منطق ترکیب چندمنبعی و Cross-Check. |
| ۰۳ | دنیای دارایی‌ها | `Item_03_Universe.md` | B35_B36_B37_Master (بخش B35) | B20 | فهرست ۱۲۵ دارایی از CoinGecko. `asset_id` پایدار، Stablecoins (حذف از Top 10/5/3)، حذف Wrapped Coins، Historical Scan، Survivorship Bias پذیرفته‌شده. |
| ۰۴ | جدول مهاجرت | `Item_04_Migration_Map.md` | B35_B36_B37_Master (بخش B35) | — | نگاشت symbol قدیم/جدید (MATIC→POL، FTM→S، RNDR→RENDER). `asset_id` پایدار، Strict Boundary Rule، راه‌حل ساپلای POL از on-chain. |
| ۰۵ | جفت‌ارزها | `Item_05_Canonical_Pairs.md` | B03_Master + B04_Master | — | جفت‌های استاندارد `XXX/USDT` و `XXX/BTC`. قواعد Direct/Implied/Converted، فرمول Fiat Conversion، ثبت Provenance در Metadata. |
| ۰۶ | بازه و تایم‌فریم | `Item_06_Part1_Timeframes.md` | B05_Master (شامل B06، B09) | B75 | ۳ تایم‌فریم پایه (5m، 1h، 1d)، جدول نگاشت Range به TF خروجی، Aggregation با مرز UTC، وضعیت PARTIAL برای کندل ناقص. |
| ۰۷ | دقت و زمان | `Item_07_Precision_Time.md` | B12_Master + B13_Master | — | دقت Decimal (ممنوعیت Float در مسیرهای حساس)، منطقه زمانی UTC، قواعد گرد کردن و تبدیل. |
| ۰۸ | قرارداد داده | `Item_08_Data_Contract.md` | — | B43, B46, B47, B48 | schema استاندارد خروجی داده. فیلدهای الزامی، انواع Provenance، تعریف UNAVAILABLE/PARTIAL، مرز B↔C. |
| ۰۹ | محدودیت نرخ | `Item_09_Rate_Limit.md` | B14_Master_1..5_Decision_LOCKED | B72 | محدودیت نرخ API صرافی‌ها و اگریگیتورها. per-user limit در Telegram، مکانیزم backoff و retry. |
| ۱۰ | خطا | `Item_10_Error.md` | B15_Master_1 | B33 | مدیریت خطا و fallback. تبدیل خطاها به UNAVAILABLE، لاگ و retry، زنجیره جایگزین. |
| ۱۱ | کش | `Item_11_Cache.md` | — | B53 | TTL و استراتژی کش. کش Supply (۲۴ ساعت)، کش OHLCV (لغزان 5m، دائمی 1h/1d). |
| ۱۲ | ذخیره‌سازی | `Item_12_Storage.md` | — | B50, B54 | ذخیره‌سازی روی Google Drive. retention policy، ساختار پوشه، مدیریت حجم. |
| ۱۳ | دریافت اولیه | `Item_13_Bootstrap.md` | — | B51 | دریافت اولیه ۱۲۵ دارایی از ۲۰۱۷ تا امروز. طرح chunking و مدیریت GitHub Actions limit. |
| ۱۴ | به‌روزرسانی روزانه | `Item_14_Incremental.md` | — | B52 | به‌روزرسانی روزانه داده‌ها. incremental fetch، append به کش تاریخی. |
| ۱۵ | ساپلای | `Item_15_Supply.md` | — | B16 | موتور ساپلای Circulating. دریافت از منابع مختلف با اولویت، ثبت `source_timestamp`/`fetched_at`، مدیریت دارایی‌های UNAVAILABLE. |
| ۱۶ | کندل | `Item_16_OHLCV.md` | B07_Master + B08_Master (بخشی) | B22, B26 | کندل و Open/High/Low/Close/Volume. Aggregation از تایم‌فریم پایه، Cross-Check از CryptoCompare. |
| ۱۷ | حجم صرافی | `Item_17_Exchange_Volume.md` | B08_Master (بخشی) | B55 | حجم صرافی برای هر دارایی. حجم ۲۴ ساعته و حجم تاریخی. |
| ۱۸ | قیمت صرافی | `Item_18_Exchange_Price.md` | B04_Master | B25, B42 | قیمت هر دارایی در هر صرافی. Direct/Implied/Converted، ثبت Provenance. |
| ۱۹ | مارکت‌کپ صرافی | `Item_19_Exchange_MC.md` | — | B29 | مارکت‌کپ صرافی = Exchange Price × Supply. |
| ۲۰ | اعتبار صرافی | `Item_20_Exchange_Reliability.md` | — | B32 (بخش فرمول) | امتیاز اعتبار صرافی. بر اساس پوشش Universe، اختلاف Cross-Check، سرعت پاسخ. |
| ۲۱ | اعتبار داده | `Item_21_Data_Reliability.md` | — | B32, B71 | امتیاز اعتبار داده. ترکیب reliability صرافی و وضعیت داده (FULL/PARTIAL). |
| ۲۲ | دامیننس صرافی | `Item_22_Exchange_Dominance.md` | — | B30 | دامیننس هر صرافی = Exchange MC / Total MC. |
| ۲۳ | قیمت کیچن | `Item_23_Kitchen_Price.md` | — | B23, B24 | قیمت ترکیبی از ۵ صرافی. وزن هر صرافی بر اساس Reliability و Provenance. |
| ۲۴ | حجم کیچن | `Item_24_Kitchen_Volume.md` | — | B27, B56 | حجم ترکیبی از ۵ صرافی. مشابه Kitchen Price. |
| ۲۵ | مارکت‌کپ کیچن | `Item_25_Kitchen_MC.md` | — | B28 | مارکت‌کپ کیچن = Kitchen Price × Supply. |
| ۲۶ | پوشش کیچن | `Item_26_Kitchen_Coverage.md` | — | جدید (بدون Legacy) | درصد پوشش داده در هر بازه. نشان می‌دهد چند دارایی داده معتبر دارند. |
| ۲۷ | رتبه‌بندی کیچن | `Item_27_Kitchen_Ranking.md` | B17_B18_Master | B49, B69 | رتبه‌بندی ۱۲۵ دارایی بر اساس Kitchen MC. Replacement Logic برای Stablecoins. |
| ۲۸ | گروه‌بندی | `Item_28_Grouping.md` | B35_B36_B37_Master (بخش B36) | B38 | گروه‌بندی دارایی‌ها (Layer 1، DeFi، Stablecoin، ...). تعریف گروه‌های اصلی و فرعی. |
| ۲۹ | دامیننس کیچن | `Item_29_Kitchen_Dominance.md` | — | B31, B44 | دامیننس دارایی در مارکت کیچن. BTC.D، ETH.D، Stablecoins.D. |
| ۳۰ | اسنپ‌شات | `Item_30_Snapshot.md` | B40_B41_Master | B39, B45 | ثبت روزانه داده‌ها با هش SHA-256. نسخه‌دار، برای بازتولیدپذیری. |

---

## توضیح موارد ویژه

### فایل‌های Legacy موجود (۱۹ فایل)

این‌ها در جلسات گذشته نوشته شده‌اند و طراحی‌شان موجود است:

`B01_Master` · `B02_Master` · `B03_Master` · `B04_Master` · `B05_Master` · `B07_Master` · `B08_Master` · `B10_B11_Master` · `B12_Master` · `B13_Master` · `B14_Master_1..5` · `B15_Master_1` · `B17_B18_Master` · `B35_B36_B37_Master` · `B40_B41_Master`

### فایل‌های Legacy که نوشته نشده‌اند

این Legacyها در MAP اصلی v1.0 به آن‌ها ارجاع شده بود، ولی در جلسات گذشته هرگز نوشته نشدند. طراحی این‌ها باید بر اساس تجربه و تست‌های جدید انجام شود:

`B16` · `B20` · `B22` · `B23` · `B24` · `B25` · `B26` · `B27` · `B28` · `B29` · `B30` · `B31` · `B32` · `B33` · `B38` · `B39` · `B42` · `B43` · `B44` · `B45` · `B46` · `B47` · `B48` · `B49` · `B50` · `B51` · `B52` · `B53` · `B54` · `B55` · `B56` · `B69` · `B71` · `B72` · `B75`

### Legacyهای ادغام‌شده

این Legacyها به عنوان فایل مستقل وجود ندارند — محتوایشان داخل Legacyهای دیگر یا Itemهای جدید مدیریت می‌شود:

- `B-06` و `B-09` → داخل `B05_Master` ادغام شده‌اند
- `B-19` (Stablecoin) → داخل `Item_03` (Universe) مدیریت می‌شود
- `B-21` (XXX/BTC Coverage) → داخل `B04_Master` مدیریت می‌شود
- `B-37` (Priority) → داخل `B14_Master` مدیریت می‌شود
- `B-70` (Canonical Data Model) → داخل `B07_Master` و `B08_Master` مدیریت می‌شود
- `B-73` و `B-74` → هرگز وجود نداشتند (شماره‌گذاری پرش داشت)

### B-10 و B-11 — خارج از ۳۰ آیتم

`B-10` (Order Book) و `B-11` (Trades) در ۳۰ آیتم نیستند. هر دو به فاز ۳ (Trade Management) موکول شده‌اند.

---

## قواعد استفاده

۱. برای یافتن هر آیتم: از جدول بالا استفاده کن.

۲. برای تغییر یک آیتم فعال: Amendment جدید به فایل `B_items/Item_XX_*.md` اضافه کن.

۳. برای مرجع تاریخی: به `B_legacy/BXX_*.md` مراجعه کن.

۴. برای درخواست آیتم جدید: ابتدا با Owner هماهنگ کن. بعد به جدول اضافه کن (شماره ۳۱، ۳۲، و...).

۵. هر آیتم جدیدی که نوشته می‌شود، باید در همین جدول به‌روزرسانی شود.

---

## تغییرات این فایل

| نسخه | تاریخ | تغییرات |
|---|---|---|
| ۱.۰ | ۲۶ اکتبر ۲۰۲۶ | نسخه اولیه. ۳۰ آیتم. |
| ۱.۱ | ۲۸ اکتبر ۲۰۲۶ | حذف ستون وضعیت (به دلیل تغییرات مستمر). اصلاح مسیرها به `B_items`/`B_legacy`. افزودن ستون دامنه مسئولیت. به‌روزرسانی Legacy موجود/نوشته‌نشده. |

---

**پایان MAP.md**
```

---
