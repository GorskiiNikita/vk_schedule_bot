from pymongo import MongoClient
from storage import *


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

    def start_func(self, user_id):
        self.db.users.insert_one({'_id': user_id, 'group': None})

    def update_user_group(self, user_id, group):
        self.db.users.update_one({
            '_id': user_id
        }, {
            '$set': {
                'group': group.lower()
            }
        }, upsert=False)



