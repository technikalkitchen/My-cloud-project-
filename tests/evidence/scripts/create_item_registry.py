import shutil
from pathlib import Path
from datetime import datetime

TARGET = Path("docs/B_items/Item_Registry.md")

def main():
    content = """# Item_Registry.md — یادداشت‌های اختصاصی آیتم‌ها

تاریخ ایجاد: ۱۲ نوامبر ۲۰۲۶
هدف: ثبت تصمیمات، محدودیت‌ها و یادداشت‌هایی که هنگام نوشتن هر یک از ۳۰ آیتم باید به آن‌ها رجوع کنیم.
وضعیت: WORKING NOTE

---

## Item_01 — Exchanges
- **CIN-1 (سابق):** تشخیص وضعیت بازار (Listed/Not Listed) باید از Metadata معتبر خود صرافی باشد، نه از نبود داده در کش.
- **R-11:** Bybit به عنوان صرافی ششم اضافه شد (۶ صرافی).

## Item_02 — Aggregators
- (در آپدیت‌های جدید حذف شده، نیازمند بررسی و نگارش مجدد)

## Item_03 — Universe
- **R-29:** Universe = ۱۵۰ CMC → حذف Wrapped → نمایش ۱۲۵ خالص.
- **CIN-8:** ۷ NO_DATA به دلیل Symbol Collision بود. `cmc_id` صحیح از Appendix C خوانده شود.
- **CIN-9:** 币安人生 (rank 82) نیازمند تایید Extractor.

## Item_04 — Migration Map
- **R-32:** RNDR دو تاریخ دارد. UI از `listing_dates` (Appendix A) استفاده کند. `policy_date` فقط بک‌گراند.
- **CIN-10:** KMNO cmc_id از 32415 به 30986 اصلاح شد.

## Item_05 — Canonical Pairs
- ۴ باگ شناسایی شده (تغییر ۱۲۵ به ۱۵۰، اصلاح Binance، تغییر نام‌گذاری، حذف Stage B) باید اعمال شود.

## Item_06 — Timeframes
- **R-30:** ۱۵m پایه ذخیره‌سازی است. ۵m شناور (Live Edge) و ۳۰m On-Demand.
- **CIN-6:** تفاوت ۲ ماهه Default و Custom در Crypto.com.
- **CIN-2 (سابق):** ساخت TFهای بالاتر از 1h (مثل 4h) وظیفه Item_06 است (On-the-Fly Aggregation).
- **CIN-3 (سابق):** الگوریتم Edge Filling در Item_06 طراحی می‌شود.

## Item_07 — Precision & Time
- (نوشته شده در فاز ۱ — APPROVED)

## Item_08 — Data Contract
- (نوشته شده در فاز ۱ — APPROVED)

## Item_09 — Rate Limit
- این آیتم فقط جدول رجیستری است. جزئیات فنی در آیتم‌های مصرف‌کننده نوشته می‌شود.
- **R-01:** سقف تلگرام (۳۰ سخت/۲۵ عملیاتی). | **R-15:** ثبت مصرف منابع (آستانه ۸۰٪).

## Item_10 — Error Handling
- (نوشته شده در فاز ۱ — APPROVED)

## Item_11 — Cache
- **R-02:** دو بافر (بسته ۲۸۸ + باز ۱ = ۲۸۹).
- **R-03:** WebSocket فقط Live Edge.
- **CIN-4 (سابق):** مدیریت صف ارسال (Outbox) و Pacing در این آیتم.
- (APPROVED)

## Item_12 — Storage
- **R-04:** چرخه Job و پنجره ۵ دقیقه.
- **R-05:** اتلاف Pacing.
- **R-06:** مالکیت used_at.
- **R-07:** ۱۶ فیلد NOT NULL در SQLite.
- **CIN-5 (سابق):** ذخیره‌سازی فیزیکی و State Machine در این آیتم.
- (APPROVED)

## Item_13 — Bootstrap
- BLOCKED (منتظر A8).

## Item_14 — Collector
- **CIN-11:** زمان‌بندی اجرای Collector در این آیتم است (Cron-job).

## Item_15 — Supply
- **R-31a:** تست DefiLlama برای USD1.
- **R-31b:** DefiLlama برای ۷ NO_DATA حذف شد.
- **CIN-12:** A5 = ۱۱۷ کلید، final_125 = ۱۱۸ FILLED (تفاوت USD1).

## Item_16 — OHLCV
- **CIN-13:** TTL برای وضعیت NOT_LISTED در این آیتم تعریف می‌شود.

## Item_17 تا Item_30
- (در جلسات آینده تکمیل می‌شود)

---

## Package A (زیرساخت)
- (یادداشت‌های WebSocket و RAM)

## Package D (تلگرام)
- **CIN-7:** کیبورد Default داینامیک (سالگرد).
- **CIN-14:** متن نمایش نهایی و هشدارها در Package D تعیین می‌شود.

---
"""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    if TARGET.exists():
        shutil.copy2(TARGET, TARGET.with_suffix(f".md.bak-{ts}"))
    TARGET.write_text(content, encoding="utf-8")
    print("✅ Item_Registry.md ساخته شد با ساختار ۳۰ آیتم.")

if __name__ == "__main__":
    main()
