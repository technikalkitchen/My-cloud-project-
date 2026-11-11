#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v3.4.4 — FIX-4..7 + Appendix D (A6) + E (A4 schema)."""
import sys, json, shutil
from pathlib import Path
from datetime import datetime

TEST_MAP = Path("tests/TEST_MAP_v3.4_FINAL.md")
P_A6 = Path("tests/evidence/A6_A7_discovery_2026-11-08.json")
P_A6_OKX = Path("tests/evidence/A6_A7_okx_correction_2026-11-09.json")
P_A9 = Path("tests/evidence/a9_asset_start_dates_2026-11-08.json")
APPLY = "--apply" in sys.argv


def load(p):
    if not p.exists():
        print(f"  ⚠️ {p} نیست")
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  ❌ PARSE {p}: {e}")
        return None


# ============ FIX-4..7 ============

def fix4_5r(c):
    if "R-12a، R-12b، R-26، R-27، R-28 — Protocol rules" in c:
        return c, "skip"
    a = "Section 6 — فایل‌های منتظر"
    if a not in c:
        return c, "not_found"
    b = """R-12a، R-12b، R-26، R-27، R-28 — Protocol rules (Patcher HOLD)

توجه: این ۵ R در Cross_Item_Notes v1.0 (R-01..R-25) نیستند. در TEST_MAP ثبت موقت می‌شوند تا Patcher در Cross_Item_Notes ثبت کند.

R-12a — شواهد بزرگ | متن: فایل‌های >۱۰MB در results/ با git add -f؛ <۱۰MB در tests/evidence/ | دلیل: A5 (۱۳MB) نیازمند -f بود | وضعیت: RESOLVED

R-12b — اسکریپت‌ها در repo | متن: اسکریپت‌های تست در tests/evidence/scripts/ — نه /tmp | دلیل: /tmp سه بار پاک شد | وضعیت: RESOLVED

R-26 — Diagnostic First | متن: قبل از هر اجرای multi-exchange، ۵-۱۰ تست BTC per-exchange | دلیل: A9 v2 (بدون diagnostic) → ۰/۱۵۰ → ۴۰ دقیقه اتلاف | وضعیت: RESOLVED

R-27 — Save تدریجی | متن: اسکریپت‌های >۵ دقیقه، save per-10-asset | دلیل: A9 v2 (۴۰ دقیقه) — ریسک از دست دادن با قطع VPN | وضعیت: RESOLVED

R-28 — Return-type sync | متن: تغییر return type تابع → همه callerها آپدیت | دلیل: A9 OKX v3.1 (walk_back_quote tuple→dict) → diagnostic خطا | وضعیت: RESOLVED

Section 6 — فایل‌های منتظر"""
    return c.replace(a, b, 1), "applied"


def fix5_header(c):
    if "این فایل TEST_MAP است." in c:
        return c, "skip"
    a = "وضعیت: FINAL — ۹ patch TD+Extractor اعمال‌شده"
    if a not in c:
        return c, "not_found"
    b = """وضعیت: FINAL — ۹ patch TD+Extractor اعمال‌شده

این فایل TEST_MAP است. برای ساختار ۳۰ آیتم → docs/MAP.md v1.1. برای قوانین و CINها → docs/B_items/Cross_Item_Notes.md. برای محتوای هر آیتم → docs/B_items/Item_XX_*.md. برای شواهد تست → tests/evidence/."""
    return c.replace(a, b, 1), "applied"


def fix6_paths(c):
    if "Section 2.10 — File Paths Reference" in c:
        return c, "skip"
    a = "Section 3 — وضعیت هر آیتم"
    if a not in c:
        return c, "not_found"
    b = """Section 2.10 — File Paths Reference

فایل | مسیر
A5 Supply | results/supply_timeseries/supply_timeseries_2026-11-07.json
final_125_supply | results/final_supply_harvest/run_40351779336/final-125-supply-results/final_125_supply.json
asset_universe_master | tests/evidence/asset_universe_master_2026-11-08.json
cmc_top150 | tests/evidence/cmc_top150_2026-11-08.json
A6_A7 Discovery | tests/evidence/A6_A7_discovery_2026-11-08.json
A6_A7 OKX Correction | tests/evidence/A6_A7_okx_correction_2026-11-09.json
A9 OKX | tests/evidence/a9_okx_2026-11-09.json
A9 OKX v3.2 | tests/evidence/a9_okx_v3_2026-11-09.json
A9 OKX USDC retry | tests/evidence/a9_okx_usdc_retry_2026-11-09.json
POL Bybit Test | tests/evidence/pol_bybit_test_2026-11-08.json
A4 OHLCV Format | tests/evidence/2026-11-07_A4_OHLCV_Format.md
audit_2026-11-11 | tests/evidence/audit_2026-11-11.json + .md
Coinbase Diagnostic | tests/evidence/scripts/coinbase_btc_diagnostic.py
Cross_Item_Notes | docs/B_items/Cross_Item_Notes.md
MAP | docs/MAP.md
TEST_MAP v2.1 | tests/TEST_MAP.md — SUPERSEDED با v3.4

Section 3 — وضعیت هر آیتم"""
    return c.replace(a, b, 1), "applied"


