from .models import InitDatabaseModel


class DataInitialization():

    def initialization(self):
        InitDatabaseModel().initializeConfigurationDatabase()
        InitDatabaseModel().initializeCommonDatabase()