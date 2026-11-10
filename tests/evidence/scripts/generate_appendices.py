#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v3.4.2 — Generate Appendix A/B/C (patched: a9_okx flat + exchanges Capital)."""
import sys, json, shutil
from pathlib import Path
from datetime import datetime

TEST_MAP = Path("tests/TEST_MAP_v3.4_FINAL.md")
APPENDIX_FILE = Path("tests/TEST_MAP_v3.4.2_appendices.md")

P_A9_OKX = Path("tests/evidence/a9_okx_2026-11-09.json")
P_A9_ALL = Path("tests/evidence/a9_asset_start_dates_2026-11-08.json")
P_CMC = Path("tests/evidence/cmc_top150_2026-11-08.json")
P_SUPPLY = Path("results/supply_timeseries/supply_timeseries_2026-11-07.json")

APPLY = "--append" in sys.argv


def load(p):
    if not p.exists():
        print(f"  NOT FOUND: {p}")
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  PARSE FAIL: {p} — {e}")
        return None


def okx_statuses():
    """a9_okx: d[sym]['okx']['status']"""
    d = load(P_A9_OKX)
    if not d:
        return {}
    r = {}
    for sym, data in d.items():
        if not isinstance(data, dict):
            continue
        okx = data.get("okx")
        if isinstance(okx, dict):
            r[sym] = okx.get("status", "?")
        else:
            r[sym] = "?"
    return r


def other_statuses():
    """a9_all: d[sym]['exchanges']['Binance'|'Bybit'|'Bitstamp']"""
    d = load(P_A9_ALL)
    if not d:
        return {}, {}, {}
    bn, bb, bs = {}, {}, {}
    for sym, data in d.items():
        if not isinstance(data, dict):
            continue
        ex = data.get("exchanges", {})
        if not isinstance(ex, dict):
            continue
        def st(name):
            v = ex.get(name)
            return v.get("status", "?") if isinstance(v, dict) else "?"
        bn[sym] = st("Binance")
        bb[sym] = st("Bybit")
        bs[sym] = st("Bitstamp")
    return bn, bb, bs


def cmc_list():
    d = load(P_CMC)
    if not d:
        return []
    items = d.get("assets", d) if isinstance(d, dict) else d
    if not isinstance(items, list):
        return []
    return [(a.get("rank"), a["symbol"], a.get("cmc_id"))
            for a in items if isinstance(a, dict) and a.get("symbol")]


def supply_dates():
    d = load(P_SUPPLY)
    if not d:
        return {}
    r = {}
    for sym, data in d.items():
        if not isinstance(sym, str):
            continue
        date = None
        if isinstance(data, dict):
            dd = data.get("dates")
            if isinstance(dd, list) and dd:
                date = dd[0]
            if not date:
                for key in ("series", "data", "timeseries", "points"):
                    s = data.get(key)
                    if isinstance(s, list) and s:
                        f = s[0]
                        if isinstance(f, dict):
                            date = f.get("date") or f.get("timestamp") or f.get("t") or f.get("time")
                        elif isinstance(f, (str, int)):
                            date = f
                        if date:
                            break
            if not date:
                date = data.get("first_date") or data.get("available_from") or data.get("oldest")
        elif isinstance(data, list) and data:
            f = data[0]
            if isinstance(f, dict):
                date = f.get("date") or f.get("timestamp") or f.get("t")
            elif isinstance(f, (str, int)):
                date = f
        if date:
            s = str(date)
            r[sym] = s[:10] if len(s) >= 10 else s
    return r


def fmt_a(okx, bn, bb, bs):
    syms = sorted(set(okx) | set(bn) | set(bb) | set(bs))
    out = [
        "### Appendix A — A9 Per-Exchange Coverage",
        "",
        "**منبع:** `a9_okx_2026-11-09.json` (OKX — 105/150 TESTED، USDT+USD+USDC) + `a9_asset_start_dates_2026-11-08.json` (Binance/Bybit/Bitstamp)",
        "",
        "**کاوئات‌ها:**",
        "",
        "- **OKX:** ۱۰۵/۱۵۰ TESTED (نسخه a9_okx، جایگزین باگ a9_asset_start_dates). ۴۵ NOT_LISTED با USDT+USD+USDC هر سه تأیید شد.",
        "- **Bitstamp:** فقط BTC=TESTED (۱/۱۵۰)؛ بقیه `NOT_FOUND` = باگ pair A9 v2 (`btcusdt` vs `btcusd`). نیازمند retest (P0).",
        "- **Binance/Bybit `NOT_FOUND`:** فقط USDT/USD تست شد؛ A9 v3 (BTC/USD) اجرا نشد. NOT_FOUND ≠ «کلاً نیست».",
        "",
        "| Symbol | OKX | Binance | Bybit | Bitstamp |",
        "|---|---|---|---|---|",
    ]
    for s in syms:
        out.append(f"| {s} | {okx.get(s,'-')} | {bn.get(s,'-')} | {bb.get(s,'-')} | {bs.get(s,'-')} |")
    out.append("")
    out.append(f"**جمع:** {len(syms)} asset")
    return "\n".join(out)