def fix7_a5(c):
    if "تفاوت ۱۱۷ vs ۱۱۸:" in c:
        return c, "skip"
    a = "Reproduction note: A1-A3 اسکریپت در Repo ندارند (no_commit)."
    if a not in c:
        return c, "not_found"
    b = """تفاوت ۱۱۷ vs ۱۱۸: A5 = ۱۱۷ کلید (USD1 با ۵۰۲ error شکست خورد)؛ final_125_supply = ۱۱۸ FILLED. تفاوت فقط USD1 است.

Reproduction note: A1-A3 اسکریپت در Repo ندارند (no_commit)."""
    return c.replace(a, b, 1), "applied"


# ============ Appendix D (A6 per-item) ============

A6_ASSETS = ["MATIC", "POL", "RNDR", "RENDER", "FTM", "S", "FTT", "LUNA", "UST", "LUNC"]


def build_d():
    a6 = load(P_A6) or {}
    a6_okx = load(P_A6_OKX) or {}
    a9 = load(P_A9) or {}

    # نگاشت نقش‌ها
    roles = {
        "MATIC": "migration_source (→POL)",
        "POL": "migration_target (MATIC→)",
        "RNDR": "migration_source (→RENDER، rename)",
        "RENDER": "migration_target (RNDR→، rename)",
        "FTM": "migration_source (→S)",
        "S": "migration_target (FTM→)",
        "FTT": "delisted",
        "LUNA": "delisted",
        "UST": "delisted",
        "LUNC": "survivor",
    }

    def get_status(sym, ex):
        # OKX از a6_okx
        if ex == "OKX":
            entry = a6_okx.get("assets", {}).get(sym)
            if isinstance(entry, dict):
                best = entry.get("best")
                if isinstance(best, dict):
                    return f"TESTED {best.get('oldest','?')}"
                return "NOT_LISTED"
        # Binance/Bybit/Bitstamp/Coinbase از a9
        entry = a9.get(sym)
        if isinstance(entry, dict):
            ex_data = entry.get("exchanges", {}).get(ex)
            if isinstance(ex_data, dict):
                st = ex_data.get("status", "?")
                ps = ex_data.get("price_start")
                return f"{st} {ps or ''}".strip()
        return "-"

    lines = [
        "### Appendix D — A6 Migration/Delisted Per-Item",
        "",
        "**منبع:** `A6_A7_discovery_2026-11-08.json` + `A6_A7_okx_correction_2026-11-09.json` + `a9_asset_start_dates_2026-11-08.json`",
        "",
        "**کاوئات:**",
        "- **MATIC/RNDR/FTM (source):** OKX pair را rename کرده — sourceها NOT_LISTED، فقط target",
        "- **Binance/Bybit:** هر دو source و target (dual-listing)",
        "- **POL Bybit:** از 2023-10-25 (test_date)، launchTime=null — pre-migration alias",
        "",
        "| Asset | Role | OKX | Binance | Bybit | Bitstamp | Coinbase |",
        "|---|---|---|---|---|---|---|",
    ]
    for sym in A6_ASSETS:
        role = roles.get(sym, "?")
        okx = get_status(sym, "OKX")
        bn = get_status(sym, "Binance")
        bb = get_status(sym, "Bybit")
        bs = get_status(sym, "Bitstamp")
        cb = get_status(sym, "Coinbase")
        lines.append(f"| {sym} | {role} | {okx} | {bn} | {bb} | {bs} | {cb} |")
    lines.append("")
    lines.append("**جمع:** ۱۰ asset (۶ migration + ۳ delisted + ۱ survivor)")
    return "\n".join(lines)


