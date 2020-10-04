import datetime
import threading
import time
import os
import sys

import vk_api
from vk_api.bot_longpoll import VkBotEventType
from vk_api.utils import get_random_id

from commands_bot import where_is, what_is_today, what_is_tomorrow, when_to_study
from db_client import ClientMongoDb
from settings import VK_TOKEN, VK_GROUP_ID, PATH_TO_LOG_FILE, VK_ADMIN_ID
from utils import create_custom_keyboard
from vk_long_poll import MyVkBotLongPoll


class Texts:
    def __init__(self, mongo_client):
        self.data = mongo_client.get_texts()
        self.last_update_time = mongo_client.get_last_update_texts()

    def start_check_loop(self, mongo_client):
        while True:
            if self.last_update_time != mongo_client.get_last_update_texts():
                self.last_update_time = mongo_client.get_last_update_texts()
                self.data = mongo_client.get_texts()
            time.sleep(5)


class Groups:
    def __init__(self, mongo_client):
        self.data = mongo_client.get_list_of_groups()
        self.last_update_time = mongo_client.get_last_update_groups()

    def start_check_loop(self, mongo_client):
        while True:
            if self.last_update_time != mongo_client.get_last_update_groups():
                self.last_update_time = mongo_client.get_last_update_groups()
                self.data = mongo_client.get_list_of_groups()
            time.sleep(0.05)


class Holidays:
    def __init__(self, mongo_client):
        self.data = mongo_client.get_holidays()
        self.last_update_time = mongo_client.get_last_update_holidays()

    def start_check_loop(self, mongo_client):
        while True:
            if self.last_update_time != mongo_client.get_last_update_holidays():
                self.last_update_time = mongo_client.get_last_update_groups()
                self.data = mongo_client.get_holidays()
            time.sleep(5)


def main():
    mongo_client = ClientMongoDb()

    texts = Texts(mongo_client)
    thread_check_texts = threading.Thread(target=texts.start_check_loop, args=(mongo_client, ))
    thread_check_texts.daemon = True
    thread_check_texts.start()

    groups = Groups(mongo_client)
    thread_check_groups = threading.Thread(target=groups.start_check_loop, args=(mongo_client,))
    thread_check_groups.daemon = True
    thread_check_groups.start()

    holidays = Holidays(mongo_client)
    thread_check_holidays = threading.Thread(target=holidays.start_check_loop, args=(mongo_client,))
    thread_check_holidays.daemon = True
    thread_check_holidays.start()

    vk_session = vk_api.VkApi(token=VK_TOKEN)
    longpoll = MyVkBotLongPoll(vk_session, VK_GROUP_ID)

    vk = vk_session.get_api()

    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            now = datetime.datetime.now() + datetime.timedelta(hours=3)
            group = mongo_client.get_group(event.obj.from_id)

            if event.obj.text.lower().strip() == 'начать' or group is None:
                if group is None:
                    mongo_client.init_user(event.obj.from_id)
                else:
                    mongo_client.change_action_user(event.obj.from_id, 'wait')
                vk.messages.send(user_id=event.obj.from_id,
                                 keyboard=create_custom_keyboard(['Узнать расписание',
                                                                  'Задать вопрос']),
                                 message=texts.data['welcome_message'],
                                 random_id=get_random_id())

            elif not mongo_client.get_schedule_status() and event.obj.text.lower().strip() in ['где пара?', 'какие сегодня пары?', 'какие завтра пары?', 'когда на учёбу?', 'узнать расписание']:
                vk.messages.send(user_id=event.obj.from_id,
                                 message=texts.data['schedule_disable'],
                                 random_id=get_random_id())

            elif event.obj.text.lower().strip() == 'узнать расписание':
                mongo_client.change_action_user(event.obj.from_id, 'get')
                vk.messages.send(user_id=event.obj.from_id,
                                 keyboard=create_custom_keyboard(['Где пара?',
                                                                  'Какие сегодня пары?',
                                                                  'Какие завтра пары?',
                                                                  'Когда на учёбу?',
                                                                  'Заказать работу',
                                                                  'На главную']),
                                 message=texts.data['query_schedule'],
                                 random_id=get_random_id())

            elif event.obj.text.lower().strip() == 'задать вопрос' or event.obj.text.lower().strip() == 'заказать работу':
                mongo_client.change_action_user(event.obj.from_id, 'alert')
                vk.messages.send(user_id=event.obj.from_id,
                                 keyboard=create_custom_keyboard(['На главную']),
                                 message=texts.data['question'],
                                 random_id=get_random_id())

            elif event.obj.text.lower().strip() == 'на главную':
                mongo_client.change_action_user(event.obj.from_id, 'wait')
                vk.messages.send(user_id=event.obj.from_id,
                                 keyboard=create_custom_keyboard(['Узнать расписание',
                                                                  'Задать вопрос']),
                                 message=texts.data['to_main'],
                                 random_id=get_random_id())
            elif group['action'] == 'get':

                if group['group'] not in groups.data:
                    group['group'] = None

                if event.obj.text.lower().strip() in groups.data:
                    mongo_client.update_user_group(event.obj.from_id, event.obj.text.lower().strip())
                    vk.messages.send(user_id=event.obj.from_id,
                                     message=texts.data['valid_group'],
                                     random_id=get_random_id())

                elif group['group'] is None:
                    vk.messages.send(user_id=event.obj.from_id,
                                     message=texts.data['input_group'],
                                     random_id=get_random_id())
                    continue

                elif event.obj.text.lower().strip() == 'где пара?':
                    vk.messages.send(user_id=event.obj.from_id,
                                     message=where_is(group['group'], now, mongo_client, holidays),
                                     random_id=get_random_id())

                elif event.obj.text.lower().strip() == 'какие сегодня пары?':
                    vk.messages.send(user_id=event.obj.from_id,
                                     message=what_is_today(group['group'], now, mongo_client, holidays),
                                     random_id=get_random_id())

                elif event.obj.text.lower().strip() == 'какие завтра пары?':
                    vk.messages.send(user_id=event.obj.from_id,
                                     message=what_is_tomorrow(group['group'], now, mongo_client, holidays),
                                     random_id=get_random_id())

                elif event.obj.text.lower().strip() == 'когда на учёбу?':
                    vk.messages.send(user_id=event.obj.from_id,
                                     message=when_to_study(group['group'], now, mongo_client, holidays),
                                     random_id=get_random_id())

                else:
                    vk.messages.send(user_id=event.obj.from_id,
                                     message=texts.data['schedule_error'],
                                     random_id=get_random_id())
            elif group['action'] == 'question' or group['action'] == 'alert':
                vk.messages.send(user_ids=','.join(VK_ADMIN_ID),
                                 message='тук-тук',
                                 forward_messages=event.obj.id,
                                 random_id=get_random_id())

                if group['action'] == 'alert':
                    mongo_client.change_action_user(event.obj.from_id, 'question')
                    vk.messages.send(user_id=event.obj.from_id,
                                     message=texts.data['receive_to_admin'],
                                     random_id=get_random_id())


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    err = open(PATH_TO_LOG_FILE, 'a+')
    sys.stderr = err
    sys.stdout = err
    main()
