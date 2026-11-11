import json
import shutil
from pathlib import Path
from datetime import datetime

TARGET = Path("tests/TEST_MAP_v3.4_FINAL.md")
P_COINBASE = Path("tests/evidence/a9_coinbase_2026-11-11.json")

def main():
    c = TARGET.read_text(encoding="utf-8")
    
    # Check Coinbase BTC direct_start for Row 4
    btc_direct = None
    if P_COINBASE.exists():
        with open(P_COINBASE) as f:
            cb = json.load(f)
            btc_data = cb.get("assets", {}).get("BTC", {})
            btc_direct = btc_data.get("direct_start")
            
    # 1. Fix Appendix A Caveats with check
    old_bitstamp = "- **Bitstamp:** فقط BTC=TESTED (۱/۱۵۰)؛ بقیه `NOT_FOUND` = باگ pair A9 v2 (`btcusdt` vs `btcusd`). نیازمند retest (P0)."
    new_bitstamp = "- **Bitstamp:** ۸۵/۱۵۰ TESTED (پس از اجرای A9 Bitstamp full در ۱۱ Nov). ۶۵ NOT_LISTED واقعی (در USDT/USD/BTC چک شد)."
    
    old_binance = "- **Binance/Bybit `NOT_FOUND`:** فقط USDT/USD تست شد؛ A9 v3 (BTC/USD) اجرا نشد. NOT_FOUND ≠ «کلاً نیست»."
    new_binance = "- **Binance/Bybit:** ۱۱۴/۱۵۰ و ۱۲۱/۱۵۰ TESTED. مقادیر NOT_FOUND با کوئوت‌های محدود (USDT/USD) تست شده‌اند.\n- **Coinbase:** ۹۹/۱۵۰ TESTED (22 Direct USDT, 77 Converted USD از USDT-USD 2021-05-04). ۵۱ NOT_LISTED."

    c = c.replace(old_bitstamp, new_bitstamp)
    c = c.replace(old_binance, new_binance)
    print(f"Caveats: Bitstamp={'✅' if new_bitstamp in c else '⚠️'}, Binance={'✅' if new_binance in c else '⚠️'}")

    # 2. Fix Section 13 - Update Row 4 based on BTC direct_start
    if btc_direct:
        c = c.replace(
            "| 4 | Coinbase BTC-USDT date unknown | P1 | TD | ۰۵ |",
            f"| 4 | Coinbase BTC-USDT date found ({btc_direct}) | ✅ RESOLVED | TD | ۰۵ |"
        )
        print(f"Row 4: ✅ RESOLVED (BTC direct_start={btc_direct})")
    else:
        c = c.replace(
            "| 4 | Coinbase BTC-USDT date unknown | P1 | TD | ۰۵ |",
            "| 4 | Coinbase BTC-USDT date unknown (قطعاً بعد از 2020) | P1 | TD | ۰۵ |"
        )
        print("Row 4: ⏭ P1 (No BTC direct_start)")

    # 3. Fix the Note (TD's point 2)
    old_note = "**Note:** Issues 1, 2, 4, 5, 6, 7, 8, 11, 13 are DATA/DESIGN gaps (mostly P2/Owner), NOT test failures. They do not block Phase 1 (writing items)."
    new_note = "**Note:** These issues do not block Item_08 (Data Contract). Resolve before writing: #1(7 NO_DATA)→Item_03/15, #2(KMNO)→Item_03/15, #5(POL Bybit)→Item_04, #7(币安人生)→Item_03."
    c = c.replace(old_note, new_note)
    print(f"Note: {'✅' if new_note in c else '⚠️ (old note not found)'}")

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy2(TARGET, TARGET.with_suffix(f".md.bak-{ts}"))
    TARGET.write_text(c, encoding="utf-8")
    print("✅ TEST_MAP updated.")

if __name__ == "__main__":
    main()
