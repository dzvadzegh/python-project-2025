from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command("stats"))
async def bot_stats(message: Message):
    db = message.bot["db"]
    user_id = message.from_user.id

    user = await db.get_user(user_id)
    if not user:
        await message.answer(
            "Похоже, вы ещё не зарегистрированы.\n"
            "Нажмите /start, чтобы начать пользоваться ботом."
        )
        return

    stats = await db.get_user_stats(user_id)
    if not stats:
        await message.answer(
            "У вас пока нет статистики.\n" "Добавьте первое слово с помощью /add"
        )
        return

    activity_log = stats.activity_log or []

    total_actions = len(activity_log)
    added_words = sum(
        1 for a in activity_log if a.get("action", "").startswith("add_word")
    )

    success_rate = stats.success_rate or 0.0
    learned_words = stats.learned_words or 0

    last_activity = activity_log[-1]["timestamp"] if activity_log else "—"

    text = (
        "*Ваша статистика изучения слов*\n\n"
        f"Добавлено слов: *{added_words}*\n"
        f"Выучено слов: *{learned_words}*\n"
        f"Успешность: *{success_rate:.1f}%*\n"
        f"Всего действий: *{total_actions}*\n"
        f"Последняя активность: *{last_activity}*"
    )

    await message.answer(text, parse_mode="Markdown")
