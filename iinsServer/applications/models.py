from bson import ObjectId
from pymongo import ASCENDING,MongoClient
from flask import g

class ApplicationModel():
    def __init__(self):
        self.collection = getattr(g,'database',MongoClient('localhost', 27017)).iins_op.application


    def get_application_list(self):
        result = []
        req = self.collection.find().sort('insurer', ASCENDING)
        if req.count() > 0:
            for r in req:
                r['_id'] = str(r['_id'])
                result.append(r)
        return result

    def save_application(self,application):
        self.collection.update_one({},{"$set":application},upsert=True)
        return application

    def submit_application(self,application):
        self.collection.update_one({},{"$set":application},upsert=True)
        return application