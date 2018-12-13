import logging, os
from pytlas.utils import get_caller_package_name
from pytlas.importers import should_load_resources

# Training data per module / lang => func
module_trainings = {}

def get_training_data(lang):
  """Retrieve all training data for the given language.

  It will evaluate all register functions for the given language.

  Args:
    lang (str): Language to get

  Returns:
    dict: Dictionary with package name as key and training DSL string as value

  """

  return { k: v.get(lang, lambda: None)() for k, v in module_trainings.items()}

def register(lang, func, package=None):
  """Register training data written using the chatl DSL language into the system.

  Args:
    lang (str): Language for which the training has been made for
    func (func): Function to call to return training data written using the chatl DSL
    package (str): Optional package name (usually __package__), if not given pytlas will try to determine it based on the call stack

  """

  package = package or get_caller_package_name()

  if not should_load_resources(lang):
    return logging.debug('Skipped "%s" training data for language "%s"' % (package, lang))

  if package not in module_trainings:
    module_trainings[package] = {}

  module_trainings[package][lang] = func

  logging.info('Registered "%s.%s" training data for the lang "%s"' % (package, func.__name__, lang))

def training(lang, package=None):
  """Decorator applied to a function that returns DSL data to register training data.

  Args:
    lang (str): Lang of the training data
    package (str): Optional package name (usually __package__), if not given pytlas will try to determine it based on the call stack

  """

  def new(func):
    register(lang, func, package or get_caller_package_name() or func.__module__)
    return func

  return new