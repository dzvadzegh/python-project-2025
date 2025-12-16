import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from commands.start import start_router
from commands.info import info_router
from commands.stats import stats_router
from commands.add import add_router
from commands.settings import settings_router

from services.database import Database
from services.notification import NotificationService
from services.scheduler import Scheduler

from infrastructure.config import BOT_TOKEN


async def main():
    db = Database()
    dp = Dispatcher()
    dp["db"] = db
    await db.connect()

    notifier = NotificationService(db)
    scheduler = Scheduler(db, notifier)

    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)

    dp.include_router(start_router)
    dp.include_router(info_router)
    dp.include_router(stats_router)
    dp.include_router(add_router)
    dp.include_router(settings_router)

    print("Everything ok")

    asyncio.create_task(scheduler.start())

    try:
        await dp.start_polling(bot)
    finally:
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
