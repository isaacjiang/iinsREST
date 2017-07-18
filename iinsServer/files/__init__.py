from . import controller
from flask import Blueprint

# print (__name__)
blueprint = Blueprint(__name__, __name__, url_prefix='/rest/files')


# blueprint.add_url_rule('/getall', view_func=controller.FileService().get_all, methods=['GET', 'POST'])
blueprint.add_url_rule('/upload', view_func=controller.FileService().upload_file, methods=['GET', 'POST'])
# blueprint.add_url_rule('/createfolder', view_func=controller.FileService().createFolder, methods=['GET', 'POST'])
blueprint.add_url_rule('/delete', view_func=controller.FileService().delete_file, methods=['GET', 'POST'])
blueprint.add_url_rule('/download', view_func=controller.FileService().download_file, methods=['GET', 'POST'])
# blueprint.add_url_rule('/paste', view_func=controller.FileService().paste_file, methods=['GET', 'POST'])

# blueprint.add_url_rule('/kmlupload', view_func=controller.FileService().kml_upload, methods=['GET', 'POST'])
