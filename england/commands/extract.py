import argparse
import sys
from barbados.connectors.mixologytech import MixologyTechConnector
# from barbados.connectors.sqlite import SqliteConnector
from barbados.models.mixologytech import IngredientModel, RecipeFactoidModel, RecipeModel, RecipeKeywordModel


class Extract:
    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        mc = MixologyTechConnector(database_path=args.database)

        mc.get_ingredients()




        # recipe = RecipeModel.query.filter(RecipeModel.title == 'Framboise Fizz')[0]
        #
        # dependency_ids = [dep[0] for dep in recipe.ingredient_dependencies_json]
        #
        # dependencies = [IngredientModel.query.filter(IngredientModel.remote_id == dep_id)[0] for dep_id in dependency_ids]
        # print(recipe.title)
        # print([dep.canonical_name for dep in dependencies])
        #
        # raw_keywords = RecipeFactoidModel.query.filter(RecipeFactoidModel.fok_recipe == 8192, RecipeFactoidModel.recipe_id == recipe.id)[0].content
        # raw_keywords = raw_keywords.split(', ')
        # keywords = [RecipeKeywordModel.query.filter(RecipeKeywordModel.remote_id == keyword)[0].shortname for keyword in raw_keywords]
        # print(keywords)
        #
        # pprint.pprint(recipe.detail_json)

    @staticmethod
    def _setup_args():
        parser = argparse.ArgumentParser(description='Convert an object from MixologyTech Database.',
                                         usage='amari extract [options]')
        parser.add_argument('database', help='path to sqlite database')

        return parser.parse_args(sys.argv[2:])

    @staticmethod
    def _validate_args(args):
        pass
