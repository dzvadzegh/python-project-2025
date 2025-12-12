import asyncio
from datetime import datetime, timezone, timedelta


class Scheduler:
    def __init__(self, db, notifier):
        self.db = db
        self.notifier = notifier
        self.tasks = []

    def start(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.revise_words_task())
        loop.create_task(self.daily_motivation_task())

    async def revise_words_task(self):
        while True:
            users = await self.db.get_all_users()
            for user in users:
                words = await self.db.get_user_words(user['user_id'])
                now = datetime.now(timezone.utc)
                for word in words:
                    if word['next_repeat'] and word['next_repeat'] <= now:
                        await self.notifier.send_word_reminder(user['user_id'], word['text'])
                        await self.db.update_word_next_repeat(user['user_id'], word['id'])
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
                tzinfo=timezone.utc
            )
            if next_run <= now:
                next_run += timedelta(days=1)
            wait_seconds = (next_run - now).total_seconds()
            await asyncio.sleep(wait_seconds)

            users = await self.db.get_all_users()
            for user in users:
                await self.notifier.send_motivation(user['user_id'])

