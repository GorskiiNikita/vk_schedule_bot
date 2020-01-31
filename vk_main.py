import datetime
import time

import vk_api
from pymongo import MongoClient
from vk_api.bot_longpoll import VkBotEventType
from vk_api.utils import get_random_id

from commands_bot import where_is, what_is_today, what_is_tomorrow, when_to_study
from db_client import ClientMongoDb
from settings import VK_TOKEN, VK_GROUP_ID
from utils import add_keyboard
from vk_long_poll import MyVkBotLongPoll


class Holidays:
    def __init__(self):
        self.today_is_holiday = False
        self.client = MongoClient()
        self.db = self.client.botdb

        self.holiday_dates = self.get_holiday_dates()
        self.response_text = ''

    def get_holiday_dates(self):
        cur = self.db.holidays.find()
        hols = []
        for i in cur:
            hols.append(i)
        return hols

    def check_holidays(self):
        now = datetime.datetime.now() + datetime.timedelta(hours=3)
        for holiday in self.holiday_dates:
            if datetime.datetime.strptime(holiday['start_holidays'], '%d-%m-%Y') < now < datetime.datetime.strptime(holiday['end_holidays'], '%d-%m-%Y'):
                self.response_text = holiday['text']
                return True
        return False

    def start_loop(self):
        while True:
            time.sleep(30)
            if self.check_holidays():
                self.today_is_holiday = True
            else:
                self.today_is_holiday = False


def main():
    mongo_client = ClientMongoDb()
    vk_session = vk_api.VkApi(token=VK_TOKEN)

    longpoll = MyVkBotLongPoll(vk_session, VK_GROUP_ID)

    vk = vk_session.get_api()

    list_of_groups = mongo_client.get_list_of_groups()

    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            now = datetime.datetime.now() + datetime.timedelta(hours=3)
            group = mongo_client.get_group(event.obj.from_id)
            if not group:
                vk.messages.send(user_id=event.obj.from_id,
                                 keyboard=add_keyboard(),
                                 message='Привет, Введите номер группы',
                                 random_id=get_random_id())
                mongo_client.start_func(event.obj.from_id)
                continue

            if event.obj.text.lower() in list_of_groups:
                vk.messages.send(user_id=event.obj.from_id,
                                 keyboard=add_keyboard(),
                                 message='Номер принят',
                                 random_id=get_random_id())
                mongo_client.update_user_group(event.obj.from_id, event.obj.text)

            elif group['group'] in list_of_groups:
                if event.obj.text.lower().strip() == 'где пара?':
                    vk.messages.send(user_id=event.obj.from_id,
                                     message=where_is(group['group'], now, mongo_client),
                                     random_id=get_random_id())

                elif event.obj.text.lower().strip() == 'какие сегодня пары?':
                    vk.messages.send(user_id=event.obj.from_id,
                                     message=what_is_today(group['group'], now),
                                     random_id=get_random_id())

                elif event.obj.text.lower().strip() == 'какие завтра пары?':
                    vk.messages.send(user_id=event.obj.from_id,
                                     message=what_is_tomorrow(group['group'], now),
                                     random_id=get_random_id())

                elif event.obj.text.lower().strip() == 'когда на учёбу?':
                    vk.messages.send(user_id=event.obj.from_id,
                                     message=when_to_study(group['group'], now),
                                     random_id=get_random_id())

                else:
                    vk.messages.send(user_id=event.obj.from_id,
                                     message='Бот вас не понял. Введите команду или номер группы.',
                                     random_id=get_random_id())

            else:
                vk.messages.send(user_id=event.obj.from_id,
                                 message='Введите номер группы',
                                 random_id=get_random_id())


if __name__ == '__main__':
    main()
