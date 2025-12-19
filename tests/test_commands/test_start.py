import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from bot.commands.start import bot_start, start_router


@pytest.mark.asyncio
async def test_start_success_with_new_user():
    """Тест успешного выполнения команды /start для нового пользователя"""
    message = MagicMock()
    message.message_id = 1
    message.date = datetime.now(timezone.utc)
    message.text = "/start"

    message.from_user = MagicMock()
    message.from_user.id = 123
    message.from_user.username = "test_user"
    message.from_user.first_name = "Test"
    message.from_user.is_bot = False

    message.chat = MagicMock()
    message.chat.id = 456
    message.chat.type = "private"

    message.answer = AsyncMock()

    mock_db = AsyncMock()
    mock_db.get_user = AsyncMock(return_value=None)
    mock_db.add_user = AsyncMock()

    mock_bot = MagicMock()
    mock_bot.__getitem__ = MagicMock(return_value=mock_db)
    message.bot = mock_bot

    await bot_start(message)

    mock_db.get_user.assert_called_once_with(123)
    mock_db.add_user.assert_called_once_with(
        user_id=123,
        username="test_user"
    )

    message.answer.assert_called_once()

    call_args = message.answer.call_args
    if call_args.args:
        answer_text = call_args.args[0]
    else:
        answer_text = call_args.kwargs.get('text', '')

    assert "🎉 *Добро пожаловать в бот-напоминалку для изучения слов!" in answer_text
    assert "🎯 *Доступные команды:*" in answer_text
    assert "/add - добавить новое слово с переводом в словарь" in answer_text
    assert "/stats - посмотреть статистику обучения" in answer_text
    assert "/settings - изменить настройки отправки напоминаний" in answer_text
    assert "/info - информация о настройках" in answer_text
    assert "🚀 *Начните с добавления первого слова в словарь с помощью команды /add!*" in answer_text

    call_kwargs = message.answer.call_args[1]
    assert call_kwargs.get("parse_mode") == "Markdown"


@pytest.mark.asyncio
async def test_start_success_with_existing_user():
    """Тест успешного выполнения команды /start для существующего пользователя"""
    message = MagicMock()
    message.message_id = 1
    message.date = datetime.now(timezone.utc)
    message.text = "/start"

    message.from_user = MagicMock()
    message.from_user.id = 123
    message.from_user.username = "test_user"
    message.from_user.first_name = "Test"
    message.from_user.is_bot = False

    message.chat = MagicMock()
    message.chat.id = 456
    message.chat.type = "private"

    message.answer = AsyncMock()

    mock_db = AsyncMock()
    get_user_mock = AsyncMock()
    get_user_mock.return_value = {
        "user_id": 123,
        "username": "test_user",
        "settings": {
            "notification_time": "09:00",
        }
    }

    mock_db.get_user = get_user_mock
    mock_db.add_user = AsyncMock()

    mock_bot = MagicMock()
    mock_bot.__getitem__ = MagicMock(return_value=mock_db)
    message.bot = mock_bot

    await bot_start(message)

    mock_db.get_user.assert_called_once_with(123)
    mock_db.add_user.assert_not_called()
    message.answer.assert_called_once()

    call_args = message.answer.call_args
    if call_args.args:
        answer_text = call_args.args[0]
    else:
        answer_text = call_args.kwargs.get('text', '')

    assert "👋 *С возвращением!*" in answer_text
    assert "🎯 *Доступные команды:*" in answer_text
    assert "/add - добавить новое слово с переводом в словарь" in answer_text
    assert "/stats - посмотреть статистику обучения" in answer_text
    assert "/settings - изменить настройки отправки напоминаний" in answer_text
    assert "/info - информация о настройках" in answer_text
    assert "Продолжаем учить слова! 📚" in answer_text

    call_kwargs = message.answer.call_args[1]
    assert call_kwargs.get("parse_mode") == "Markdown"


@pytest.mark.asyncio
async def test_start_database_error():
    """Тест обработки ошибок базы данных"""
    message = MagicMock()
    message.from_user = MagicMock(id=123)
    message.answer = AsyncMock()
    message.reply = AsyncMock()

    mock_db = AsyncMock()
    mock_db.get_user = AsyncMock(side_effect=Exception("Database connection failed"))

    message.bot = {"db": mock_db}

    await bot_start(message)

    mock_db.get_user.assert_called_once_with(123)
    message.answer.assert_called_once()

    call_args = message.answer.call_args
    if call_args.args:
        answer_text = call_args.args[0]
    else:
        answer_text = call_args.kwargs.get('text', '')

    assert "Ошибка подключения к базе данных" in answer_text
