#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v3.4 FINAL — Session 2 patches (3 TD #13 + 5 R + 3 appends)."""
import sys, shutil
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


def save(c):
    if DRY:
        print("\n  [DRY-RUN] بدون تغییر")
        return
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    bk = TARGET.with_suffix(f".md.bak-{ts}")
    shutil.copy2(TARGET, bk)
    TARGET.write_text(c, encoding="utf-8")
    print(f"\n  ✅ ذخیره: {TARGET}")
    print(f"  🔒 backup: {bk.name}")


# === TD #13 — 3 critical ===

def fix1(c):
    if "**منبع A9 cmc_ids:**" in c:
        return c, "skip"
    a = "**اقدام P2:** Extractor `/search?keyword=X` → تعیین cmc_id واقعی."
    if a not in c:
        return c, "not_found"
    b = a + "\n\n**منبع A9 cmc_ids:** `cmc_top150_2026-11-08.json` (CMC listing، ۸ Nov) — authoritative. `final_125_supply.json` با cmc_idهای اشتباه ساخته شده."
    return c.replace(a, b, 1), "applied"


def fix2(c):
    if "dict ۱۱۷ کلید (PROVISIONAL" in c:
        return c, "skip"
    a = "| A5 Supply timeseries | Q7 | ۱۵، ۱۹، ۲۵ | d0fd6dd | dict ۱۱۷ کلید، ۱۳.۱۷MB |"
    if a not in c:
        return c, "not_found"
    b = "| A5 Supply timeseries | Q7 | ۱۵، ۱۹، ۲۵ | d0fd6dd | dict ۱۱۷ کلید (PROVISIONAL — pending 7 NO_DATA fix)، ۱۳.۱۷MB |"
    return c.replace(a, b, 1), "applied"


def fix3(c):
    if "Coinbase USDT-USD آنلاین (۱۱ Nov) → same-exchange rate. Binance fallback" in c:
        return c, "skip"
    a = "| ۲ | §3.6 | «... منابع جایگزین (مانند Binance)» | «Binance BTC-pair دارد (A9 v3.2، 3cd2cf0)، OKX ندارد. Binance به‌عنوان rate source جایگزین معتبر است، مشروط به ثبت `rate_source`» | A9 v3.2 |"
    if a not in c:
        return c, "not_found"
    b = "| ۲ | §3.6 | «... منابع جایگزین (مانند Binance)» | «Coinbase USDT-USD آنلاین (۱۱ Nov) → same-exchange rate. Binance fallback فقط اگر USDT-USD در صرافی مبدأ نبود» | Coinbase Diagnostic t8، ۱۱ Nov |"
    return c.replace(a, b, 1), "applied"


# === 5 R — Section 5 extension ===

def fix4(c):
    if "### R-12a، R-12b، R-26، R-27، R-28" in c:
        return c, "skip"
    a = "## Section 6 — فایل‌های منتظر"
    if a not in c:
        return c, "not_found"
    b = """### R-12a، R-12b، R-26، R-27، R-28 — Protocol rules (Patcher HOLD، ثبت موقت اینجا)

**توجه:** این ۵ R در Cross_Item_Notes v1.0 (R-01..R-25) نیستند. برای خودکفایی TEST_MAP، اینجا ثبت می‌شوند. Patcher در HOLD دارد تا در Cross_Item_Notes ثبت کند.

#### R-12a — شواهد بزرگ
- **متن:** فایل‌های >۱۰MB در `results/` با `git add -f`؛ <۱۰MB در `tests/evidence/`
- **دلیل:** A5 (۱۳MB) نیازمند `-f` بود
- **وضعیت:** RESOLVED (commit d0fd6dd)

#### R-12b — اسکریپت‌ها در repo
- **متن:** اسکریپت‌های تست در `tests/evidence/scripts/` — نه `/tmp`
- **دلیل:** `/tmp` سه بار پاک شد (A1-A3، A4، S+FTM)
- **وضعیت:** RESOLVED (۸ Nov)

#### R-26 — Diagnostic First
- **متن:** قبل از هر اجرای multi-exchange، ۵-۱۰ تست BTC per-exchange
- **دلیل:** A9 v2 (بدون diagnostic) → ۰/۱۵۰ → ۴۰ دقیقه اتلاف؛ A9 OKX (۸ diagnostic) → ۱۰۵/۱۵۰ → ۶.۶ دقیقه
- **وضعیت:** RESOLVED (A9 OKX v2 walk-back)

#### R-27 — Save تدریجی
- **متن:** اسکریپت‌های >۵ دقیقه، save per-10-asset
- **دلیل:** A9 v2 (۴۰ دقیقه) — ریسک از دست دادن با قطع VPN
- **وضعیت:** RESOLVED (A9 OKX v2)

#### R-28 — Return-type sync
- **متن:** تغییر return type تابع → همه callerها آپدیت
- **دلیل:** A9 OKX v3.1 (walk_back_quote tuple→dict) → diagnostic خطا
- **وضعیت:** RESOLVED (۸ Nov)

## Section 6 — فایل‌های منتظر"""
    return c.replace(a, b, 1), "applied"


# === 3 appends (handoff) ===

