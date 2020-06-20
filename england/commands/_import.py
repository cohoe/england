import argparse
import sys
import england.util
import os
from barbados.models import CocktailModel, IngredientModel, MenuModel
from barbados.factories import CocktailFactory, MenuFactory
from barbados.services.registry import Registry
from barbados.services.logging import Log
from barbados.objects.ingredient import Ingredient
from barbados.objects.ingredientkinds import IngredientKinds
from barbados.text import Slug
from barbados.serializers import ObjectSerializer
from barbados.validators import ObjectValidator
from barbados.caches import IngredientTreeCache, CocktailScanCache, MenuScanCache
from barbados.indexers import indexer_factory
from barbados.indexes import index_factory, RecipeIndex, IngredientIndex, MenuIndex


class Importer:
    importers = {}

    @classmethod
    def register_importer(cls, importer_class):
        cls.importers[importer_class.kind] = importer_class

    @classmethod
    def get_importer(cls, kind):
        return cls.importers[kind]()

    @classmethod
    def supported_importers(cls):
        return cls.importers.keys()


class BaseImporter:

    def __init__(self):
        self.pgconn = Registry.get_database_connection()

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

    def import_(self, filepath):
        dicts_to_import = RecipeImporter._fetch_data_from_path(filepath)

        if len(dicts_to_import) > 1:
            self.delete(delete_all=True)

        for cocktail_dict in dicts_to_import:
            try:
                slug = Slug(cocktail_dict['display_name'])
                Log.info("Working %s" % slug)
                c = CocktailFactory.raw_to_obj(cocktail_dict, slug)
            except KeyError as e:
                Log.error("Something has bad data!")
                Log.error(cocktail_dict)
                Log.error(e)
                continue

            self.delete(cocktail=c)

            db_obj = CocktailModel(**ObjectSerializer.serialize(c, 'dict'))
            with self.pgconn.get_session() as session:
                session.add(db_obj)
                Log.info("Successfully [re]created %s" % c.slug)

                ObjectValidator.validate(db_obj, session=session, fatal=False)

            indexer_factory.get_indexer(c).index(c)

        CocktailScanCache.invalidate()

    def delete(self, cocktail=None, delete_all=False):

        if cocktail:
            with self.pgconn.get_session() as session:
                existing = session.query(CocktailModel).get(cocktail.slug)

                if existing:
                    Log.debug("Deleting %s" % existing.slug)
                    deleted = session.delete(existing)
            return

        if delete_all is True:
            with self.pgconn.get_session() as session:
                Log.debug("Deleting all CocktailModel")
                deleted = session.query(CocktailModel).delete()
                Log.info("Deleted %s from %s" % (deleted, CocktailModel.__tablename__))
                index_factory.rebuild(RecipeIndex)


class IngredientImporter(BaseImporter):
    kind = 'ingredients'

    def import_(self, filepath):
        data = IngredientImporter._fetch_data_from_path(filepath)

        # Delete old data
        self.delete()

        Log.info("Starting import")
        for ingredient in data:
            i = Ingredient(**ingredient)
            db_obj = IngredientModel(**ObjectSerializer.serialize(i, 'dict'))

            # Test for existing
            with self.pgconn.get_session() as session:
                # existing = IngredientModel.query.get(i.slug)
                existing = session.query(IngredientModel).get(i.slug)
                if existing:
                    if existing.kind == IngredientKinds('category').value or existing.kind == IngredientKinds('family').value:
                        if i.kind is IngredientKinds('ingredient'):
                            Log.error("Skipping %s (t:%s) since a broader entry exists (%s)" % (i.slug, i.kind.value, existing.kind))
                        else:
                            Log.error("%s (p:%s) already exists as a %s (p:%s)" % (i.slug, i.parent, existing.kind, existing.parent))
                    else:
                        Log.error("%s (p:%s) already exists as a %s (p:%s)" % (i.slug, i.parent, existing.kind, existing.parent))
                else:
                    session.add(db_obj)
                    indexer_factory.get_indexer(i).index(i)

        Log.info("Validating")
        with self.pgconn.get_session() as session:
            objects = session.query(IngredientModel).all()
            for db_obj in objects:
                # Validate
                ObjectValidator.validate(db_obj, session=session, fatal=False)

        # Invalidate the cache
        IngredientTreeCache.invalidate()

    def delete(self):
        Log.debug("Deleting old data from database")
        with self.pgconn.get_session() as session:
            deleted = session.query(IngredientModel).delete()

        # deleted = IngredientModel.query.delete()
        Log.info("Deleted %s" % deleted)
        index_factory.rebuild(IngredientIndex)


class MenuImporter(BaseImporter):
    kind = 'menus'
    model = MenuModel

    def import_(self, filepath):
        data = MenuImporter._fetch_data_from_path(filepath)

        # Delete old data
        self.delete()

        Log.info("Starting import")
        for menu in data:
            m = MenuFactory.raw_to_obj(menu)
            db_obj = MenuModel(**ObjectSerializer.serialize(m, 'dict'))

            # Test for existing
            with self.pgconn.get_session() as session:
                session.add(db_obj)
                indexer_factory.get_indexer(m).index(m)

        # Validate
        self.validate()

        # Clear Cache and Index
        MenuScanCache.invalidate()

    def delete(self):
        Log.debug("Deleting old data from database")
        with self.pgconn.get_session() as session:
            deleted = session.query(self.model).delete()

        Log.info("Deleted %s" % deleted)
        index_factory.rebuild(MenuIndex)

    def validate(self):
        Log.info("Validating")
        with self.pgconn.get_session() as session:
            objects = session.query(self.model).all()
            for db_obj in objects:
                ObjectValidator.validate(db_obj, session=session, fatal=False)


Importer.register_importer(RecipeImporter)
Importer.register_importer(IngredientImporter)
Importer.register_importer(MenuImporter)


class Import:

    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        Importer.get_importer(args.object).import_(args.filepath)

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
