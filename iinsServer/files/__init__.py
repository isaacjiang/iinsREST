from . import controller
from flask import Blueprint

# print (__name__)
blueprint = Blueprint(__name__, __name__, url_prefix='/rest/files')
blueprint.add_url_rule('/upload', view_func=controller.FileService().upload_documents, methods=['POST'])
blueprint.add_url_rule('/download', view_func=controller.FileService().download_documents)

