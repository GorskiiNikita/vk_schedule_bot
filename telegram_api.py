import requests
import settings


def invoke_telegram(method, **kwargs):
    resp = requests.post(f'{settings.URL}/bot{settings.TELEGRAM_BOT_TOKEN}/{method}', data=kwargs)
    return resp
