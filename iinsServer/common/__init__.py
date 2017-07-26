from flask import Blueprint
from .controller import DataInitialization

# print(__name__)
blueprint = Blueprint(__name__, __name__, url_prefix='/rest/common')
#
# blueprint.add_url_rule('/getbackups', view_func=controller.DatabackupService().get_backups,
#                        methods=['GET', 'POST'])
