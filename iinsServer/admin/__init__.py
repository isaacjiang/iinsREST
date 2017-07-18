from flask import Blueprint
from .controller import ConfigurationService,UserService

# print (__name__)
blueprint = Blueprint(__name__, __name__, url_prefix='/rest/admin')
blueprint.add_url_rule('/userstatus', view_func=UserService().getCurrentUser)
blueprint.add_url_rule('/register', view_func=UserService().register,methods=['POST'])
blueprint.add_url_rule('/login', view_func=UserService().login,methods=['POST'])
blueprint.add_url_rule('/logout', view_func=UserService().logout)
blueprint.add_url_rule('/deluser', view_func=UserService().delete,methods=['POST'])
blueprint.add_url_rule('/getusers', view_func=UserService().get_users,methods=['POST'])