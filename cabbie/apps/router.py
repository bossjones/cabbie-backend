from cabbie.apps.drive.models import Location as DriverLocation 

import pdb

class DriverLocationRouter(object):
    def db_for_read(self, model, **hints):
        if model == DriverLocation:
            return 'driver_location'
        return None

    def db_for_write(self, model, **hints):
        if model == DriverLocation:
            return 'driver_location'
        return None


    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        return False 

    def allow_migrate(self, db, model):
        """
        Make sure the auth app only appears in the 'auth_db'
        database.
        """
        if db == 'driver_location':
            return model == DriverLocation
        else:
            return model != DriverLocation
