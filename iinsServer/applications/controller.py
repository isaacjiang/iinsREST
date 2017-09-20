from . import models
from flask import json, request
from ..customers import models as customersModel



class ApplicationService():
    def __init__(self):
        self.model = models

    def get_application_list(self):
        # print(request.args)
        results = self.model.ApplicationModel().get_application_list()
        return json.dumps(results)

    def save_application(self):
        application = json.loads(request.data)
        print(application)
        application['status'] = 'save'
        results = self.model.ApplicationModel().save_application(application)
        customersModel.CustomersModel().save(application['customer'])
        return json.dumps(results)

    def submit_application(self):
        application = json.loads(request.data)
        print(application)
        application['status'] = 'submit'
        results = self.model.ApplicationModel().submit_application(application)
        return json.dumps(results)