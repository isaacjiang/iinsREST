import os
from flask import json
from bson import ObjectId
from pymongo import MongoClient

class CommonModel:
    def __init__(self):
        self.db = MongoClient('localhost', 27017).iins_sys

    def get_insurance_company_list(self):
        result = list(self.db.insurance_companies.find())
        for res in result:
            res['_id'] =str(res['_id'])
        return result

    def get_insurance_company(self,id):
        result = self.db.insurance_companies.find_one({"_id":id})
        result['_id'] =str(result['_id'])
        return result

    def get_provinces_list(self):
        result = list(self.db.canada_provinces.find())
        for res in result:
            res['_id'] =str(res['_id'])
        return result

class InitDatabaseModel:

    db= MongoClient('localhost', 27017).iins_sys
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'json')

    def initializeConfigurationDatabase(self):
        if self.db.configuration.find({}).count() == 0:
            with open(os.path.join(self.path, 'configuration.json')) as data:
                params = json.load(data)
                data.close()
                self.db.configuration.update_one({'paramsName': params['paramsName']}, {"$set": params}, upsert=True)
        if self.db.users.find({'username': 'Admin'}).count() == 0:
            with open(os.path.join(self.path, 'accounts.json')) as data:
                params = json.load(data)
                data.close()
                self.db.users.update_one({'username': params['username']}, {"$set": params}, upsert=True)

    def initializeCommonDatabase(self):
        if self.db.workflow_temp.find({}).count() == 0:
            with open(os.path.join(self.path, 'workflow.json')) as data:
                params = json.load(data)
                data.close()
                for param in params:
                    self.db.workflow_temp.update_one({'jobID': param['jobID'],'taskID': param['taskID']}, {"$set": param}, upsert=True)

        if self.db.insurance_companies.find({}).count() == 0:
            with open(os.path.join(self.path, 'insurance_companies.json')) as data:
                params = json.load(data)
                data.close()
                for param in params:
                    self.db.insurance_companies.update_one({'_id': param['IC_ID']}, {"$set": param}, upsert=True)

        if self.db.canada_provinces.find({}).count() == 0:
            with open(os.path.join(self.path, 'canada_provinces.json')) as data:
                params = json.load(data)
                data.close()
                for param in params:
                    self.db.canada_provinces.update_one({"Abbr":param['Abbr']}, {"$set": param}, upsert=True)

