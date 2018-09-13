import json, logging, os
from .utils import get_caller_package_name, get_module_path

# Represents translations by module/lang
module_translations = {}

def register(lang, path_or_data, package=None):
  """Register translations into the system.

  Args:
    lang (str): Language being loaded
    path_or_data (str, dict): Path or dict data representing the translations
    package (str): Optional package name (usually __package__), if not given pytlas will try to determine it based on the call stack

  """

  package = package or get_caller_package_name()
  
  if type (path_or_data) is dict:
    data = path_or_data
  else:
    path = path_or_data if os.path.isabs(path_or_data) else os.path.abspath(os.path.join(get_module_path(package), path_or_data))

    with open (path, encoding='utf-8') as f:
      data = json.load(f)

  if package not in module_translations:
    module_translations[package] = {}

  module_translations[package][lang] = data

  logging.info('Imported "%d" translations from "%s" for the lang "%s"' % (len(data), package, lang))

def translations(lang, package=None):
  """Decorator applied to a function that returns a dictionary to indicate translations.

  Args:
    lang (str): Lang of the translations
    package (str): Optional package name (usually __package__), if not given pytlas will try to determine it based on the call stack

  """

  def new(func):
    register(lang, func(), package or get_caller_package_name() or func.__module__)
    return func

  return new