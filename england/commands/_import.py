import argparse
import sys
import england.util
from barbados.models import CocktailModel, IngredientModel
from barbados.factories import CocktailFactory
from barbados.connectors import PostgresqlConnector
from barbados.objects import Ingredient
from barbados.constants import IngredientTypes


class Import:
    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        pgconn = PostgresqlConnector(database='amari', username='postgres', password='s3krAt')

        if args.object == 'recipe':
            self._import_recipe(args.filepath)
        elif args.object == 'recipes':
            recipe_dir = args.filepath
            for filename in england.util.list_files(recipe_dir):
                self._import_recipe("%s/%s" % (recipe_dir, filename))
        elif args.object == 'ingredients':
            data = england.util.read_yaml_file(args.filepath)

            # Drop the data and reload
            print("deleting old data")
            deleted = IngredientModel.query.delete()
            print(deleted)

            print("starting import")
            for ingredient in data:
                i = Ingredient(**ingredient)
                db_obj = IngredientModel(**i.serialize())

                # Test for existing
                existing = IngredientModel.query.get(i.slug)
                if existing:
                    if existing.type == IngredientTypes.CATEGORY.value or existing.type == IngredientTypes.FAMILY.value:
                        if i.type_ is IngredientTypes.INGREDIENT:
                            print("Skipping %s (t:%s) since a broader entry exists (%s)" % (i.slug, i.type_.value, existing.type))
                        else:
                            print("%s (p:%s) already exists as a %s (p:%s)" % (i.slug, i.parent, existing.type, existing.parent))
                    else:
                        print("%s (p:%s) already exists as a %s (p:%s)" % (i.slug, i.parent, existing.type, existing.parent))
                else:
                    db_obj.save()

            # Validate
            pgconn.commit()
            print("starting validation")
            ingredients = IngredientModel.query.all()
            for ingredient in ingredients:
                # find parent
                if not ingredient.parent:
                    continue
                parent = IngredientModel.query.get(ingredient.parent)
                if not parent:
                    print("Could not find parent %s for %s" % (ingredient.parent, ingredient.slug))
                    continue
                if parent.type == IngredientTypes.ALIAS.value:
                    print("%s cannot be a child of an alias (%s)." % (ingredient.slug, parent.slug))
                    continue
                if parent.type == IngredientTypes.PRODUCT.value:
                    if ingredient.type != IngredientTypes.PRODUCT.value:
                        print("%s cannot be a child of a product (%s)." % (ingredient.slug, parent.slug))
                        continue
        else:
            exit(1)

        IngredientModel.get_usable_ingredients()

    @staticmethod
    def _setup_args():
        parser = argparse.ArgumentParser(description='Import something to the database',
                                         usage='amari import <object> <recipepath>')
        parser.add_argument('object', help='object to import', choices=['recipe', 'recipes', 'ingredients'])
        parser.add_argument('filepath', help='path to the yaml file (or directory) containing the objects')

        return parser.parse_args(sys.argv[2:])

    @staticmethod
    def _validate_args(args):
        pass

    @staticmethod
    def _import_recipe(filepath):
        data = england.util.read_yaml_file(filepath)[0]
        slug = england.util.get_slug_from_path(filepath)
        c = CocktailFactory.raw_to_obj(data, slug)
        print("Working %s" % filepath)

        # Drop the data and reload
        print("deleting old data")
        # Test for existing
        existing = CocktailModel.query.get(c.slug)
        if existing:
            existing.delete()

        db_obj = CocktailModel(**c.serialize())
        # db_conn.save(db_obj)
        db_obj.save()
        print("created new")
