from bson import ObjectId
from pymongo import ASCENDING,MongoClient
from flask import g

class SettingModel():
    def __init__(self, settingId=None):
        self._id = ObjectId(settingId)
        self.collection = getattr(g,'database',MongoClient('localhost', 27017)).db_meta.settings
        self.collection_config = getattr(g,'database',MongoClient('localhost', 27017)).db_meta.configuration

    def get_all(self):
        result = []
        req = self.collection.find({}).sort('group', ASCENDING)
        if req.count() > 0:
            result = []
            for r in req:
                r['_id'] = str(r['_id'])
                result.append(r)
        return result

    def get_version(self):
        req = self.collection_config.find_one()
        req['_id']=str(req['_id'])
        return req