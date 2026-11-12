import os
import shutil
import sys

REGISTRY = "docs/B_items/Item_Registry.md"

# دیکشنری گنجینه‌های استخراج‌شده
TREASURES = {
    "Item_01": """
### [Legacy] محدودیت صرافی‌های خارج از Custom Range
- **Kraken:** فقط ۷۲۰ کندل آخر را دارد.
- **CEX.io:** فقط تایم‌فریم 1d دارد.
- **Bitfinex:** کند است (۱۰-۹۰ req/min).
*(منبع: B75 بخش ۷)*
""",
    "Item_08": """
### [Legacy] ساختار Metadata برای Custom Range
```json
{
  "range_type": "custom",
  "start_requested": "2020-03-01T14:45:00Z",
  "start_actual": "2020-03-01T14:45:00Z",
  "start_precision": "1d",
  "start_offset_minutes": 1003,
  "end_requested": "2024-04-01T14:45:00Z",
  "end_actual": "2024-04-01T14:45:00Z",
  "rule": "close_to_close",
  "middle_timeframe": "1d",
  "coverage_ratio": 0.5
}
```
*(منبع: B75 بخش ۱۳ و B05 بخش ۱۰)*
""",
    "Item_11": """
### [Legacy] هرم کش (Cache Pyramid) و حجم حافظه
- **5m:** ۳۰ روز اخیر (~۱۷۰ MB)
- **15m:** ۹۰ روز اخیر (~۱۷۰ MB)
- **1h:** از ۲۰۱۷ (~۱.۸ GB)
- **1d:** از ۲۰۱۱/۲۰۱۷ (~۵۰ MB)
- **TTL:** 5m (۵ دقیقه)، 15m (۱۵ دقیقه)، 1h (۱ ساعت)، 4h (۴ ساعت).
*(منبع: B75 بخش ۸ و ۹)*
""",
    "Item_15": """
### [Legacy] قانون منبع ساپلای
- **Circulating Supply:** روزانه از CoinGecko.
- **منبع واحد:** ساپلای یک منبع واحد دارد (نه per-exchange). همیشه ثابت برای همه صرافی‌ها.
*(منبع: B75 بخش ۱۲)*
""",
    "Item_20": """
### [Legacy] فرمول Coverage Ratio و وزن‌دهی
`coverage_ratio = (پایان بازه - شروع صرافی) ÷ (پایان بازه - شروع بازه)`
- اگر صرافی دیرتر آمده باشد، حذف نمی‌شود، بلکه وزن آن در محاسبات به اندازه این نسبت کاهش می‌یابد.
- تفکیک «Historical Context» (تعداد صرافی در آن دوره) از «Actual Reliability».
*(منبع: B75 بخش ۱۰ و ۱۱)*
""",
    "Item_23": """
### [Legacy] مبدأ کیچن (Kitchen Origin)
- **تاریخ دقیق:** `2017-08-01T00:00:00Z`.
*(منبع: B05 بخش ۵)*
""",
    "Item_25": """
### [Legacy] فرمول Market Cap کیچن
- `Kitchen MC = Kitchen Price × Supply`
- (در مقایسه با: `Exchange MC = Exchange Price × Supply`)
*(منبع: B75 بخش ۱۲)*
""",
    "Item_29": """
### [Legacy] فرمول Dominance
- `Exchange Dominance = Exchange MC ÷ Exchange Total MC`
- `Kitchen Dominance = Kitchen MC ÷ Kitchen Total MC`
*(منبع: B75 بخش ۱۲)*
""",
    "Package D": """
### [Legacy] منوی داینامیک و هشدارها
- منوی Default برای تک‌صرافی باید پویا باشد (مثلاً برای Crypto.com گزینه ۱۰ ساله نمایش داده نشود).
- متن نمایش تفاوت ۲ ماهه (CIN-6) و هشدارهای بازه‌ها در این پکیج مدیریت می‌شود.
*(منبع: B05 بخش ۷ و B75 بخش ۱۱)*
"""
}

def main():
    if not os.path.isfile(REGISTRY):
        print(f"[ABORT] Registry not found: {REGISTRY}")
        sys.exit(1)

    with open(REGISTRY, "r", encoding="utf-8") as f:
        reg_text = f.read()

    backup_made = False
    changes_made = 0

    for item_code, content in TREASURES.items():
        marker = f"### [Legacy] {content.split(chr(10))[0].replace('### [Legacy] ', '')}"
        if marker in reg_text:
            print(f"[SKIP] {item_code} already has legacy data.")
            continue

        anchor = f"## {item_code}"
        lines = reg_text.splitlines(keepends=True)
        inserted = False
        
        for i, line in enumerate(lines):
            if line.startswith(anchor):
                # Insert after the header line
                lines.insert(i + 1, "\n" + content.strip() + "\n\n---\n")
                inserted = True
                break

        if inserted:
            reg_text = "".join(lines)
            changes_made += 1
            print(f"[OK] Parked legacy data for {item_code}")
        else:
            print(f"[WARNING] Anchor '{anchor}' not found in Registry.")

    if changes_made > 0:
        shutil.copy2(REGISTRY, REGISTRY + ".bak")
        print("[BACKUP] Created Item_Registry.md.bak")
        with open(REGISTRY, "w", encoding="utf-8") as f:
            f.write(reg_text)
        print(f"[DONE] Parked legacy treasures for {changes_made} items.")
    else:
        print("[SKIP] No changes made.")

if __name__ == "__main__":
    main()
