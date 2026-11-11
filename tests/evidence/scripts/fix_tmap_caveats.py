import shutil
from pathlib import Path
from datetime import datetime

TARGET = Path("tests/TEST_MAP_v3.4_FINAL.md")

def main():
    c = TARGET.read_text(encoding="utf-8")

    # 1. Fix Appendix A Caveats (Old text replaced with new reality)
    old_bitstamp_caveat = "- **Bitstamp:** فقط BTC=TESTED (۱/۱۵۰)؛ بقیه `NOT_FOUND` = باگ pair A9 v2 (`btcusdt` vs `btcusd`). نیازمند retest (P0)."
    new_bitstamp_caveat = "- **Bitstamp:** ۸۵/۱۵۰ TESTED (پس از اجرای A9 Bitstamp full در ۱۱ Nov). ۶۵ NOT_LISTED واقعی (در USDT/USD/BTC چک شد)."
    
    old_binance_caveat = "- **Binance/Bybit `NOT_FOUND`:** فقط USDT/USD تست شد؛ A9 v3 (BTC/USD) اجرا نشد. NOT_FOUND ≠ «کلاً نیست»."
    new_binance_caveat = "- **Binance/Bybit:** ۱۱۴/۱۵۰ و ۱۲۱/۱۵۰ TESTED. مقادیر NOT_FOUND با کوئوت‌های محدود (USDT/USD) تست شده‌اند.\n- **Coinbase:** ۹۹/۱۵۰ TESTED (22 Direct USDT, 77 Converted USD از USDT-USD 2021-05-04). ۵۱ NOT_LISTED."

    c = c.replace(old_bitstamp_caveat, new_bitstamp_caveat)
    c = c.replace(old_binance_caveat, new_binance_caveat)

    # 2. Fix Section 13 - Update the issue title to reflect new status
    c = c.replace(
        "| 4 | Coinbase BTC-USDT date unknown | P1 | TD | ۰۵ |",
        "| 4 | Coinbase BTC-USDT date unknown (قطعاً بعد از 2020) | P1 | TD | ۰۵ |"
    )
    
    # 3. Fix the remaining 10 issues status note in Section 13
    c = c.replace(
        "| 13 | 25 Wrapped assets for 150→125 filter | P2 | Extractor | ۰۳ |",
        "| 13 | 25 Wrapped assets for 150→125 filter | P2 | Extractor | ۰۳ |\n\n**Note:** Issues 1, 2, 4, 5, 6, 7, 8, 11, 13 are DATA/DESIGN gaps (mostly P2/Owner), NOT test failures. They do not block Phase 1 (writing items)."
    )

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy2(TARGET, TARGET.with_suffix(f".md.bak-{ts}"))
    TARGET.write_text(c, encoding="utf-8")
    print("✅ TEST_MAP caveats and Section 13 updated.")

if __name__ == "__main__":
    main()
