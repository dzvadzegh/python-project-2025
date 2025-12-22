import pytest
from unittest.mock import AsyncMock, MagicMock


from bot.commands.add import bot_add


@pytest.mark.asyncio
async def test_add_command_success():
    """Тест успешного добавления слова"""
    message = AsyncMock()
    message.message_id = 1
    message.text = "/add apple:яблоко"

    message.from_user = AsyncMock()
    message.from_user.id = 123
    message.from_user.username = "test_user"
    message.from_user.first_name = "Test"

    message.answer = AsyncMock()

    mock_db = AsyncMock()
    mock_db.get_user = AsyncMock()
    mock_db.add_user = AsyncMock()
    mock_db.add_word = AsyncMock()

    mock_bot = AsyncMock()
    mock_bot.db = mock_db
    message.bot = mock_bot

    await bot_add(message)

    mock_db.add_word.assert_called_once_with(text="apple", translation="яблоко", user_id=123)
    call_args = mock_db.add_word.call_args

    assert call_args.kwargs['text'] == "apple"
    assert call_args.kwargs['translation'] == "яблоко"
    assert call_args.kwargs['user_id'] == 123

    mock_db.log_activity.assert_called_once_with(123, "add_word:apple")
    message.answer.assert_called_once()
    answer_text = message.answer.call_args[0][0]

    assert "✅ *Слово успешно добавлено!*" in answer_text
    assert "📖 *Слово:* apple" in answer_text
    assert "🌐 *Перевод:* яблоко" in answer_text
    assert "/add" in answer_text
    assert "/stats" in answer_text


@pytest.mark.asyncio
async def test_add_database_error():
    """Тест обработки ошибок базы данных"""
    message = MagicMock()
    message.from_user = MagicMock(id=123)
    message.answer = AsyncMock()
    message.reply = AsyncMock()

    mock_db = AsyncMock()
    mock_db.get_user = AsyncMock(side_effect=Exception("Database connection failed"))

    message.bot = {"db": mock_db}

    await bot_add(message)

    message.answer.assert_called_once()

    call_args = message.answer.call_args
    if call_args.args:
        answer_text = call_args.args[0]
    else:
        answer_text = call_args.kwargs.get('text', '')

    assert "Ошибка подключения к базе данных" in answer_text


@pytest.mark.asyncio
async def test_add_command_missing_colon():
    """Тест добавления слова без двоеточия"""
    message = AsyncMock()
    message.message_id = 1
    message.text = "/add apple   яблоко"

    message.from_user = AsyncMock()
    message.from_user.id = 123
    message.from_user.username = "test_user"
    message.from_user.first_name = "Test"

    message.answer = AsyncMock()

    mock_db = AsyncMock()
    mock_db.get_user = AsyncMock()
    mock_db.add_user = AsyncMock()
    mock_db.add_word = AsyncMock()

    mock_bot = AsyncMock()
    mock_bot.db = mock_db
    message.bot = mock_bot

    await bot_add(message)

    call_args = message.answer.call_args
    if call_args.args:
        answer_text = call_args.args[0]
    else:
        answer_text = call_args.kwargs.get('text', '')

    assert "❌ Неверный формат.\n" "Используйте:\n" "`/add слово:перевод`" in answer_text

    call_kwargs = message.answer.call_args[1]
    assert call_kwargs.get("parse_mode") == "Markdown"

    mock_db.add_word.assert_not_called()


@pytest.mark.asyncio
async def test_add_command_empty_command():
    """Тест вызова команды без аргументов"""
    message = AsyncMock()
    message.message_id = 1
    message.text = "/add"

    message.from_user = AsyncMock()
    message.from_user.id = 123
    message.from_user.username = "test_user"
    message.from_user.first_name = "Test"

    message.answer = AsyncMock()

    mock_db = AsyncMock()
    mock_db.get_user = AsyncMock()
    mock_db.add_user = AsyncMock()
    mock_db.add_word = AsyncMock()

    mock_bot = AsyncMock()
    mock_bot.db = mock_db
    message.bot = mock_bot

    await bot_add(message)

    call_args = message.answer.call_args
    if call_args.args:
        answer_text = call_args.args[0]
    else:
        answer_text = call_args.kwargs.get('text', '')

    assert "📝 Введите слово в формате:\n" "`/add слово:перевод`" in answer_text

    call_kwargs = message.answer.call_args[1]
    assert call_kwargs.get("parse_mode") == "Markdown"

    mock_db.add_word.assert_not_called()


