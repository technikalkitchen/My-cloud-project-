# draft item_09 — پیش‌نویس تأییدنشده، قاعده نیست
Source: docs/B_items/Item_09_Rate_Limit.md (62 خط) | Extracted: 2026-11-21 | وضعیت سند: PROPOSED (v10.1، ۳۱ اکتبر ۲۰۲۶)

## ادعاهای سند (به ترتیب بخش‌ها)
- [§هدف] رجیستری مرکزی محدودیت‌ها؛ هیچ مکانیزمی طراحی نمی‌شود؛ فقط اعلام محدودیت، اثر، شاهد، محل اثر، راهکار، مالک
- [§رجیستری] C-001: وزن Kline در Binance = ۲ (OBSERVED، تست ۲۹ اکتبر، وابسته به پارامتر) → Item_11
- [§رجیستری] C-002: سقف ۳۰۰ کندل در هر درخواست (OBSERVED، تست ۲۸ اکتبر) → Item_11 (فچ)/Item_16 (داده)
- [§رجیستری] C-003: نرخ CMC ~۳ req/s (OBSERVED، تست ۲۸ اکتبر، سقف واقعی نامشخص) → Item_02/Item_15
- [§رجیستری] C-004: PythonAnywhere ۱۰۰ ثانیه CPU روزانه (OBSERVED) → Package A/Item_13
- [§رجیستری] C-005: PythonAnywhere فقط ۱ وب‌ورکر (OBSERVED) → Package A/Item_13
- [§رجیستری] C-006: قفل SQLite روی NFS (OBSERVED) → Item_12 (نوشتن سریالی در صف)
- [§رجیستری] C-007: نرخ ارسال Telegram Bot ~۳۰ پیام/ثانیه (OBSERVED) → Package D
- [§رجیستری] C-008: مهلت پاسخ Webhook تلگرام ≤۳ ثانیه (POLICY) → Package D/Item_10
- [§رجیستری] C-009: محدودیت کاربر ۲ درخواست/دقیقه + ۲ تریگر/۵ دقیقه (POLICY) → Item_10/Package D
- [§رجیستری] C-010: پنجره کش ۵ دقیقه (POLICY) → Item_11
- [§رجیستری] C-011: دقایق و جاب‌های GitHub ASSUMED (سهمیه پلن رایگان) → Item_13
- [§رجیستری] C-012: نرخ Google Drive ASSUMED (نیازمند تست) → Item_12
- [§رجیستری] C-013: فضای ذخیره‌سازی ۱۵ گیگابایت (OBSERVED) → Item_12
- [§رجیستری] C-014: تاخیر Cron-job.org ۳ ثانیه (OBSERVED، تست ۳۰ اکتبر) → Item_14
- [§کاندید] C-015: مسدود شدن IP (HTTP 418) OPEN → Item_10
- [§کاندید] C-016: حافظه RAM PythonAnywhere OPEN (نیازمند اندازه‌گیری) → Package A
- [§کاندید] C-017: حجم پاسخ API OPEN (نیازمند تست) → Item_11
- [§کاندید] C-018: محدودیت اتصال همزمان SQLite OPEN (نیازمند تست) → Item_12
- [§کاندید] C-019: سقف اتصال همزمان WebSocket OPEN (وابسته به معماری) → Item_11
- [§کاندید] C-020: حجم فایل آپلود Telegram ≤۵۰MB (OBSERVED) → Package D
- [§Provenance] با توجه به حذف Redistribution Map، تاریخچه انتقال محتوا در خود آیتم‌ها حفظ می‌شود
- [§Provenance] مکانیزم‌های B-14 (مثل Coalescing) در بخش مربوطه آیتم‌های مقصد با ذکر منبع ثبت می‌شوند

## سؤال‌های باز و TODOهای خود سند
- C-015 تا C-019 وضعیت OPEN (نیازمند تایید Stage B)
- C-003: سقف واقعی CMC نامشخص
- وضعیت سند PROPOSED

## تکیه بر تصمیم/Item دیگر
- Item_11 (فچ/کش)، Item_16 (داده)، Item_02/15 (CMC/ساپلای)، Item_12 (ذخیره‌سازی)، Item_10 (Error)، Item_13 (Bootstrap)، Item_14 (Incremental)، Package A/D

## چک کامل بودن
بخش‌های سند: 4 (هدف + رجیستری + کاندید + Provenance) | در خلاصه: 4 | ردشده با دلیل: هیچ
EOF