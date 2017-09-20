from bson.objectid import ObjectId
from pymongo import ASCENDING,MongoClient
from flask import g

class ApplicationModel():
    def __init__(self):
        self.collection = getattr(g,'database',MongoClient('localhost', 27017)).iins_op.application


    def get_application_list(self,status=None):
        result = []
        filter={"status":status} if status else {}
        req = self.collection.find().sort('insurer', ASCENDING)
        if req.count() > 0:
            for r in req:
                r['_id'] = str(r['_id'])
                result.append(r)
        return result

    def save_application(self,application):
        if '_id' in application.keys():
            filter ={'_id':ObjectId(application['_id'])}
            del application['_id']
        else:
            filter ={'_id':ObjectId()}
        self.collection.update_one(filter,{"$set":application},upsert=True)
        application['_id']= str(filter['_id'])
        return application

    def submit_application(self,application):
        id = ObjectId(application['_id']) if '_id' in application.keys() else ObjectId()
        self.collection.update_one({'_id',id},{"$set":application},upsert=True)
        return application