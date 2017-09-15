from .models import InitDatabaseModel,CommonModel
from flask import json, request

class DataInitialization:

    def initialization(self):
        InitDatabaseModel().initializeConfigurationDatabase()
        InitDatabaseModel().initializeCommonDatabase()


class CommonService:
    def __init__(self):
        self.model = CommonModel()

    def get_insurance_company(self):
        if request.args:
            params = request.args
            result = self.model.get_insurance_company(params['IC_ID'])
        else:
            result = self.model.get_insurance_company_list()
        return json.dumps(result)

    def get_provinces(self):
        result = self.model.get_provinces_list()
        return json.dumps(result)