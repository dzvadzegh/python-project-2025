from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from bot.services.parser import parse_settings_command, ParseError

settings_router = Router()


@settings_router.message(Command("settings"))
async def bot_settings(message: Message):
    db = message.bot.db

    user_id = message.from_user.id

    try:
        new_value = parse_settings_command(message.text)
    except ParseError as e:
        await message.answer(str(e))
        return

    user = await db.get_user(user_id)
    settings = user.settings or {}
    current = settings.get("reminders_per_day", 1)

    if new_value is None:
        await message.answer(
            f"⚙️ *Настройки*\n\n"
            f"🔔 Напоминаний в день: {current}\n\n"
            f"Чтобы изменить, напишите:\n"
            f"`/settings 1` или `/settings 3`",
            parse_mode="Markdown",
        )
        return

    await db.update_user_setting(user_id, "reminders_per_day", new_value)

    await message.answer(
        f"✅ Теперь напоминаний в день: {new_value}",
        parse_mode="Markdown",
    )
