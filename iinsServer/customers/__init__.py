from flask import Blueprint
from .controller import CustomersService

# print (__name__)
blueprint = Blueprint(__name__, __name__, url_prefix='/rest/customers')

blueprint.add_url_rule('/getlist', view_func=CustomersService().get_list)

blueprint.add_url_rule('/save', view_func=CustomersService().save, methods=['POST'])