# ============ Appendix E (A4 ExchangeCandleSchema) ============

def build_e():
    lines = [
        "### Appendix E — ExchangeCandleSchema (A4 CLOSED)",
        "",
        "**منبع:** `tests/evidence/2026-11-07_A4_OHLCV_Format.md` (A4، ۷ Nov، commit 8c1f4d5 + 6320395)",
        "",
        "**۵ ناسازگاری حیاتی:**",
        "1. **Field order:** Coinbase `[ts, low, high, open, close, vol]` — معکوس",
        "2. **۴ timestamp format:** ms+int / ms+str / s+int / s+str",
        "3. **Coinbase price = float** (بقیه str)",
        "4. **Direction:** asc (Binance/Bitstamp/CC) vs desc (OKX/Coinbase/Bybit)",
        "5. **Field counts:** ۱۲/۹/۷/۶",
        "",
        "**جدول کامل:**",
        "",
        "| Exchange | field_order | ts_unit | ts_type | price_type | direction | field_count |",
        "|---|---|---|---|---|---|---|",
        "| Binance | [ts,o,h,l,c,v,...] | ms | int | str | asc | 12 |",
        "| OKX | [ts,o,h,l,c,v,...] | ms | str | str | desc | 9 |",
        "| Coinbase | [ts,**l**,**h**,**o**,c,v] | s | int | **num** | desc | 6 |",
        "| Bitstamp | {timestamp,open,high,low,close,volume} | s | str | str | asc | 6 |",
        "| Crypto.com | {t,o,h,l,c,v} | ms | int | str | asc | 6 |",
        "| Bybit | [ts,o,h,l,c,v,turnover] | ms | str | str | desc | 7 |",
        "",
        "**پیامد Item_16:** Adapter باید per-exchange parse کند. ExchangeCandleSchema مرجع اجباری است.",
    ]
    return "\n".join(lines)


# ============ Main ============

def main():
    print("=" * 60)
    print("v3.4.4 — FIX-4..7 + Appendix D + E")
    print("Mode:", "APPLY" if APPLY else "DRY")
    print("=" * 60)

    if not TEST_MAP.exists():
        print(f"❌ {TEST_MAP} نیست")
        sys.exit(1)

    c = TEST_MAP.read_text(encoding="utf-8")
    print(f"📂 {TEST_MAP} ({len(c)} chars)\n")

    results = []
    for fid, fn in [
        ("FIX-4 (5R)", fix4_5r),
        ("FIX-5 (header)", fix5_header),
        ("FIX-6 (paths)", fix6_paths),
        ("FIX-7 (A5 off-by-one)", fix7_a5),
    ]:
        c, st = fn(c)
        results.append((fid, st))
        print(f"[{fid}] {st}")

    # Appendix D + E
    if "### Appendix D — A6 Migration/Delisted Per-Item" in c:
        print("[Appendix D] skip (already)")
    else:
        d = build_d()
        marker = "\n---\n"  # آخر فایل appendix C
        # append بعد از Appendix C — قبل از `---` پایانی
        # ساده‌تر: قبل از "**جمع:** 150 asset\n\n---" آخر
        a = "**جمع:** 150 asset\n\n---"
        if a in c:
            c = c.replace(a, "**جمع:** 150 asset\n\n---\n\n" + d, 1)
            print("[Appendix D] applied")
        else:
            c = c.rstrip() + "\n\n---\n\n" + d + "\n"
            print("[Appendix D] applied (appended at end)")

    if "### Appendix E — ExchangeCandleSchema" in c:
        print("[Appendix E] skip (already)")
    else:
        e = build_e()
        c = c.rstrip() + "\n\n" + e + "\n"
        print("[Appendix E] applied (appended at end)")

    if APPLY:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        bk = TEST_MAP.with_suffix(f".md.bak-{ts}")
        shutil.copy2(TEST_MAP, bk)
        TEST_MAP.write_text(c, encoding="utf-8")
        print(f"\n✅ ذخیره: {TEST_MAP}")
        print(f"🔒 backup: {bk.name}")
    else:
        # ذخیره preview در فایل جدا
        preview = Path("tests/TEST_MAP_v3.4.4_preview.md")
        preview.write_text(c, encoding="utf-8")
        print(f"\n[DRY] preview: {preview}")


if __name__ == "__main__":
    main()
