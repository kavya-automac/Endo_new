import socket
from dev_pro.models import Patientsdetails

class DatabaseRouter:
    @classmethod
    def is_internet_available(cls):
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

    @classmethod
    def db_for_read(cls, model=None, **hints):
        return 'default' if cls.is_internet_available() else 'fallback'
        # return ['default',Patientsdetails] if cls.is_internet_available() else ['fallback',Patientsdetails]


    @classmethod
    def db_for_write(cls, model=None, **hints):

        return 'default' if cls.is_internet_available() else 'fallback'
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db in ['default', 'fallback']

