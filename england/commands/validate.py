import argparse
import sys
from barbados.connectors import ElasticsearchConnector
from barbados.factories import CocktailFactory
from barbados.constants import IngredientTypes
import england.util
import logging

logging.basicConfig(level=logging.ERROR)


class Validate:
    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        print(args.path)

        elements = self._load_yaml_data(path=args.path)
        cache = self._build_cache(elements)

        for element in elements:
            logging.info("Testing slug %s" % element['slug'])
            self._validate_element(element, elements, cache)

    def _validate_element(self, element, elements, cache):
        element = self._normalize_element(element)
        self._check_parent(element, cache)
        self._check_type(element)

    @staticmethod
    def _check_type(element):
        try:
            IngredientTypes(element['type'])
        except ValueError:
            logging.error("Element %s has bad type: %s" % (element['slug'], element['type']))

    @staticmethod
    def _normalize_element(element):
        required_keys = ['slug', 'parent', 'display_name', 'type']
        for key in required_keys:
            if key not in element.keys():
                logging.error("Element is missing key %s" % key)
                element[key] = None

        return element

    def _check_parent(self, element, cache):
        self._check_parent_existence(element, cache)

    @staticmethod
    def _check_parent_existence(element, cache):
        # Test if the parent exists at all
        try:
            parent = cache[element['parent']]
        except KeyError:
            if element['type'] != IngredientTypes.CATEGORY.value:
                logging.error("Parent of %s does not exist (%s)" % (element['slug'], element['parent']))

        # If the element is a category it should not have a parent
        if element['type'] == IngredientTypes.CATEGORY.value:
            if element['parent'] is not None:
                logging.error("Parent of category %s is not None (set to %s)" % (element['slug'], element['parent']))

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
