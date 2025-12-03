from datetime import datetime, timedelta


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
        difficulty: float = 0.5,
        ml_score: float = 0.5,
        history: list | None = None,
    ):
        self.id = word_id
        self.user_id = user_id
        self.text = text
        self.translation = translation
        self.next_repeat = next_repeat
        self.repeat_count = repeat_count
        self.created_at = created_at
        self.difficulty = difficulty
        self.ml_score = ml_score
        self.history = history

    def check_translation(self, answer: str) -> bool:
        return answer.strip().lower() == self.translation.lower()

    def update_repeat(self):
        self.repeat_count += 1
        self.next_repeat = datetime.now(datetime.timezone.utc) + timedelta(days=1)

    def schedule_next_repeat(self, days: int):
        self.next_repeat = datetime.now(datetime.timezone.utc) + timedelta(days=days)

    def is_due(self) -> bool:
        return datetime.now(datetime.timezone.utc) >= self.next_repeat

    def record_history(self, result: bool):
        self.history.append(
            {"timestamp": datetime.now(datetime.timezone.utc), "result": result}
        )

    def get_info(self):
        return {
            "word": self.text,
            "translation": self.translation,
            "repeat_count": self.repeat_count,
            "next_repeat": self.next_repeat,
            "difficulty": self.difficulty,
        }
