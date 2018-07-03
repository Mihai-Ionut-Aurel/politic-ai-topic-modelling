import logging

import psycopg2


class PostgresManager:
    """docstring for Postgres"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)

            cls._instance.connect()

        return cls._instance

    def __init__(self):
        self.connection = self._instance.connection
        self.cursor = self._instance.cursor

    def select(self, query):
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()

        except Exception as error:
            logging.warning('error execting query "{}", error: {}'.format(query, error))
            return None
        else:
            return result

    def select_with_args(self, query, args):
        try:
            self.cursor.execute(query, args)
            result = self.cursor.fetchall()

        except Exception as error:
            logging.warning('error execting query "{}", error: {}'.format(query, error))
            return None
        else:
            return result

    def insert(self, query):
        try:
            result = self.cursor.execute(query)
        except Exception as error:
            logging.warning('error execting query "{}", error: {}'.format(query, error))
            return None
        else:
            return result

    def insert_with_args(self, query, values):
        try:
            result = self.cursor.execute(query, values)
        except Exception as error:
            logging.warning('error execting query "{}", error: {}'.format(query, error))
            return None
        else:
            return result

    def commit_changes(self):
        self.connection.commit()

    def __del__(self):
        self.connection.close()
        self.cursor.close()

    def connect(self):

        # normally the db_credenials would be fetched from a config file or the enviroment
        # meaning shouldn't be hardcoded as follow
        hostname = ""  # os.environ["DATABASE_IP"]
        port = 5432  # os.environ["DATABASE_PORT"]
        username = ""  # os.environ["DATABASE_USERNAME"]
        password = ""  # os.environ["DATABASE_PASSWORD"]
        database = ""  # os.environ["DATABASE_NAME"]
        db_config = {'dbname': database, 'host': hostname,
                     'password': password, 'port': port, 'user': username}

        try:
            print('connecting to PostgreSQL database...')
            connection = PostgresManager._instance.connection = psycopg2.connect(**db_config)
            cursor = PostgresManager._instance.cursor = connection.cursor()
            cursor.execute('SELECT VERSION()')

            db_version = cursor.fetchone()

        except Exception as error:
            logging.error('Error: connection not established {}'.format(error))
            PostgresManager._instance = None

        else:
            print('connection established\n{}'.format(db_version[0]))
