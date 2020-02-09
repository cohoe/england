import argparse
import sys
from barbados.connectors import ElasticsearchConnector
from barbados.factories import CocktailFactory
from barbados.constants import IngredientKinds
from barbados.models import IngredientModel
from barbados.connectors import PostgresqlConnector
from barbados.exceptions import ValidationException
import england.util
import logging

logging.basicConfig(level=logging.INFO)


class Validate:
    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        print(args.path)
        pgconn = PostgresqlConnector(database='amari', username='postgres', password='s3krAt')

        # elements = self._load_yaml_data(path=args.path)
        # cache = self._build_cache(elements)

        elements = IngredientModel.query.all()

        for element in elements:
            logging.info("Testing slug %s" % element.slug)
            try:
                element.validate()
            except ValidationException as e:
                logging.error(e)
            # except Exception as e:
            #     logging.error("HEY SOMETHING REALLY BAD! %s" % e)

    def _validate_element(self, element, elements, cache):
        element = self._normalize_element(element)
        # self._check_parent(element, cache)
        self._check_kind(element)

    @staticmethod
    def _check_kind(element):
        try:
            IngredientKinds(element['kind'])
        except ValueError:
            logging.error("Element %s has bad kind: %s" % (element['slug'], element['kind']))

    @staticmethod
    def _normalize_element(element):
        required_keys = ['slug', 'parent', 'display_name', 'kind']
        for key in required_keys:
            if key not in element.keys():
                logging.error("Element is missing key %s" % key)
                element[key] = None

        return element

    @staticmethod
    def _build_cache(elements):
        logging.debug('Building parent cache.')
        cache = {}
        for element in elements:
            cache[element['slug']] = element
        logging.info('Successfully built parent cache.')
        return cache

    @staticmethod
    def _load_yaml_data(path, extension='.yaml'):
        result_data = []
        files = england.util.find_all_files(path=path, extension=extension)
        for file in files:
            data = england.util.read_yaml_file(file)
            result_data += data

        return result_data

    @staticmethod
    def _setup_args():
        parser = argparse.ArgumentParser(description='Validate something',
                                         usage='amari validate <path>')
        parser.add_argument('path', help='path to some stuff')

        return parser.parse_args(sys.argv[2:])

    @staticmethod
    def _validate_args(args):
        pass
