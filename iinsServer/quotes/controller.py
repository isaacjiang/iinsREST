from . import models
from flask import json, request



class QuotesService():
    def __init__(self):
        self.model = models

    def get_list(self):
        print(request.args)
        results = self.model.QuotesModel().get_list()
        return json.dumps(results)

    def save(self):
        policyInfo = json.loads(request.data)
        results = self.model.QuotesModel().save(policyInfo)
        return json.dumps(results)