def fix5(c):
    if "**این فایل TEST_MAP است.**" in c:
        return c, "skip"
    a = "**وضعیت:** FINAL — ۹ patch TD+Extractor اعمال‌شده\n\n---"
    if a not in c:
        return c, "not_found"
    b = """**وضعیت:** FINAL — ۹ patch TD+Extractor اعمال‌شده

**این فایل TEST_MAP است.** برای ساختار ۳۰ آیتم → `docs/MAP.md` v1.1. برای قوانین و CINها → `docs/B_items/Cross_Item_Notes.md`. برای محتوای هر آیتم → `docs/B_items/Item_XX_*.md`. برای شواهد تست → `tests/evidence/`.

---"""
    return c.replace(a, b, 1), "applied"


def fix6(c):
    if "## Section 2.10 — File Paths Reference" in c:
        return c, "skip"
    a = "## Section 3 — وضعیت هر آیتم"
    if a not in c:
        return c, "not_found"
    b = """## Section 2.10 — File Paths Reference

مسیر کامل فایل‌های داده (برای دستیار جدید که شواهد را چک می‌کند):

| فایل | مسیر |
|---|---|
| A5 Supply timeseries | `results/supply_timeseries/supply_timeseries_2026-11-07.json` |
| final_125_supply | `results/final_supply_harvest/run_40351779336/final-125-supply-results/final_125_supply.json` |
| asset_universe_master | `tests/evidence/asset_universe_master_2026-11-08.json` |
| cmc_top150 | `tests/evidence/cmc_top150_2026-11-08.json` |
| A6_A7 Discovery | `tests/evidence/A6_A7_discovery_2026-11-08.json` |
| A6_A7 OKX Correction | `tests/evidence/A6_A7_okx_correction_2026-11-09.json` |
| A9 OKX | `tests/evidence/a9_okx_2026-11-09.json` |
| A9 OKX v3.2 | `tests/evidence/a9_okx_v3_2026-11-09.json` |
| A9 OKX USDC retry | `tests/evidence/a9_okx_usdc_retry_2026-11-09.json` |
| POL Bybit Test | `tests/evidence/pol_bybit_test_2026-11-08.json` |
| A4 OHLCV Format | `tests/evidence/2026-11-07_A4_OHLCV_Format.md` |
| audit_2026-11-11 | `tests/evidence/audit_2026-11-11.json` + `.md` |
| Coinbase Diagnostic | `tests/evidence/scripts/coinbase_btc_diagnostic.py` |
| Cross_Item_Notes | `docs/B_items/Cross_Item_Notes.md` |
| MAP | `docs/MAP.md` |
| TEST_MAP v2.1 (قدیمی) | `tests/TEST_MAP.md` — **SUPERSEDED با v3.4** |

## Section 3 — وضعیت هر آیتم"""
    return c.replace(a, b, 1), "applied"


def fix7(c):
    if "**تفاوت ۱۱۷ vs ۱۱۸:**" in c:
        return c, "skip"
    a = "**Reproduction note:** A1-A3 اسکریپت در Repo ندارند (`no_commit`). خروجی‌ها در TEST_MAP v2.1 ثبت شده. برای بازتولید → TD باید بازنویسی کند (R-12b)."
    if a not in c:
        return c, "not_found"
    b = """**تفاوت ۱۱۷ vs ۱۱۸:** A5 = ۱۱۷ کلید (USD1 با ۵۰۲ error شکست خورد)؛ final_125_supply = ۱۱۸ FILLED (شامل USD1). تفاوت فقط USD1 است.

**Reproduction note:** A1-A3 اسکریپت در Repo ندارند (`no_commit`). خروجی‌ها در TEST_MAP v2.1 ثبت شده. برای بازتولید → TD باید بازنویسی کند (R-12b)."""
    return c.replace(a, b, 1), "applied"


FIXES = [
    ("FIX-1", "TD13: منبع A9 cmc_ids", fix1),
    ("FIX-2", "TD13: A5 provisional", fix2),
    ("FIX-3", "TD13: Item_05 §3.6", fix3),
    ("FIX-4", "5 R در Section 5", fix4),
    ("FIX-5", "Header reference", fix5),
    ("FIX-6", "Section 2.10 File Paths", fix6),
    ("FIX-7", "A5 off-by-one (USD1)", fix7),
]


def main():
    print("═" * 60)
    print("v3.4 FINAL — Session 2 patches (7 grouped)")
    print("Mode:", "APPLY" if APPLY else "DRY-RUN")
    print("═" * 60)
    c = load()
    print(f"\n📂 {TARGET} ({len(c)} chars)")

    s = {"applied": 0, "skip": 0, "not_found": 0}
    for fid, desc, fn in FIXES:
        print(f"\n[{fid}] {desc}")
        c, st = fn(c)
        s[st] += 1
        print({"applied": "  ✅ applied", "skip": "  ⏭  skip", "not_found": "  ⚠️  anchor not found"}[st])

    print("\n" + "═" * 60)
    print(f"  applied: {s['applied']}/7 | skip: {s['skip']}/7 | not_found: {s['not_found']}/7")
    print("═" * 60)

    if s["not_found"] > 0:
        print("\n  ⚠️ anchor not found — فایل markdown خراب است؟")
        print("  راه‌حل: بازنویسی با cat heredoc.")

    if not DRY and s["applied"] > 0:
        save(c)
        print("\n  بعد:")
        print("    git add tests/TEST_MAP_v3.4_FINAL.md tests/evidence/scripts/patch_v34_session2.py")
        print("    git commit -m 'docs(TEST_MAP): v3.4 FINAL — Session 2 (7 patches: TD13 + 5R + 3 appends)'")
        print("    git push")


if __name__ == "__main__":
    main()
