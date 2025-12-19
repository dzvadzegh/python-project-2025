from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State

from bot.services.parser import parse_add_command, ParseError

add_router = Router()


class AddWordStates(StatesGroup):
    waiting_for_word_pair = State()


@add_router.message(Command("add"))
async def bot_add(message: Message):
    db = message.bot.db
    user_id = message.from_user.id

    try:
        word, translation = parse_add_command(message.text)
    except ParseError as e:
        await message.answer(str(e), parse_mode="Markdown")
        return

    await db.add_word(word, translation, user_id)

    await db.log_activity(user_id, f"add_word:{word}")
    success_message = (
        f"✅ *Слово успешно добавлено!*\n\n"
        f"📖 *Слово:* {word}\n"
        f"🌐 *Перевод:* {translation}\n"
        f"Добавить еще слово: /add\n"
        f"Посмотреть статистику: /stats"
    )
    await message.answer(success_message, parse_mode="Markdown")
