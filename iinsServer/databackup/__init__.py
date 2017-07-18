from flask import Blueprint
from .controller import *

# print(__name__)
blueprint = Blueprint(__name__, __name__, url_prefix='/mnm/databackup')

blueprint.add_url_rule('/getbackups', view_func=controller.DatabackupService().get_backups,
                       methods=['GET', 'POST'])
blueprint.add_url_rule('/deletebackup', view_func=controller.DatabackupService().backup_delete,
                       methods=['GET', 'POST'])
blueprint.add_url_rule('/startbackup', view_func=controller.DatabackupService().backup_start,
                       methods=['GET', 'POST'])
blueprint.add_url_rule('/downloadbackup', view_func=controller.DatabackupService().backup_download,
                       methods=['GET', 'POST'])
blueprint.add_url_rule('/restore', view_func=controller.DatabackupService().backup_restore,
                       methods=['GET', 'POST'])
blueprint.add_url_rule('/periodicbackup', view_func=controller.DatabackupService().set_periodic_task,
                       methods=['GET', 'POST'])
blueprint.add_url_rule('/updateperiodictask', view_func=controller.DatabackupService().update_periodic_task,
                       methods=['GET', 'POST'])
blueprint.add_url_rule('/deleteperiodictask', view_func=controller.DatabackupService().delete_periodic_task,
                       methods=['GET', 'POST'])