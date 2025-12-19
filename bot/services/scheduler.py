import asyncio
from datetime import datetime, timezone, timedelta


class Scheduler:
    def __init__(self, db, notifier):
        self.db = db
        self.notifier = notifier

    def start(self):
        """Запуск задач планировщика"""
        asyncio.create_task(self.revise_words_task())
        asyncio.create_task(self.daily_motivation_task())

    async def revise_words_task(self):
        """Задача для повторения слов, настройка интервала по количеству напоминаний"""
        default_interval = 86400  # 24 часа в секундах
        while True:
            try:
                users = await self.db.get_all_users()
                now = datetime.now(timezone.utc)
                interval = default_interval

                for user in users:
                    settings = user.settings or {}
                    reminders_per_day = settings.get("reminders_per_day", 1)
                    interval = default_interval // max(reminders_per_day, 1)

                    words = await self.db.get_user_words(user.user_id)
                    for word in words:
                        if word.next_repeat:
                            next_repeat = (
                                word.next_repeat
                                if word.next_repeat.tzinfo
                                else word.next_repeat.replace(tzinfo=timezone.utc)
                            )

                            if next_repeat <= now:
                                await self.notifier.send_word_reminder(
                                    user.user_id, word.text
                                )

                                next_repeat = now + timedelta(seconds=interval)
                                await self.db.update_word_next_repeat(
                                    user.user_id, word.word_id, next_repeat
                                )

                                break

                await asyncio.sleep(interval)

            except Exception as e:
                print(f"Ошибка в revise_words_task: {e}")
                await asyncio.sleep(60)

    async def daily_motivation_task(self):
        """Задача для отправки ежедневной мотивации всем пользователям"""
        daily_hour = 12
        daily_minute = 0

        while True:
            now = datetime.now(timezone.utc)

            next_run = datetime(
                year=now.year,
                month=now.month,
                day=now.day,
                hour=daily_hour,
                minute=daily_minute,
                tzinfo=timezone.utc,
            )

            if next_run <= now:
                next_run += timedelta(days=1)

            wait_seconds = (next_run - now).total_seconds()
            await asyncio.sleep(wait_seconds)

            users = await self.db.get_all_users()
            for user in users:
                await self.notifier.send_motivation(user.user_id)