@pytest.mark.asyncio
async def test_add_command_empty_word():
    """Тест добавления слова без перевода"""
    message = AsyncMock()
    message.message_id = 1
    message.text = "/add apple:"

    message.from_user = AsyncMock()
    message.from_user.id = 123
    message.from_user.username = "test_user"
    message.from_user.first_name = "Test"

    message.answer = AsyncMock()

    mock_db = AsyncMock()
    mock_db.get_user = AsyncMock()
    mock_db.add_user = AsyncMock()
    mock_db.add_word = AsyncMock()

    mock_bot = AsyncMock()
    mock_bot.db = mock_db
    message.bot = mock_bot

    await bot_add(message)

    call_args = message.answer.call_args
    if call_args.args:
        answer_text = call_args.args[0]
    else:
        answer_text = call_args.kwargs.get('text', '')

    assert "❌ Слово и перевод не могут быть пустыми" in answer_text

    call_kwargs = message.answer.call_args[1]
    assert call_kwargs.get("parse_mode") == "Markdown"

    mock_db.add_word.assert_not_called()


@pytest.mark.asyncio
async def test_add_command_empty_translation():
    """Тест добавления перевода без слова"""
    message = AsyncMock()
    message.message_id = 1
    message.text = "/add :яблоко"

    message.from_user = AsyncMock()
    message.from_user.id = 123
    message.from_user.username = "test_user"
    message.from_user.first_name = "Test"

    message.answer = AsyncMock()

    mock_db = AsyncMock()
    mock_db.get_user = AsyncMock()
    mock_db.add_user = AsyncMock()
    mock_db.add_word = AsyncMock()

    mock_bot = AsyncMock()
    mock_bot.db = mock_db
    message.bot = mock_bot

    await bot_add(message)

    call_args = message.answer.call_args
    if call_args.args:
        answer_text = call_args.args[0]
    else:
        answer_text = call_args.kwargs.get('text', '')

    assert "❌ Слово и перевод не могут быть пустыми" in answer_text

    call_kwargs = message.answer.call_args[1]
    assert call_kwargs.get("parse_mode") == "Markdown"

    mock_db.add_word.assert_not_called()


@pytest.mark.asyncio
async def test_add_command_with_spaces():
    """Тест добавления словосочетаний с пробелами"""
    message = AsyncMock()
    message.message_id = 1
    message.text = "/add hello world :привет мир"

    message.from_user = AsyncMock()
    message.from_user.id = 123
    message.from_user.username = "test_user"
    message.from_user.first_name = "Test"

    message.answer = AsyncMock()

    mock_db = AsyncMock()
    mock_db.get_user = AsyncMock()
    mock_db.add_user = AsyncMock()
    mock_db.add_word = AsyncMock()

    mock_bot = AsyncMock()
    mock_bot.db = mock_db
    message.bot = mock_bot

    await bot_add(message)

    mock_db.add_word.assert_called_once_with(text="hello world", translation="привет мир", user_id=123)
    call_args = mock_db.add_word.call_args

    assert call_args.kwargs['text'] == "hello world"
    assert call_args.kwargs['translation'] == "привет мир"
    assert call_args.kwargs['user_id'] == 123

    mock_db.log_activity.assert_called_once_with(123, "add_word:hello world")
    message.answer.assert_called_once()
    answer_text = message.answer.call_args[0][0]

    assert "✅ *Слово успешно добавлено!*" in answer_text
    assert "📖 *Слово:* hello world" in answer_text
    assert "🌐 *Перевод:* привет мир" in answer_text
    assert "/add" in answer_text
    assert "/stats" in answer_text
