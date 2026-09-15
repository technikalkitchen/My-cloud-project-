from __future__ import annotations

import os

BOT_TOKEN = os.getenv("BOT_TOKEN", os.getenv("TELEGRAM_BOT_TOKEN", ""))
BOT_USERNAME = os.getenv("BOT_USERNAME", "KitchenAssistantBot")

COMMAND_TOP3 = "/top3"
COMMAND_HELP = "/help"

HELP_TEXT = (
    "KITCHEN ROBOT — Scanner Bot\n\n"
    "Commands:\n"
    "/top3 — Run Scanner: U06.5 → Top 10 → Strong Movers → Top 3\n"
    "/help — Show this help message\n\n"
    "⚠️ توجه: اطلاعات و انتخاب‌های ارائه‌شده توسط Scanner "
    "به‌هیچ‌وجه سیگنال ورود یا خروج از معامله نیستند."
)
