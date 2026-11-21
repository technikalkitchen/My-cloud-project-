# گزارش جستجو — یونیورس هر صرافی

نتیجه: تست «یونیورس هر صرافی» به Item_13 (Bootstrap) و Item_20 (Exchange Reliability) تعلق دارد.

شواهد:
- docs/B_items/Item_Registry.md خط 12: available_from و presence_status در Item_13 (Bootstrap) محاسبه می‌شوند.
- docs/B_items/Item_Registry.md خط 22-23: Item_13 = تاریخ شروع داده‌ها per-exchange؛ Item_20 = پوشش هر صرافی از ۱۲۵ دارایی (Per-Exchange Coverage).
- docs/MAP.md خط 68: Item_13 «دریافت اولیه ۱۲۵ دارایی از ۲۰۱۷ تا امروز».
- docs/MAP.md خط 75: Item_20 «امتیاز اعتبار صرافی. بر اساس پوشش Universe...».
- tests/TEST_MAP_v3.4_FINAL.md خط 20: Q1 (هر صرافی چند کوین و از چه تاریخی؟) → Items 01، 03، 13.

Itemهای مرتبط با «داده‌ی صرافی‌ها»: Item_01 (صرافی‌ها/Endpointها)، Item_13 (Bootstrap/دریافت اولیه)، Item_20 (اعتبار صرافی/پوشش).
EOF