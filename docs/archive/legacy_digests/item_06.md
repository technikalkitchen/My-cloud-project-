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
EOF