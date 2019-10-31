from pymongo import MongoClient

client = MongoClient()
db = client.botdb
collection = db.groups
cm1 = collection.find_one()['monday']
