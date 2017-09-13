from flask import Blueprint
from .controller import CommonService,DataInitialization

# print(__name__)
blueprint = Blueprint(__name__, __name__, url_prefix='/rest/common')
#
blueprint.add_url_rule('/insurancecompany', view_func=CommonService().get_insurance_company)
blueprint.add_url_rule('/provinces', view_func=CommonService().get_provinces)