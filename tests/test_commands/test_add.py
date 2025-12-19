import pytest
from bot.commands.add import bot_add


@pytest.mark.asyncio
async def test_add_command_success(mock_message, mock_db):
    """Тест успешного добавления слова"""
    message = mock_message(text="/add apple:яблоко", user_id=123)
    message.bot["db"] = mock_db

    await bot_add(message)

    mock_db.add_word.assert_called_once()
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
async def test_add_command_missing_colon(mock_message, mock_db):
    """Тест добавления слова без двоеточия (неправильный формат)"""
    message = mock_message(text="/add apple яблоко", user_id=123)
    message.bot["db"] = mock_db

    await bot_add(message)

    message.answer.assert_called_once()
    answer_text = message.answer.call_args[0][0]

    assert "❌ *Неверный формат ввода*" in answer_text
    assert "Используйте формат" in answer_text

    mock_db.add_word.assert_not_called()
    mock_db.log_activity.assert_not_called()


@pytest.mark.asyncio
async def test_add_command_empty_word(mock_message, mock_db):
    """Тест добавления с пустым словом"""
    message = mock_message(text="/add :перевод", user_id=123)
    message.bot["db"] = mock_db

    await bot_add(message)

    message.answer.assert_called_once()
    answer_text = message.answer.call_args[0][0]

    assert "❌ *Ошибка*" in answer_text
    assert "не могут быть пустыми" in answer_text

    mock_db.add_word.assert_not_called()
    mock_db.log_activity.assert_not_called()


@pytest.mark.asyncio
async def test_add_command_only_word(mock_message, mock_db):
    """Тест добавления только слова без перевода"""
    message = mock_message(text="/add apple:", user_id=123)
    message.bot["db"] = mock_db

    await bot_add(message)

    message.answer.assert_called_once()
    answer_text = message.answer.call_args[0][0]

    assert "❌ *Ошибка*" in answer_text
    assert "не могут быть пустыми" in answer_text

    mock_db.add_word.assert_not_called()


@pytest.mark.asyncio
async def test_add_command_no_arguments(mock_message, mock_db):
    """Тест команды /add без аргументов"""
    message = mock_message(text="/add", user_id=123)
    message.bot["db"] = mock_db

    await bot_add(message)

    message.answer.assert_called_once()
    answer_text = message.answer.call_args[0][0]

    assert "📝 *Добавление нового слова*" in answer_text
    assert "Введите пару слов в формате" in answer_text
    assert "Пример" in answer_text

    mock_db.add_word.assert_not_called()
    mock_db.log_activity.assert_not_called()


@pytest.mark.asyncio
async def test_add_command_with_spaces(mock_message, mock_db):
    """Тест добавления словосочетаний с пробелами"""
    message = mock_message(text="/add hello world:привет мир", user_id=123)
    message.bot["db"] = mock_db

    await bot_add(message)

    mock_db.add_word.assert_called_once()
    call_args = mock_db.add_word.call_args

    assert call_args.kwargs['text'] == "hello world"
    assert call_args.kwargs['translation'] == "привет мир"
