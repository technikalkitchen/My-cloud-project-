#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v3.4 FINAL — 9 corrective patches (TD 5 + Extractor 4)
Idempotent — اجرای دوباره، skip می‌کند.

Usage:
  python3 tests/evidence/scripts/patch_v34_7fixes.py --dry-run
  python3 tests/evidence/scripts/patch_v34_7fixes.py --apply
"""
import sys
import re
import shutil
from pathlib import Path
from datetime import datetime

TARGET = Path("tests/TEST_MAP_v3.4_FINAL.md")
APPLY = "--apply" in sys.argv
DRY = not APPLY


def load():
    if not TARGET.exists():
        print(f"❌ فایل پیدا نشد: {TARGET}")
        sys.exit(1)
    return TARGET.read_text(encoding="utf-8")


def save(content):
    if DRY:
        print("\n  [DRY-RUN] بدون تغییر فایل")
        return
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = TARGET.with_suffix(f".md.bak-{ts}")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(content, encoding="utf-8")
    print(f"\n  ✅ ذخیره: {TARGET}")
    print(f"  🔒 backup: {backup.name}")


# FIX-1: ۷ NO_DATA names + targeting caveat
def fix1(c):
    if "۷ NO_DATA (A5، ۶ Nov — audit ۱۱ Nov)" in c:
        return c, "skip"
    a = "### ۲.۳ — دورهٔ آماتور (نگه‌داری، ۱۰ تست)"
    if a not in c:
        return c, "not_found"
    b = """### ۲.۲.۵ — ۷ NO_DATA (A5، ۶ Nov — audit ۱۱ Nov)

| Symbol | CMC ID در final_125 | CMC ID در A9 | تفاوت |
|---|---|---|---|
| SPX | 33203 | 28081 | ⚠️ متناقض |
| XPL | 37535 | 36645 | ⚠️ متناقض |
| FF | 39273 | 38482 | ⚠️ متناقض |
| PIEVERSE | 38543 | 38849 | ⚠️ متناقض |
| KITE | 39275 | 38828 | ⚠️ متناقض |
| MON | 38320 | 30495 | ⚠️ متناقض |
| NFT | 39003 | 9816 | ⚠️ متناقض |

**کاوئات targeting (Extractor):** این ۷ با cmc_id متناقض، احتمالاً **دارایی اشتباه** را در `final_125_supply` تست کرده‌اند. «NO_DATA» ≠ «عدم وجود داده در CMC» — بلکه «عدم داده برای این cmc_id». دارایی اصلی ممکن است داده داشته باشد.

**اقدام P2:** Extractor `/search?keyword=X` → تعیین cmc_id واقعی.

"""
    return c.replace(a, b + a, 1), "applied"


# FIX-2: Section 11 — Item_05 ۴ باگ
def fix2(c):
    if "| ۱ | §۲.۱ | «۱۲۵ دارایی»" in c:
        return c, "skip"
    p = r"## Section 11 — Item_05.*?(?=\n## Section |\Z)"
    m = re.search(p, c, re.DOTALL)
    if not m:
        return c, "not_found"
    n = """## Section 11 — Item_05: ۴ باگ Amendment (LOCKED v1.0 → amendment)

| # | بخش | قبل (v1.0) | بعد (Amendment) | مرجع |
|---|---|---|---|---|
| ۱ | §2.1 | «USDT واحد مظنه استاندارد اصلی برای تمام ۱۲۵ دارایی Universe است» | «برای ۱۵۰ دارایی CMC (نمایش ۱۲۵ خالص پس از حذف Wrapped)» | R-29، ۹ Nov |
| ۲ | §3.6 | «... منابع جایگزین (مانند Binance)» | «Binance BTC-pair دارد (A9 v3.2، 3cd2cf0)، OKX ندارد. Binance به‌عنوان rate source جایگزین معتبر است، مشروط به ثبت `rate_source`» | A9 v3.2 |
| ۳ | §1.3 | `converted_fiat` | `Direct_USD_Converted` — ۴ دسته: Direct_USDT / Direct_BTC / Direct_USD_Converted / Implied | Amendment ۳۰ Oct |
| ۴ | §4 | «۵ پارامتر معلق Stage B» | «۵ پارامتر در همین سند (LOCKED، نه Stage B)» | LOCKED |

**مرجع:** `Item_05_Pending_Amendments.md` (۳۰ Oct) — ۴ تغییر پوشش داده ولی اعمال نشده.
"""
    return c[:m.start()] + n + c[m.end():], "applied"


# FIX-3: Section 5 — R-29..R-32
def fix3(c):
    if "### R-29 — Universe نهایی" in c:
        return c, "skip"
    p = r"## Section 5 — تصمیم‌های Owner.*?(?=\n## Section |\Z)"
    m = re.search(p, c, re.DOTALL)
    if not m:
        return c, "not_found"
    n = """## Section 5 — تصمیم‌های Owner

