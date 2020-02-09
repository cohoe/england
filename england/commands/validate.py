import argparse
import sys
from barbados.models import IngredientModel
from barbados.connectors import PostgresqlConnector
from barbados.exceptions import ValidationException
import logging

logging.basicConfig(level=logging.WARN)


class Validate:
    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        pgconn = PostgresqlConnector(database='amari', username='postgres', password='s3krAt')

        elements = IngredientModel.query.all()

        for element in elements:
            logging.info("Testing slug %s" % element.slug)
            try:
                element.validate()
            except ValidationException as e:
                logging.error(e)


    @staticmethod
    def _setup_args():
        parser = argparse.ArgumentParser(description='Validate something',
                                         usage='amari validate')

        return parser.parse_args(sys.argv[2:])

    @staticmethod
    def _validate_args(args):
        pass
