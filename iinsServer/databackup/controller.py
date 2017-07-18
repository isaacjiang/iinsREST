from . import models
from flask import json, request
from datetime import datetime,timedelta


class DatabackupService():
    def __init__(self):
        self.model = models

    def get_backups(self):
        if request.method == 'POST':
            data = json.loads(request.data)
            results = []
            if data['key'] == 'all':
                results = self.model.DatabackModel().get_all()
            elif data['key'] == 'periodic':
                results = self.model.DatabackModel().get_periodic_tasks()
            return json.dumps(results)

    def backup_delete(self):
        if request.method == 'POST':
            data = json.loads(request.data)
            res = self.model.DatabackModel().delete(request.data)
            self.model.DatabackModel().LoggingModel(data['username'], "Backup",
                                                    "Delete Backup: " + data['backupName'], 'Backup', None, None,
                                                    []).save()
            return json.dumps(res)

    def backup_start(self):
        if request.method == 'POST':
            data = json.loads(request.data)
            result = self.model.DatabackModel().backup(username=data['username'])
            return json.dumps(result)

    def backup_download(self):
        if request.method == 'POST':
            data = json.loads(request.data)
            res = self.model.DatabackModel().download(data)
            return json.dumps(res)

    def backup_restore(self):
        if request.method == 'POST':
            data = json.loads(request.data)
            res = self.model.DatabackModel().restore(data)
            self.model.DatabackModel().LoggingModel(data['username'], "Backup",
                                                    "Restore Backup: " + data['backupName'], 'Backup',
                                                    None, None, []).save()
            return json.dumps(res)

    def set_periodic_task(self):
        if request.method == 'POST':
            data = json.loads(request.data)['data']
            results = []
            # result = self.model.DatabackModel().backup(username=data['username'])

            results = self.model.DatabackModel().set_periodic_taks(
                taskName="TasksScheduler.tasksNV.periodicBackup",
                params={
                    "duration": 0,
                    "username": data['username'],
                    "repeatType": data['repeat'],
                    "nextUpdateYear": data['startYear'],
                    "nextUpdateMonth": data['startMonth'],
                    "nextUpdateDay": data['startDay'],
                    "nextUpdateHour": data['startHour'],
                    "nextUpdateMinute": data['startMinute'],
                    "type":"long_run"
                },
                status="Up",
                source="NV"
            )
            return json.dumps(results)

    def update_periodic_task(self):
        if request.method == 'POST':
            data = json.loads(request.data)
            result = self.model.DatabackModel(data['_id']).fast_set_mss(status=data['status'])
            return json.dumps(result)

    def delete_periodic_task(self):
        if request.method == 'POST':
            data = json.loads(request.data)
            result = self.model.DatabackModel(data['_id']).delete_periodic_task()
            return json.dumps([])