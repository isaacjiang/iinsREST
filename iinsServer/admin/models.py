from flask_login import UserMixin
from werkzeug.security import check_password_hash
from bson import ObjectId
from flask import json, g
from pymongo import MongoClient
import os
from datetime import datetime
from urllib.request import Request, urlopen



class Configuration:
    def __init__(self):
        self.db = MongoClient('localhost', 27017).iins_sys

    def http_request(self, url, params=None, proxy_host=None):
        if params == None:
            req = Request('http://' + url)
        else:
            params = str(params).encode()
            req = Request('http://' + url, params)
        req.add_header('Content-Type', 'application/json')
        req.add_header('User-Agent',
                       'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36')
        if proxy_host != None:
            req.set_proxy(proxy_host, 'http')
        response = urlopen(req).read().decode('utf8')
        return response

    # def initialization(self):
    #     if self.db.configuration.find({}).count() == 0:
    #         with open(os.path.join(os.getcwd(), 'configuration.json')) as data:
    #             params = json.load(data)
    #             data.close()
    #             self.db.configuration.update_one({'paramsName': params['paramsName']}, {"$set": params}, upsert=True)
    #     if self.db.users.find({'username': 'Admin'}).count() == 0:
    #         with open(os.path.join(os.getcwd(), 'accounts.json')) as data:
    #             params = json.load(data)
    #             data.close()
    #             self.db.users.update_one({'username': params['username']}, {"$set": params}, upsert=True)

    def getConfiguration(self):
        # self.initialization()
        server = self.db.configuration.find_one({}, {"_id": 0})
        return server



class UserModel(UserMixin):
    def __init__(self, id=None):
        self.uid = id
        self.db = getattr(g, 'database', MongoClient('localhost', 27017)).db_mss
        self.userInfo = self.get_id()

    def get_id(self):
        self.userInfo = self.db.users.find_one({"_id": ObjectId(self.uid)}, {"password": 0})
        return self.userInfo

    def get_all(self):
        userList = []
        allUsers = self.db.users.find()
        for user in allUsers:
            user['_id'] = str(user['_id'])
            userList.append(user)
        return userList

    def _get_username(self, username=None):
        userInfo = self.db.users.find_one({"username": username})
        if userInfo:
            userInfo['_id'] = str(userInfo['_id'])
        return userInfo

    def _set(self, **kwargs):
        self.db.users.update_one({"_id": ObjectId(self.uid)}, {"$set": kwargs}, upsert=True)

    def _del(self):
        self.db.users.delete_one({"_id": ObjectId(self.uid)})



    def _get_eLicense(self):
        sn = self.db.configurations.find_one({'paramsName': 'NVRT_HTTP_SERVER'},
                                             {"eLicense": 1, "entityID": 1, "_id": 0})
        return sn

    def checkLicenses(self, uid, uLicense, eLicense):
        authorizationCheckLevel = getattr(g, "parameters", "")['authorizationCheckLevel']
        if authorizationCheckLevel == 'PCRS':
            result = self._check_licenses_on_server(uid, uLicense, eLicense)
        else:
            result = self._check_licenses_local(uid, uLicense)
        return result

    def _check_licenses_local(self, uid, uLicense):
        result = False
        user = self.db.users.find_one({"_id": ObjectId(uid)}, {"authorization": 1, "entityID": 1, "_id": 0})
        if user:
            uLicense1 = json.dumps(user['authorization'])
            result = check_password_hash('pbkdf2:sha256:50000$' + uLicense, uLicense1)
        return result

