import os
import psycopg2

class DbConnection():

    """ 
    Postgress connection manager 
    """

    def __init__(self):
        self.connection = None
    
    def init_app(self, db_name, db_host, db_user, db_password):
        try:
            self.connection = psycopg2.connect(user=db_user, password=db_password, host=db_host, database=db_name)
        except:
            print("I am unable to connect to the database")
            raise ValueError("unable to connect to database. set the environment variables")

    def get_cursor(self):
        if not self.connection:
            raise RuntimeError("attempt to get postgres connection on uninitialized connection")
        return self.connection.cursor()
    
    def commit(self):
        if not self.connection:
            raise RuntimeError("attempt to get postgres connection on uninitialized connection")
        return self.connection.commit()

def close_connections():
    if postgres_conn:
        postgres_conn.connection.close()

postgres_conn = DbConnection()

def validate_param(param_name):
    """
    Validating OS environment variables
    """

    if param_name not in os.environ:
        raise ValueError("missing environment variable " + param_name)
    return os.environ[param_name]