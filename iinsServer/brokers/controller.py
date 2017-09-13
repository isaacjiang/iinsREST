from . import models
from flask import json, request



class PolicyService():
    def __init__(self):
        self.model = models

    def get_policy_list(self):
        print(request.args)
        results = self.model.PolicyModel().get_policy_list()
        return json.dumps(results)

    def save_policy(self):
        policyInfo = json.loads(request.data)
        results = self.model.PolicyModel().save_policy(policyInfo)
        return json.dumps(results)