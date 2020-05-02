import argparse
import sys
import england.util
import os
import logging
from barbados.models import CocktailModel, IngredientModel
from barbados.factories import CocktailFactory
from barbados.services import Registry
from barbados.objects.ingredient import Ingredient
from barbados.objects.ingredientkinds import IngredientKinds
from barbados.text import Slug
from barbados.serializers import ObjectSerializer
from barbados.validators import ObjectValidator
from barbados.exceptions import ValidationException
from barbados.caches import IngredientTreeCache, CocktailScanCache
from barbados.indexers import indexer_factory
from barbados.indexes import index_factory, RecipeIndex, IngredientIndex


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

    pgconn = Registry.get_database_connection()

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

        if len(dicts_to_import) > 1:
            RecipeImporter.delete(delete_all=True)

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
            with pgconn.get_session() as session:
                session.add(db_obj)
                logging.info("Successfully [re]created %s" % c.slug)

                ObjectValidator.validate(db_obj, session=session, fatal=False)

            indexer_factory.get_indexer(c).index(c)

        CocktailScanCache.invalidate()

    @staticmethod
    def delete(cocktail=None, delete_all=False):

        if cocktail:
            with pgconn.get_session() as session:
                existing = session.query(CocktailModel).get(cocktail.slug)

                if existing:
                    logging.debug("Deleting %s" % existing.slug)
                    deleted = session.delete(existing)
            return

        if delete_all is True:
            with pgconn.get_session() as session:
                logging.debug("Deleting all CocktailModel")
                deleted = session.query(CocktailModel).delete()
                logging.info("Deleted %s from %s" % (deleted, CocktailModel.__tablename__))
                index_factory.rebuild(RecipeIndex)


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
            with BaseImporter.pgconn.get_session() as session:
                # existing = IngredientModel.query.get(i.slug)
                existing = session.query(IngredientModel).get(i.slug)
                if existing:
                    if existing.kind == IngredientKinds('category').value or existing.kind == IngredientKinds('family').value:
                        if i.kind is IngredientKinds('ingredient'):
                            logging.error("Skipping %s (t:%s) since a broader entry exists (%s)" % (i.slug, i.kind.value, existing.kind))
                        else:
                            logging.error("%s (p:%s) already exists as a %s (p:%s)" % (i.slug, i.parent, existing.kind, existing.parent))
                    else:
                        logging.error("%s (p:%s) already exists as a %s (p:%s)" % (i.slug, i.parent, existing.kind, existing.parent))
                else:
                    session.add(db_obj)
                    indexer_factory.get_indexer(i).index(i)

        logging.info("Validating")
        with BaseImporter.pgconn.get_session() as session:
            objects = session.query(IngredientModel).all()
            for db_obj in objects:
                # Validate
                ObjectValidator.validate(db_obj, session=session, fatal=False)

        # Invalidate the cache
        IngredientTreeCache.invalidate()

    @staticmethod
    def delete():
        logging.debug("Deleting old data from database")
        with BaseImporter.pgconn.get_session() as session:
            deleted = session.query(IngredientModel).delete()

        # deleted = IngredientModel.query.delete()
        logging.info("Deleted %s" % deleted)
        index_factory.rebuild(IngredientIndex)

    @staticmethod
    def validate():
        logging.info("starting validation")
        with BaseImporter.pgconn.get_session() as session:
            ingredients = session.query(IngredientModel).all()
        # ingredients = IngredientModel.query.all()
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

        # pgconn = Registry.get_database_connection()

        Importer.get_importer(args.object).import_(args.filepath)

        # pgconn.commit()

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
