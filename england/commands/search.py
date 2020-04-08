import argparse
import sys
import logging
from barbados.indexes import RecipeIndex


# from barbados.indexes import IngredientIndex


class Search:
    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        # query_params = {
        #     'name_or_query': 'match_phrase',
        #     'specs__components__parents': 'rum',
        #     'specs__components__slug': 'rum',
        #     'slug': 'rum',
        # }
        query_params = {
            'name_or_query': 'multi_match',
            'query': 'whiskey',
            # 'fields': ['specs__components__slug']
            'type': 'phrase_prefix',
            'fields': ['specs.components.slug', 'specs.components.display_name', 'specs.components.parents'],
        }

        query_params = {
            'name_or_query': 'bool',
            'must': [
                {
                    'multi_match': {
                        'query': 'rum',
                        'type': 'phrase_prefix',
                        'fields': ['specs.components.slug', 'specs.components.display_name', 'specs.components.parents'],
                    }
                },
                {
                    'multi_match': {
                        'query': 'sherry',
                        'type': 'phrase_prefix',
                        'fields': ['specs.components.slug', 'specs.components.display_name', 'specs.components.parents'],
                    }
                }
            ]
        }

        # https://github.com/elastic/elasticsearch-dsl-py/issues/126
        # results = RecipeIndex.search()[0:1000].query(**query_params).sort('_score').execute()
        results = RecipeIndex.search()[0:1000].query(**query_params).sort('_score').execute()
        # results = IngredientIndex.search()[0:1000].query(**query_params).sort('_score').execute()
        logging.info("Got %s results." % results.hits.total.value)
        for hit in results:
            logging.info("%s :: %s" % (hit.slug, hit.meta.score))

    @staticmethod
    def _setup_args():
        parser = argparse.ArgumentParser(description='search',
                                         usage='amari search')

        return parser.parse_args(sys.argv[2:])

    @staticmethod
    def _validate_args(args):
        pass
