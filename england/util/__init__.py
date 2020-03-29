import os
import sys
import yaml
import jinja2

# Constants
pretty_fractions = {
    '.25': '¼',
    '.33': '⅓',
    '.5': '½',
    '.75': '¾',
}


# Functions
def die(message, code=1):
    """
    Exit hard with an error message
    :param message: Message to print
    :param code: exit code
    :return: None
    """
    sys.stderr.write(message + "\n")
    exit(code)


def read_file(path):
    """
    Read contents of a file
    :param path:
    :return:
    """
    try:
        with open(path, 'r+') as fh:
            contents = fh.read()
    except IOError as e:
        die("Error: %s" % e)

    return contents


def read_yaml_file(path, fatal=True):
    contents = read_file(path)
    try:
        # Heads up! This will automagically do date conversion to date
        # Date objects. Some kind of implicit type nonsense.
        data = yaml.safe_load(contents)
        return data
    except Exception as e:
        if fatal is True:
            die("Error loading YAML from %s: %s" % (path, e))
        else:
            raise e


def write_file(path, contents):
    try:
        with open(path, 'w+') as fh:
            fh.write(contents)
    except IOError as e:
        die("Error: %s" % e)


def infer_bool(input_value):
    """
    Infer a boolean from the given value
    :param input_value: String, Integer, Boolean, None
    :return: Boolean
    """
    # Boolean
    if isinstance(input_value, bool):
        return input_value

    # Integer
    if isinstance(input_value, int):
        return bool(input_value)

    # String
    if isinstance(input_value, str):
        if 'Y' in input_value.upper():
            return True
        else:
            return False

    # None
    if input_value is None:
        return False


def load_template_from_file(path):
    template_content = read_file(path)
    jt = jinja2.Template(template_content)

    return jt


def list_files(path):
    return os.listdir(path)


def get_slug_from_path(path):
    file_name = os.path.basename(path)
    return os.path.splitext(file_name)[0]


def find_all_files(path, extension=None):
    """
    https://stackoverflow.com/questions/3964681/find-all-files-in-a-directory-with-extension-txt-in-python
    :param path:
    :param extension:
    :return:
    """
    file_paths = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if extension:
                if file.endswith(extension):
                    file_paths.append(os.path.join(root, file))
            else:
                file_paths.append(os.path.join(root, file))

    return file_paths


def load_yaml_data_from_path(path, extension='.yaml'):
    result_data = []
    files = find_all_files(path=path, extension=extension)
    for file in files:
        data = read_yaml_file(file)
        result_data += data

    return result_data