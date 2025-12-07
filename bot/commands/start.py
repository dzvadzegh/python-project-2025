from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from datetime import datetime

from models.user import User
from models.stats import Stats

router = Router()

@router.message(CommandStart())
async def bot_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    if not username:
        username = ""

    db = message.bot.db
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or ""

    try:
        user = await db.get_user(user_id)
        if user:
            welcome_text = (
                f"👋 *С возвращением!*\n\n"
                "🎯 *Доступные команды:*\n"
                "/add - добавить новое слово с переводом в словарь\n"
                "/stats - посмотреть статистику обучения\n"
                "/settings - изменить настройки отправки напоминаний\n"
                "/info - информация о настройках\n\n"
                "Продолжаем учить слова! 📚"
            )
        else:
            user = User(
                user_id=user_id,
                username=username,
                settings={
                    "reminders_per_day": 3,
                    "timezone": "UTC",
                    "language": "en"
                },
                progress={
                    "streak_days": 0,  # сколько дней подряд активен пользователь
                    "total_words": 0,  # всего выучено слов
                    "last_active": None  # последняя активность
                },
                words_added={},
                last_active=datetime.utcnow(),
                stats=Stats(user_id=user_id),
                ml_profile={
                    "learning_rate": 1.0,
                    "difficulty_preference": "medium"
                }
            )
            welcome_text=(
                f"🎉 *Добро пожаловать в бот-напоминалку для изучения слов!*\n\n"
                "🎯 *Доступные команды:*\n"
                "/add - добавить новое слово с переводом в словарь\n"
                "/stats - посмотреть статистику обучения\n"
                "/settings - изменить настройки отправки напоминаний\n"
                "/info - информация о настройках\n\n"
                "🚀 *Начните с добавления первого слова в словарь с помощью команды /add!*\n"
            )
    user.update_last_active()

    await message.answer(
        text=welcome_text,
        parse_mode="Markdown"
    )
