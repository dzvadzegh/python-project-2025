from datetime import datetime, timedelta
from difflib import SequenceMatcher
from stats import Stats
from ml.src.ml_inference import predict_interval_and_score


class Checker:
    def __init__(self, user, word, answer: str, stats: Stats | None = None):
        self.user = user
        self.word = word
        self.answer = answer.strip().lower()
        self.stats = stats
        self.ml_result = {}

    def check(self) -> bool:
        return self.word.check_translation(self.answer)

    def update_with_rating(self, rating: int) -> None:
        """
        rating: 1=Again, 2=Hard, 3=Good, 4=Easy
        """
        self.word.repeat_count += 1

        is_correct = rating >= 3

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
            0.7 * self.word.base_difficulty +
            0.3 * self.word.personal_difficulty
        )

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

        if hasattr(self.word, "add_history_event"):
            self.word.add_history_event(rating=rating, is_correct=is_correct)

        self.ml_result = {
            "rating": rating,
            "correct": is_correct,
            "next_repeat_days": days,
            "ml_score": ml_score,
        }

    def feedback(self) -> dict:
        """
        Готовый ответ для отправки пользователю/сервиса:
        {
            "correct": bool,
            "next_repeat_days": int,
            "ml_score": float,
            "rating": int
        }
        """
        if not self.ml_result:
            is_correct = self.check()
            return {
                "correct": is_correct,
                "next_repeat_days": None,
            }
        return {
            "correct": self.ml_result.get("correct"),
            "next_repeat_days": self.ml_result.get("next_repeat_days"),
            "ml_score": self.ml_result.get("ml_score"),
            "rating": self.ml_result.get("rating"),
        }

    def _rate_answer(self) -> tuple[int, bool]:
        """
        Пример: если ответ совпал с переводом, считаем rating=4 (Easy),
        иначе rating=1 (Again). Здесь можешь оставить свою реализацию.
        """
        is_correct = self.word.check_translation(self.answer)
        rating = 4 if is_correct else 1
        return rating, is_correct

    def evaluate_with_ml(self, ml_model=None) -> None:
        """
        Обновляет слово (difficulty, stability, next_repeat, ml_score)
        и заполняет self.ml_result.
        Параметр ml_model оставлен для совместимости.
        """
        rating, is_correct = self._rate_answer()

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
                0.7 * self.word.base_difficulty +
                0.3 * self.word.personal_difficulty
        )

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

        if hasattr(self.word, "add_history_event"):
            self.word.add_history_event(rating=rating, is_correct=is_correct)

        self.ml_result = {
            "rating": rating,
            "correct": is_correct,
            "next_repeat_days": days,
            "ml_score": ml_score,
        }

        if self.stats is not None:
            pass