import logging, os
from .utils import get_caller_package_name, get_module_path
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

  path = path_or_data if os.path.isabs(path_or_data) else os.path.abspath(os.path.join(get_module_path(package), path_or_data))
  
  if os.path.isfile(path):
    with open(path) as f:
      data = f.read()
  else:
    data = path_or_data

  if package not in module_trainings:
    module_trainings[package] = {}

  parsed_data = parse(data)

  module_trainings[package][lang] = parsed_data

  logging.info('Imported training data ("%d" intents, "%d" entities and "%d" synonyms) from "%s" for the lang "%s"' % 
    (len(parsed_data['intents']), len(parsed_data['entities']), len(parsed_data['synonyms']), package, lang))

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