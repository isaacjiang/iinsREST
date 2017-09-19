from bson import ObjectId
from pymongo import ASCENDING,MongoClient,TEXT
from flask import g



class CustomersModel:
    def __init__(self):
        self.collection = getattr(g,'database',MongoClient('localhost', 27017)).iins_op.customers
        if 'customer_text' not in self.collection.index_information().keys():
            self.collection.create_index([('firstName',TEXT),('lastName',TEXT),('dateOfBirth',TEXT),('address',TEXT)],
                                         name="customer_text")


    def get_list(self):
        result = []
        req = self.collection.find().sort('customer_name', ASCENDING)
        if req.count() > 0:
            for r in req:
                r['_id'] = str(r['_id'])
                result.append(r)
        return result

    def search(self,searchText):
        result = []
        req = self.collection.find({'$text': {'$search': searchText}})
        if req.count() > 0:
            for r in req:
                r['_id'] = str(r['_id'])
                result.append(r)
        return result

    def save(self,policyInfo):
        self.collection.update_one({"policy.policyNumber":policyInfo['policy']['policyNumber']},{"$set":policyInfo},upsert=True)
        return policyInfo

