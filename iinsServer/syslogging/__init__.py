from flask import Blueprint
from . import controller

# print (__name__)
blueprint = Blueprint(__name__, __name__, url_prefix='/mnm/syslogging')


blueprint.add_url_rule('/querytoday', view_func=controller.LoggingService().query_today, methods=['GET', 'POST'])
blueprint.add_url_rule('/queryperiod', view_func=controller.LoggingService().query_period, methods=['GET', 'POST'])
blueprint.add_url_rule('/exportlogs', methods=['GET','POST'], view_func=controller.LoggingService().export_logs)
blueprint.add_url_rule('/getchanges', methods=['GET','POST'], view_func=controller.LoggingService().getChanges)
blueprint.add_url_rule('/get', methods=['GET','POST'], view_func=controller.LoggingService().get)

blueprint.add_url_rule('/makemulticastlog', methods=['GET','POST'], view_func=controller.LoggingService().make_multicast_log)

