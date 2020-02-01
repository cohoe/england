import argparse
import sys
from barbados.objects import AppConfig


class Config:
    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        # zk = ZookeeperConnector()

        test_key_path = "/barbados/cache/redis/host"
        test_key_value = "127.0.0.1"

        try:
            print(AppConfig.get(test_key_path))
            print(AppConfig.get(test_key_path))
            print(AppConfig.get(test_key_path))
            print(AppConfig.get(test_key_path))
        except KeyError:
            print("KeyError")
        AppConfig.set(test_key_path, test_key_value)
        # print(zk.get(test_key_path))

        # AppConfig.set('/jamaica/api/v1/cocktail_name_list_key', 'cocktail_name_list')
        # AppConfig.set('/jamaica/api/v1/ingredient_name_list_key', 'ingredient_name_list')
        print(AppConfig.get('/jamaica/api/v1/cocktail_name_list_key'))
        print(AppConfig.get('/jamaica/api/v1/ingredient_name_list_key'))


    @staticmethod
    def _setup_args():
        parser = argparse.ArgumentParser(description='Manage configuration',
                                         usage='amari config <action> [key] [value]')
        parser.add_argument('action', help='action to perform', choices=['dump', 'get', 'set'])
        # parser.add_argument('key', default=None, help='configuration key')
        # parser.add_argument('value', default=None, help='configuration value')

        return parser.parse_args(sys.argv[2:])

    @staticmethod
    def _validate_args(args):
        pass
