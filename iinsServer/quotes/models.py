from bson import ObjectId
from pymongo import ASCENDING,MongoClient
from flask import g



class QuotesModel:
    def __init__(self):
        self.collection = getattr(g,'database',MongoClient('localhost', 27017)).iins_op.quotes


    def get_list(self):
        result = []
        req = self.collection.find().sort('insurer', ASCENDING)
        if req.count() > 0:
            for r in req:
                r['_id'] = str(r['_id'])
                result.append(r)
        return result

    def save(self,policyInfo):
        self.collection.update_one({"policy.policyNumber":policyInfo['policy']['policyNumber']},{"$set":policyInfo},upsert=True)
        return policyInfo

