from dataclasses import dataclass


@dataclass
class StatsDTO:
    total_words: int
    learned_words: int
    success_rate: float
    learned_week: int
    learned_month: int
    activity_records: int


class Stats:
    def __init__(self, user_id: int, db, min_repetitions: int = 3):
        self.user_id = user_id
        self.db = db
        self.min_repetitions = min_repetitions

    async def update(self, word_id: int, is_correct: bool) -> None:
        """
        Записать факт ответа пользователя в таблицу stat.
        """
        await self.db.execute(
            """
            INSERT INTO stat (user_id, action_type, details, created_at)
            VALUES (:user_id, :action_type, :details, NOW())
            """,
            {
                "user_id": self.user_id,
                "action_type": "answer_correct" if is_correct else "answer_wrong",
                "details": {"word_id": word_id},
            },
        )

    async def load(self) -> StatsDTO:
        total_words = await self.db.fetch_val(
            "SELECT COUNT(*) FROM word WHERE user_id = :user_id",
            {"user_id": self.user_id},
        )

        learned_words = await self.db.fetch_val(
            """
            SELECT COUNT(*) FROM word
            WHERE user_id = :user_id
              AND repetitions >= :min_rep
            """,
            {"user_id": self.user_id, "min_rep": self.min_repetitions},
        )

        learned_week = await self.db.fetch_val(
            """
            SELECT COUNT(*) FROM stat
            WHERE user_id = :user_id
              AND action_type = 'word_learned'
              AND created_at >= NOW() - INTERVAL '7 days'
            """,
            {"user_id": self.user_id},
        )

        learned_month = await self.db.fetch_val(
            """
            SELECT COUNT(*) FROM stat
            WHERE user_id = :user_id
              AND action_type = 'word_learned'
              AND created_at >= NOW() - INTERVAL '30 days'
            """,
            {"user_id": self.user_id},
        )

        activity_records = await self.db.fetch_val(
            "SELECT COUNT(*) FROM stat WHERE user_id = :user_id",
            {"user_id": self.user_id},
        )

        success_rate = 0.0
        if total_words:
            success_rate = round(learned_words / total_words * 100, 1)

        return StatsDTO(
            total_words=total_words,
            learned_words=learned_words,
            success_rate=success_rate,
            learned_week=learned_week,
            learned_month=learned_month,
            activity_records=activity_records,
        )
