import argparse
import sys
from barbados.connectors import PostgresqlConnector
from barbados.services import Registry
from barbados.indexes import index_factory


class Init:
    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        db_username = 'postgres'
        db_password = 's3krAt'
        db_database = 'amari'

        conn = PostgresqlConnector(username=db_username, password=db_password, database=db_database)
        conn.create_all()

        Registry.set('/jamaica/api/v1/cocktail_name_list_key', 'cocktail_name_index')
        Registry.set('/jamaica/api/v1/ingredient_name_list_key', 'ingredient_name_index')
        Registry.set('/database/postgres/hostname', '127.0.0.1')
        Registry.set('/database/postgres/port', '5432')
        Registry.set('/database/postgres/username', db_username)
        Registry.set('/database/postgres/password', db_password)
        Registry.set('/database/postgres/database', db_database)

        index_factory.init()

    @staticmethod
    def _setup_args():
        parser = argparse.ArgumentParser(description='Bootstrap the database and application config',
                                         usage='amari init')

        return parser.parse_args(sys.argv[2:])

    @staticmethod
    def _validate_args(args):
        pass
