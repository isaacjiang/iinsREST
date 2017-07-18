from flask import Blueprint
from . import controller

from .controller import MongoSessionInterface

blueprint = Blueprint(__name__, __name__, url_prefix='/mnm/sessions')
blueprint.add_url_rule('/sessions', methods=['GET', 'POST'], view_func=controller.SystemService().sessions)
