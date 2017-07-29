from flask import json,g
from pymongo import MongoClient

class WorkFlowModel():
    def __init__(self, jobName=None,username=None):
        self.collection = getattr(g,'database',MongoClient('localhost', 27017)).iins_sys
        self.jobName = jobName
        self.taskList = list(self.collection.workflow.find({"jobName": jobName, "username": username}, {"_id": 0}))
        if len(self.taskList) == 0:
            self.taskList = list(self.collection.workflow_temp.find({"jobName": jobName}, {"_id": 0}))
            for task in self.taskList:
                if username != None:
                    task['username'] = username
                    self.collection.workflow.update_one(
                        {"jobName": jobName, "username": username, "taskID": task['taskID']},
                        {"$set": task}, upsert=True)


    def getWorkflow(self):
        return self.taskList

    def set(self,taskID,func, **kwargs):
        workflows = self.collection.workflow.find({"processName": self.processName, "userName": self.userName}, {"_id": 0}).sort(
            "taskID", 1)
        for w in workflows:
            if w['taskID']==taskID:
                if func:
                    kwargs['status']='saved'
                self.collection.workflow.update_one({"processName": self.processName, "userName": self.userName, "taskID": w['taskID']}, {"$set": kwargs})
            else:
                if 'status' in kwargs:
                    del kwargs['status']
                self.collection.workflow.update_one({"processName": self.processName, "userName": self.userName, "taskID": w['taskID']}, {"$set": kwargs})

    def update_task(self, processName, userName, taskID, setValues):
        self.collection.workflow.update_one({"processName": processName, "userName": userName, "taskID": taskID},
                                            {"$set": setValues})

    def clear_user_all_task(self):
        workflows = []
        workflowTemp = self.collection.workflow.find({"processName": self.processName, "userName": self.userName}, {"_id": 0}).sort(
            "taskID", 1)
        if workflowTemp.count() == 0:
            self.__init__(self.processName, self.userName)
        for w in workflowTemp:
            workflows.append(w)
        for workflow in workflows:
            self.collection.workflow.delete_one(
                {"$and": [{"processName": workflow['processName']}, {"userName": workflow['userName']}]})
