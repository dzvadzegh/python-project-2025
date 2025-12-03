from datetime import datetime
from .stats import Stats


class User:
    def __init__(
        self,
        user_id: int,
        username: str,
        settings: dict | None = None,
        progress: dict | None = None,
        words_added: dict | None = None,
        last_active: datetime | None = None,  # время последней активности
        stats: Stats | None = None,
        ml_profile: dict | None = None,
    ):
        self.user_id = user_id
        self.username = username
        self.settings = settings
        self.progress = progress
        self.words_added = words_added
        self.last_active = last_active
        self.stats = Stats(user_id)
        self.ml_profile = ml_profile

    def add_word(self, word, translation) -> None:
        self.words_added[word] = translation

    def update_last_active(self) -> None:
        self.last_active = datetime.now(datetime.timezone.utc)

    def get_info(self) -> dict:
        return {
            "username": self.username,
            "settings": self.settings,
            "progress": self.progress,
            "words_total": len(self.words_added),
        }

    def get_stats(self):
        return self.stats.get_statistics()

    def update_ml_profile(self, data: dict):
        self.ml_profile.update(data)
