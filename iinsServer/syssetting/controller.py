from . import models
from flask import json, request
from datetime import datetime


class SettingService():
    def __init__(self):
        self.model = models

    def get_setting(self):
        if request.method == 'POST':
            data = json.loads(request.data)
            results=[]
            if data['key'] == 'all':
                results = self.model.SettingModel().get_all()
            return json.dumps(results)

    def get_version(self):
        if request.method == 'GET':
            results = self.model.SettingModel().get_version()['version']
            return json.dumps(results)