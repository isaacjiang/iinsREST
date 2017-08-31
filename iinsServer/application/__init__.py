from flask import Blueprint
from .controller import PolicyService

# print (__name__)
blueprint = Blueprint(__name__, __name__, url_prefix='/rest/application')

blueprint.add_url_rule('/getlist', view_func=controller.PolicyService().get_application_list)

blueprint.add_url_rule('/save', view_func=PolicyService().save_application, methods=['POST'])