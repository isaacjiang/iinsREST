import os
from flask import json
from pymongo import MongoClient


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



