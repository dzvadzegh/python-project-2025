from services.database import Database
from services.notification import NotificationService
from services.scheduler import Scheduler

from commands.add import bot_add
from commands.start import bot_start
from commands.info import bot_info
from commands.stats import bot_stats


def main():
    db = Database()
    notifier = NotificationService(db)
    scheduler = Scheduler(db, notifier)

    try:
        bot_start()
        bot_info()
        bot_stats()
        bot_add()

        print("Bot started")
    except Exception as e:
        raise Exception(f"Error with interconnection (commands): {e}")


if __name__ == "__main__":
    main()
