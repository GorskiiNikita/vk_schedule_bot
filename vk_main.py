import random
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

TOKEN = 'cbb736a0eaa5cbb7c5a8feec57b57479ef7b518cdee16c9bab004299f0c83cd44f830247c4063dc637f11'


def start():
    keyboard = VkKeyboard()
    keyboard.add_button('Где пара?', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Какие сегодня пары?', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Какие завтра пары?', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Когда на учёбу?', color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()


def where_is():
    return 'в пизде'


def what_is_today():
    return 'хуй'


def what_is_tomorrow():
    return 'пизда'


def when_to_study():
    return 'иди на хуй'


def main():
    vk_session = vk_api.VkApi(
        token=TOKEN)

    longpoll = VkBotLongPoll(vk_session, '187821773')

    vk = vk_session.get_api()

    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.obj.text.lower().strip() == 'старт':
                vk.messages.send(user_id=event.obj.from_id,
                                 keyboard=start(),
                                 message='Прувет',
                                 random_id=random.randint(0, 18446744073709551615))

            elif event.obj.text.lower().strip() == 'где пара?':
                vk.messages.send(user_id=event.obj.from_id,
                                 message=where_is(),
                                 random_id=random.randint(0, 18446744073709551615))

            elif event.obj.text.lower().strip() == 'какие сегодня пары?':
                vk.messages.send(user_id=event.obj.from_id,
                                 message=what_is_today(),
                                 random_id=random.randint(0, 18446744073709551615))

            elif event.obj.text.lower().strip() == 'какие завтра пары?':
                vk.messages.send(user_id=event.obj.from_id,
                                 message=what_is_tomorrow(),
                                 random_id=random.randint(0, 18446744073709551615))

            elif event.obj.text.lower().strip() == 'когда на учёбу?':
                vk.messages.send(user_id=event.obj.from_id,
                                 message=when_to_study(),
                                 random_id=random.randint(0, 18446744073709551615))

            else:
                vk.messages.send(user_id=event.obj.from_id,
                                 message='Не понел тебя',
                                 random_id=random.randint(0, 18446744073709551615))


main()
