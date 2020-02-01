import os
import sys
import argparse
import editor
import england.util


class Make:
    def __init__(self):
        pass

    def run(self):
        args = self._setup_args()
        self._validate_args(args)

        # Path to the file we're going to write
        filepath = os.path.join(args.recipe_dir, args.drink_name + '.yaml')

        # Default content (load existing or grab template)
        default_content = self._prepare_default_content(filepath=filepath, template=args.template, raw_drink_name=args.drink_name)

        # Edit
        editor.edit(contents=default_content, filename=filepath)

        # Validate syntax
        try:
            england.util.read_yaml_file(filepath, fatal=False)
            print('Syntax OK!')
        except Exception:
            print('Syntax failure! Edit the file and try again.')

    @staticmethod
    def _get_stylized_drink_name(drink_file_name):
        return drink_file_name.replace('-', ' ').title()

    @staticmethod
    def _prepare_default_content(filepath, template, raw_drink_name):
        default_content_source = template
        if os.path.exists(filepath):
            default_content_source = filepath

        default_content = england.util.read_file(default_content_source)

        stylized_drink_name = Make._get_stylized_drink_name(raw_drink_name)
        default_content = default_content.replace('StylizedDrinkName', stylized_drink_name)

        return default_content

    @staticmethod
    def _setup_args():
        parser = argparse.ArgumentParser(description='Create a new recipe YAML',
                                         usage='amari make <amari-name>')
        parser.add_argument('drink_name', help='name of yaml file to create')
        parser.add_argument('-d', '--recipedir', help='Recipe archive directory',
                            required=False, default='./data/recipes', dest='recipe_dir')
        parser.add_argument('-t', '--template', help='Template for new file',
                            required=False, default='./templates/recipe.yaml', dest='template')

        return parser.parse_args(sys.argv[2:])

    @staticmethod
    def _validate_args(args):
        if ' ' in args.drink_name:
            england.util.die("Drink name '%s' cannot have spaces. Use dashes." % args.drink_name)

        if not os.path.isdir(args.recipe_dir):
            england.util.die("Recipe path '%s' is not a directory" % args.recipe_dir)

        if not os.path.isfile(args.template):
            england.util.die("Template path '%s' is not a file." % args.template)
