from _io import TextIOWrapper
import requests
import settings


class TelegramLogger(TextIOWrapper):
    def write(self, text):
        TextIOWrapper.write(self, text)

        self.alert_to_telegram('sendMessage', chat_id=settings.CHAT_ID, text=text)

    @staticmethod
    def alert_to_telegram(method, **kwargs):
        requests.post(f'{settings.URL}/bot{settings.TELEGRAM_BOT_TOKEN}/{method}', data=kwargs, proxies=settings.PROXIES)

