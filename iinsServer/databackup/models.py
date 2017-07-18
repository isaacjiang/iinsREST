import importlib
from bson import ObjectId
from pymongo import DESCENDING,MongoClient
import subprocess
from flask import json
from datetime import datetime
from flask import g

class DatabackModel():
    def __init__(self, databackupId=None):
        self._id = ObjectId(databackupId)
        self.collection = getattr(g,'database',MongoClient('localhost', 27017)).db_meta.backup
        self.collection_mss = getattr(g,'database',MongoClient('localhost', 27017)).db_mss.schedulerNV
        self.sourcedb_host = "localhost"
        self.sourcedb_port = "27017"
        self.backupdb_host = "localhost"
        self.backupdb_port = "27017"
        self.backup_databse = ['db_mnm', 'db_file','db_mss']
        self.createDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.model_logging = importlib.import_module("NetvisServer.syslogging.models")
        self.LoggingModel = self.model_logging.Logging
        self.temp_folder = '/tmp/'
        self.download_folder = '/tmp/'

    def fast_set_mss(self, **kwargs):
        self.collection_mss.update_one({"_id": self._id}, {"$set": kwargs})

    def get_all(self):
        result = []
        req = self.collection.find({}).sort('backupDate', DESCENDING)
        if req.count() > 0:
            result = []
            for r in req:
                r['_id'] = str(r['_id'])
                result.append(r)
        return result

    def delete(self, data):
        data = json.loads(data)
        if len(data.keys()) > 0:
            if len(data['filenames']) > 0:
                for file in data['filenames']:
                    subprocess.check_call(
                        ['/usr/bin/mongofiles', "--host", data['backupHost'], "--port", data['backupPort'], "-d",
                         'dbbackup',
                         "delete", file])
                self.collection.delete_one({"backupDate": data['backupDate']})
        return self.get_all()

    def backup(self, **kwargs):
        # find: char, replace: char
        def filter_string(str, find, replace):
            s = ""
            for c in str:
                if (c == find):
                    s += replace
                else:
                    s += c
            return s

        subprocess.check_call(['/bin/mkdir', '-p', self.temp_folder + 'backup'])
        # subprocess.check_call(['sudo','chown', 'mvrt', 'backup'])
        filenames = []
        for db in self.backup_databse:
            subprocess.check_call(
                ['/usr/bin/mongodump', "--host", self.sourcedb_host, "--port", self.sourcedb_port, "-d", db,
                 "--archive=" + self.temp_folder + "backup/" + db + "_backup"])
            subprocess.check_call(
                ['/usr/bin/mongofiles', "--host", self.backupdb_host, "--port", self.backupdb_port, "-d",
                 "dbbackup",
                 "--local",
                 self.temp_folder + "backup/" + db + "_backup", "--replace", "put", db + "_backup_" + self.createDate])
            filenames.append(db + "_backup_" + self.createDate)
        self.collection.update_one({"backupDate": self.createDate}, {
            "$set": {"backupName": filter_string(filter_string(self.createDate, '-', ''), ' ', '-') + "-MVRT-BACKUP",
                     "database": self.backup_databse,
                     "filenames": filenames, "backupHost": self.backupdb_host, "backupPort": self.backupdb_port,
                     "username": kwargs['username']}}, upsert=True)
        return self.get_all()

    def download(self, data):
        if len(data.keys()) > 0:
            if len(data['filenames']) > 0:
                # subprocess.check_call(['/bin/mkdir', '-p', self.temp_folder + 'backup'])
                for file in data['filenames']:
                    subprocess.check_call(
                        ['/usr/bin/mongofiles', "--host", data['backupHost'], "--port", data['backupPort'],
                         "--local",
                         self.download_folder + file, "-d", 'dbbackup', "get", file])
        return self.get_all()

    def restore(self, data):
        if len(data.keys()) > 0:
            if len(data['filenames']) > 0:
                subprocess.check_call(['/bin/mkdir', '-p', self.temp_folder + 'backup'])
                for file in data['filenames']:
                    subprocess.check_call(
                        ['/usr/bin/mongofiles', "--host", data['backupHost'], "--port", data['backupPort'],
                         "--local",
                         self.temp_folder + "backup/" + file, "-d", 'dbbackup', "get", file])
                    ss = subprocess.check_call(
                        ['/usr/bin/mongorestore', "--host", self.sourcedb_host, "--port", self.sourcedb_port,
                         "--drop",
                         "--archive=" + self.temp_folder + "backup/" + file])
        return self.get_all()

    def set_periodic_taks(self, **kwargs):
        self.collection_mss.update_one({"_id": self._id}, {"$set": kwargs}, upsert=True)
        return str(self._id)

    def get_periodic_tasks(self):
        results = []
        req = self.collection_mss.find()
        for r in req:
            r['_id'] = str(r['_id'])
            r['tempTime'] = int(str(r['params']['nextUpdateYear']) + str(r['params']['nextUpdateMonth']) + str(
                r['params']['nextUpdateDay']) + str(r['params']['nextUpdateHour']) + str(
                r['params']['nextUpdateMinute']))
            results.append(r)
        results = sorted(results, key=lambda k: k['tempTime'])
        return results

    def delete_periodic_task(self):
        req = self.collection_mss.find_one_and_delete({'_id': self._id})
        return req
