import logging, os
from .utils import get_caller_package_name, get_absolute_path_to_package_file
from pychatl import parse

# Training data per module / lang
module_trainings = {}

def register(lang, path_or_data, package=None):
  """Register training data written using the chatl DSL language into the system.

  Args:
    lang (str): Language for which the training has been made for
    path_or_data (str): Path or raw data representing the training data
    package (str): Optional package name (usually __package__), if not given pytlas will try to determine it based on the call stack

  """

  package = package or get_caller_package_name()

  abspath = get_absolute_path_to_package_file(path_or_data, package)
  
  if os.path.isfile(abspath):
    with open(abspath) as f:
      data = f.read()
  else:
    data = path_or_data

  if package not in module_trainings:
    module_trainings[package] = {}

  parsed_data = parse(data)

  module_trainings[package][lang] = parsed_data

  def flatten(type):
    return ', '.join(['"%s"' % d for d in parsed_data[type].keys()])

  logging.info('Imported training data (intents: %s / entities: %s / synonyms: %s) from "%s" for the lang "%s"' % 
    (flatten('intents'), flatten('entities'), flatten('synonyms'), package, lang))

def training(lang, package=None):
  """Decorator applied to a function that returns DSL data to register training data.

  Args:
    lang (str): Lang of the training data
    package (str): Optional package name (usually __package__), if not given pytlas will try to determine it based on the call stack

  """

  def new(func):
    register(lang, func(), package or get_caller_package_name() or func.__module__)
    return func

  return new