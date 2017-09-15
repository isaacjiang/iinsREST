from . import models
from flask import json, request



class CustomersService():
    def __init__(self):
        self.model = models

    def get_list(self):
        # print(request.args)
        results = self.model.CustomersModel().get_list()
        return json.dumps(results)

    def search(self):
        print(request.args)
        searchText = request.args['searchText']
        results = self.model.CustomersModel().search(searchText)
        return json.dumps(results)

    def save(self):
        policyInfo = json.loads(request.data)
        results = self.model.CustomersModel().save(policyInfo)
        return json.dumps(results)