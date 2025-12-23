import pytest
from unittest.mock import AsyncMock, MagicMock

from bot.services.parser import ParseError, parse_settings_command
from bot.commands.settings import bot_settings


@pytest.mark.asyncio
async def test_settings_show_current():
    """Тест успешного отображения текущих настроек"""
    message = MagicMock()
    message.from_user = MagicMock(id=123)
    message.text = "/settings"
    message.answer = AsyncMock()

    mock_user = MagicMock()
    mock_user.settings = {"reminders_per_day": 3}

    mock_db = AsyncMock()
    mock_db.get_user = AsyncMock(return_value=mock_user)

    mock_bot = MagicMock()
    mock_bot.db = mock_db
    message.bot = mock_bot

    await bot_settings(message)

    mock_db.get_user.assert_called_once_with(123)
    message.answer.assert_called_once()

    call_args = message.answer.call_args
    answer_text = call_args.kwargs.get('text', call_args.args[0] if call_args.args else "")

    assert "⚙️ *Настройки*" in answer_text
    assert "Напоминаний в день: 3" in answer_text
    assert "Пример ввода: /settings 1" in answer_text
    assert call_args.kwargs.get("parse_mode") == "Markdown"


@pytest.mark.asyncio
async def test_settings_update_value():
    """Тест обновления значения настроек"""
    message = MagicMock()
    message.from_user = MagicMock(id=123)
    message.text = "/settings 5"
    message.answer = AsyncMock()

    mock_user = MagicMock()
    mock_user.settings = {"reminders_per_day": 3}

    mock_db = AsyncMock()
    mock_db.get_user = AsyncMock(return_value=mock_user)
    mock_db.update_user_setting = AsyncMock()

    mock_bot = MagicMock()
    mock_bot.db = mock_db
    message.bot = mock_bot

    await bot_settings(message)

    mock_db.get_user.assert_called_once_with(123)
    mock_db.update_user_setting.assert_called_once_with(123, "reminders_per_day", 5)
    message.answer.assert_called_once()

    call_args = message.answer.call_args
    answer_text = call_args.kwargs.get('text', call_args.args[0] if call_args.args else "")

    assert "Теперь напоминаний в день: 5" in answer_text
    assert call_args.kwargs.get("parse_mode") == "Markdown"


@pytest.mark.asyncio
async def test_settings_not_digit_parse_error():
    """Тест ошибки парсинга команды, когда вводится не число"""
    message = MagicMock()
    message.from_user = MagicMock(id=123)
    message.text = "/settings invalid"
    message.answer = AsyncMock()

    mock_db = AsyncMock()
    mock_bot = MagicMock()
    mock_bot.db = mock_db
    message.bot = mock_bot

    await bot_settings(message)

    message.answer.assert_called_once()
    call_args = message.answer.call_args
    answer_text = call_args.kwargs.get('text', call_args.args[0] if call_args.args else "")

    assert "Нужно указать число" in answer_text


@pytest.mark.asyncio
async def test_settings_invalid_digit_parse_error():
    """Тест ошибки парсинга команды, когда вводится неправильное число"""
    message = MagicMock()
    message.from_user = MagicMock(id=123)
    message.text = "/settings -3"
    message.answer = AsyncMock()

    mock_db = AsyncMock()
    mock_bot = MagicMock()
    mock_bot.db = mock_db
    message.bot = mock_bot

    await bot_settings(message)

    message.answer.assert_called_once()
    call_args = message.answer.call_args
    answer_text = call_args.kwargs.get('text', call_args.args[0] if call_args.args else "")

    assert "Число должно быть от 1 до 23" in answer_text


@pytest.mark.asyncio
async def test_settings_parse_error():
    """Тест ошибки парсинга команды, когда вводится больше одного числа"""
    message = MagicMock()
    message.from_user = MagicMock(id=123)
    message.text = "/settings 2 2"
    message.answer = AsyncMock()

    mock_db = AsyncMock()
    mock_bot = MagicMock()
    mock_bot.db = mock_db
    message.bot = mock_bot

    await bot_settings(message)

    message.answer.assert_called_once()
    call_args = message.answer.call_args
    answer_text = call_args.kwargs.get('text', call_args.args[0] if call_args.args else "")

    assert "Неверный формат. Используйте: /settings 3" in answer_text


@pytest.mark.asyncio
async def test_settings_user_not_found():
    """Тест, когда пользователь не найден"""
    message = MagicMock()
    message.from_user = MagicMock(id=123)
    message.text = "/settings"
    message.answer = AsyncMock()

    mock_db = AsyncMock()
    mock_db.get_user = AsyncMock(return_value=None)

    mock_bot = MagicMock()
    mock_bot.db = mock_db
    message.bot = mock_bot

    await bot_settings(message)

    mock_db.get_user.assert_called_once_with(123)
    message.answer.assert_called_once()

    call_args = message.answer.call_args
    answer_text = call_args.kwargs.get('text', call_args.args[0] if call_args.args else "")

    assert "Вы ещё не зарегистрированы" in answer_text
    assert "Нажмите /start, чтобы начать пользоваться ботом." in answer_text


@pytest.mark.asyncio
async def test_settings_default_value():
    """Тест отображения настроек, когда стоит значение по умолчанию"""
    message = MagicMock()
    message.from_user = MagicMock(id=123)
    message.text = "/settings"
    message.answer = AsyncMock()

    mock_user = MagicMock()
    mock_user.settings = {}

    mock_db = AsyncMock()
    mock_db.get_user = AsyncMock(return_value=mock_user)

    mock_bot = MagicMock()
    mock_bot.db = mock_db
    message.bot = mock_bot

    await bot_settings(message)

    message.answer.assert_called_once()

    call_args = message.answer.call_args
    answer_text = call_args.kwargs.get('text', call_args.args[0] if call_args.args else "")

    assert "Напоминаний в день: 1" in answer_text


@pytest.mark.asyncio
async def test_settings_update_from_default():
    """Тест обновления значения с дефолтного"""
    message = MagicMock()
    message.from_user = MagicMock(id=123)
    message.text = "/settings 2"
    message.answer = AsyncMock()

    mock_user = MagicMock()
    mock_user.settings = {}

    mock_db = AsyncMock()
    mock_db.get_user = AsyncMock(return_value=mock_user)
    mock_db.update_user_setting = AsyncMock()

    mock_bot = MagicMock()
    mock_bot.db = mock_db
    message.bot = mock_bot

    await bot_settings(message)

    mock_db.update_user_setting.assert_called_once_with(123, "reminders_per_day", 2)
    message.answer.assert_called_once()

    call_args = message.answer.call_args
    answer_text = call_args.kwargs.get('text', call_args.args[0] if call_args.args else "")

    assert "Теперь напоминаний в день: 2" in answer_text


@pytest.mark.asyncio
async def test_settings_database_error():
    """Тест обработки ошибок базы данных"""
    message = MagicMock()
    message.from_user = MagicMock(id=123)
    message.answer = AsyncMock()
    message.reply = AsyncMock()
    message.text = "/settings"

    mock_db = AsyncMock()
    mock_db.get_user = AsyncMock(side_effect=Exception("Database connection failed"))

    mock_bot = MagicMock()
    mock_bot.db = mock_db
    message.bot = mock_bot

    await bot_settings(message)

    message.answer.assert_called_once()

    call_args = message.answer.call_args
    if call_args.args:
        answer_text = call_args.args[0]
    else:
        answer_text = call_args.kwargs.get('text', '')

    assert "Ошибка подключения к базе данных" in answer_text
