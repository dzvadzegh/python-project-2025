from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command("settings"))
async def bot_settings(message: Message):
    db = message.bot["db"]
    user_id = message.from_user.id

    parts = message.text.strip().split()

    user = await db.get_user(user_id)
    settings = user["settings"] or {}
    current = settings.get("reminders_per_day", 1)

    if len(parts) == 1:
        await message.answer(
            f"⚙️ *Настройки*\n\n"
            f"🔔 Напоминаний в день: {current}\n\n"
            f"Чтобы изменить, напишите:\n"
            f"`/settings 1` или `/settings 3`",
            parse_mode="Markdown",
        )
        return

    if len(parts) == 2:
        if not parts[1].isdigit():
            await message.answer("Нужно указать число")
            return

        count = int(parts[1])
        if count < 1 or count > 23:
            await message.answer("Число должно быть от 1 до 23")
            return

        await db.update_user_setting(
            user_id,
            "reminders_per_day",
            count,
        )

        await message.answer(f"Теперь напоминаний в день: {count}")