### R-29 — Universe نهایی
- **متن:** CMC Top 150 → حذف Wrapped → نمایش ۱۲۵ خالص
- **اثر:** Item_03 §۲.۱، Item_27 | **تصمیم:** Owner | **تاریخ:** ۹ Nov | **وضعیت:** APPROVED

### R-30 — ۳۰m ذخیره یا on-demand
- **متن:** on-demand (نه ذخیره) | **اثر:** Item_06، Item_12، Item_16 | **تاریخ:** ۱۱ Nov | **وضعیت:** PROPOSED

### R-31a — DefiLlama برای USD1
- **متن:** تست (تنها stablecoin بدون داده) | **اثر:** Item_15 | **تاریخ:** ۱۱ Nov | **وضعیت:** PROPOSED

### R-31b — DefiLlama برای ۷ NO_DATA
- **متن:** حذف (این ۷ stablecoin نیستند) | **اثر:** Item_15 | **تاریخ:** ۱۱ Nov | **وضعیت:** PROPOSED

### R-32 — RNDR UI: دو تاریخ یا effective_at تنها؟
- **متن:** Item_04 `effective_at=2023-11-02` + `listing_dates={binance:2024-07-22, okx:2024-07-14}`. UI کدام؟
- **اثر:** Item_04، Item_27، Package D | **تاریخ:** ۱۱ Nov | **وضعیت:** OPEN (Owner)

### تأییدهای ۱۱ Nov (بدون R جدید)
- BTC-USDC از Coinbase scope حذف (delisted)
- USDC-USD از Coinbase scope حذف (NOT_FOUND)
- Coinbase quotes = USD + USDT فقط
- POL/Bybit Policy A (strict 2024-09-04) + ثبت test_date=2023-10-25
"""
    return c[:m.start()] + n + c[m.end():], "applied"


# FIX-4: KMNO reason
def fix4(c):
    if "دلیل: نامعلوم — احتمالاً CMC re-listing" in c:
        return c, "skip"
    a = "### KMNO cmc_id: 32415 → 30986"
    if a not in c:
        return c, "not_found"
    b = """### KMNO cmc_id: 32415 → 30986
- **تاریخ:** نامعلوم | **دلیل:** نامعلوم — احتمالاً CMC re-listing یا symbol collision
- **اقدام:** Extractor تأیید (P2، در batch `/search`)
- **patch (۵ فایل):** asset_universe_master، supply JSON ×۲، supply_timeseries، Item_15
- **نگه‌داری (نه patch):** A6_discovery (`cmc_id_changes` جدا)، checkpoint ۸ Nov"""
    return c.replace(a, b, 1), "applied"


# FIX-5: A9 v3.2 stats
def fix5(c):
    if "**BTC-pair: PENDING" in c:
        return c, "skip"
    old = "| **A9 OKX v3.2** | Q6 | ۰۵، ۱۸ | **3cd2cf0** | **EXISTS ✅ — ETH BTC-pair=2018-01-10 (11 iter)، BTC/USD=NOT_LISTED، effective_min تغییر نکرد** |"
    if old not in c:
        return c, "not_found"
    new = "| **A9 OKX v3.2** | Q6 | ۰۵، ۱۸ | **3cd2cf0** | **EXISTS ✅ — BTC-pair: PENDING (نیازمند اسکریپت)، USD: PENDING، USDT: ۱۰۵/۱۵۰. ETH BTC-pair=2018-01-10 (11 iter). BTC/USD=NOT_LISTED. effective_min changes=0** |"
    return c.replace(old, new, 1), "applied"


# FIX-6: Section 7 — count 28→30
def fix6(c):
    if "**جمع** | **۲۸ ردیف** | **۳۰ آیتم**" in c:
        return c, "skip"
    p = r"## Section 7 — شمارش نهایی.*?(?=\n## Section |\Z)"
    m = re.search(p, c, re.DOTALL)
    if not m:
        return c, "not_found"
    n = """## Section 7 — شمارش نهایی (۳۰ آیتم)

| دسته | ردیف | آیتم |
|---|---|---|
| READY | ۶ | ۶ |
| READY_NEEDS_DOC | ۱۶ | ۱۸ |
| PARTIAL | ۵ | ۵ |
| BLOCKED | ۱ | ۱ |
| **جمع** | **۲۸ ردیف** | **۳۰ آیتم** |

**READY (۶):** ۰۲، ۰۳، ۰۴، ۰۷، ۱۵، ۱۶
**READY_NEEDS_DOC (۱۶ ردیف / ۱۸ آیتم):** ۰۶، ۰۸، ۱۰، ۱۲، ۱۴، ۱۷، ۱۹، **۲۰، ۲۱**، ۲۲، **۲۳، ۲۴**، ۲۵، ۲۶، ۲۷، ۲۸، ۲۹، ۳۰
**PARTIAL (۵):** ۰۱، ۰۵، ۰۹، ۱۱، ۱۸
**BLOCKED (۱):** ۱۳

