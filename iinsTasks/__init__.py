import os

from celery import Celery
from importlib import import_module
from iinsREST.iinsServer import admin

# Update configuration
configuration = admin.controller.ConfigurationService().getConfiguration()
configuration['celeryConfig']['security_key'] = os.urandom(24)

capp = Celery(__name__)
capp.conf.update(configuration["celeryConfig"])


DATABASE_DOMAIN =configuration['database']['domain'] if configuration['database']['domain'] !=None else 'localhost'
DATABASE_PORT =configuration['database']['port'] if configuration['database']['port'] !=None else 27017


@capp.on_after_configure.connect
def initialization(sender, **kwargs):
    tasksModule = import_module("iinsTasks.processing")
    getattr(tasksModule,"initializationTasks").delay()
