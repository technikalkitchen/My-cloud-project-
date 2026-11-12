import os
import shutil

REGISTRY = "docs/B_items/Item_Registry.md"

TREASURES = {
    "Item_08": "### [Legacy] ساختار Metadata برای Custom Range\n- `range_type`, `start_requested`, `start_actual`, `offset_minutes`, `coverage_ratio`, `historical_context`. (منبع: B75 بخش ۱۳)",
    "Item_11": "### [Legacy] هرم کش (Cache Pyramid)\n- 5m: ۳۰ روز (~۱۷۰MB)، 15m: ۹۰ روز (~۱۷۰MB)، 1h: از ۲۰۱۷ (~۱.۸GB)، 1d: از ۲۰۱۱ (~۵۰MB). (منبع: B75 بخش ۸)",
    "Item_15": "### [Legacy] قانون منبع ساپلای\n- ساپلای روزانه از CoinGecko. یک منبع واحد برای همه صرافی‌ها. (منبع: B75 بخش ۱۲)",
    "Item_20": "### [Legacy] فرمول Coverage Ratio\n- `coverage_ratio = (پایان بازه - شروع صرافی) ÷ (پایان بازه - شروع بازه)`. تفکیک Historical Context از Actual Reliability. (منبع: B75 بخش ۱۱)",
    "Item_23": "### [Legacy] مبدأ کیچن (Kitchen Origin)\n- تاریخ دقیق: `2017-08-01T00:00:00Z`. (منبع: B05 بخش ۵)",
    "Item_25": "### [Legacy] فرمول Market Cap کیچن\n- `Kitchen MC = Kitchen Price × Supply`. (منبع: B75 بخش ۱۲)",
    "Item_29": "### [Legacy] فرمول Dominance\n- `Exchange Dominance = Exchange MC ÷ Exchange Total MC`\n- `Kitchen Dominance = Kitchen MC ÷ Kitchen Total MC`. (منبع: B75 بخش ۱۲)",
    "Package D": "### [Legacy] منوی داینامیک و هشدارها\n- فیلتر پویا برای تک‌صرافی‌ها. متن نمایش تفاوت‌ها در Package D. (منبع: B05 و B75)"
}

def main():
    with open(REGISTRY, "r", encoding="utf-8") as f:
        lines = f.readlines()

    changes = 0
    for item, text in TREASURES.items():
        anchor = f"## {item}"
        for i, line in enumerate(lines):
            if line.startswith(anchor):
                lines.insert(i + 1, f"\n{text}\n\n---\n")
                changes += 1
                break

    if changes > 0:
        shutil.copy2(REGISTRY, REGISTRY + ".bak2")
        with open(REGISTRY, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"[DONE] Forcefully added {changes} treasures.")
    else:
        print("[WARNING] No anchors found.")

if __name__ == "__main__":
    main()
