import asyncio
from datetime import datetime, timezone, timedelta
from bot.commands.review import user_pending_word


class Scheduler:
    def __init__(self, db, notifier):
        self.db = db
        self.notifier = notifier
        self.tasks = []

    def start(self):
        self.tasks.append(asyncio.create_task(self.revise_words_task()))
        self.tasks.append(asyncio.create_task(self.daily_motivation_task()))

    async def stop(self):
        for task in self.tasks:
            task.cancel()

        for task in self.tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass

    async def revise_words_task(self):
        DEFAULT_INTERVAL = 86400  # 24 часа

        while True:
            try:
                users = await self.db.get_all_users()
                now = datetime.now(timezone.utc)

                for user in users:
                    settings = user.settings or {}
                    reminders_per_day = max(settings.get("reminders_per_day", 1), 1)
                    interval = DEFAULT_INTERVAL // reminders_per_day

                    words = await self.db.get_user_words(user.user_id)
                    for word in words:
                        next_repeat = word.next_repeat
                        if next_repeat and next_repeat.tzinfo is None:
                            next_repeat = next_repeat.replace(tzinfo=timezone.utc)

                        if next_repeat and next_repeat <= now:
                            await self.notifier.send_word_reminder(
                                user.user_id, word.text
                            )
                            await self.db.update_word_next_repeat(
                                user.user_id,
                                word.id,
                                now + timedelta(seconds=interval),
                            )
                            user_pending_word[user.user_id] = {
                                "stage": "answer",
                                "word": word,
                            }
                            break  # одно слово за проход

                await asyncio.sleep(DEFAULT_INTERVAL)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Ошибка в revise_words_task: {e}")
                await asyncio.sleep(60)

    async def daily_motivation_task(self):
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
                await self.notifier.send_motivation(user["user_id"])
