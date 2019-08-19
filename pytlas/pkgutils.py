"""pkgutils provides helper methods to deal with package names.
"""

import os, sys, inspect

def get_root_package_name(name):
  """Get the root package name of a nested module one.

  Args:
    name (str): Full name of the module
  
  Returns:
    str: The root package name

  Examples:
    >>> get_root_package_name('weather.nested.file')
    'weather'
    >>> get_root_package_name('weather')
    'weather'

  """
  return name.split('.')[0] if name else name

def get_package_name_from_module(module_name):
  """Retrieve a package name from a module one.

  Args:
    module_name (str): Name of a module

  Returns:
    str: The package in which this module was defined

  """
  return get_root_package_name(sys.modules[module_name].__package__)

def get_caller_package_name():
  """Retrieve the caller package name. This is used with the register methods for the skills.

  Returns:
    str: Package name of the caller

  """
  return get_root_package_name(inspect.currentframe().f_back.f_back.f_globals['__name__'])

def get_module_path(module_name):
  """Retrieve the path where a module is defined. If the module could not be found
  or it doesn't have a path property, the current working directory will be returned.

  Args:
    module_name (str): Name of the module

  Returns:
    str: Path where the module is defined

  """
  try:
    return sys.modules[module_name].__path__[0]
  except (AttributeError, KeyError):
    return os.getcwd()
