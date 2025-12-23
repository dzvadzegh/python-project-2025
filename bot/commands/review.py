from aiogram import Router, types
from bot.models.checker import Checker

review_router = Router()

user_pending_word: dict[int, dict] = {}


@review_router.message()
async def review_flow(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip().lower()
    db = message.bot.db

    if user_id not in user_pending_word:
        return

    state = user_pending_word[user_id]

    if state["stage"] == "answer":
        word = state["word"]

        checker = Checker(
            user=message.from_user,
            word=word,
            answer=text,
            db=db,
        )

        await checker.evaluate_with_ml()
        feedback = checker.feedback()

        user_pending_word[user_id] = {
            "stage": "confirm",
            "word": word,
            "feedback": feedback,
            "answer": text,
        }

        await message.answer(
            f"Ваш перевод: *{text}*\n"
            f"Правильный перевод: *{word.translation}*\n\n"
            "Вы правильно перевели слово? Напишите **да** или **нет**"
        )
        return
    if state["stage"] == "confirm":
        if text not in ("да", "нет", "yes", "no"):
            await message.answer("Пожалуйста, ответьте **да** или **нет**")
            return

        correct = text in ("да", "yes")
        word = state["word"]
        feedback = state["feedback"]

        rating = feedback.get("rating", 3)

        word.record_history(rating=rating, is_correct=correct)

        await db.update_word_next_repeat(
            user_id=user_id,
            word_id=word.id,
            next_repeat=word.next_repeat,
        )

        await db.log_activity(
            user_id,
            f"answered:{word.text}:{'correct' if correct else 'wrong'}",
        )

        await message.answer(f"✅ Ответ сохранён.\n")

        del user_pending_word[user_id]
