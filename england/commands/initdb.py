import argparse
import sys
from barbados.connectors import PostgresqlConnector
from barbados.services import AppConfig
from barbados.indexes import index_factory


class Initdb:
    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        conn = PostgresqlConnector(username='postgres', password='s3krAt', database='amari')
        conn.create_all()

        AppConfig.set('/jamaica/api/v1/cocktail_name_list_key', 'cocktail_name_index')
        AppConfig.set('/jamaica/api/v1/ingredient_name_list_key', 'ingredient_name_index')

        index_factory.init()

    @staticmethod
    def _setup_args():
        parser = argparse.ArgumentParser(description='Bootstrap the database',
                                         usage='amari initdb')

        return parser.parse_args(sys.argv[2:])

    @staticmethod
    def _validate_args(args):
        pass
