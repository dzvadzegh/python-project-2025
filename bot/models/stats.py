class Stats:
    def __init__(
        self,
        user_id: int,
        learned_words: int = 0,
        success_rate: float = 0.0,
        activity_log: list | None = None,
        histogram_data: dict | None = None,
        ml_stats: dict | None = None,
    ):
        self.user_id = user_id
        self.learned_words = learned_words
        self.success_rate = success_rate
        self.activity_log = activity_log
        self.histogram_data = histogram_data
        self.ml_stats = ml_stats

    def update(self, word_id: int, result: bool):
        self.activity_log.append({"word_id": word_id, "result": result})

    def get_statistics(self):
        return {
            "learned_words": self.learned_words,
            "success_rate": self.success_rate,
            "activity_records": len(self.activity_log),
        }

    def get_histogram(self):
        return self.histogram_data
