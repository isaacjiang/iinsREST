from flask import Blueprint
from .controller import ApplicationService

# print (__name__)
blueprint = Blueprint(__name__, __name__, url_prefix='/rest/application')

blueprint.add_url_rule('/getlist', view_func=ApplicationService().get_application_list)

blueprint.add_url_rule('/save', view_func=ApplicationService().save_application, methods=['POST'])
blueprint.add_url_rule('/submit', view_func=ApplicationService().submit_application, methods=['POST'])