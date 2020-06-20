import argparse
import sys
from barbados.connectors import UpneatConnector, MixologyTechConnector
from barbados.services.registry import Registry
from barbados.models import CocktailModel
from barbados.serializers import ObjectSerializer
from barbados.caches import CocktailScanCache
from barbados.indexers import indexer_factory
from pprint import pprint
import ruamel.yaml
from england.util import write_file


class Scrape:
    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        # objects = UpneatConnector.get_recipes()
        objects = MixologyTechConnector(database_path='/home/grant/Desktop/Data.sqlite').get_recipes()
        for c in objects:
            content = ruamel.yaml.round_trip_dump([ObjectSerializer.serialize(c, 'dict')])
            filename = "%s.yaml" % c.slug
            write_file(path="../tortuga/dump/pdtapp/%s" % filename, contents=content)


    @staticmethod
    def _setup_args():
        parser = argparse.ArgumentParser(description='Scrape something',
                                         usage='amari scrape <source>')
        parser.add_argument('source', help='source')

        return parser.parse_args(sys.argv[2:])

    @staticmethod
    def _validate_args(args):
        pass
