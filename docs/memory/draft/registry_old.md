# draft registry_old — پیش‌نویس تأییدنشده، قاعده نیست
Source: docs/B_items/Item_Registry.md (29 خط) | Extracted: 2026-11-21 | وضعیت سند: جایگزین آرشیو شده (docs/legacy/Item_Registry_2026-11-15_ARCHIVE.md)

## ادعاهای سند (به ترتیب بخش‌ها)
- [§CIN-03] تست ۳ (cmc_available_from) لغو شد؛ هیچ تاریخ خامی در Item_03 ذخیره نمی‌شود
- [§CIN-03] available_from و presence_status در Item_13 (Bootstrap) محاسبه می‌شوند
- [§CIN-03] فرمول: effective_start = max(exchange_start, listing_date)
- [§CIN-03] cmc_date_added (اداری CMC) ≠ available_from (داده واقعی بازار)
- [§CIN-03] Item_03_data.md فقط لیست ۱۲۵ دارایی، بدون تاریخ شروع
- [§CIN-04] Item_03 = Global Universe (لیست مادر ۱۲۵)؛ Item_13 = تاریخ شروع per-exchange؛ Item_20 = پوشش per-exchange؛ Item_26 = پوشش تاریخی
- [§CIN-05] برای دارایی‌های مهاجرت‌شده (POL/MATIC, RENDER/RNDR, S/FTM): available_from = min(date_new, date_old) در Item_13
- [§CIN-05] Item_04 لیست مهاجرت‌ها را نگه می‌دارد؛ Item_03 فقط symbol فعلی را می‌شناسد

## سؤال‌های باز و TODOهای خود سند
- هیچ (همه CINها RESOLVED)

## تکیه بر تصمیم/Item دیگر
- Item_03 (Universe)، Item_04 (Migration Map)، Item_13 (Bootstrap)، Item_20 (Exchange Reliability)، Item_26 (Kitchen Coverage)

## چک کامل بودن
بخش‌های سند: 3 (CIN-03, CIN-04, CIN-05) | در خلاصه: 3 | ردشده با دلیل: هیچ
EOF