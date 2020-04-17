import argparse
import sys
import england.util
import os
import logging
from barbados.models import CocktailModel, IngredientModel
from barbados.factories import CocktailFactory
from barbados.connectors import PostgresqlConnector
from barbados.objects.ingredient import Ingredient
from barbados.objects.ingredientkinds import IngredientKinds
from barbados.text import Slug
from barbados.serializers import ObjectSerializer
from barbados.validators import ObjectValidator
from barbados.exceptions import ValidationException
from barbados.caches import IngredientTreeCache
from barbados.indexers import indexer_factory


class Importer:
    importers = {}

    @classmethod
    def register_importer(cls, importer_class):
        cls.importers[importer_class.kind] = importer_class

    @classmethod
    def get_importer(cls, kind):
        return cls.importers[kind]

    @classmethod
    def supported_importers(cls):
        return cls.importers.keys()


class BaseImporter:
    @staticmethod
    def import_(*args, **kwargs):
        raise NotImplementedError()

    @staticmethod
    def _fetch_data_from_path(filepath):
        if os.path.isfile(filepath):
            return england.util.read_yaml_file(filepath)
        else:
            return england.util.load_yaml_data_from_path(filepath)


class RecipeImporter(BaseImporter):
    kind = 'recipe'

    @staticmethod
    def import_(filepath):
        dicts_to_import = RecipeImporter._fetch_data_from_path(filepath)

        for cocktail_dict in dicts_to_import:
            try:
                slug = Slug(cocktail_dict['display_name'])
                logging.info("Working %s" % slug)
                c = CocktailFactory.raw_to_obj(cocktail_dict, slug)
            except KeyError as e:
                logging.error("Something has bad data!")
                logging.error(cocktail_dict)
                logging.error(e)
                continue

            RecipeImporter.delete(cocktail=c)

            db_obj = CocktailModel(**ObjectSerializer.serialize(c, 'dict'))
            db_obj.save()
            logging.info("Successfully [re]created %s" % c.slug)

            ObjectValidator.validate(db_obj, fatal=False)

            indexer_factory.get_indexer(c).index(c)

    @staticmethod
    def delete(cocktail=None, delete_all=False):

        if cocktail:
            existing = CocktailModel.query.get(cocktail.slug)

            if existing:
                logging.debug("Deleting %s" % existing.slug)
                deleted = CocktailModel.delete(existing)
                return

        if delete_all is True:
            logging.debug("Deleting all CocktailModel")
            deleted = CocktailModel.query.delete()
            logging.info("Deleted %s from %s" % (deleted, CocktailModel.__tablename__))


class IngredientImporter(BaseImporter):
    kind = 'ingredients'

    @staticmethod
    def import_(filepath):
        data = IngredientImporter._fetch_data_from_path(filepath)

        # Delete old data
        IngredientImporter.delete()

        logging.info("Starting import")
        for ingredient in data:
            i = Ingredient(**ingredient)
            db_obj = IngredientModel(**ObjectSerializer.serialize(i, 'dict'))

            # Test for existing
            existing = IngredientModel.query.get(i.slug)
            if existing:
                if existing.kind == IngredientKinds('category').value or existing.kind == IngredientKinds('family').value:
                    if i.kind is IngredientKinds('ingredient'):
                        logging.error("Skipping %s (t:%s) since a broader entry exists (%s)" % (i.slug, i.kind.value, existing.kind))
                    else:
                        logging.error("%s (p:%s) already exists as a %s (p:%s)" % (i.slug, i.parent, existing.kind, existing.parent))
                else:
                    logging.error("%s (p:%s) already exists as a %s (p:%s)" % (i.slug, i.parent, existing.kind, existing.parent))
            else:
                db_obj.save()

        # Validate
        IngredientImporter.validate()

        # Invalidate the cache
        logging.info("invalidating cache")
        IngredientTreeCache.invalidate()

    @staticmethod
    def delete():
        logging.debug("Deleting old data")
        deleted = IngredientModel.query.delete()
        logging.info("Deleted %s" % deleted)

    @staticmethod
    def validate():
        logging.info("starting validation")
        ingredients = IngredientModel.query.all()
        for ingredient in ingredients:
            try:
                ingredient.validate()
            except ValidationException as e:
                logging.error(e)


Importer.register_importer(RecipeImporter)
Importer.register_importer(IngredientImporter)


class Import:
    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        pgconn = PostgresqlConnector(database='amari', username='postgres', password='s3krAt')

        Importer.get_importer(args.object).import_(args.filepath)

        pgconn.commit()

    @staticmethod
    def _setup_args():
        parser = argparse.ArgumentParser(description='Import something to the database',
                                         usage='amari import <object> <recipepath>')
        parser.add_argument('object', help='object to import', choices=Importer.supported_importers())
        parser.add_argument('filepath', help='path to the yaml file (or directory) containing the objects')

        return parser.parse_args(sys.argv[2:])

    @staticmethod
    def _validate_args(args):
        pass
