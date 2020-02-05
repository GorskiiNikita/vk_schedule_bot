VK_TOKEN = None
VK_GROUP_ID = None
PATH_TO_LOG_FILE = None
URL = None
TELEGRAM_BOT_TOKEN = None
PROXIES = None
CHAT_ID = None

try:
    from local_settings import *
except ImportError:
    pass
