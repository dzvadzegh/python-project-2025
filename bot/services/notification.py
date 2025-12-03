class NotificationService:
    def __init__(self, word_repo, user_repo, telegram_io):
        self.word_repo = word_repo
        self.user_repo = user_repo
        self.telegram_io = telegram_io


    async def send_notification(self, user, word):
        pass
