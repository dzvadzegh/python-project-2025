from aiogram.enums import ParseMode


class NotificationService:
    def __init__(self, db, telegram_io):
        self.db = db
        self.telegram_io = telegram_io

    async def send_word_reminder(self, user_id: int, word_text: str):
        text = (
            f"Слово: *{word_text}*\n\n" "Напишите перевод слова, а затем проверьте себя"
        )

        await self.telegram_io.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
        )

        await self.db.log_activity(user_id, f"reminder:{word_text}")

    async def send_motivation(self, user_id: int):
        text = (
            "✨ *Небольшая мотивация*\n\n"
            "С каждым выученным словом вы все ближе к цели!"
        )

        await self.telegram_io.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
        )

        await self.db.log_activity(user_id, "daily_motivation")
