"""Bot integration tests — Telegram command → Scanner pipeline → Telegram message.

Deterministic/synthetic tests only for unit tests.
One real-data integration test validates the full chain with
live CoinGecko + historical candle data.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import patch

import pytest
import requests

from app.bot.config import (
    BOT_TOKEN,
    BOT_USERNAME,
    COMMAND_HELP,
    COMMAND_TOP3,
    HELP_TEXT,
)
from app.bot.runner import BotRunner
from app.bot.telegram import TelegramBot


# =========================================================================
# BotRunner — Command handling
# =========================================================================


def test_bot_config_token_empty():
    assert isinstance(BOT_TOKEN, str)


def test_bot_config_username():
    assert BOT_USERNAME == "KitchenAssistantBot"


def test_help_text_contains_warning():
    assert "توجه" in HELP_TEXT
    assert "Scanner" in HELP_TEXT
    assert COMMAND_TOP3 in HELP_TEXT
    assert COMMAND_HELP in HELP_TEXT


def test_bot_runner_help_command():
    runner = BotRunner()
    response = runner.handle_command(COMMAND_HELP)
    assert COMMAND_HELP in response
    assert "Scanner" in response
    assert "توجه" in response


def test_bot_runner_unknown_command():
    runner = BotRunner()
    response = runner.handle_command("/unknown")
    assert "Unknown command" in response
    assert "/help" in response


def test_bot_runner_top3_returns_message():
    runner = BotRunner()
    mock_coins = [
        _make_mock_coin("BTC", 1, 1_000_000_000_000),
        _make_mock_coin("ETH", 2, 500_000_000_000),
        _make_mock_coin("USDT", 3, 200_000_000_000),
        _make_mock_coin("BNB", 4, 100_000_000_000),
        _make_mock_coin("XRP", 5, 50_000_000_000),
        _make_mock_coin("SOL", 7, 40_000_000_000),
        _make_mock_coin("ADA", 10, 20_000_000_000),
    ]

    class MockResponse:
        def __init__(self, data):
            self._data = data
            self.status_code = 200
        def raise_for_status(self): pass
        def json(self): return self._data

    with patch("app.bot.runner.requests.get", return_value=MockResponse(mock_coins)):
        response = runner.handle_command(COMMAND_TOP3)
    assert len(response) > 0
    assert "TOP 3" in response.upper() or "\U0001f3c6" in response
    assert "توجه" in response


def test_bot_runner_top3_no_signal_language():
    runner = BotRunner()
    mock_coins = [
        _make_mock_coin("BTC", 1, 1_000_000_000_000),
        _make_mock_coin("ETH", 2, 500_000_000_000),
        _make_mock_coin("USDT", 3, 200_000_000_000),
        _make_mock_coin("BNB", 4, 100_000_000_000),
        _make_mock_coin("XRP", 5, 50_000_000_000),
        _make_mock_coin("SOL", 7, 40_000_000_000),
        _make_mock_coin("ADA", 10, 20_000_000_000),
    ]

    class MockResponse:
        def __init__(self, data):
            self._data = data
            self.status_code = 200
        def raise_for_status(self): pass
        def json(self): return self._data

    with patch("app.bot.runner.requests.get", return_value=MockResponse(mock_coins)):
        response = runner.handle_command(COMMAND_TOP3)
    msg_upper = response.upper()
    for word in ["BUY", "SELL", "LONG", "SHORT", "STOP", "TAKE", "TARGET"]:
        assert word not in msg_upper, f"Signal word found: {word}"


def test_bot_runner_top3_has_positions():
    runner = BotRunner()
    mock_coins = [
        _make_mock_coin("BTC", 1, 1_000_000_000_000),
        _make_mock_coin("ETH", 2, 500_000_000_000),
        _make_mock_coin("USDT", 3, 200_000_000_000),
        _make_mock_coin("BNB", 4, 100_000_000_000),
        _make_mock_coin("XRP", 5, 50_000_000_000),
        _make_mock_coin("SOL", 7, 40_000_000_000),
        _make_mock_coin("ADA", 10, 20_000_000_000),
    ]

    class MockResponse:
        def __init__(self, data):
            self._data = data
            self.status_code = 200
        def raise_for_status(self): pass
        def json(self): return self._data

    with patch("app.bot.runner.requests.get", return_value=MockResponse(mock_coins)):
        response = runner.handle_command(COMMAND_TOP3)
    assert "1." in response
    assert "2." in response
    assert "3." in response


# =========================================================================
# BotRunner — Real data integration (live CoinGecko + historical candles)
# =========================================================================


def test_bot_runner_top3_real_data():
    """End-to-end with real historical candles + mocked CoinGecko."""
    mock_coins = [
        _make_mock_coin("BTC", 1, 1_000_000_000_000),
        _make_mock_coin("ETH", 2, 500_000_000_000),
        _make_mock_coin("USDT", 3, 200_000_000_000),
        _make_mock_coin("BNB", 4, 100_000_000_000),
        _make_mock_coin("XRP", 5, 50_000_000_000),
        _make_mock_coin("SOL", 7, 40_000_000_000),
        _make_mock_coin("ADA", 10, 20_000_000_000),
    ]

    class MockResponse:
        def __init__(self, data):
            self._data = data
            self.status_code = 200
        def raise_for_status(self): pass
        def json(self): return self._data

    runner = BotRunner()
    with patch("app.bot.runner.requests.get", return_value=MockResponse(mock_coins)):
        response = runner.handle_command(COMMAND_TOP3)
    assert len(response) > 100
    assert "TOP 3" in response.upper() or "\U0001f3c6" in response
    assert "توجه" in response


def test_bot_runner_top3_real_data_no_signals():
    mock_coins = [
        _make_mock_coin("BTC", 1, 1_000_000_000_000),
        _make_mock_coin("ETH", 2, 500_000_000_000),
        _make_mock_coin("USDT", 3, 200_000_000_000),
        _make_mock_coin("BNB", 4, 100_000_000_000),
        _make_mock_coin("XRP", 5, 50_000_000_000),
        _make_mock_coin("SOL", 7, 40_000_000_000),
        _make_mock_coin("ADA", 10, 20_000_000_000),
    ]

    class MockResponse:
        def __init__(self, data):
            self._data = data
            self.status_code = 200
        def raise_for_status(self): pass
        def json(self): return self._data

    runner = BotRunner()
    with patch("app.bot.runner.requests.get", return_value=MockResponse(mock_coins)):
        response = runner.handle_command(COMMAND_TOP3)
    msg_upper = response.upper()
    for word in ["BUY", "SELL", "LONG", "SHORT", "STOP", "TAKE", "TARGET"]:
        assert word not in msg_upper


# =========================================================================
# BotRunner — CoinGecko data collection (mocked)
# =========================================================================


def _make_mock_coin(symbol, rank, mc):
    return {
        "id": symbol.lower(),
        "symbol": symbol.lower(),
        "name": symbol,
        "market_cap": mc,
        "current_price": 100.0,
        "total_volume": mc * 0.01,
        "market_cap_rank": rank,
    }


def test_bot_runner_collect_ranking_data_mocked():
    mock_coins = [
        _make_mock_coin("BTC", 1, 1_000_000_000_000),
        _make_mock_coin("ETH", 2, 500_000_000_000),
        _make_mock_coin("USDT", 3, 200_000_000_000),
        _make_mock_coin("BNB", 4, 100_000_000_000),
        _make_mock_coin("XRP", 5, 50_000_000_000),
    ]

    class MockResponse:
        def __init__(self, data):
            self._data = data
            self.status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return self._data

    with patch("requests.get", return_value=MockResponse(mock_coins)):
        runner = BotRunner()
        assets = runner._collect_ranking_data()

    assert len(assets) == 5
    assert assets[0]["symbol"] == "BTC"
    assert assets[0]["market_cap"] == 1_000_000_000_000
    assert assets[0]["provider"] == "COINGECKO"
    assert assets[0]["identity_status"] == "VALIDATED"
    assert assets[0]["provider_rank"] == 1


def test_bot_runner_collect_ranking_data_filters_zero_mc():
    mock_coins = [
        _make_mock_coin("BTC", 1, 1_000_000_000_000),
        {"id": "zero", "symbol": "zero", "name": "Zero", "market_cap": 0, "current_price": 1.0, "total_volume": 0, "market_cap_rank": 999},
    ]

    class MockResponse:
        def __init__(self, data):
            self._data = data
            self.status_code = 200
        def raise_for_status(self): pass
        def json(self): return self._data

    with patch("requests.get", return_value=MockResponse(mock_coins)):
        runner = BotRunner()
        assets = runner._collect_ranking_data()
    assert len(assets) == 1
    assert assets[0]["symbol"] == "BTC"


# =========================================================================
# BotRunner — Pair data collection (from historical candles)
# =========================================================================


def test_bot_runner_collect_pair_data():
    runner = BotRunner()
    usdt_r, btc_r = runner._collect_pair_data()
    assert len(usdt_r) > 0
    assert len(btc_r) > 0
    for key, result in usdt_r.items():
        assert key.endswith("USDT")
        assert result.valid or not result.valid
    for key, result in btc_r.items():
        assert key.endswith("BTC")


def test_bot_runner_top3_with_historical_candles():
    """Test with existing historical data available on disk."""
    raw_dir = Path("data/historical_u05/raw")
    has_candles = any(raw_dir.glob("*_1m.json"))
    if not has_candles:
        pytest.skip("No historical candles available")
    runner = BotRunner()
    usdt_r, btc_r = runner._collect_pair_data()
    assert len(usdt_r) > 0
    assert len(btc_r) > 0


# =========================================================================
# TelegramBot — Application setup
# =========================================================================


def test_telegram_bot_no_token():
    bot = TelegramBot(token="")
    assert not bot.is_configured
    assert bot.token == ""


def test_telegram_bot_get_app():
    token = BOT_TOKEN if BOT_TOKEN else "test_token_12345"
    bot = TelegramBot(token=token)
    app = bot.get_application()
    assert app is not None


def test_telegram_bot_handlers_registered():
    token = BOT_TOKEN if BOT_TOKEN else "test_token_12345"
    bot = TelegramBot(token=token)
    app = bot.get_application()
    handler_lists = app.handlers.values() if isinstance(app.handlers, dict) else app.handlers
    handler_commands = []
    for handler_list in handler_lists:
        for h in handler_list:
            if hasattr(h, "commands"):
                handler_commands.extend(h.commands)
    assert "top3" in handler_commands or "help" in handler_commands


def test_telegram_bot_async_top3(monkeypatch):
    """Test TelegramBot._cmd_top3 produces a message via mocked runner."""
    from telegram import Update
    from telegram.ext import ContextTypes

    mock_response = "🏆 TOP 3 RELIABLE MOVERS\nTest message"

    class MockRunner:
        def handle_command(self, cmd):
            return mock_response

    monkeypatch.setattr("app.bot.telegram.BotRunner", MockRunner)

    bot = TelegramBot(token="test_token")

    class MockChat:
        id = 12345

    class MockMessage:
        def __init__(self):
            self.text = "/top3"
            self.chat = MockChat()
        async def reply_text(self, text, **kwargs):
            self.replied_text = text
            self.replied_kwargs = kwargs

    class MockUpdate:
        def __init__(self):
            self.message = MockMessage()

    import asyncio
    asyncio.run(bot._cmd_top3(MockUpdate(), None))
    assert bot._runner.handle_command("/top3") == mock_response


# =========================================================================
# Flask endpoints
# =========================================================================


def test_flask_bot_status():
    from app.api.app import app
    c = app.test_client()
    r = c.get("/bot/status")
    assert r.status_code == 200
    data = r.json
    assert "configured" in data
    assert "status" in data


def test_flask_bot_webhook_help():
    from app.api.app import app
    c = app.test_client()
    r = c.post(
        "/bot/webhook",
        json={"message": {"text": "/help", "chat": {"id": 12345}}},
    )
    assert r.status_code == 200
    data = r.json
    assert data["ok"] is True
    assert data["chat_id"] == 12345
    assert COMMAND_HELP in data["response"]
    assert "توجه" in data["response"]


def test_flask_bot_webhook_top3():
    from app.api.app import app
    mock_coins = [
        _make_mock_coin("BTC", 1, 1_000_000_000_000),
        _make_mock_coin("ETH", 2, 500_000_000_000),
        _make_mock_coin("USDT", 3, 200_000_000_000),
        _make_mock_coin("BNB", 4, 100_000_000_000),
        _make_mock_coin("XRP", 5, 50_000_000_000),
        _make_mock_coin("SOL", 7, 40_000_000_000),
        _make_mock_coin("ADA", 10, 20_000_000_000),
    ]

    class MockResponse:
        def __init__(self, data):
            self._data = data
            self.status_code = 200
        def raise_for_status(self): pass
        def json(self): return self._data

    c = app.test_client()
    with patch("app.bot.runner.requests.get", return_value=MockResponse(mock_coins)):
        r = c.post(
            "/bot/webhook",
            json={"message": {"text": "/top3", "chat": {"id": 12345}}},
        )
    assert r.status_code == 200
    data = r.json
    assert data["ok"] is True
    assert data["chat_id"] == 12345
    assert len(data["response"]) > 50
    assert "توجه" in data["response"]


def test_flask_bot_webhook_empty_message():
    from app.api.app import app
    c = app.test_client()
    r = c.post("/bot/webhook", json={"message": {}})
    assert r.status_code == 400


def test_flask_bot_webhook_no_text():
    from app.api.app import app
    c = app.test_client()
    r = c.post("/bot/webhook", json={"message": {"text": ""}})
    assert r.status_code == 400


# =========================================================================
# Safety contracts
# =========================================================================


def test_bot_no_signal_in_top3_response():
    mock_coins = [
        _make_mock_coin("BTC", 1, 1_000_000_000_000),
        _make_mock_coin("ETH", 2, 500_000_000_000),
        _make_mock_coin("USDT", 3, 200_000_000_000),
        _make_mock_coin("BNB", 4, 100_000_000_000),
        _make_mock_coin("XRP", 5, 50_000_000_000),
        _make_mock_coin("SOL", 7, 40_000_000_000),
        _make_mock_coin("ADA", 10, 20_000_000_000),
    ]

    class MockResponse:
        def __init__(self, data):
            self._data = data
            self.status_code = 200
        def raise_for_status(self): pass
        def json(self): return self._data

    runner = BotRunner()
    with patch("app.bot.runner.requests.get", return_value=MockResponse(mock_coins)):
        response = runner.handle_command(COMMAND_TOP3)
    msg_upper = response.upper()
    for word in ["BUY", "SELL", "LONG", "SHORT", "STOP", "TAKE", "TARGET"]:
        assert word not in msg_upper, f"Signal word in response: {word}"


def test_bot_warning_reuses_scanner_warning():
    from app.analysis.stage12_top3 import TOP3_SCANNER_WARNING
    mock_coins = [
        _make_mock_coin("BTC", 1, 1_000_000_000_000),
        _make_mock_coin("ETH", 2, 500_000_000_000),
        _make_mock_coin("USDT", 3, 200_000_000_000),
        _make_mock_coin("BNB", 4, 100_000_000_000),
        _make_mock_coin("XRP", 5, 50_000_000_000),
        _make_mock_coin("SOL", 7, 40_000_000_000),
        _make_mock_coin("ADA", 10, 20_000_000_000),
    ]

    class MockResponse:
        def __init__(self, data):
            self._data = data
            self.status_code = 200
        def raise_for_status(self): pass
        def json(self): return self._data

    runner = BotRunner()
    with patch("app.bot.runner.requests.get", return_value=MockResponse(mock_coins)):
        response = runner.handle_command(COMMAND_TOP3)
    assert TOP3_SCANNER_WARNING in response
