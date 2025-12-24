from datetime import datetime, timedelta
from bot.models.stats import Stats
from ml.src.ml_inference import predict_interval_and_score


class Checker:
    def __init__(self, user, word, answer: str, db, stats: Stats | None = None):
        self.user = user
        self.word = word
        self.answer = answer.strip().lower()
        self.stats = stats
        self.db = db
        self.ml_result = {}

    def _rate_answer(self) -> tuple[int, bool]:
        """
        Вычисляем правильность ответа и рейтинг:
        4 = Easy (правильно), 1 = Again (неправильно)
        """
        is_correct = self.word.check_translation(self.answer)
        rating = 4 if is_correct else 1
        return rating, is_correct

    async def evaluate_with_ml(self, ml_model=None):
        """
        Основной метод: обновляет слово (difficulty, stability, next_repeat, ml_score)
        и сохраняет изменения в базе.
        """
        rating, is_correct = self._rate_answer()

        # Обновление параметров слова в памяти
        self.word.repeat_count += 1

        if is_correct:
            self.word.personal_difficulty = max(
                0.0,
                self.word.personal_difficulty * 0.95,
            )
        else:
            self.word.personal_difficulty = min(
                1.0,
                self.word.personal_difficulty * 1.10,
            )

        self.word.difficulty = (
            0.7 * self.word.base_difficulty + 0.3 * self.word.personal_difficulty
        )

        # ML-предсказание интервала и вероятности успеха
        features = {
            "base_difficulty": self.word.base_difficulty,
            "personal_difficulty": self.word.personal_difficulty,
            "difficulty": self.word.difficulty,
            "repeat_count": self.word.repeat_count,
            "stability": self.word.stability,
            "user_rating": rating,
        }
        interval_days, ml_score = predict_interval_and_score(features)

        self.word.ml_score = ml_score
        self.word.stability = max(1.0, float(interval_days))
        days = max(1, int(round(interval_days)))
        self.word.next_repeat = datetime.utcnow() + timedelta(days=days)

        # Обновление истории слова
        if hasattr(self.word, "record_history"):
            self.word.record_history(rating=rating, is_correct=is_correct)

        # Формирование результата для feedback
        self.ml_result = {
            "rating": rating,
            "correct": is_correct,
            "next_repeat_days": days,
            "ml_score": ml_score,
        }

        # Сохраняем изменения слова в базе (используем твой Database)
        await self.db.update_word_after_check(
            user_id=self.word.user_id,
            word_id=self.word.id,
            next_repeat=self.word.next_repeat,
            personal_difficulty=self.word.personal_difficulty,
            stability=self.word.stability,
            ml_score=self.word.ml_score,
            repeat_count=self.word.repeat_count,
        )

        # Можно добавить статистику
        if self.stats is not None:
            self.stats.record_answer(self.word.id, rating, is_correct)

    def feedback(self) -> dict:
        """
        Возвращает результат проверки для бота:
        correct: bool - правильно/неправильно
        next_repeat_days: int - через сколько дней повторять
        ml_score: float - вероятность успеха
        rating: int - рейтинг
        """
        if not self.ml_result:
            is_correct = self._rate_answer()[1]
            rating = 4 if is_correct else 1
            return {
                "correct": is_correct,
                "next_repeat_days": None,
                "ml_score": None,
                "rating": rating,
            }

        return {
            "correct": self.ml_result.get("correct"),
            "next_repeat_days": self.ml_result.get("next_repeat_days"),
            "ml_score": self.ml_result.get("ml_score"),
            "rating": self.ml_result.get("rating"),
        }
