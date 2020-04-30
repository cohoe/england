import argparse
import sys
from barbados.connectors import UpneatConnector
from barbados.services import Registry
from barbados.models import CocktailModel
from barbados.serializers import ObjectSerializer
from barbados.caches import CocktailScanCache
from barbados.indexers import indexer_factory
from pprint import pprint
import ruamel.yaml


class Scrape:
    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        pgconn = Registry.get_database_connection()
        # c = UpneatConnector.scrape_recipe(args.source)
        #
        # with pgconn.get_session() as session:
        #     db_obj = CocktailModel(**ObjectSerializer.serialize(c, 'dict'))
        #     session.add(db_obj)
        #
        objects = UpneatConnector.get_recipes()
        # with pgconn.get_session() as session:
        #     for c in objects:
        #         db_obj = CocktailModel(**ObjectSerializer.serialize(c, 'dict'))
        #         session.add(db_obj)
        #         indexer_factory.get_indexer(c).index(c)
        #
        # CocktailScanCache.invalidate()
        # for c in objects:
        #     print(ruamel.yaml.round_trip_dump(ObjectSerializer.serialize(c, 'dict'), indent=2, block_seq_indent=3))
        #     return


    @staticmethod
    def _setup_args():
        parser = argparse.ArgumentParser(description='Scrape something',
                                         usage='amari scrape <source>')
        parser.add_argument('source', help='source')

        return parser.parse_args(sys.argv[2:])

    @staticmethod
    def _validate_args(args):
        pass
