# گزارش بررسی — قدم ۵ (فقط بررسی)

## ۱) تعداد خطوط
- docs/Agents/AGENTS.md: ۶۷ خط (هدف <۹۰) ✅
- docs/Agents/STATE.md: ۲۰ خط (هدف <۴۰) ✅
- AGENTS.md ریشه: ۶ خط (هدف <۸) ✅

## ۲) مسیرهای Map
همه موجودند: docs/Agents/{AGENTS,STATE,LEDGER,00_START_HERE}.md، docs/memory/{registry,lessons,CONFLICTS,OPEN_QUESTIONS,TEST_QUEUE}.md، docs/memory/draft/ و INDEX.md، docs/B_items/، docs/PLAN_MEMORY_SETUP.md، docs/reports/LAST_REPORT.md، docs/archive/، docs/legacy/، docs/MAP.md، docs/TEAM_PROTOCOL.md، tests/evidence/، tests/evidence/gen_manifest.py.
مسیر ناموجود: ندارد.

## ۳) Placeholderها
هیچ {…} خالی نماند. تعداد: ۹ نام (۱۰ جایگزینی): {BRANCH} دوبار، {PATH_MAP}، {PATH_TEAM_PROTOCOL}، {PATH_EVIDENCE}، {PATH_STORAGE_SCRIPT}، {S_ITEM_DOCS}، {S_STORAGE}، {S_TEST_FLOW}، {S_CHANGE_CONTROL}.

## ۴) خطوط AGENTS.md قدیمی که در فایل‌های جدید نیامد
- «Main protocol: docs/Agents/00_START_HERE.md» → در Map هست.
- «Persistent state: WORK_STATE.md» → با STATE.md جایگزین شد.
- «Action log: LEDGER.md» → در Map هست.
- «LEDGER.md (tail 30)» → در فایل جدید tail -20 شد.
- سه قاعده‌ی مهاجرت (۱: PLAN، ۲: LEDGER، ۳: عدم گزارش کار انجام‌نشده) → هر سه در فایل جدید پوشش داده شده.
نتیجه: قاعده‌ای گم نشده؛ فقط اشاره‌ها به‌روز شده.

## ۵) ناهماهنگی START_HERE بخش ۶ با «registry اول»
بخش ۶ این ترتیب را دارد: ۱ Approved test Manifest، ۲ Item Registry، ۳ MAP.md، ۴ Item docs، ۵ Item data، ۶ evidence، ۷ checkpoint.
ناهماهنگی: (الف) در فایل جدید، docs/memory/registry.md (تصمیم‌های تأییدشده Owner) رتبه ۱ است و دستور Owner رتبه ۲؛ (ب) بخش ۶ واژه «Item Registry» را دارد که به Item_Registry.md قدیمی اشاره دارد، نه registry.md جدید؛ (ج) بخش ۶ Manifest را بالاتر از همه می‌گذارد، ولی Manifest هنوز ساخته نشده و منبع تصمیم نیست. تغییر ندادم.

## ۶) تخمین توکن شروع session
مجموع ۹۳ خط / ۵۷۰۹ کاراکتر → حدود ۱۴۰۰ تا ۱۶۰۰ توکن.