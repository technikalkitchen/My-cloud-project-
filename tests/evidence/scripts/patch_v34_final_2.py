#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, shutil, re
from pathlib import Path
from datetime import datetime

TARGET = Path("tests/TEST_MAP_v3.4_FINAL.md")
APPLY = "--apply" in sys.argv

def load():
    if not TARGET.exists():
        print(f"❌ File not found: {TARGET}")
        sys.exit(1)
    return TARGET.read_text(encoding="utf-8")

def save(c):
    if not APPLY:
        print("  [DRY-RUN] No changes saved.")
        return
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    bk = TARGET.with_suffix(f".md.bak-{ts}")
    shutil.copy2(TARGET, bk)
    TARGET.write_text(c, encoding="utf-8")
    print(f"\n  ✅ Saved: {TARGET}")

def main():
    c = load()
    applied = 0

    # FIX 3: Section 4 - Coinbase BTC-USDT date
    # پیدا کردن خطی که شامل این عبارت است
    pattern_sec4 = r"(.*Coinbase BTC-USDT pair date.*?)\(در full scan پوشش\)"
    if re.search(pattern_sec4, c):
        c = re.sub(pattern_sec4, r"\1تاریخ دقیق نامشخص (قطعاً بعد از June 2020، شاهد: t4=0)", c)
        print("[3] ✅ Section 4: Coinbase BTC-USDT note updated.")
        applied += 1
    else:
        print("[3] ⏭ Section 4 note skipped (already applied or text changed).")

    # FIX 4: Section 5 - R-29 Wrapped placeholder
    # پیدا کردن بخش R-29 و اضافه کردن خط جدید بعد از خط 'اثر'
    pattern_sec5 = r"(R-29 — Universe نهایی.*?(?:اثر|· اثر):.*?\n)"
    if re.search(pattern_sec5, c, re.DOTALL):
        # بررسی اینکه آیا قبلا اضافه شده یا نه
        if "لیست ۲۵ دارایی حذف‌شده" not in c:
            c = re.sub(pattern_sec5, r"\1- **لیست ۲۵ دارایی حذف‌شده (Wrapped):** PENDING (Extractor در سشن بعد لیست ۲۵تایی را استخراج و ثبت می‌کند).\n", c, count=1, flags=re.DOTALL)
            print("[4] ✅ Section 5: R-29 Wrapped assets placeholder added.")
            applied += 1
        else:
            print("[4] ⏭ Section 5 R-29 placeholder already exists.")
    else:
        print("[4] ⚠️ Section 5: R-29 block not found.")

    print(f"\n📊 Summary: {applied} applied.")

    if APPLY:
        save(c)

if __name__ == "__main__":
    main()
