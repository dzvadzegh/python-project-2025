import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from aiogram import Bot, Dispatcher
from aiogram.types import User, Chat, Message, Update

from bot.commands.info import bot_info, info_router


@pytest.mark.asyncio
async def test_info_success():
    """Тест успешного выполнения команды /info"""
    message = MagicMock()
    message.message_id = 1
    message.date = datetime.now(timezone.utc)
    message.text = "/info"

    message.from_user = MagicMock()
    message.from_user.id = 123
    message.from_user.username = "test_user"
    message.from_user.first_name = "Test"
    message.from_user.is_bot = False

    message.chat = MagicMock()
    message.chat.id = 456
    message.chat.type = "private"

    message.answer = AsyncMock()

    message.bot = {}

    mock_db = MagicMock()

    get_user_mock = AsyncMock()
    get_user_mock.return_value = {
        "user_id": 123,
        "username": "test_user",
        "settings": {
            "notification_time": "09:00",
            "reminders_per_day": 3,
            "timezone": "Europe/Moscow",
            "language": "русский"
        }
    }

    mock_db.get_user = get_user_mock

    message.bot = {"db":mock_db}

    await bot_info(message)

    get_user_mock.assert_called_once_with(123)
    message.answer.assert_called_once()

    call_args = message.answer.call_args
    if call_args.args:
        answer_text = call_args.args[0]
    else:
        answer_text = call_args.kwargs.get('text', '')

    assert "⚙️ *Информация о настройках*" in answer_text
    assert "Время уведомлений: 09:00" in answer_text
    assert "Уведомлений в день: 3" in answer_text
    assert "Временная зона: Europe/Moscow" in answer_text
    assert "Язык: русский" in answer_text
    assert "Посмотреть статистику: /stats" in answer_text

    call_kwargs = message.answer.call_args[1]
    assert call_kwargs.get("parse_mode") == "Markdown"


@pytest.mark.asyncio
async def test_info_partial_settings():
    """Тест с неполными настройками пользователя"""
    message = MagicMock()
    message.message_id = 1
    message.date = datetime.now(timezone.utc)
    message.text = "/info"

    message.from_user = MagicMock()
    message.from_user.id = 123
    message.from_user.username = "test_user"
    message.from_user.first_name = "Test"
    message.from_user.is_bot = False

    message.chat = MagicMock()
    message.chat.id = 456
    message.chat.type = "private"

    message.answer = AsyncMock()

    message.bot = {}

    mock_db = MagicMock()

    get_user_mock = AsyncMock()
    get_user_mock.return_value = {
        "user_id": 123,
        "username": "test_user",
        "settings": {
            "notification_time": "09:00",
        }
    }

    mock_db.get_user = get_user_mock

    message.bot = {"db":mock_db}

    await bot_info(message)

    get_user_mock.assert_called_once_with(123)
    message.answer.assert_called_once()

    call_args = message.answer.call_args
    if call_args.args:
        answer_text = call_args.args[0]
    else:
        answer_text = call_args.kwargs.get('text', '')

    assert "⚙️ *Информация о настройках*" in answer_text
    assert "Время уведомлений: 09:00" in answer_text
    assert "Уведомлений в день: 1" in answer_text
    assert "Временная зона: UTC" in answer_text
    assert "Язык: рус" in answer_text
    assert "Посмотреть статистику: /stats" in answer_text

    call_kwargs = message.answer.call_args[1]
    assert call_kwargs.get("parse_mode") == "Markdown"


@pytest.mark.parametrize("time_input,expected", [
    ("09:00", "09:00"),
    ("9:00", "9:00"),
    ("23:59", "23:59"),
    ("00:00", "00:00"),
])


@pytest.mark.asyncio
async def test_info_time_formats(time_input, expected):
    """Тест с различными форматами времени уведомлений"""
    message = MagicMock()
    message.from_user = MagicMock(id=123)
    message.answer = AsyncMock()

    mock_db = AsyncMock()
    mock_db.get_user = AsyncMock(return_value={
        "user_id": 123,
        "settings": {"notification_time": time_input}
    })

    message.bot = {"db": mock_db}

    await bot_info(message)

    call_args = message.answer.call_args
    answer_text = call_args.args[0] if call_args.args else call_args.kwargs.get('text', '')

    assert f"Время уведомлений: {expected}" in answer_text


@pytest.mark.asyncio
async def test_info_database_error():
    """Тест обработки ошибок базы данных"""
    message = MagicMock()
    message.from_user = MagicMock(id=123)
    message.answer = AsyncMock()
    message.reply = AsyncMock()

    mock_db = AsyncMock()
    mock_db.get_user = AsyncMock(side_effect=Exception("Database connection failed"))

    message.bot = {"db": mock_db}

    await bot_info(message)

    mock_db.get_user.assert_called_once_with(123)
    message.answer.assert_called_once()

    call_args = message.answer.call_args
    if call_args.args:
        answer_text = call_args.args[0]
    else:
        answer_text = call_args.kwargs.get('text', '')

    assert "Ошибка подключения к базе данных" in answer_text


@pytest.mark.asyncio
async def test_info_user_not_found():
    """Тест отсутствия пользователя в БД"""
    message = MagicMock()
    message.from_user = MagicMock(id=999)
    message.answer = AsyncMock()

    mock_db = AsyncMock()
    mock_db.get_user = AsyncMock(return_value=None)

    message.bot = {"db": mock_db}

    await bot_info(message)

    message.answer.assert_called_once()
    answer_text = message.answer.call_args.kwargs.get('text', '')
    assert "❌ Нет информации о пользователе ❌" in answer_text
