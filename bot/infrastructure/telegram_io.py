from aiogram import Bot
from aiogram.enums import ParseMode


class TelegramIO:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: ParseMode | None = None,
        reply_markup=None,
    ):
        await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
        )
