import sys, inspect, os

def get_root_package_name(name):
  """Get the root package name of a nested module one.

  Args:
    name (str): Full name of the module
  
  Returns:
    str: The root package name

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
  """Retrieve the path where a module is defined.

  Args:
    module_name (str): Name of the module

  Returns:
    str: Path where the module is defined

  """

  return sys.modules[module_name].__path__[0]
