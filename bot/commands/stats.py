from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from bot.models.stats import Stats

stats_router = Router()


@stats_router.message(Command("stats"))
async def bot_stats(message: Message):
    """
    Команда /stats — выводит прогресс изучения слов для текущего пользователя.
    """
    db = message.bot["db"]
    tg_user_id = message.from_user.id

    user_row = await db.fetch_one(
        "SELECT id FROM user WHERE user_id = :tg_id",
        {"tg_id": tg_user_id},
    )
    if not user_row:
        await message.answer(
            "Похоже, вы ещё не зарегистрированы.\n"
            "Нажмите /start, чтобы начать пользоваться ботом."
        )
        return

    internal_user_id = user_row["id"]

    stats_model = Stats(user_id=internal_user_id, db=db)
    stats = await stats_model.load()

    text = (
        "*Ваша статистика изучения слов*\n\n"
        f"Всего слов в словаре: *{stats.total_words}*\n"
        f"Выучено слов: *{stats.learned_words}* "
        f"({stats.success_rate}% от всех)\n\n"
        f"За последнюю неделю: *+{stats.learned_week}* слов\n"
        f"За последний месяц: *+{stats.learned_month}* слов\n\n"
        f"Всего зафиксировано действий: *{stats.activity_records}*"
    )

    await message.answer(text, parse_mode="Markdown")
