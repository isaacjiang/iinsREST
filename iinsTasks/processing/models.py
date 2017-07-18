from importlib import  import_module
from pymongo import MongoClient
from datetime import datetime
dbConnect =None

class TasksManagement:
    def __init__(self,taskName=None):
        self.taskName =taskName
        global dbConnect
        if dbConnect != None:
            self.db = dbConnect.db_mss
        else:
            try:
                from .. import DATABASE_DOMAIN,DATABASE_PORT
                dbConnect = MongoClient(DATABASE_DOMAIN, DATABASE_PORT, maxPoolSize=200, connect=False)
                self.db = dbConnect.db_mss
            except:
                print('Cannot connect Database.')

    def getTasks(self,queue=None):
        if queue == None:
            queueList = ['default','long_run']
        else:
            queueList =[queue]
        tasks = self.db.schedule.find({"status":'Up','queue':{'$in':queueList}})

        return list(tasks)

    def setTask(self,queue='default',params=None):
        if 'ip' not in params.keys():
            params["ip"] = "localhost"
        params['queue'] = queue
        params['module'] = self.taskName[0:self.taskName.rfind('.')]
        params['status'] ='Up'
        params["updateTime"]=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        taskName = self.taskName + '@'+params['ip']
        self.db.schedule.update_one({'taskName': taskName},{"$set": params}, upsert=True)

    def killTasks(self):
        tasks = self.getTasks()
        for task in tasks:
            if 'type' in task.keys() and task['type'] == 'Flex':
                self.stopTaskByName(task['taskName'])

    def stopTaskByIP(self,params=None):
        taskName = self.taskName + '@'+params['ip']
        self.db.schedule.update_one({'taskName': taskName},{"$set": {"status":'Down'}})

    def stopTaskByName(self,taskName):
        self.db.schedule.update_one({'taskName': taskName},{"$set": {"status":'Down'}})

    def stopAllTasks(self):
        tasks = self.getTasks()
        if len(tasks)>0:
            for task in tasks:
                self.db.schedule.update_one({'taskName': task['taskName']},{"$set": {"status":'Down'}})