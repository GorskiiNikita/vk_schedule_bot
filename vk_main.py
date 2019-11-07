import vk_api
import datetime
from pymongo import MongoClient
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id


DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
DAYS = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
TIME_LESSONS = {'first': datetime.time(9, 0, 0),
                'second': datetime.time(10, 45, 0),
                'third': datetime.time(12, 30, 0),
                'fourth': datetime.time(15, 0, 0),
                'fifth': datetime.time(16, 45, 0)}

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


def update_user_group(user_id, group):
    client = MongoClient()
    db = client.botdb
    db.users.update_one({
        '_id': user_id
    }, {
        '$set': {
            'group': group.lower()
        }
    }, upsert=False)


def get_group(user_id):
    client = MongoClient()
    db = client.botdb
    group = db.users.find_one({'_id': user_id})
    return group


def start_func(user_id):
    client = MongoClient()
    db = client.botdb
    group = db.users.insert_one({'_id': user_id, 'group': None})


def get_schedule(group, date):
    client = MongoClient()
    db = client.botdb
    day = date.isoweekday()
    schedule = db.groups.find_one({'_id': group})[DAYS_OF_WEEK[day - 1]]
    for lesson in schedule.keys():
        if schedule[lesson] is None:
            continue
        elif len(schedule[lesson]) == 1:
            schedule[lesson] = schedule[lesson][0]
        elif len(schedule[lesson]) == 2:
            schedule[lesson] = schedule[lesson][date.isocalendar()[1] % 2]
    return schedule


def where_is(group, date):
    now = date
    next_lesson_time = None
    next_lesson_key = None
    day = now.isoweekday()
    time = now.time()
    if day in range(1, 7):
        schedule = get_schedule(group, now)
        for key in TIME_LESSONS.keys():
            if schedule[key] is not None and TIME_LESSONS[key] > time:
                next_lesson_time = TIME_LESSONS[key]
                next_lesson_key = key
                break

        if next_lesson_time is None:
            return 'Пары сегодня уже закончились'
        else:
            minutes = next_lesson_time.hour * 60 + next_lesson_time.minute - time.minute - time.hour * 60
            minutes_left = minutes % 60
            hours_left = minutes // 60
            return f'Следующая пара: {schedule[next_lesson_key]["name"]} \n Через: {hours_left} ч. {minutes_left} м. \n' \
                   f'Пара в {schedule[next_lesson_key]["where"]} аудитории'

    else:
        return 'Сегодня выходной'


def what_is_today(group, date):
    resp = []
    lessons_time = {'first': '9:00 - 10:30',
                    'second': '10:45 - 12:15',
                    'third': '12:30 - 14:00',
                    'fourth': '15:00 - 16:30',
                    'fifth': '16:45 - 18:15'}
    now = date
    if now.isoweekday() in range(1, 7):
        schedule = get_schedule(group, now)
        for lesson in schedule.keys():
            if schedule[lesson] is not None:
                resp.append(f'{lessons_time[lesson]} \n{schedule[lesson]["name"]} {schedule[lesson]["where"]}')
        resp = '\n\n'.join(resp)
        if resp:
            return resp
    return 'Сегодня выходной'


def what_is_tomorrow(group, date):
    date += datetime.timedelta(days=1)
    resp = what_is_today(group, date)
    if resp == 'Сегодня выходной':
        resp = 'Завтра выходной'
    return resp


def when_to_study(group, date):
    resp = where_is(group, date)
    if resp == 'Пары сегодня уже закончились' or resp == 'Сегодня выходной':
        date += datetime.timedelta(days=1)
        resp = what_is_today(group, date)
        while resp == 'Сегодня выходной':
            date += datetime.timedelta(days=1)
            resp = what_is_today(group, date)
        day = date.isoweekday()
        date = date.strftime('%d.%m.%Y')
        resp = f'На учёбу {date}, {DAYS[day-1]} \n\n Расписание в этот день:\n' + resp
        return resp
    else:
        return f'На учёбу {date.strftime("%d.%m.%Y")}, Сегодня \n {what_is_today(group, date)}'


def main():
    vk_session = vk_api.VkApi(token=TOKEN)

    client = MongoClient()
    db = client.botdb

    longpoll = VkBotLongPoll(vk_session, '187821773')

    vk = vk_session.get_api()

    LIST_OF_GROUPS = [group['_id'] for group in db.groups.find()]

    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            group = get_group(event.obj.from_id)
            if not group:
                vk.messages.send(user_id=event.obj.from_id,
                                 keyboard=add_keyboard(),
                                 message='Привет, Введите номер группы',
                                 random_id=get_random_id())
                start_func(event.obj.from_id)
                continue

            if event.obj.text.lower() in LIST_OF_GROUPS:
                vk.messages.send(user_id=event.obj.from_id,
                                 keyboard=add_keyboard(),
                                 message='Номер принят',
                                 random_id=get_random_id())
                update_user_group(event.obj.from_id, event.obj.text)

            elif group['group'] in LIST_OF_GROUPS:
                if event.obj.text.lower().strip() == 'где пара?':
                    vk.messages.send(user_id=event.obj.from_id,
                                     message=where_is(group['group'], datetime.datetime.now()),
                                     random_id=get_random_id())

                elif event.obj.text.lower().strip() == 'какие сегодня пары?':
                    vk.messages.send(user_id=event.obj.from_id,
                                     message=what_is_today(group['group'], datetime.datetime.now()),
                                     random_id=get_random_id())

                elif event.obj.text.lower().strip() == 'какие завтра пары?':
                    vk.messages.send(user_id=event.obj.from_id,
                                     message=what_is_tomorrow(group['group'], datetime.datetime.now()),
                                     random_id=get_random_id())

                elif event.obj.text.lower().strip() == 'когда на учёбу?':
                    vk.messages.send(user_id=event.obj.from_id,
                                     message=when_to_study(group['group'], datetime.datetime.now()),
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
