import argparse
import sys
import pprint
from barbados.connectors.sqlite import SqliteConnector
from barbados.models.mixologytech import IngredientModel, RecipeFactoidModel, RecipeModel, RecipeKeywordModel


class Extract:
    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        dbconn = SqliteConnector(path=args.database)

        # print(len(IngredientModel.query.all()))
        # for ingredient in IngredientModel.query.all():
        #     print(ingredient.canonical_name)
        # for altname in IngredientAlternateSpellingModel.query.all():
        #     print(altname.ingredient_id)
        recipe = RecipeModel.query.filter(RecipeModel.title == 'Framboise Fizz')[0]

        dependency_ids = [dep[0] for dep in recipe.ingredient_dependencies_json]

        dependencies = [IngredientModel.query.filter(IngredientModel.remote_id == dep_id)[0] for dep_id in dependency_ids]
        print(recipe.title)
        print([dep.canonical_name for dep in dependencies])

        raw_keywords = RecipeFactoidModel.query.filter(RecipeFactoidModel.fok_recipe == 8192, RecipeFactoidModel.recipe_id == recipe.id)[0].content
        raw_keywords = raw_keywords.split(', ')
        keywords = [RecipeKeywordModel.query.filter(RecipeKeywordModel.remote_id == keyword)[0].shortname for keyword in raw_keywords]
        print(keywords)

        pprint.pprint(recipe.detail_json)

    # def run(self):
    #     args = self._setup_args()
    #     self._validate_args(args)
    #
    #     d = Database(args.database)
    #
    #     # raw_ingredient = d.get_rows('ZINGREDIENT', 'Z_PK', 83)[0]
    #     raw_ingredient = d.get_rows('ZINGREDIENT', 'ZCANONICALNAME', 'grape brandy')[0]
    #
    #     category_mappings = d.get_rows('Z_1CATEGORIES', 'Z_1INGREDIENTS1', raw_ingredient['Z_PK'])
    #     # print(category_mappings)
    #
    #     raw_categories = []
    #     for mapping in category_mappings:
    #         category_pk = mapping['Z_3CATEGORIES']
    #         raw_category = d.get_rows('ZINGREDIENTCATEGORY', 'Z_PK', category_pk)[0]
    #         if raw_category['ZDISPLAYNAME'] is not None:
    #             raw_categories.append(raw_category)
    #     # results = d.get_rows('Z_1CATEGORIES', 'Z_1INGREDIENTS1', raw_ingredient['Z_PK'])
    #
    #     raw_synonyms = d.get_rows('ZINGREDIENTSYNONYM', 'ZINGREDIENT', raw_ingredient['Z_PK'])
    #     raw_altnames = d.get_rows('ZINGREDIENTALTERNATESPELLING', 'ZINGREDIENT', raw_ingredient['Z_PK'])
    #
    #     details = self._parse_detail_json(raw_ingredient['ZDETAILJSON'])
    #
    #     template = england.util.load_template_from_file('./templates/ingredient.j2.yaml')
    #
    #     content = template.render(ingredient=raw_ingredient, synonyms=raw_synonyms, altnames=raw_altnames, details=details, categories=raw_categories)
    #     print(content)
    #
    #
    #     # print(raw_altnames)
    #     # print(raw_synonyms)
    #     # print(raw_categories)
    #     # print(raw_ingredient)

    # @staticmethod
    # def _parse_detail_json(detail_json):
    #     raw_details = json.loads(detail_json)
    #
    #     details = {
    #         'images': [],
    #         'description': None,
    #         'citations': [],
    #         'origin': None,
    #         'abv': None,
    #         'substitute': None,
    #         'avg_price_retail_us': None
    #     }
    #
    #     for raw_detail in raw_details:
    #         if raw_detail['kind'] == 'art':
    #             for i in range(0,len(raw_detail['images'])):
    #                 image = {
    #                     'path': raw_detail['images'][i],
    #                     'dims': raw_detail['dims'][i]
    #                 }
    #                 details['images'].append(image)
    #         elif raw_detail['kind'] == 'ingDesc':
    #             details['description'] = raw_detail['text']
    #         elif raw_detail['kind'] == 'citation':
    #             details['citations'].append({
    #                 'text': raw_detail['text']
    #             })
    #         elif raw_detail['kind'] == 'tabular':
    #             for row in raw_detail['rows']:
    #                 if 'origin' in row[0].lower():
    #                     details['origin'] = row[1]
    #                 elif 'abv' in row[0].lower():
    #                     details['abv'] = row[1]
    #                 elif 'substitute' in row[0].lower():
    #                     details['substitute'] = row[1]
    #                 elif 'avg' in row[0].lower():
    #                     details['avg_price_retail_us'] = row[1]
    #         else:
    #             print(raw_detail)
    #
    #     return details

    @staticmethod
    def _setup_args():
        parser = argparse.ArgumentParser(description='Convert an object from MixologyTech Database.',
                                         usage='amari extract [options]')
        parser.add_argument('database', help='path to sqlite database')

        return parser.parse_args(sys.argv[2:])

    @staticmethod
    def _validate_args(args):
        pass
