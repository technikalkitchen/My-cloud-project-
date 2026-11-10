#!/usr/bin/env python3
"""v3.4 — 3 fixes (matching stripped format)."""
import sys, shutil
from pathlib import Path
from datetime import datetime

TARGET = Path("tests/TEST_MAP_v3.4_FINAL.md")
APPLY = "--apply" in sys.argv
DRY = not APPLY


def load():
    if not TARGET.exists():
        print(f"❌ فایل نیست: {TARGET}")
        sys.exit(1)
    return TARGET.read_text(encoding="utf-8")


def save(c):
    if DRY:
        print("  [DRY] بدون تغییر")
        return
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    bk = TARGET.with_suffix(f".md.bak-{ts}")
    shutil.copy2(TARGET, bk)
    TARGET.write_text(c, encoding="utf-8")
    print(f"  ✅ ذخیره: {TARGET}")
    print(f"  🔒 backup: {bk.name}")


def fix1(c):
    a = "اقدام P2: Extractor /search?keyword=X → تعیین cmc_id واقعی."
    if a not in c:
        return c, "not_found"
    if "منبع A9 cmc_ids:" in c:
        return c, "skip"
    b = a + "\n\nمنبع A9 cmc_ids: cmc_top150_2026-11-08.json (CMC listing، ۸ Nov) — authoritative. final_125_supply.json با cmc_idهای اشتباه ساخته شده."
    return c.replace(a, b, 1), "applied"


def fix2(c):
    a = "dict ۱۱۷ کلید، ۱۳.۱۷MB"
    if a not in c:
        return c, "not_found"
    if "dict ۱۱۷ کلید (PROVISIONAL" in c:
        return c, "skip"
    b = "dict ۱۱۷ کلید (PROVISIONAL — pending 7 NO_DATA fix)، ۱۳.۱۷MB"
    return c.replace(a, b, 1), "applied"


def fix3(c):
    a = "«Binance BTC-pair دارد (A9 v3.2، 3cd2cf0)، OKX ندارد. Binance به‌عنوان rate source جایگزین معتبر است، مشروط به ثبت rate_source» A9 v3.2"
    if a not in c:
        return c, "not_found"
    if "Coinbase USDT-USD آنلاین (۱۱ Nov)" in c:
        return c, "skip"
    b = "«Coinbase USDT-USD آنلاین (۱۱ Nov) → same-exchange rate. Binance fallback فقط اگر USDT-USD در صرافی مبدأ نبود» Coinbase Diagnostic t8، ۱۱ Nov"
    return c.replace(a, b, 1), "applied"


FIXES = [
    ("FIX-1", "منبع A9 cmc_ids", fix1),
    ("FIX-2", "A5 provisional", fix2),
    ("FIX-3", "Item_05 §3.6", fix3),
]


def main():
    print("═" * 50)
    print("v3.4 — 3 fixes (stripped format)")
    print("Mode:", "APPLY" if APPLY else "DRY")
    print("═" * 50)
    c = load()
    print(f"📂 {TARGET} ({len(c)} chars)\n")
    s = {"applied": 0, "skip": 0, "not_found": 0}
    for fid, desc, fn in FIXES:
        print(f"[{fid}] {desc}")
        c, st = fn(c)
        s[st] += 1
        print(f"  {'✅ applied' if st=='applied' else '⏭ skip' if st=='skip' else '⚠️ not_found'}")
    print("\n" + "═" * 50)
    print(f"applied: {s['applied']}/3 | skip: {s['skip']}/3 | not_found: {s['not_found']}/3")
    print("═" * 50)
    if not DRY and s["applied"] > 0:
        save(c)


if __name__ == "__main__":
    main()
