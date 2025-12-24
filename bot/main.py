import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from bot.commands.start import start_router
from bot.commands.info import info_router
from bot.commands.stats import stats_router
from bot.commands.add import add_router
from bot.commands.settings import settings_router
from bot.commands.review import review_router

from bot.services.database import Database
from bot.services.notification import NotificationService
from bot.services.scheduler import Scheduler

from bot.infrastructure.config import BOT_TOKEN
from bot.infrastructure.telegram_io import TelegramIO

# python -m bot.main


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )

    db = Database()
    await db.connect()
    bot.db = db

    dp = Dispatcher()

    telegram_io = TelegramIO(bot)
    notifier = NotificationService(db, telegram_io)
    scheduler = Scheduler(db, notifier)

    dp.include_router(start_router)
    dp.include_router(info_router)
    dp.include_router(stats_router)
    dp.include_router(add_router)
    dp.include_router(settings_router)
    dp.include_router(review_router)

    print("Everything is ok")

    scheduler.start()

    try:
        await dp.start_polling(bot)
    finally:
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
