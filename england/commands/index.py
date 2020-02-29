import argparse
import sys
from barbados.factories import CocktailFactory
import england.util
from barbados.indexes import RecipeIndex


class Index:
    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        raw_recipe = england.util.read_yaml_file(args.recipepath)[0]
        slug = england.util.get_slug_from_path(args.recipepath)

        c = CocktailFactory.raw_to_obj(raw_recipe, slug)
        print("Working %s" % args.recipepath)

        index = CocktailFactory.obj_to_index(c, RecipeIndex)
        index.save()


    @staticmethod
    def _setup_args():
        parser = argparse.ArgumentParser(description='Index a cocktail object',
                                         usage='amari index <recipepath>')
        parser.add_argument('recipepath', help='name of yaml file to create')

        return parser.parse_args(sys.argv[2:])

    @staticmethod
    def _validate_args(args):
        pass
