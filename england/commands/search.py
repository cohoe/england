import argparse
import sys
import logging
from barbados.indexes import RecipeIndex


class Search:
    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        # https://github.com/elastic/elasticsearch-dsl-py/issues/126
        results = RecipeIndex.search()[0:1000].query("match_phrase", specs__ingredients__name="rum").sort('_score').execute()
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
