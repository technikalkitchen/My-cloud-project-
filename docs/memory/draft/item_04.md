# draft item_04 — پیش‌نویس تأییدنشده، قاعده نیست
Source: docs/B_items/Item_04_Migration_Map.md (104 خط) | Extracted: 2026-11-21 | وضعیت سند: ✅ CLOSED (TD و Owner، ۲۸ اکتبر ۲۰۲۶)

## ادعاهای سند (به ترتیب بخش‌ها)
- [§1] دامنه: فقط مهاجرت‌ها و renameهای ساده؛ موارد پیچیده در جدول جداگانه New Assets
- [§2] asset_id پایدار داخلی؛ CMC ID صرفاً Source ID
- [§2] فیلدها: asset_id, old_symbol, new_symbol, old_source_id, new_source_id, migration_type, effective_at, conversion_ratio, event_status
- [§3] POL: MATIC→POL, migration, effective 2024-09-04, ratio 1, CONFIRMED
- [§3] S: FTM→S, rename, effective 2024-12-18, ratio 1, CONFIRMED
- [§3] RENDER: RNDR→RENDER, migration, effective 2023-11-02, ratio 1, CONFIRMED
- [§3] effective_at = مرز هویت در سطح پروژه؛ تاریخ دقیق per-exchange در Adapter (Stage B) و Item_05
- [§4.1] تاریخ < effective_at → old_symbol؛ ≥ effective_at → new_symbol
- [§4.2] ساپلای تاریخی old_symbol از اولین داده معتبر تا مرز مهاجرت؛ قبل از آن UNAVAILABLE
- [§4.2] برای FTM/S، نسبت ۱:۱ مجوز ادغام کورکورانه نیست ( FTMO Sonic زنجیره جدید)
- [§5] CMC داده POL اوایل ۲۰۲۴ (۷۴ میلیون) خطای داده‌ای؛ ۱۰ میلیارد = Initial Supply نه Circulating
- [§5] ساپلای MATIC از CMC (ID 3890) تا مرز مهاجرت
- [§5] ساپلای POL از مرز مهاجرت: منبع جایگزین (Polygon explorer یا POLTRACK)
- [§5] O-2: تعریف دقیق endpoint و نوع متریک منبع جایگزین در Stage B؛ تا آن زمان UNAVAILABLE
- [§6] هر رکورد ساپلای: source, source_timestamp, supply_method, validation_status
- [§6] asset_id واحد = هویت پایدار؛ CMC ID = مشخصات منبع
- [§7] O-1: پشتیبانی مهاجرت‌های پیچیده (BTT, LUNA) در فاز ۲ (Owner)
- [§7] O-2: تعریف منبع جایگزین POLTRACK/آن‌چین و نوع متریک (TD، Stage B)
- [§7] O-3: قالب نمایش نماد قدیم/جدید در UI (TD/D، طراحی D)

## سؤال‌های باز و TODOهای خود سند
- O-1: پشتیبانی مهاجرت‌های پیچیده در فاز ۲ (تصمیم Owner)
- O-2: تعریف دقیق منبع جایگزین برای ساپلای POL (TD، Stage B)
- O-3: قالب نمایش نماد قدیم/جدید در UI (TD/D)

## تکیه بر تصمیم/Item دیگر
- Item_03 (Universe، asset_id)، Item_05 (Canonical Pair، تاریخ per-exchange)، Item_08 (Data Contract)، Item_15 (Supply)

## چک کامل بودن
بخش‌های سند: 7 (چه چیزی + زیرمجموعه ۱-۶ + موارد OPEN + وضعیت نهایی) | در خلاصه: 7 | ردشده با دلیل: هیچ
EOF