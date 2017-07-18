import importlib
from datetime import datetime
from bson import ObjectId
from flask import json,g
from pymongo import MongoClient


class Logging():
    def __init__(self, user=None, function=None, content=None, location=None, before=None, after=None,
                 additionalinfo=[]):
        self.user = user
        self.function = function
        self.content = content
        self.location = location
        self.before = before
        self.after = after
        self.additionalinfo = additionalinfo
        self.model_devices = importlib.import_module("NetvisServer.devices.models")
        self.DeviceModel = self.model_devices.DeviceModel
        self.date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.date = datetime.today().strftime('%Y-%m-%d')  # '2016-01' + '-' + str(random.randrange(10, 28))#
        self.status = 'init'
        self.db = getattr(g,'database',MongoClient('localhost', 27017)).sys_log

    # Replace additional info with new additional info
    def set(self, targetLog, additionalInfo, date):

        req = self.db.get_collection(date).update_one({"_id": ObjectId(targetLog)},
                                                      {"$set": {"additionalinfo": additionalInfo}}, upsert=True)

    def get(self, target_id, date):
        if date in self.db.collection_names():
            log = self.db.get_collection(date).find_one({"_id": ObjectId(target_id)})
            return log
        print("Get Log-ID Not Found")
        return

    def save(self):
        if self.date not in self.db.collection_names():
            self.db.create_collection(self.date)
        collection = self.db.get_collection(self.date)
        result = collection.insert_one(
            {"function": self.function, "user": self.user, "content": self.content, "date_time": self.date_time,
             'status': self.status, 'location': self.location, 'before': self.before, 'after': self.after,
             'additionalinfo': self.additionalinfo})
        return {"_id": str(result.inserted_id), "date": self.date, "content": self.content}

    def query_today(self):
        collection = self.db.get_collection(self.date)
        cursor = collection.find({}, {"function": 1, "content": 1, "date_time": 1, 'status': 1, 'user': 1, 'before': 1,
                                      'after': 1, 'additionalinfo': 1, '_id': 1})
        contents = []
        for content in cursor:
            contents.append(
                {"function": content['function'], "content": content['content'], "date_time": content['date_time'],
                 'status': content['status'], "user": content['user'], "before": content['before'],
                 "after": content['after'], "additionalinfo": content['additionalinfo']})
        return json.dumps(contents)

    # def query_today_limit(self, number):
    #     collection = self.db.get_collection(self.date)
    #     cursor = collection.find({}, {"function": 1, "content": 1, "date_time": 1, 'status': 1,'user':1,'target':1, '_id': 0}).limit(number)
    #     contents = []
    #     for content in cursor:
    #         contents.append({"function": content['function'], "content": content['content'], "date_time": content['date_time'],"user":content['user'],
    #                        'status': content['status'],'target': content['target']})
    #     return json.dumps(contents)

    def query_period(self, start_date, end_date, python=False):
        def compare(d):
            return (d >= start_date) and (d <= end_date)

        start_date = start_date[:10]
        end_date = end_date[:10]
        collections = list(filter(compare, self.db.collection_names()))
        collections.sort()
        contents = []
        for col in collections:
            collection = self.db.get_collection(col)
            cursor = collection.find({},
                                     {"function": 1, "content": 1, "date_time": 1, 'status': 1, 'user': 1, 'before': 1,
                                      'after': 1, 'additionalinfo': 1, 'location': 1, '_id': 1})
            for content in cursor:
                contents.append(
                    {"_id": str(content['_id']), "function": content['function'], "content": content['content'],
                     "date_time": content['date_time'], "user": content['user'],
                     'status': content['status'], 'before': content['before'], 'after': content['after'],
                     'location': content['location'], 'additionalinfo': content['additionalinfo']})
        contents = sorted(contents, key=lambda k: k['date_time'], reverse=True)
        if python:
            return contents
        else:
            return json.dumps(contents)

            # def query_today_summary(self):
            #     collection = self.db.get_collection(self.date)
            #     cursor = collection.aggregate([{"$group": {"_id": "$function", "count": {"$sum": 1}}}])
            #     contents = []
            #     for content in cursor:
            #         contents.append({"function": content['_id'], "count": content['count']})
            #     return json.dumps(contents)
            #
            # def query_period_summary(self, start_date, end_date):
            #     def compare(d):
            #         return (d >= start_date) & (d <= end_date)
            #
            #     collections = filter(compare, self.db.collection_names())
            #     contents = {}
            #     for col in collections:
            #         collection = self.db.get_collection(col)
            #         cursor = collection.aggregate([{"$group": {"_id": "$function", "count": {"$sum": 1}}}])
            #         for content in cursor:
            #             if content['_id'] in contents:
            #                 contents[content['_id']] += content['count']
            #             else:
            #                 contents[content['_id']] = content['count']
            #         contents_output = [{'function': key, 'count': value} for key, value in contents.items()]
            #     return json.dumps(contents_output)

            # Formatting additional info and hidden info

    def log_device(self):
        self.Logging()
