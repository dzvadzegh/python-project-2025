import os

os.environ['DB_PORT'] = '5432'
os.environ['DB_USER'] = 'test_user'
os.environ['DB_PASSWORD'] = 'test_password'
os.environ['DB_NAME'] = 'test_db'
os.environ['DB_HOST'] = 'localhost'

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, timezone

from bot.commands.stats import bot_stats


@pytest.mark.asyncio
async def test_stats_success():
    """Тест успешного выполнения команды /stats"""
    message = MagicMock()
    message.from_user = MagicMock(id=123)
    message.text = "/stats"
    message.answer = AsyncMock()

    mock_user = MagicMock()
    mock_user.user_id = 123

    mock_stats = MagicMock()
    now = datetime.now(timezone.utc)
    mock_stats.activity_log = [
        {"action": "add_word:hello", "timestamp": (now - timedelta(days=3)).isoformat()},
        {"action": "add_word:world", "timestamp": (now - timedelta(days=10)).isoformat()},
    ]

    mock_stats_data = MagicMock()
    mock_stats_data.learned_words = 15
    mock_stats_data.success_rate = 75.5

    mock_db = AsyncMock()
    mock_db.get_user_stats = AsyncMock(return_value=mock_stats_data)

    mock_bot = MagicMock()
    mock_bot.db = mock_db
    message.bot = mock_bot

    with patch('bot.commands.stats.AsyncSessionLocal') as mock_session_local:
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        mock_user_result = MagicMock()
        mock_user_result.fetchone.return_value = mock_user

        mock_stats_result = MagicMock()
        mock_stats_result.fetchone.return_value = mock_stats

        mock_session.execute.side_effect = [mock_user_result, mock_stats_result]

        await bot_stats(message)

    message.answer.assert_called_once()

    call_args = message.answer.call_args
    answer_text = call_args.kwargs.get('text', call_args.args[0] if call_args.args else "")

    assert "*Ваша статистика изучения слов*" in answer_text
    assert "Выучено слов: *15*" in answer_text
    assert "75.5% от всех" in answer_text
    assert "За последнюю неделю: *+1* слов" in answer_text
    assert "За последний месяц: *+2* слов" in answer_text
    assert call_args.kwargs.get("parse_mode") == "Markdown"


@pytest.mark.asyncio
async def test_stats_user_not_found():
    """Тест, когда пользователь не найден в БД"""
    message = MagicMock()
    message.from_user = MagicMock(id=999)
    message.text = "/stats"
    message.answer = AsyncMock()

    mock_bot = MagicMock()
    mock_bot.db = AsyncMock()
    message.bot = mock_bot

    with patch('bot.commands.stats.AsyncSessionLocal') as mock_session_local:
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_session.execute.return_value = mock_result

        await bot_stats(message)

    message.answer.assert_called_once()

    call_args = message.answer.call_args
    answer_text = call_args.kwargs.get('text', call_args.args[0] if call_args.args else "")

    assert "Похоже, вы ещё не зарегистрированы" in answer_text
    assert "Нажмите /start, чтобы начать пользоваться ботом." in answer_text


@pytest.mark.asyncio
async def test_stats_no_stats():
    """Тест, когда нет статистики для пользователя"""
    message = MagicMock()
    message.from_user = MagicMock(id=123)
    message.text = "/stats"
    message.answer = AsyncMock()

    mock_user = MagicMock()
    mock_user.user_id = 123

    mock_bot = MagicMock()
    mock_bot.db = AsyncMock()
    message.bot = mock_bot

    with patch('bot.commands.stats.AsyncSessionLocal') as mock_session_local:
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        mock_user_result = MagicMock()
        mock_user_result.fetchone.return_value = mock_user

        mock_stats_result = MagicMock()
        mock_stats_result.fetchone.return_value = None

        mock_session.execute.side_effect = [mock_user_result, mock_stats_result]

        await bot_stats(message)

    message.answer.assert_called_once()

    call_args = message.answer.call_args
    answer_text = call_args.kwargs.get('text', call_args.args[0] if call_args.args else "")

    assert "Статистика для пользователя ещё не собрана." in answer_text
