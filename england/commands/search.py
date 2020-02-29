import argparse
import sys
from barbados.connectors import ElasticsearchConnector
from barbados.factories import CocktailFactory
import england.util
from barbados.serializers import ObjectSerializer
import logging


class Search:
    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        es = ElasticsearchConnector()

        # https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html
        query_body = {
            'query': {
                "bool": {
                    "must": [
                        {
                            "bool": {
                                "must": [
                                    {"match_phrase": {"specs.ingredients.name": "rum"}}
                                ],
                            }
                        },
                        {
                            "bool": {
                                "must": [
                                    {"match_phrase": {"specs.ingredients.name": "sherry"}}
                                ],
                            }
                        },
                        # {
                        #     "bool": {
                        #         "filter": [
                        #             {"match_phrase": {"specs.instructions": "stir"}}
                        #         ],
                        #     }
                        # }
                    ]
                }
            },
            'sort': [
                '_score'
            ]
        }

        results = es.search(index='recipe', body=query_body)
        count = results['hits']['total']['value']
        logging.info("Got %s results." % count)
        for hit in results['hits']['hits']:
            logging.info("%s :: %s" % (hit['_id'], hit['_score']))
            # print(hit['_id'] + " :: " + hit['_score'])
        # print(results)

    @staticmethod
    def _setup_args():
        parser = argparse.ArgumentParser(description='search',
                                         usage='amari search')
        # parser.add_argument('recipepath', help='name of yaml file to create')

        return parser.parse_args(sys.argv[2:])

    @staticmethod
    def _validate_args(args):
        pass
