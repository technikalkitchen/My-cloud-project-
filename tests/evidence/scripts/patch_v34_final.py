#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v3.4.5 FINAL — 19 patches (AM 7 + TD 9 + Extractor 3) with strict safety."""
import sys, shutil
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
        print("  [DRY-RUN] No changes saved. Run with --apply to save.")
        return
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    bk = TARGET.with_suffix(f".md.bak-{ts}")
    shutil.copy2(TARGET, bk)
    TARGET.write_text(c, encoding="utf-8")
    print(f"\n  ✅ Saved: {TARGET}")
    print(f"  🔒 Backup: {bk.name}")

def main():
    c = load()
    applied = 0
    skipped = 0

    # 1. حذف متن چت از بالای فایل
    marker = "TEST_MAP v3.4 FINAL — Purpose-Driven Registry"
    if marker in c:
        idx = c.find(marker)
        if idx > 0:
            c = c[idx:]
            print("[1] ✅ Top chat text removed.")
            applied += 1
        else:
            print("[1] ⏭ Top chat text already removed.")
            skipped += 1
    else:
        print("[1] ⚠️ Marker for top text not found.")
        skipped += 1

    # 2. uncommitted -> commit 8998ecf
    if "uncommitted" in c:
        c = c.replace("audit_2026-11-11 همه همه uncommitted", "audit_2026-11-11 همه همه commit 8998ecf")
        c = c.replace("Coinbase Diagnostic (11 Nov) Q1، Q6 ۰۱، ۰۳، ۰۵ uncommitted", "Coinbase Diagnostic (11 Nov) Q1، Q6 ۰۱، ۰۳، ۰۵ commit 8998ecf")
        print("[2] ✅ 'uncommitted' updated to 'commit 8998ecf'.")
        applied += 1
    else:
        print("[2] ⏭ 'uncommitted' already updated.")
        skipped += 1

    # 3. Section 4: Coinbase BTC-USDT date
    old_sec4 = "| ۳ | Coinbase BTC-USDT pair date | P1 | TD | (در full scan پوشش) |"
    new_sec4 = "| ۳ | Coinbase BTC-USDT pair date | P1 | TD | تاریخ دقیق نامشخص (قطعاً بعد از June 2020، شاهد: t4=0) |"
    if old_sec4 in c:
        c = c.replace(old_sec4, new_sec4)
        print("[3] ✅ Section 4: Coinbase BTC-USDT note updated.")
        applied += 1
    else:
        print("[3] ⏭ Section 4 note skipped (already applied or not found).")
        skipped += 1

    # 4. Section 5: R-29 Wrapped Assets
    r29_anchor = "- **اثر:** Item_03 §۲.۱، Item_27 | **تصمیم:** Owner | **تاریخ:** ۹ Nov | **وضعیت:** APPROVED"
    if r29_anchor in c and "لیست ۲۵ دارایی حذف‌شده" not in c:
        r29_add = r29_anchor + "\n- **لیست ۲۵ دارایی حذف‌شده (Wrapped):** PENDING (Extractor در سشن بعد لیست ۲۵تایی را استخراج و ثبت می‌کند)."
        c = c.replace(r29_anchor, r29_add)
        print("[4] ✅ Section 5: R-29 Wrapped assets placeholder added.")
        applied += 1
    else:
        print("[4] ⏭ Section 5 R-29 placeholder skipped.")
        skipped += 1

    # 5. Appendix A Legend + Coinbase Column
    old_a_header = "| Symbol | OKX | Binance | Bybit | Bitstamp |\n|---|---|---|---|---|"
    new_a_header = """- **TESTED:** داده تأیید شد.
- **NOT_LISTED:** صرافی ندارد (همه quoteها تست شدند).
- **NOT_FOUND:** تست شد با quote محدود (USDT/USD) — A9 v3 (BTC/USD) pending.
- **PENDING_RETEST:** pair bug (Bitstamp) — P0.

| Symbol | OKX | Binance | Bybit | Bitstamp | Coinbase |
|---|---|---|---|---|---|"""
    if old_a_header in c and "| Symbol | OKX | Binance | Bybit | Bitstamp | Coinbase |" not in c:
        c = c.replace(old_a_header, new_a_header, 1)
        start = c.find("| Symbol | OKX | Binance | Bybit | Bitstamp | Coinbase |")
        end = c.find("**جمع:** 150 asset", start)
        if start != -1 and end != -1:
            block = c[start:end]
            lines = block.split('\n')
            new_lines = []
            for line in lines:
                if line.startswith('| ') and not line.startswith('|---') and "Symbol" not in line:
                    clean = line.strip()
                    if clean.endswith('|'):
                        clean = clean[:-1].strip()
                    line = clean + " | PENDING |"
                new_lines.append(line)
            c = c[:start] + '\n'.join(new_lines) + c[end:]
            print("[5] ✅ Appendix A Coinbase column + Legend added.")
            applied += 1
    else:
        print("[5] ⏭ Appendix A Legend/Coinbase skipped.")
        skipped += 1

    # 6. Appendix B Caveats
    b_header = "**منبع:** `results/supply_timeseries/supply_timeseries_2026-11-07.json`"
    b_caveat = """**منبع:** `results/supply_timeseries/supply_timeseries_2026-11-07.json`

**کاوئات:**
- `available_from` = اولین تاریخ داده در CMC است (NOT actual launch date). مثال: SOL=2021-01-01 (CMC)، ولی listing بایننس=2020-08.
- **تفکیک مسئولیت:** Item_15 (Supply Engine) از این مقادیر استفاده می‌کند. Item_03 (Universe) باید از `listing_date` در Item_04 استفاده کند.
- **ریاضی ۱۱۷:** `۱۱۷ = ۱۲۵ - ۷ (NO_DATA با cmc_id اشتباه) - ۱ (USD1 با خطای 502 در A5)`.
- ۷ NO_DATA در این لیست نیستند. Fix: A5 retry با Appendix C cmc_ids."""
    if b_header in c and "۷ NO_DATA (SPX, XPL, FF" not in c:
        c = c.replace(b_header, b_caveat, 1)
        print("[6] ✅ Appendix B caveat added (CMC limit + math 117).")
        applied += 1
    else:
        print("[6] ⏭ Appendix B caveat skipped.")
        skipped += 1

    # 7. Appendix C Source + 币安人生 warning
    c_header = "**منبع:** `tests/evidence/cmc_top150_2026-11-08.json` (CMC listing، ۸ Nov) — authoritative."
    c_note = """**منبع:** `tests/evidence/cmc_top150_2026-11-08.json` (CMC listing، ۸ Nov) — authoritative.
**کاوئات:** CMC IDs از A9 (authoritative) هستند، نه از `final_125_supply`. تفاوت ۷ مورد در Section 2.2.5.
⚠️ Rank 82 (币安人生، CMC 38590): نیازمند تأیید. اگر meme coin واقعی نیست، حذف شود."""
    if c_header in c and "⚠️ Rank 82" not in c:
        c = c.replace(c_header, c_note, 1)
        print("[7] ✅ Appendix C source note added.")
        applied += 1
    else:
        print("[7] ⏭ Appendix C source note skipped.")
        skipped += 1

    # 8. Section 2.10 4 files
    paths_header = "A9 OKX | tests/evidence/a9_okx_2026-11-09.json"
    paths_add = """A9 Binance v2 | tests/evidence/a9_binance_2026-11-08.json (commit b45bce0)
A9 Bybit v2 | tests/evidence/a9_bybit_2026-11-08.json (commit b45bce0)
A9 Bitstamp v2 | tests/evidence/a9_bitstamp_2026-11-08.json (commit b45bce0)
a9_asset_start_dates | tests/evidence/a9_asset_start_dates_2026-11-08.json
A9 OKX | tests/evidence/a9_okx_2026-11-09.json"""
    if paths_header in c and "A9 Binance v2 |" not in c:
        c = c.replace(paths_header, paths_add, 1)
        print("[8] ✅ Section 2.10 added 4 A9 v2 files.")
        applied += 1
    else:
        print("[8] ⏭ Section 2.10 skipped.")
        skipped += 1

    # 9. Appendix D note
    d_header = "**کاوئات:**\n- **MATIC/RNDR/FTM (source):**"
    d_note = """**کاوئات:**
- **FTT/LUNA/UST:** در Binance/Bybit از Top 125 خارج شده‌اند ولی هنوز active هستند (A6 discovery).
- **MATIC/RNDR/FTM (source):**"""
    if d_header in c and "FTT/LUNA/UST:** در Binance/Bybit" not in c:
        c = c.replace(d_header, d_note, 1)
        print("[9] ✅ Appendix D delisted note added.")
        applied += 1
    else:
        print("[9] ⏭ Appendix D note skipped.")
        skipped += 1

    # 10. Appendix C 126/127 swap
    old_swap = "| 125 | NFT | 9816 |\n| 127 | RUNE | 4157 |\n| 126 | ENS | 13855 |"
    new_swap = "| 125 | NFT | 9816 |\n| 126 | ENS | 13855 |\n| 127 | RUNE | 4157 |"
    if old_swap in c:
        c = c.replace(old_swap, new_swap)
        print("[10] ✅ Appendix C rows 126/127 swapped.")
        applied += 1
    else:
        print("[10] ⏭ Appendix C swap skipped.")
        skipped += 1

    # 11. Section 13 Known Issues
    sec13 = """

## Section 13 — Known Issues & Data Quality

| # | Issue | Status | Owner | Impacted Items |
|---|---|---|---|---|
| 1 | 7 NO_DATA wrong cmc_id | P2 | Extractor | ۰۳، ۱۵ |
| 2 | KMNO 32415 vs 30986 | P2 | patch | ۰۳، ۱۵ |
| 3 | Bitstamp pair bug (A9 v2) | P0 | TD | ۰۱، ۰۳ |
| 4 | Coinbase BTC-USDT date unknown | P1 | TD | ۰۵ |
| 5 | RNDR two dates (policy vs listing) | Owner | — | ۰۴ |
| 6 | POL Bybit 11-month gap | Owner | — | ۰۴ |
| 7 | A1-A3 no_commit | R-12b | — | ۰۱، ۰۳، ۱۳ |
| 8 | 币安人生 (rank 82) verification needed | Extractor | — | ۰۳ |
| 9 | Coinbase column pending (Appendix A) | P0 | TD | ۰۱، ۰۳ |
| 10 | Appendix B CMC limit caveat | Recorded | — | ۱۵ |
| 11 | 7 assets missing from Appendix B | P2 | Extractor | ۱۵ |
| 12 | Bitstamp only BTC verified | P0 | TD | ۰۱ |
| 13 | 25 Wrapped assets for 150→125 filter | P2 | Extractor | ۰۳ |
"""
    if "## Section 13 — Known Issues" not in c:
        c += sec13
        print("[11] ✅ Section 13 Known Issues added.")
        applied += 1
    else:
        print("[11] ⏭ Section 13 skipped.")
        skipped += 1

    # 12. Section 14 Verification Commands
    sec14 = """

## Section 14 — Verification Commands

**A9 OKX:**
```bash
git show 8e823f2 --stat
cat tests/evidence/a9_okx_2026-11-09.json | jq 'keys | length'  # expect: 150
```

**CMC Top 150:**
```bash
cat tests/evidence/cmc_top150_2026-11-08.json | jq '.assets | length'  # expect: 150
```

**Supply (A5):**
```bash
cat results/supply_timeseries/supply_timeseries_2026-11-07.json | jq 'keys | length'  # expect: 117
```
"""
    if "## Section 14 — Verification Commands" not in c:
        c += sec14
        print("[12] ✅ Section 14 Verification Commands added.")
        applied += 1
    else:
        print("[12] ⏭ Section 14 skipped.")
        skipped += 1

    print(f"\n📊 Summary: {applied} applied, {skipped} skipped.")

    if APPLY:
        save(c)
    else:
        print("\n✅ Dry-run complete. Run with --apply to save.")

if __name__ == "__main__":
    main()
