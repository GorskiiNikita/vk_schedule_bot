from storage import *


def where_is(group, date, mongo_client):
    now = date
    next_lesson_time = None
    next_lesson_key = None
    day = now.isoweekday()
    time = now.time()
    if day in range(1, 7):
        schedule = mongo_client.get_schedule(group, now)
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


def what_is_today(group, date, mongo_client):
    resp = []
    lessons_time = {'first': '9:00 - 10:30',
                    'second': '10:45 - 12:15',
                    'third': '12:30 - 14:00',
                    'fourth': '15:00 - 16:30',
                    'fifth': '16:45 - 18:15'}
    now = date
    if now.isoweekday() in range(1, 7):
        schedule = mongo_client.get_schedule(group, now)
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

