import json, logging, os
from pytlas.utils import get_caller_package_name
from pytlas.importers import should_load_resources

# Represents translations by module/lang => func
module_translations = {}

def get_translations(lang):
  """Retrieve all translations for the given language.

  It will evaluate all register functions for the given language.

  Args:
    lang (str): Language to get

  Returns:
    dict: Dictionary with package name as key and translations as values

  """

  return { k: v.get(lang, lambda: {})() for k, v in module_translations.items()}

def register(lang, func, package=None):
  """Register translations into the system.

  Args:
    lang (str): Language being loaded
    func (func): Function to call to load a dictionary of translations
    package (str): Optional package name (usually __package__), if not given pytlas will try to determine it based on the call stack

  """
  
  package = package or get_caller_package_name()

  if not should_load_resources(lang):
    return logging.debug('Skipped "%s" translations for language "%s"' % (package, lang))
  
  if package not in module_translations:
    module_translations[package] = {}

  module_translations[package][lang] = func

  logging.info('Registered "%s.%s" translations for the lang "%s"' % (package, func.__name__, lang))

def translations(lang, package=None):
  """Decorator applied to a function that returns a dictionary to indicate translations.

  Args:
    lang (str): Lang of the translations
    package (str): Optional package name (usually __package__), if not given pytlas will try to determine it based on the call stack

  """

  def new(func):
    register(lang, func, package or get_caller_package_name() or func.__module__)
    return func

  return new