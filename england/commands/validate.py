import argparse
import sys
from barbados.connectors import ElasticsearchConnector
from barbados.factories import CocktailFactory
from barbados.constants import IngredientKinds
import england.util
import logging

logging.basicConfig(level=logging.WARN)


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

    def _check_parent(self, element, cache):
        self._check_parent_existence(element, cache)
        self._check_parent_kind(element, cache)

    @staticmethod
    def _check_parent_kind(element, cache):
        try:
            parent = cache[element['parent']]
        except KeyError:
            # logging.warning("Error with parent %s of %s (you probably already know)" % (element['parent'], element['slug']))
            return

        if element['kind'] == IngredientKinds.FAMILY.value:
            # Parents of Families can only be Categories
            allowed_parent_kinds = [IngredientKinds.CATEGORY.value]
            if parent['kind'] not in allowed_parent_kinds:
                logging.error("Parent (%s) of %s has invalid kind (%s)." % (parent['slug'], element['slug'], parent['kind']))
        elif element['kind'] == IngredientKinds.CATEGORY.value:
            if element['parent'] is not None:
                logging.error("Parent of category %s is not None (set to %s)" % (element['slug'], element['parent']))
        elif element['kind'] == IngredientKinds.INGREDIENT.value:
            allowed_parent_kinds = [IngredientKinds.INGREDIENT.value, IngredientKinds.FAMILY.value]
            if parent['kind'] not in allowed_parent_kinds:
                logging.error("Parent (%s) of %s has invalid kind (%s)." % (parent['slug'], element['slug'], parent['kind']))
        elif element['kind'] == IngredientKinds.PRODUCT.value:
            allowed_parent_kinds = [IngredientKinds.INGREDIENT.value, IngredientKinds.FAMILY.value]
            if parent['kind'] not in allowed_parent_kinds:
                logging.error("Parent (%s) of %s has invalid kind (%s)." % (parent['slug'], element['slug'], parent['kind']))
        elif element['kind'] == IngredientKinds.CUSTOM.value:
            allowed_parent_kinds = [IngredientKinds.INGREDIENT.value, IngredientKinds.PRODUCT.value]
            if parent['kind'] not in allowed_parent_kinds:
                logging.error("Parent (%s) of %s has invalid kind (%s)." % (parent['slug'], element['slug'], parent['kind']))

    @staticmethod
    def _check_parent_existence(element, cache):
        # Test if the parent exists at all
        try:
            parent = cache[element['parent']]
        except KeyError:
            if element['kind'] != IngredientKinds.CATEGORY.value:
                logging.error("Parent of %s does not exist (%s)" % (element['slug'], element['parent']))

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
