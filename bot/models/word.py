from datetime import datetime, timedelta
from difflib import SequenceMatcher


class Word:
    def __init__(
        self,
        word_id: int,
        user_id: int,
        text: str,
        translation: str,
        next_repeat: datetime | None = None,
        repeat_count: int = 0,
        created_at: datetime | None = None,
        base_difficulty: float = 0.5,  # базовая сложность слова
        personal_difficulty: float = 0.5,  # сложность конкретно для пользователя
        difficulty: float = 0.5,  # итоговая сложность (смесь)
        stability: float = 1.0,  # "длина" интервала в днях
        ml_score: float = 0.5,  # вероятность успеха
        history: list | None = None,
    ):
        self.id = word_id
        self.user_id = user_id
        self.text = text
        self.translation = translation
        self.next_repeat = next_repeat
        self.repeat_count = repeat_count
        self.created_at = created_at
        self.base_difficulty = base_difficulty
        self.personal_difficulty = personal_difficulty
        self.difficulty = difficulty
        self.stability = stability
        self.ml_score = ml_score
        self.history = history

    def check_translation(self, answer: str, threshold: float = 0.8) -> bool:
        """
        Заглушка: сейчас проверка перевода не используется,
        т.к. пользователь сам оценивает знание слова (rating 1–4).
        Метод оставлен для совместимости с интерфейсом Checker.
        """
        return True

    def update_repeat(self):
        self.repeat_count += 1
        self.next_repeat = datetime.now(datetime.timezone.utc) + timedelta(days=1)

    def schedule_next_repeat(self, days: int):
        self.next_repeat = datetime.now(datetime.timezone.utc) + timedelta(days=days)

    def is_due(self) -> bool:
        return datetime.now(datetime.timezone.utc) >= self.next_repeat

    def record_history(self, rating: int, is_correct: bool) -> None:
        self.history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "rating": rating,
                "is_correct": is_correct,
            }
        )

    def get_info(self):
        return {
            "word": self.text,
            "translation": self.translation,
            "repeat_count": self.repeat_count,
            "next_repeat": self.next_repeat,
            "difficulty": self.difficulty,
        }
