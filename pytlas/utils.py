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

def get_absolute_path_to_package_file(path, package):
  """Returns an absolute filepath to a path contained within a package.

  Args:
    path (str): Path to manipulate
    package (str): Name of the package

  Returns:
    str: If path is already an absolute path, nothing will be made, else, the absolute path will be computed

  """

  return path if os.path.isabs(path) else os.path.abspath(os.path.join(get_module_path(package), path))

def read_file(path, ignore_errors=False):
  """Read the file content at the specified path.

  Args:
    path (str): Path to be read
    ignore_errors: True if you don't want exception to be raised (None will be returned)

  Returns:
    str: Content of the file or None if not found and ignore_errors was true
    
  """

  try:
    with open(path) as f:
      return f.read()
  except Exception as e:
    if not ignore_errors:
      raise e

    return None