import vk_api
from pymongo import MongoClient
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id


TOKEN = 'cbb736a0eaa5cbb7c5a8feec57b57479ef7b518cdee16c9bab004299f0c83cd44f830247c4063dc637f11'


def add_keyboard():
    keyboard = VkKeyboard()
    keyboard.add_button('Где пара?', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Какие сегодня пары?', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Какие завтра пары?', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Когда на учёбу?', color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()


def get_group(user_id):
    client = MongoClient()
    db = client.botdb
    group = db.users.find_one({'_id': user_id})
    return group


def start_func(user_id):
    client = MongoClient()
    db = client.botdb
    group = db.users.insert_one({'_id': user_id, 'group': None})


def where_is():
    return 'в пизде'


def what_is_today():
    return 'хуй'


def what_is_tomorrow():
    return 'пизда'


def when_to_study():
    return 'иди на хуй'


def main():
    vk_session = vk_api.VkApi(token=TOKEN)

    client = MongoClient()
    db = client.botdb

    longpoll = VkBotLongPoll(vk_session, '187821773')

    vk = vk_session.get_api()

    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.obj.text.lower().strip() == 'начать' and not db.users.find_one({'_id': event.obj.from_id}):
                vk.messages.send(user_id=event.obj.from_id,
                                 keyboard=add_keyboard(),
                                 message='Прувет',
                                 random_id=get_random_id())
                start_func(event.obj.from_id)

            elif event.obj.text.lower().strip() == 'где пара?':
                vk.messages.send(user_id=event.obj.from_id,
                                 message=where_is(),
                                 random_id=get_random_id())
                get_group(event.obj.from_id)

            elif event.obj.text.lower().strip() == 'какие сегодня пары?':
                vk.messages.send(user_id=event.obj.from_id,
                                 message=what_is_today(),
                                 random_id=get_random_id())

            elif event.obj.text.lower().strip() == 'какие завтра пары?':
                vk.messages.send(user_id=event.obj.from_id,
                                 message=what_is_tomorrow(),
                                 random_id=get_random_id())

            elif event.obj.text.lower().strip() == 'когда на учёбу?':
                vk.messages.send(user_id=event.obj.from_id,
                                 message=when_to_study(),
                                 random_id=get_random_id())

            else:
                vk.messages.send(user_id=event.obj.from_id,
                                 message='Не понел',
                                 random_id=get_random_id())


if __name__ == '__main__':
    main()
