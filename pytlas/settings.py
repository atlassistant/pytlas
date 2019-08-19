from configparser import ConfigParser
from functools import wraps
from pytlas.store import Store
import os, re

DEFAULT_SECTION = 'pytlas'

# Here are builtin settings used by the library
SETTING_ALLOWED_LANGUAGES = 'allowed_languages'

env_sanitizer_re = re.compile('[^0-9a-zA-Z]+')

def to_env_key(section, setting):
  """Convert a section and a setting to an environment key.

  Args:
    section (str): Section of the configuration
    setting (str): Setting key to look for

  Returns:
    str: Environment variable name

  Examples:
    >>> to_env_key('pytlas', 'lang')
    'PYTLAS_LANG'
    >>> to_env_key('pytlas.a skill', 'password')
    'PYTLAS_A_SKILL_PASSWORD'

  """
  return env_sanitizer_re.sub('_', '%s_%s' % (section, setting)).upper()

def stringify(value):
  """Stringify the given value.

  Args:
    value (object): Value to stringify

  Returns:
    str: String version of the value

  Examples:
    >>> stringify('a string')
    'a string'
    >>> stringify(5)
    '5'
    >>> stringify(2.3)
    '2.3'
    >>> stringify(True)
    'True'
    >>> stringify(['one', 'two', 'three'])
    'one,two,three'
    >>> stringify([1, 2, 3.2])
    '1,2,3.2'
  
  """
  if isinstance(value, str):
    return value

  if isinstance(value, list):
    return ','.join(map(str, value))

  return str(value)

class SettingsStore(Store):
  """Hold application settings with an internal ConfigParser instance. It provides
  a lot of utility methods to convert settings to particular representations.

  Why? You may ask. Because it starts by looking for the given settings into
  an optional additional lookup dict, if its not found, it will look in the system
  environment and finally, it will use the ConfigParser instance which is probably
  loaded from a configuration file.
  
  And since everything in the env are considered as strings, you can use the provided
  methods to make things easier.
  """

  def __init__(self, config=None, additional_lookup=None):
    """Instantiates a new store.

    Args:
      config (ConfigParser): Existing ConfigParser instance to use
      additional_lookup (dict): Dictionary with additional settings where keys are the same as when looking in OS envs

    """
    super().__init__('settings', additional_lookup or {})

    if config:
      self.config = config
    else:
      self.config = ConfigParser()

  def load_from_file(self, path):
    """Load settings from a file.

    Args:
      path (str): Name of the file to read

    """
    abspath = os.path.abspath(path)
    self._logger.info(f'Loading configuration from "{abspath}"')
    self.config.read(abspath)

  def set(self, setting, value, section=DEFAULT_SECTION):
    """Sets a setting value in the `_data` dictionary so it will take
    precedence over all the others.

    Value will be stringified by this method (since all value can be read from env variables).

    Args:
      setting (str): Setting key to write
      value (object): Value to write
      section (str): Section to write to

    """
    self._data[to_env_key(section, setting)] = stringify(value)

  def get(self, setting, default=None, section=DEFAULT_SECTION):
    """Gets a setting value, if an environment variable is defined, it will take
    precedence over the value hold in the inner config object.

    For example, if you got a setting 'lang' in the 'pytlas' section, defining the
    environment varialbe PYTLAS_LANG will take precedence.

    Args:
      setting (str): Name of the configuration option
      default (str): Fallback value
      section (str): Section to look in

    Returns:
      str: Value of the setting

    """
    env_key = to_env_key(section, setting)

    return self._data.get(env_key, 
                os.environ.get(env_key, 
                self.config.get(section, setting, fallback=default)))

  def getbool(self, setting, default=False, section=DEFAULT_SECTION):
    """Gets a boolean value for a setting. It uses the `get` under the hood so the same
    rules applies.

    Args:
      setting (str): Name of the configuration option
      default (bool): Fallback value
      section (str): Section to look in

    Returns:
      bool: Value of the setting

    """
    v = self.get(setting, section=section)

    return self.config._convert_to_boolean(v) if v else default

  def getint(self, setting, default=0, section=DEFAULT_SECTION):
    """Gets a int value for a setting. It uses the `get` under the hood so the same
    rules applies.

    Args:
      setting (str): Name of the configuration option
      default (int): Fallback value
      section (str): Section to look in

    Returns:
      int: Value of the setting

    """
    v = self.get(setting, section=section)

    return int(v) if v else default

  def getfloat(self, setting, default=0.0, section=DEFAULT_SECTION):
    """Gets a float value for a setting. It uses the `get` under the hood so the same
    rules applies.

    Args:
      setting (str): Name of the configuration option
      default (float): Fallback value
      section (str): Section to look in

    Returns:
      float: Value of the setting

    """
    v = self.get(setting, section=section)

    return float(v) if v else default

  def getlist(self, setting, default=[], section=DEFAULT_SECTION):
    """Gets a list for a setting. It will split values separated by a comma.
    
    It uses the `get` under the hood so the same rules applies.

    Args:
      setting (str): Name of the configuration option
      default (list): Fallback value
      section (str): Section to look in

    Returns:
      list: Value of the setting

    """
    v = self.get(setting, section=section)

    return v.split(',') if v else default

  def getpath(self, setting, default=None, section=DEFAULT_SECTION):
    """Gets an absolute path for a setting.
    
    It uses the `get` under the hood so the same rules applies.

    Args:
      setting (str): Name of the configuration option
      default (str): Fallback value
      section (str): Section to look in

    Returns:
      str: Value of the setting

    """
    v = self.get(setting, default, section=section)

    return os.path.abspath(v) if v else None

# Holds the global settings store of the application
config = SettingsStore()

def write_to_store(section=DEFAULT_SECTION, store=None):
  """Simple decorator used to write each argument value to the current settings store
  if they're set.

  Args:
    section (str): Section to write settings to
    store (SettingsStore): Store to write to, default to the global one

  """

  s = store or config

  def new(f):
    @wraps(f)
    def func(**kwargs):
      # For each argument, update the SettingsStore object if value is set
      for (k, v) in kwargs.items():
        if v:
          s.set(k, v, section)

      return f(**kwargs)
    
    return func
  
  return new