### آمار تست‌ها
| دسته | تعداد |
|---|---|
| فعال | ۳۰ |
| آماتور | ۱۰ |
| منسوخ | ۱۶ + ۱ data_source |
| PENDING واقعی | ۵ |
| تصمیم Owner | ۹ |
"""
    return c[:m.start()] + n + c[m.end():], "applied"


# FIX-7: Reproduction note A1-A3
def fix7(c):
    if "**Reproduction note:**" in c:
        return c, "skip"
    a = "| A1 مبدأ ۵m | Q1 | ۰۱، ۰۳، ۱۳ | no_commit (chat_session) | professional ۷ Nov، ۶ صرافی |"
    if a not in c:
        return c, "not_found"
    n = a + """

**Reproduction note:** A1-A3 اسکریپت در Repo ندارند (`no_commit`). خروجی‌ها در TEST_MAP v2.1 ثبت شده. برای بازتولید → TD باید بازنویسی کند (R-12b)."""
    return c.replace(a, n, 1), "applied"


# FIX-8: PENDING Table (Section 4) — TD Patch 5
def fix8(c):
    if "| ۱ | Coinbase full scan | P0 | TD | **Script in TD hands" in c:
        return c, "skip"
    p = r"## Section 4 — PENDING واقعی.*?(?=\n## Section |\Z)"
    m = re.search(p, c, re.DOTALL)
    if not m:
        return c, "not_found"
    n = """## Section 4 — PENDING واقعی (۶)

| # | تست | P | مالک | وضعیت دقیق |
|---|---|---|---|---|
| ۱ | Coinbase full scan | P0 | TD | **Script in TD hands (pending AM approval). JSON نه تولید شده.** |
| ۲ | Bitstamp diagnostic | P0 | TD | **Script not yet written.** |
| ۳ | Coinbase BTC-USDT pair date | P1 | TD | (در full scan پوشش) |
| ۴ | WS Binance/Bybit | P2 | TD | Script not written |
| ۵ | ۷ CMC ID | P2 | Extractor | `/search` endpoint patch لازم |
| ۶ | USD1 DefiLlama | P3 | Extractor | Script not written |
"""
    return c[:m.start()] + n + c[m.end():], "applied"


# FIX-9: A10 Definition (Section 2.7) — TD Patch 5
def fix9(c):
    if "**A10 = audit step ۱۰**" in c:
        return c, "skip"
    a = "قانون: TEST001 پیش از R-11 و A2 است. Item_01/06/16 نباید از TEST001 مشتق شوند."
    if a not in c:
        return c, "not_found"
    b = "**A10 = audit step ۱۰** (بررسی وجود `app/market/test001/adapters.py`) — نه تست جدا.\n\n" + a
    return c.replace(a, b, 1), "applied"


FIXES = [
    ("FIX-1", "۷ NO_DATA names + caveat", fix1),
    ("FIX-2", "Item_05 ۴ باگ", fix2),
    ("FIX-3", "R-29..R-32", fix3),
    ("FIX-4", "KMNO reason", fix4),
    ("FIX-5", "A9 v3.2 stats", fix5),
    ("FIX-6", "Section 7 count", fix6),
    ("FIX-7", "Reproduction A1-A3", fix7),
    ("FIX-8", "PENDING Table (Section 4)", fix8),
    ("FIX-9", "A10 Definition", fix9),
]


def main():
    print("═" * 60)
    print("v3.4 FINAL — 9 corrective patches")
    print("Mode:", "APPLY" if APPLY else "DRY-RUN")
    print("═" * 60)

    c = load()
    print(f"\n📂 {TARGET} ({len(c)} chars)")

    s = {"applied": 0, "skip": 0, "not_found": 0}
    for fid, desc, fn in FIXES:
        print(f"\n[{fid}] {desc}")
        c, st = fn(c)
        s[st] = s.get(st, 0) + 1
        if st == "applied":
            print("  ✅ applied")
        elif st == "skip":
            print("  ⏭  skip (already)")
        else:
            print("  ⚠️  anchor not found")

    print("\n" + "═" * 60)
    print(f"  applied: {s['applied']}/9 | skip: {s['skip']}/9 | not_found: {s['not_found']}/9")
    print("═" * 60)

    if s["not_found"] > 0:
        print("\n  ⚠️ تعدادی anchor پیدا نشد. لطفاً خروجی dry-run را برای AM-02 بفرست.")

    if not DRY and s["applied"] > 0:
        save(c)
        print("\n  بعد:")
        print("    git add tests/TEST_MAP_v3.4_FINAL.md")
        print("    git add tests/evidence/scripts/patch_v34_7fixes.py")
        print("    git commit -m 'docs(TEST_MAP): v3.4 FINAL — 9 patches (TD 5 + Extractor 4)'")
        print("    git push")
    elif DRY:
        print("\n  [DRY-RUN] برای اعمال: --apply")


if __name__ == "__main__":
    main()
