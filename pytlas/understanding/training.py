from pytlas.pkgutils import get_caller_package_name
from pytlas.datautils import should_load_resources
from pytlas.store import Store

class TrainingsStore(Store):
  """Contains training data.
  """

  def __init__(self, data=None):
    """Instantiates a new store.

    Args:
      data (dict): Optional initial data to use

    """
    super().__init__('train', data or {})

  def all(self, lang):
    """Retrieve all training data in the given language.

    It will evaluate all register functions for the given language.

    Args:
      lang (str): Language to get

    Returns:
      dict: Dictionary with package name as key and training DSL string as value

    """
    return { k: v.get(lang, lambda: None)() for k, v in self._data.items()}

  def get(self, package, lang):
    """Retrieve all training data for a particular package in the given language.

    It will evaluate all register functions for the given language.

    Args:
      package (str): Pacjage
      lang (str): Language to get

    Returns:
      str: Training data

    """
    return self._data.get(package, {}).get(lang, lambda: None)()

  def register(self, lang, func, package=None):
    """Register training data written using the chatl DSL language into the system.
  
    Args:
      lang (str): Language for which the training has been made for
      func (func): Function to call to return training data written using the chatl DSL
      package (str): Optional package name (usually __package__), if not given pytlas will try to determine it based on the call stack
  
    """
    package = package or get_caller_package_name()
  
    if not should_load_resources(lang):
      return self._logger.debug(f'Skipped "{package}" training data for language "{lang}"')
  
    if package not in self._data:
      self._data[package] = {}
  
    self._data[package][lang] = func
  
    self._logger.info(f'Registered "{package}.{func.__name__}" training data for the lang "{lang}"')

# Global trainings store
global_trainings = TrainingsStore()

def training(lang, store=None, package=None):
  """Decorator applied to a function that returns DSL data to register training data.

  Args:
    lang (str): Lang of the training data
    store (TrainingsStore): Store to use for registration, defaults to the global one
    package (str): Optional package name (usually __package__), if not given pytlas will try to determine it based on the call stack

  """
  s = store or global_trainings

  def new(func):
    s.register(lang, func, package or get_caller_package_name() or func.__module__)
    return func

  return new