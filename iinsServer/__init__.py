# blueprint
import os
from flask import Flask,g
from pymongo import MongoClient
from flask_login import LoginManager

from . import admin,files#,databackup,  initialization,  sessions,syslogging, syssetting, ipc, workflow

from .sessions import MongoSessionInterface

iinsapp = Flask(__name__)

iinsapp.register_blueprint(blueprint=admin.blueprint)
# iinsapp.register_blueprint(blueprint=workflow.blueprint)
iinsapp.register_blueprint(blueprint=files.blueprint)
# iinsapp.register_blueprint(blueprint=syssetting.blueprint)
# iinsapp.register_blueprint(blueprint=databackup.blueprint)
# iinsapp.register_blueprint(blueprint=syslogging.blueprint)
# iinsapp.register_blueprint(blueprint=sessions.blueprint)

# Update configuration

configuration = admin.controller.ConfigurationService().getConfiguration()
configuration['appConfig']['APPLICATION_ROOT'] = os.getcwd()
configuration['appConfig']['SECRET_KEY'] = os.urandom(24)
iinsapp.config.update(configuration["appConfig"])
DATABASE_DOMAIN =configuration['database']['domain'] if configuration['database']['domain'] !=None else 'localhost'
DATABASE_PORT =configuration['database']['port'] if configuration['database']['port'] !=None else 27017

# db = MongoClient(DATABASE_DOMAIN, DATABASE_PORT).db_mss
# user_login init
login_manager = LoginManager()
login_manager.init_app(iinsapp)

@login_manager.user_loader
def load_user(user):
    return admin.models.UserModel(user['_id'])
# session init
iinsapp.session_interface = MongoSessionInterface()

def instanceParams():
    g.parameters = configuration['parameters']
    g.database=  MongoClient(DATABASE_DOMAIN, DATABASE_PORT)

iinsapp.before_request(instanceParams)





