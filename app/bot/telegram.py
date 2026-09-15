from __future__ import annotations

import asyncio
import os
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from app.bot.config import BOT_TOKEN, BOT_USERNAME, HELP_TEXT
from app.bot.runner import BotRunner


class TelegramBot:
    """Telegram bot integration for the Scanner pipeline.

    Uses python-telegram-bot v22.
    Telegram command → BotRunner → Telegram message.
    """

    def __init__(self, token: Optional[str] = None):
        self._token = token or BOT_TOKEN
        self._runner = BotRunner()
        self._app = None

    @property
    def token(self) -> str:
        return self._token

    @property
    def is_configured(self) -> bool:
        return bool(self._token)

    def get_application(self) -> Application:
        if self._app is None:
            self._app = Application.builder().token(self._token).build()
            self._app.add_handler(CommandHandler("top3", self._cmd_top3))
            self._app.add_handler(CommandHandler("help", self._cmd_help))
        return self._app

    async def _cmd_top3(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update or not update.message or not update.message.text:
            return
        response = self._runner.handle_command("/top3")
        await update.message.reply_text(response, parse_mode="HTML")

    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update or not update.message or not update.message.text:
            return
        await update.message.reply_text(HELP_TEXT, parse_mode="HTML")

    def run_polling(self) -> None:
        app = self.get_application()
        app.run_polling()

    async def run_once(self) -> None:
        app = self.get_application()
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        await asyncio.sleep(1)
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
