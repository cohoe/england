import argparse
import sys
from barbados.factories import CocktailFactory, IngredientFactory
import england.util
from barbados.indexers import RecipeIndexer
from barbados.caches import IngredientTreeCache
from barbados.models.ingredientmodel import IngredientModel
from barbados.services import Registry
from barbados.indexers.ingredientindexer import IngredientIndexer


class Index:
    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        pgconn = Registry.get_database_connection()

        if args.kind == 'recipe':
            raw_recipe = england.util.read_yaml_file(args.sourcepath)[0]
            slug = england.util.get_slug_from_path(args.sourcepath)

            c = CocktailFactory.raw_to_obj(raw_recipe, slug)
            print("Working %s" % args.sourcepath)
            RecipeIndexer.index(c)
        elif args.kind == 'ingredients':
            tree = IngredientTreeCache.retrieve()
            for node in tree.nodes():
                m = IngredientModel.get_by_slug(node.tag)
                i = IngredientFactory.to_obj(m)
                IngredientIndexer.index(i)
                # return


    @staticmethod
    def _setup_args():
        parser = argparse.ArgumentParser(description='Index something into ElasticSearch',
                                         usage='amari index [kind] [sourcepath]')
        parser.add_argument('kind', help='kind of thing to index')
        parser.add_argument('sourcepath', help='name of yaml file to create')

        return parser.parse_args(sys.argv[2:])

    @staticmethod
    def _validate_args(args):
        pass
