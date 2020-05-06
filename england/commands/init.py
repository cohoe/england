import argparse
import sys
import os
import requests
from barbados.connectors import PostgresqlConnector
from barbados.services import Registry
from barbados.indexes import index_factory
from barbados.services.logging import Log


class Init:
    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        try:
            # This syntax guarantees KeyError
            db_username = os.environ['DATABASE_USERNAME']
            db_password = os.environ['DATABASE_PASSWORD']
            db_database = os.environ['DATABASE_NAME']
        except KeyError as e:
            print("Environment variable missing: %s" % e)
            exit(1)

        conn = PostgresqlConnector(username=db_username, password=db_password, database=db_database)
        conn.drop_all()
        conn.create_all()

        Registry.set('/database/postgres/hostname', '127.0.0.1')
        Registry.set('/database/postgres/port', '5432')
        Registry.set('/database/postgres/username', db_username)
        Registry.set('/database/postgres/password', db_password)
        Registry.set('/database/postgres/database', db_database)

        index_factory.init()
        self._kibana_settings()
        # Sadly I cannot create index patterns easily via API. Requires a
        # string-ified JSON blob of all fields which I am not prepared to
        # build at this time.

    @staticmethod
    def _kibana_settings():
        headers = {
            'kbn-version': '7.5.0',
            'Content-Type': 'application/json'
        }
        data = '{"changes":{"theme:darkMode":true}}'

        resp = requests.post('http://localhost:5601/api/kibana/settings', headers=headers, data=data)
        if resp.status_code == 200:
            Log.info("Kibana set to dark mode.")

    @staticmethod
    def _setup_args():
        parser = argparse.ArgumentParser(description='Bootstrap the database and application config',
                                         usage='amari init')

        return parser.parse_args(sys.argv[2:])

    @staticmethod
    def _validate_args(args):
        pass
