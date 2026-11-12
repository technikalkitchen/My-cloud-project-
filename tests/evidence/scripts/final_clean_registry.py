import os
import shutil
import sys
import re

REGISTRY = "docs/B_items/Item_Registry.md"

def main():
    if not os.path.isfile(REGISTRY):
        print(f"❌ فایل پیدا نشد: {REGISTRY}")
        sys.exit(1)

    with open(REGISTRY, "r", encoding="utf-8") as f:
        content = f.read()

    # گرفتن بکاپ
    shutil.copy2(REGISTRY, REGISTRY + ".bak_final")
    print("✅ بکاپ از Registry گرفته شد.")

    changes = 0

    # ۱. اصلاح هرم کش (با Regex)
    # الگو: سرتیتر هرم کش را پیدا کن، و هر چیزی تا قبل از --- بعدی را جایگزین کن
    pattern_cache = r"(### \[Legacy\] هرم کش \(Cache Pyramid\)\n)(.*?)(\n\n---)"
    new_cache_text = "**اصلاح‌شده طبق R-30 (TEST_MAP):** 15m پایه اصلی است (نه 5m). 5m فقط ۱ روز اخیر در RAM. 15m/1h/1d در Persistent Storage. (منبع: B75 + R-30)"
    
    new_content, n = re.subn(pattern_cache, r"\1" + new_cache_text + r"\3", content, flags=re.DOTALL)
    if n > 0:
        content = new_content
        print("✅ هرم کش (Cache) با موفقیت اصلاح شد.")
        changes += 1
    else:
        print("⚠️ سرتیتر هرم کش پیدا نشد.")

    # ۲. اصلاح منبع ساپلای (با Regex)
    pattern_supply = r"(### \[Legacy\] قانون منبع ساپلای\n)(.*?)(\n\n---)"
    new_supply_text = "**اصلاح‌شده طبق TEST_MAP:** ساپلای روزانه از CMC (منبع اصلی) و CoinGecko (Fallback). یک منبع واحد برای همه صرافی‌ها. (منبع: B75 بخش ۱۲)"
    
    new_content, n = re.subn(pattern_supply, r"\1" + new_supply_text + r"\3", content, flags=re.DOTALL)
    if n > 0:
        content = new_content
        print("✅ منبع ساپلای با موفقیت اصلاح شد.")
        changes += 1
    else:
        print("⚠️ سرتیتر منبع ساپلای پیدا نشد.")

    if changes > 0:
        with open(REGISTRY, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"🎉 {changes} مورد با موفقیت اصلاح شد.")
    else:
        print("ℹ️ هیچ تغییری اعمال نشد.")

if __name__ == "__main__":
    main()
