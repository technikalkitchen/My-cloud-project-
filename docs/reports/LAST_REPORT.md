# گزارش بررسی قواعد و AGENTS.md

## بخش ۱: قواعد ناقص در نسخه کوتاه
فقط قواعدی که در بخش‌های ۱۰، ۱۳، ۱۴ بودند و به ارجاع یک‌خطی تبدیل شدند:
- خط ۳۶۹ (کامل): "It must contain:" — بخش ۱۰.۱ — در کوتاه حذف و ارجاع شد (عمدی)
- خط ۴۲۹ (کامل): "Never invent a completed step." — بخش ۱۰.۲ — حذف و ارجاع شد (عمدی)
- خط ۵۱۱ (کامل): "The required deliverables are:" — بخش ۱۴ — حذف و ارجاع شد (عمدی)
سایر قواعد MUST/NEVER حفظ شده‌اند (فشرده یا عیناً).

## بخش ۲: AGENTS.md
- فقط یک فایل: ./AGENTS.md (ریشه)، ۹ خط. فایل AGENTS.md در docs وجود ندارد.
- ۵ خط اول: عنوان + Main protocol + Persistent state + Action log + Canonical branch.
- قاعده مهم فقط اینجا: "Do not read other files until these three are loaded."
- تناقض/تکرار: ندارد (تنها فایل است).
- پیشنهاد: ریشه AGENTS.md را ۳ خط راهنما نگه دارید (مسیر پروتکل + شاخه)، بقیه در docs/Agents/AGENTS.md جمع شود. از ریشه نباید گم شود: مسیر 00_START_HERE.md، WORK_STATE.md، LEDGER.md و شاخه canonical v4.
