# Item_Registry.md — Cross-Item Decisions (CIN)

> **Note:** The old registry has been archived to `docs/legacy/Item_Registry_2026-11-15_ARCHIVE.md`.
> This file ONLY records Cross-Item Decisions (CINs). 
> R-Rules are documented in their respective Item technical documents (e.g., Item_01.md, Item_06.md) or proven by tests in the MANIFEST.

---

### CIN-03: Item_03 (Universe) vs Item_13 (Bootstrap)
- **Status:** RESOLVED (۱۵ نوامبر ۲۰۲۶)
- **تصمیم:** تست ۳ (cmc_available_from) به طور کامل **لغو شد**. ما هیچ تاریخ خامی (نه CMC و نه صرافی) در Item_03 ذخیره نمی‌کنیم.
- **محل محاسبه:** فیلدهای `available_from` و `presence_status` در **Item_13 (Bootstrap)** محاسبه می‌شوند.
- **فرمول (طبق نظر Owner):** `effective_start = max(exchange_start, listing_date)`. (داده‌های قبل از تاریخ شروع صرافی نیازی نیست).
- **دلیل لغو تست ۳:** تاریخ `date_added` در CMC یک تاریخ اداری است و مبنای داده‌های واقعی بازار نیست.
- **تصریح مهم:** `available_from` (محاسبه‌شده در Item_13) = تاریخ داده واقعی بازار. `cmc_date_added` (در Item_08 §5) = تاریخ اداری CMC. این دو کاملاً متفاوتند و نباید قاطی شوند.
- **اثر:** فایل `Item_03_data.md` فقط لیست ۱۲۵ دارایی را دارد و شامل هیچ تاریخ شروعی نیست.

### CIN-04: Global Universe vs Per-Exchange vs Historical
- **Status:** RESOLVED (۱۵ نوامبر ۲۰۲۶)
- **تصمیم:**
  - **Item_03 (Universe):** فقط لیست مادر ۱۲۵ دارایی (Global Universe) را تعریف می‌کند.
  - **Item_13 (Bootstrap):** تاریخ شروع داده‌ها را برای هر دارایی در هر صرافی فراهم می‌کند.
  - **Item_20 (Exchange Reliability):** پوشش هر صرافی از این ۱۲۵ دارایی (Per-Exchange Coverage) را محاسبه می‌کند.
  - **Item_26 (Kitchen Coverage):** پوشش تاریخی (Historical Universe) در بازه‌های مختلف را محاسبه می‌کند.

### CIN-05: Migrated Assets & available_from
- **Status:** RESOLVED (۱۶ نوامبر ۲۰۲۶)
- **آیتم‌های درگیر:** Item_03, Item_04, Item_13
- **تصمیم:** برای دارایی‌های مهاجرت‌شده (POL↔MATIC، RENDER↔RNDR، S↔FTM)، مقدار `available_from` در Item_13 برابر است با `min(date_new, date_old)`. آیتم ۴ (Migration Map) لیست این مهاجرت‌ها را نگه می‌دارد و آیتم ۳ فقط symbol فعلی را می‌شناسد.

# یادداشت‌های منتظر (برای وقتی به آن آیتم‌ها می‌رسیم)
هر مورد فقط یک جا مالک دارد. اینجا فقط برای گم‌نشدن نگه داشته می‌شود.

## آیتم ۱۴ (کالکتور)
- کالکتور پیوسته است. عبارت «روزانه» در MAP اشتباه است.
- ۵ دقیقه‌ای‌ها از وب‌سوکت می‌آیند. هدف: حداکثر دارایی در هر درخواست.
- رم فقط ۳ کندل ۵ دقیقه‌ای اخیر را نگه می‌دارد. کش، ۱ روز ۵ دقیقه‌ای.
- هر ۱۵ دقیقه، ۳ کندل ۵ دقیقه‌ای ← ۱ کندل ۱۵ دقیقه‌ای. بقیه‌ی پایه‌ها (۱ ساعت، ۱ روز) به همین ترتیب. روش دقیق هنوز روشن نیست.
- تست: محدودیت‌های وب‌سوکت (جدول در آیتم ۱، ارجاع در آیتم ۹).
- تست: کندل ساخته‌شده‌ی خودمان در برابر کندل رسمی صرافی. ریسک: کندل گم‌شده یا هنوز بسته‌نشده.

## آیتم ۶، بخش ۲ (تجمیع)
- قانون تجمیع فقط همین‌جا نوشته شود و کالکتور هم از همین استفاده کند: Open اولین، Close آخرین، High بالاترین، Low پایین‌ترین، Volume جمع.

## آیتم ۱
- D-03 اصلاح شود: ۶ صرافی (با بایبیت)، نه ۵.

## MOCKUP_FINAL.md
- جمله‌ی «تایم‌فریم‌ها ثابت‌اند» در ردیف Default حذف شود. بازه‌های Default همان دستورهای آماده‌ی کیبورد (حدود ۴۱ تا) هستند.
- 