def fmt_b(supply):
    out = [
        "### Appendix B — A5 Supply Dates (۱۱۷ asset)",
        "",
        "**منبع:** `results/supply_timeseries/supply_timeseries_2026-11-07.json`",
        "",
        "**کاوئات:** `available_from` = اولین date سری روزانه (دقت ۱ روز).",
        "",
        "| Symbol | available_from |",
        "|---|---|",
    ]
    for s in sorted(supply):
        out.append(f"| {s} | {supply[s]} |")
    out.append("")
    out.append(f"**جمع:** {len(supply)} asset")
    return "\n".join(out)


def fmt_c(cmc):
    out = [
        "### Appendix C — CMC Top 150",
        "",
        "**منبع:** `tests/evidence/cmc_top150_2026-11-08.json` (CMC listing، ۸ Nov) — authoritative.",
        "",
        "| Rank | Symbol | CMC ID |",
        "|---|---|---|",
    ]
    for rank, sym, cid in cmc:
        out.append(f"| {rank} | {sym} | {cid} |")
    out.append("")
    out.append(f"**جمع:** {len(cmc)} asset")
    return "\n".join(out)


def main():
    print("=" * 60)
    print("v3.4.2 — Generate Appendix A/B/C (patched)")
    print("Mode:", "APPLY" if APPLY else "GENERATE-ONLY")
    print("=" * 60)

    print("\n[1/3] خواندن JSON:")
    okx = okx_statuses()
    bn, bb, bs = other_statuses()
    cmc = cmc_list()
    supply = supply_dates()

    okx_tested = sum(1 for v in okx.values() if v == "TESTED")
    bn_tested = sum(1 for v in bn.values() if v == "TESTED")
    bb_tested = sum(1 for v in bb.values() if v == "TESTED")
    bs_tested = sum(1 for v in bs.values() if v == "TESTED")

    print(f"  OKX: {len(okx)} ({okx_tested} TESTED)")
    print(f"  Binance: {len(bn)} ({bn_tested} TESTED)")
    print(f"  Bybit: {len(bb)} ({bb_tested} TESTED)")
    print(f"  Bitstamp: {len(bs)} ({bs_tested} TESTED)")
    print(f"  CMC: {len(cmc)}")
    print(f"  Supply: {len(supply)}")

    print("\n[2/3] تولید appendix:")
    content = f"""---

## Appendix — Self-Sufficiency Lists (v3.4.2)

**تاریخ:** ۱۱ نوامبر ۲۰۲۶
**منبع:** JSONهای repo (نه از حافظه)
**هدف:** دستیار جدید بدون باز کردن فایل‌های تست به آیتم‌های ۰۱، ۰۳، ۱۵، ۱۹، ۲۵ دسترسی دارد.

{fmt_a(okx, bn, bb, bs)}

{fmt_b(supply)}

{fmt_c(cmc)}

---
"""
    APPENDIX_FILE.write_text(content, encoding="utf-8")
    print(f"  ✅ {APPENDIX_FILE} ({len(content)} chars)")

    if not APPLY:
        print(f"\n[3/3] preview: head -60 {APPENDIX_FILE}")
        print(f"  برای append: --append")
        return

    if not TEST_MAP.exists():
        print(f"  ❌ {TEST_MAP} نیست")
        sys.exit(1)

    if "## Appendix — Self-Sufficiency Lists" in TEST_MAP.read_text(encoding="utf-8"):
        print(f"  ⏭  appendix قبلاً اضافه شده")
        return

    print(f"\n[3/3] append به {TEST_MAP}:")
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    bk = TEST_MAP.with_suffix(f".md.bak-{ts}")
    shutil.copy2(TEST_MAP, bk)
    print(f"  🔒 backup: {bk.name}")
    with open(TEST_MAP, "a", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ append")


if __name__ == "__main__":
    main()
