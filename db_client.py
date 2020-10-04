from pymongo import MongoClient

from storage import DAYS_OF_WEEK


class ClientMongoDb:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.botdb

    def get_group(self, user_id):
        return self.db.users.find_one({'_id': user_id})

    def get_list_of_groups(self):
        return [group['_id'] for group in self.db.groups.find()]

    def get_schedule(self, group, date):
        day = date.isoweekday()
        schedule = self.db.groups.find_one({'_id': group})[DAYS_OF_WEEK[day - 1]]
        for lesson in schedule.keys():
            if schedule[lesson] is None:
                continue
            elif len(schedule[lesson]) == 1:
                schedule[lesson] = schedule[lesson][0]
            elif len(schedule[lesson]) == 2:
                schedule[lesson] = schedule[lesson][date.isocalendar()[1] % 2]
        return schedule

    def init_user(self, user_id):
        self.db.users.insert_one({'_id': user_id, 'group': None, 'action': 'wait'})

    def update_user_group(self, user_id, group):
        self.db.users.update_one({
            '_id': user_id
        }, {
            '$set': {
                'group': group.lower()
            }
        }, upsert=False)

    def change_action_user(self, user_id, action):
        self.db.users.update_one({
            '_id': user_id
        }, {
            '$set': {
                'action': action
            }
        }, upsert=False)

    def get_texts(self):
        texts = {}
        for text in self.db.texts.find():
            texts[text['_id']] = text['text']
        return texts

    def get_last_update_texts(self):
        return self.db.times.find_one({'_id': 'last_update_texts'})['timestamp']

    def get_last_update_groups(self):
        return self.db.times.find_one({'_id': 'last_update_groups'})['timestamp']

    def get_last_update_holidays(self):
        return self.db.times.find_one({'_id': 'last_update_holidays'})['timestamp']

    def get_holidays(self):
        holidays = []
        for holiday in self.db.holidays.find():
            holidays.append(holiday['date'])
        return holidays

    def get_schedule_status(self):
        return self.db.settings.find_one({'_id': 'main'})['schedule_enabled']



