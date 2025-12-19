from datetime import datetime, timedelta, timezone
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select

from bot.services.database import AsyncSessionLocal, users, stats
from bot.models.stats import Stats

stats_router = Router()


@stats_router.message(Command("stats"))
async def bot_stats(message: Message):
    """
    Команда /stats — выводит прогресс изучения слов для текущего пользователя.
    """
    db = message.bot.db
    tg_user_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        user_row = await session.execute(
            select(users).where(users.c.user_id == tg_user_id)
        )
        user_row = user_row.fetchone()

    if not user_row:
        await message.answer(
            "Похоже, вы ещё не зарегистрированы.\n"
            "Нажмите /start, чтобы начать пользоваться ботом."
        )
        return

    internal_user_id = user_row.user_id

    stats_model = Stats(user_id=internal_user_id)
    stats_data = await db.get_user_stats(internal_user_id)

    now = datetime.now(timezone.utc)
    one_week_ago = now - timedelta(days=7)
    one_month_ago = now - timedelta(days=30)

    stats_row = await session.execute(
        select(stats).where(stats.c.user_id == internal_user_id)
    )
    stats_row = stats_row.fetchone()

    if not stats_row:
        await message.answer("Статистика для пользователя ещё не собрана.")
        return
    activity_log = stats_row.activity_log or []
    learned_week = sum(
        1
        for act in activity_log
        if "add_word" in act.get("action", "")
        and datetime.fromisoformat(act["timestamp"]) >= one_week_ago
    )
    learned_month = sum(
        1
        for act in activity_log
        if "add_word" in act.get("action", "")
        and datetime.fromisoformat(act["timestamp"]) >= one_month_ago
    )

    text = (
        "*Ваша статистика изучения слов*\n\n"
        f"Выучено слов: *{stats_data.learned_words}* "
        f"({stats_data.success_rate}% от всех)\n\n"
        f"За последнюю неделю: *+{learned_week}* слов\n"
        f"За последний месяц: *+{learned_month}* слов\n\n"
    )

    await message.answer(text, parse_mode="Markdown")
