import argparse
import sys
import england.util
from barbados.factories import CocktailFactory
from slugify import slugify


class Migrate:
    def __init__(self):
        pass

    def run(self):

        args = self._setup_args()
        self._validate_args(args)

        c = CocktailFactory.obj_from_file(args.recipepath)
        print("Working %s" % args.recipepath)

        data = england.util.read_yaml_file(args.ingredientspath)
        # i = Ingredient(**ingredient)
        # db_obj = IngredientModel(**i.serialize())
        ingredients_db = {}
        for i in data:
            ingredients_db[i['slug']] = i

        for spec in c.specs:
            for ingredient in spec.ingredients:
                spec_ingredient_slug = slugify(ingredient.name)
                try:
                    found_ingredient = ingredients_db[spec_ingredient_slug]
                    print("Found %s" % spec_ingredient_slug)
                except KeyError:
                    print("Could not find %s" % spec_ingredient_slug)

    @staticmethod
    def _setup_args():
        parser = argparse.ArgumentParser(description='Migrate a recipe',
                                         usage='amari migrate -i <ingredientspath> <recipepath>')
        parser.add_argument('recipepath', help='path to recipe yaml')
        parser.add_argument('-i', dest='ingredientspath', help='path to ingredients yaml', required=True)

        return parser.parse_args(sys.argv[2:])

    @staticmethod
    def _validate_args(args):
        pass
