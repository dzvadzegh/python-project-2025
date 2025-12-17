import asyncio
from datetime import datetime, timezone, timedelta


class Scheduler:
    def __init__(self, db, notifier):
        self.db = db
        self.notifier = notifier

    def start(self):
        """Запуск задач планировщика"""
        asyncio.create_task(self.revise_words_task())  # Задача для повторений слов
        asyncio.create_task(self.daily_motivation_task())  # Задача для мотивации

    async def revise_words_task(self):
        """Задача для повторения слов, настройка интервала по количеству напоминаний"""
        while True:
            users = await self.db.get_all_users()
            now = datetime.now(timezone.utc)

            for user in users:
                settings = user.settings or {}
                reminders_per_day = settings.get("reminders_per_day", 1)
                new_var = 86400
                interval = (
                    new_var // reminders_per_day
                )  # Интервал в секундах между напоминаниями

                words = await self.db.get_user_words(user.user_id)
                for word in words:
                    if word.next_repeat and word.next_repeat <= now:
                        # Отправка напоминания о слове
                        await self.notifier.send_word_reminder(user.user_id, word.text)

                        # Обновляем время следующего повторения
                        next_repeat = now + timedelta(seconds=interval)
                        await self.db.update_word_next_repeat(
                            user.user_id, word.id, next_repeat
                        )

                        break  # Прерываем цикл, если слово отправлено для напоминания

            await asyncio.sleep(interval)  # Пауза между итерациями

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

            # Отправляем мотивацию всем пользователям
            users = await self.db.get_all_users()
            for user in users:
                await self.notifier.send_motivation(user.user_id)
