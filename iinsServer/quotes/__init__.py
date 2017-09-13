from flask import Blueprint
from .controller import QuotesService

# print (__name__)
blueprint = Blueprint(__name__, __name__, url_prefix='/rest/quotes')

blueprint.add_url_rule('/getlist', view_func=QuotesService().get_list)

blueprint.add_url_rule('/save', view_func=QuotesService().save, methods=['POST'])