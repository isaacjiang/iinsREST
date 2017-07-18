from flask import Blueprint
from . import controller

# print (__name__)
blueprint = Blueprint(__name__, __name__, url_prefix='/mnm/syssetting')

blueprint.add_url_rule('/getsetting', view_func=controller.SettingService().get_setting,
                       methods=['GET', 'POST'])

blueprint.add_url_rule('/getversion', view_func=controller.SettingService().get_version,
                       methods=['GET', 'POST'])