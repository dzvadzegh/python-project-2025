from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

info_router = Router()


@info_router.message(Command("info"))
async def bot_info(message: Message):
    try:
        db = message.bot["db"]
        user_id = message.from_user.id
        user_data = await db.get_user(user_id)
        if user_data is None:
            await message.answer("❌ Нет информации о пользователе ❌")
            return

        settings = user_data.get("settings", {}) if user_data else {}
        notification_time = settings.get("notification_time", "10:00")
        reminders_per_day = settings.get("reminders_per_day", 1)
        timezone = settings.get("timezone", "UTC")
        language = settings.get("language", "рус")

        info_message = (
            f"⚙️ *Информация о настройках*\n\n"
            f"Время уведомлений: {notification_time}\n"
            f"Уведомлений в день: {reminders_per_day}\n"
            f"Временная зона: {timezone}\n"
            f"Язык: {language}\n"
            f"Посмотреть статистику: /stats"
        )
        await message.answer(text=info_message, parse_mode="Markdown")

    except Exception:
        await message.answer("Ошибка подключения к базе данных")
