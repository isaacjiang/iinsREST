import os
from flask import json,g
from pymongo import MongoClient
from bson import ObjectId
APP_DATA=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'initData')
class InitDatabaeModel():
    def __init__(self, id=None):
        self._id=ObjectId(id)

    def fast_set_devices(self, **kwargs):
        MongoClient('localhost', 27017).db_mnm.devices.update_one({"_id": self._id}, {"$set": kwargs})

    def fast_set_ports(self, **kwargs):
        MongoClient('localhost', 27017).db_mnm.ports.update_one({"_id": self._id}, {"$set": kwargs})

    def fast_set_nodes(self, **kwargs):
        MongoClient('localhost', 27017).db_mnm.nodes.update_one({"_id": self._id}, {"$set": kwargs})

    def fast_set_routes(self, **kwargs):
        MongoClient('localhost', 27017).db_mnm.routes.update_one({"_id": self._id}, {"$set": kwargs})

    def initDB(self):
        db_mss = MongoClient('localhost', 27017).db_mss
        db_meta = MongoClient('localhost', 27017).db_meta
        db_mnm = MongoClient('localhost', 27017).db_mnm

        if db_meta.workflowTemp.find().count() == 0:
            with open(os.path.join(APP_DATA, 'workflow.json')) as data:
                workflow = json.load(data)
                data.close()
                db_meta.workflowTemp.drop()
                for w in workflow:
                    db_meta.workflowTemp.insert_one(w)

        if db_mnm.device_conf.find().count() == 0:
            with open(os.path.join(APP_DATA, 'device_conf.json')) as data:
                devicesTypes = json.load(data)
                data.close()
                db_mnm.device_conf.drop()
                temp=[]
                for devicesType in devicesTypes:
                    if devicesType['deviceGeneralName'] not in temp:
                        temp.append(devicesType['deviceGeneralName'])
                        db_mnm.device_conf.insert_one(devicesType)

        # if db_mss.users.find({"username":"admin"}).count() == 0:
        #     db_mss.users.insert_one({
        #             "username": "admin",
        #             "userLicense":"providiusDefaultLicense",
        #         })

        # if db_meta.configuration.find().count() == 0:
        #     db_meta.configuration.insert_one({
        #         "version": "0.0.1"
        #     })

        if db_meta.settings.find().count() == 0:
            with open(os.path.join(APP_DATA, 'systemsetting.json')) as data:
                settings = json.load(data)
                data.close()
                db_meta.settings.drop()
                for setting in settings:
                    db_meta.settings.insert_one(setting)

        if db_meta.shortwords.find().count() == 0:
            with open(os.path.join(APP_DATA, 'shortwords.json')) as data:
                words = json.load(data)
                data.close()
                db_meta.shortwords.drop()
                for word in words:
                    db_meta.shortwords.insert_one(word)

        if db_mnm.typeclass.find().count() == 0:
            with open(os.path.join(APP_DATA, 'typeClass.json')) as data:
                words = json.load(data)
                data.close()
                db_mnm.typeclass.drop()
                for word in words:
                    db_mnm.typeclass.insert_one(word)

        # if "companies" not in db_mnm.collection_names():
        #     db_mnm.create_collection("companies", size=1024000, max=3600)
        # if "groups" not in db_mnm.collection_names():
        #     db_mnm.create_collection("groups", size=1024000, max=3600)



