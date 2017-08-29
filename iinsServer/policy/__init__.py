from flask import Blueprint
from .controller import PolicyService

# print (__name__)
blueprint = Blueprint(__name__, __name__, url_prefix='/rest/policy')

blueprint.add_url_rule('/getlist', view_func=controller.PolicyService().get_policy_list)

blueprint.add_url_rule('/save', view_func=PolicyService().save_policy, methods=['POST'])