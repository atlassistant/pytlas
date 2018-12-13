import logging
from pytlas.utils import get_caller_package_name

handlers = {}

# Contains module metadatas functions. Why functions? Because we want to be able
# to translate them in the user language.
module_metas = {}

def register_metadata(func, package=None):
  """Register skill package metadata

  Args:
    func (func): Function which will be called with a function to translate strings using the package translations at runtime
    package (str): Optional package name (usually __package__), if not given pytlas will try to determine it based on the call stack

  """

  package = package or get_caller_package_name()

  module_metas[package] = func

  logging.info('Registered "%s.%s" metadata' % (package, func.__name__))

def meta(package=None):
  """Decorator used to register skill metadata.

  Args:
    package (str): Optional package name (usually __package__), if not given pytlas will try to determine it based on the call stack

  """

  def new(func):
    register_metadata(func, package or get_caller_package_name() or func.__module__)

    return func
    
  return new

def register(intent, handler, package=None):
  """Register an intent handler.

  Args:
    intent (str): Name of the intent to handle
    handler (func): Handler to be called when the intent is triggered
    package (str): Optional package name (usually __package__), if not given pytlas will try to determine it based on the call stack

  """

  package = package or get_caller_package_name() or handler.__module__

  logging.info('Registered "%s.%s" which should handle "%s" intent' % (package, handler.__name__, intent))

  handlers[intent] = handler

def intent(intent_name, package=None):
  """Decorator used to register an intent handler.

  Args:
    intent_name (str): Name of the intent to handle
    package (str): Optional package name (usually __package__), if not given pytlas will try to determine it based on the call stack
  
  """
  
  def new(func):
    register(intent_name, func, package or get_caller_package_name() or func.__module__)

    return func
    
  return new