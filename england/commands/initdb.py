import argparse
import sys
from barbados.connectors import PostgresqlConnector
from barbados.models.base import Base


class Initdb:
    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        conn = PostgresqlConnector()
        Base.metadata.create_all(conn.engine)

    @staticmethod
    def _setup_args():
        parser = argparse.ArgumentParser(description='Bootstrap the database',
                                         usage='amari initdb')

        return parser.parse_args(sys.argv[2:])

    @staticmethod
    def _validate_args(args):
        pass
