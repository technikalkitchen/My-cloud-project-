# گزارش قدم ۳الف — خلاصه‌برگه‌ها

## docs/memory/item_06.md

# item_06
Source: docs/B_items/Item_06_Part1_Timeframes.md (132 خط) | Synced: 2026-11-21 | Status: NEEDS_REWORK

## قواعد معتبر
- تنها ۳ تایم‌فریم پایه: 5m (۳۰ روز اخیر، کش لغزان)، 1h و 1d (کش دائمی از مبدأ تاریخی) (زیرمجموعه ۱)
- قاعده انتخاب TF پایه: بزرگ‌ترین TF پایه که ≤TF خروجی و مرزهای زمانی قابل بازسازی باشند (زیرمجموعه ۱)
- هدف ۱۵۰ تا ۳۰۰ کندل برای هر Range (زیرمجموعه ۲)
- Aggregation: Open=اولین، High=بیشترین، Low=کمترین، Close=آخرین، Volume=مجموع فقط اگر هم‌واحد (زیرمجموعه ۳)
- کندل ناقص → data_status: PARTIAL؛ هرگز با صفر پر نشود (زیرمجموعه ۳)
- From beginning: انتخاب TF با نزدیک‌ترین تعداد کندل به محدوده ۱۵۰-۳۰۰ (الگوریتم ردیف ۴۱)
- استثناء On-Demand فقط برای لبه‌های Custom Range (زیرمجموعه ۱)

## قرار است عوض شود
- الگوریتم From beginning نهایی نشده (O-1، TD، Stage B)
- وضعیت سند PROPOSED
- Part 2 و Part 3 هنوز تعریف نشده‌اند

## ارتباط با Itemهای دیگر
Item_01، Item_16 (OHLCV)، Item_03 (Universe)، Item_13 (Bootstrap)، Item_11 (Cache)

---

## docs/memory/item_09.md

# item_09
Source: docs/B_items/Item_09_Rate_Limit.md (62 خط) | Synced: 2026-11-21 | Status: NEEDS_REWORK

## قواعد معتبر
- C-001: وزن Kline در Binance = ۲ (وابسته به پارامتر) (رجیستری)
- C-002: سقف ۳۰۰ کندل در هر درخواست (رجیستری)
- C-003: نرخ CMC ~۳ req/s (رجیستری)
- C-006: قفل SQLite روی NFS → نوشتن سریالی در صف (رجیستری)
- C-009: محدودیت کاربر ۲ درخواست/دقیقه + ۲ تریگر/۵ دقیقه (رجیستری)
- C-010: پنجره کش ۵ دقیقه (رجیستری)
- C-013: فضای ذخیره‌سازی ۱۵ گیگابایت (رجیستری)
- C-014: تاخیر Cron-job.org ۳ ثانیه (رجیستری)

## قرار است عوض شود
- C-015 تا C-019 وضعیت OPEN (نیازمند تایید Stage B)
- وضعیت سند PROPOSED
- مکانیزم‌ها در این سند طراحی نمی‌شوند (فقط رجیستری)

## ارتباط با Itemهای دیگر
Item_11 (فچ/کش)، Item_16 (داده)، Item_02/15 (CMC/ساپلای)، Item_12 (ذخیره‌سازی)، Package A/D

---

## docs/memory/item_08.md

# item_08
Source: docs/B_items/Item_08_Data_Contract.md (289 خط) | Synced: 2026-11-21 | Status: NEEDS_REWORK

## قواعد معتبر
- ۵ وضعیت داده: FULL, PARTIAL, UNAVAILABLE, N_A, PENDING (Section 1)
- PARTIAL باید coverage_ratio (0.0-1.0) و missing_ranges داشته باشد (Section 1)
- cmc_id canonical از CMC top 150 (Section 2)
- available_from = CMC data limit، نه actual launch (Section 2)
- price_path: Direct_USDT, Direct_BTC, Direct_USD_Converted, Implied, N_A (Section 4.1)
- effective_min = min(direct, converted)؛ imprecise اگر walk-back به max_iter (Section 4.3)
- Package B ۴ فایل تحویل می‌دهد: universe.json, prices.json, supply.json, ohlcv.json (Section 7)
- هر فایل schema_version: "1.0" + generated_at (Section 7)

## قرار است عوض شود
- ۷ NO_DATA cmc_id (SPX, XPL, ...) وضعیت PENDING (Section 9)
- 币安人生 (rank 82) verification pending (Section 9)
- وضعیت سند APPROVED ولی OPEN questions باقی است

## ارتباط با Itemهای دیگر
Item_03 (presence_status), Item_05 (price path), Item_15 (supply), Item_16 (OHLCV), Item_18 (provenance)
EOF