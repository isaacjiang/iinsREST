from flask import Blueprint
from . import controller

blueprint = Blueprint(__name__, __name__, url_prefix='/mnm/workflow')
##System Data Service
blueprint.add_url_rule('/queryworkflow', methods=['POST','GET'], view_func=controller.WorkflowService().queryWorkflow)
blueprint.add_url_rule('/clearworkflow', methods=['POST','GET'],
                       view_func=controller.WorkflowService().clearworkflow)
blueprint.add_url_rule('/launchworkflow', methods=['POST','GET'],
                       view_func=controller.WorkflowService().launchWorkflow)

blueprint.add_url_rule('/getworkflow', methods=['GET','POST'],
                       view_func=controller.WorkflowService().get_workflow)