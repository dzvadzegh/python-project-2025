from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime, timedelta

from models.word import Word

router = Router()


class AddWordStates(StatesGroup):
    waiting_for_word_pair = State()


@router.message(Command("add"))
async def bot_add(message: Message):
    db = message.bot["db"]
    user_id = message.from_user.id

    word_pair = message.text.strip()[4:].strip()
    if not word_pair:
        await message.answer(
            "📝 *Добавление нового слова*\n\n"
            "Введите пару слов в формате:\n"
            "`/add слово:перевод`\n\n",
            parse_mode="Markdown",
        )
        return
    if not ":" in word_pair:
        await message.answer(
            "❌ *Неверный формат ввода* ❌\n\n"
            "Введите пару слов в формате:\n"
            "`/add слово:перевод`\n\n",
            parse_mode="Markdown",
        )
        return
    two_words = word_pair.split(":")
    word = two_words[0].strip()
    translation = two_words[1].strip()
    if not word or not translation:
        await message.answer("Не введено слово или перевод", parse_mode="Markdown")
        return
    new_word = Word(
        word_id=0,
        user_id=user_id,
        text=word.lower(),
        translation=translation.lower(),
        next_repeat=datetime.utcnow() + timedelta(days=1),
        repeat_count=0,
        created_at=datetime.utcnow(),
        base_difficulty=0.5,
        personal_difficulty=0.5,
        difficulty=0.5,
        stability=1.0,
        ml_score=0.5,
    )

    # await save_word_to_db(db, new_word) НУЖЕН МЕТОД ДОБАВЛЕНИЯ В DATABASE

    await db.log_activity(user_id, f"add_word:{word}")
    success_message = (
        f"✅ *Слово успешно добавлено!*\n\n"
        f"📖 *Слово:* {word}\n"
        f"🌐 *Перевод:* {translation}\n"
        f"Добавить еще слово: /add\n"
        f"Посмотреть статистику: /stats"
    )
    await message.answer(success_message, parse_mode="Markdown")
