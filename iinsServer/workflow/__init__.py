from flask import Blueprint
from . import controller

blueprint = Blueprint(__name__, __name__, url_prefix='/rest/workflow')


blueprint.add_url_rule('/getworkflowtemp', view_func=controller.WorkflowService().getWorkflow)
