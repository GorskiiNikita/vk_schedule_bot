import settings
from telegram_api import invoke_telegram


class TelegramLogger:
    def __init__(self):
        self.text = ''

    def write(self, string):
        self.text += string

    def flush(self):
        if self.text:
            with open(settings.PATH_TO_LOG_FILE, 'a') as log_file:
                log_file.write(self.text)

            try:
                invoke_telegram('sendMessage', chat_id=settings.CHAT_ID, text=self.text)
            except:
                pass

            self.text = ''
