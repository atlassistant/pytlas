import sys, inspect, os, random
from shutil import rmtree as shrmtree
from fuzzywuzzy import process
from markdown import markdown
from bs4 import BeautifulSoup

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

def read_file(path, ignore_errors=False, relative_to_file=None):
  """Read the file content as utf-8 at the specified path.

  Args:
    path (str): Path to be read
    ignore_errors: True if you don't want exception to be raised (None will be returned)
    relative_to_file (str): If set, the path will be evaluated relative to this filepath

  Returns:
    str: Content of the file or None if not found and ignore_errors was true
    
  """

  if relative_to_file:
    path = os.path.join(os.path.dirname(relative_to_file), path)

  try:
    with open(path, encoding='utf-8') as f:
      return f.read()
  except Exception as e:
    if not ignore_errors:
      raise e

    return None

def keep_one(value):
  """Keeps only one element if value is a list.

  Args:
    value (str, list): Value to check

  Returns:
    str: Random value in the given list if it's a list, else the given value

  """

  if isinstance(value, list):
    return random.choice(value)

  return value

def strip_format(value):
  """Removes any markdown format from the source to returns a raw string.

  Args:
    value (str): Input value which may contains format characters
  
  Returns:
    str: Raw value without format characters
  
  Examples:
    >>> strip_format('contains **bold** text here')
    'contains bold text here'

    >>> strip_format('nothing fancy here')
    'nothing fancy here'

    >>> strip_format(None)

  """

  if not value:
    return None

  html = markdown(value)

  # If nothing has changed, don't rely on BeautifulSoup since this is not needed
  if html == value:
    return value

  return BeautifulSoup(html, 'html.parser').get_text()

def find_match(choices, value):
  """Find element that fuzzy match the available choices.

  Args:
    choices (list): Available choices
    value (str): Raw value to fuzzy match

  Returns:
    str: matched text in given choices

  """

  match = process.extractOne(value, choices, score_cutoff=60)

  return match[0] if match else None

def _onerror(func, path, exc_info):
  """Error handler for ``shutil.rmtree``.

  If the error is due to an access error (read only file)
  it attempts to add write permission and then retries.

  If the error is for another reason it re-raises the error.

  """
  import stat

  if not os.access(path, os.W_OK):
      # Is the error an access error ?
      os.chmod(path, stat.S_IWUSR)
      func(path)
  else:
      raise

def rmtree(path, ignore_errors=False):
  """Recursively deletes a folder and its children and handle readonly files as per
  https://stackoverflow.com/a/2656405/7641999.

  Args:
    path (str): Path to delete
    ignore_errors (bool): Should we ignore errors

  """

  shrmtree(path, ignore_errors=ignore_errors, onerror=_onerror)
