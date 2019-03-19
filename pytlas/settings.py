from configparser import ConfigParser
from functools import wraps
import os, re

DEFAULT_SECTION = 'pytlas'
DEFAULT_FILENAME = 'pytlas.conf'
DEFAULT_LANG = 'en'

config = ConfigParser()

# Needed to keep track of the settings file that has been loaded
config_loaded_from_path = None

# Here are builtin settings used by the library
SETTING_VERBOSE = 'verbose'
SETTING_DEBUG = 'debug'
SETTING_LANG = 'lang'
SETTING_SKILLS = 'skills'
DEFAULT_SETTING_SKILLS = 'skills'
SETTING_CACHE = 'cache'
SETTING_DRY = 'dry'
SETTING_PARSE = 'parse'
SETTING_WATCH = 'watch'
SETTING_TRAINING_FILE = 'training_file'
SETTING_GRAPH_FILE = 'graph'
SETTING_DEFAULT_REPO_URL = 'default_repo_url'
DEFAULT_SETTING_DEFAULT_REPO_URL = 'https://github.com/'

# Default parameters value
config[DEFAULT_SECTION] = {
  SETTING_SKILLS: DEFAULT_SETTING_SKILLS,
  SETTING_DEFAULT_REPO_URL: DEFAULT_SETTING_DEFAULT_REPO_URL,
}

def write_to_settings(section=DEFAULT_SECTION):
  """Simple decorator used to write each argument value to the settings
  if they're set and call the wrapped func without arguments. If a keyword is named
  `config`, the filepath represented by this keyword will be read in the config object.

  Args:
    section (str): Section to write the settings

  """

  def new(f):
    @wraps(f)
    def func(**kwargs):
      # Config is a specific key used to read the config from a file
      conf = kwargs.get('config')

      # And read it if it exists
      if conf and os.path.isfile(conf):
        global config_loaded_from_path
        config_loaded_from_path = os.path.abspath(conf)
        config.read(config_loaded_from_path)

      # And then, for each argument, write its value in the config object
      for (k, v) in kwargs.items():
        if v:
          config.set(section, k, str(v))

      return f()
    
    return func
  
  return new

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

def set(setting, value, section=DEFAULT_SECTION):
  """Sets a setting value in the inner config.

  Value will be stringified by this method (since all value can be read from env variables).

  Args:
    setting (str): Setting key to write
    value (object): Value to write
    section (str): Section to write to

  """

  if section not in config:
    config[section] = {}

  config[section][setting] = stringify(value)

def get(setting, default=None, section=DEFAULT_SECTION, additional_lookup={}):
  """Gets a setting value, if an environment variable is defined, it will take
  precedence over the value hold in the inner config object.

  For example, if you got a setting 'lang' in the 'pytlas' section, defining the
  environment varialbe PYTLAS_LANG will take precedence.

  Args:
    setting (str): Name of the configuration option
    default (str): Fallback value
    section (str): Section to look in
    additional_lookup (dict): Additional dictionary to look in

  Returns:
    str: Value of the setting

  """

  env_key = to_env_key(section, setting)

  return additional_lookup.get(env_key, os.environ.get(env_key, config.get(section, setting, fallback=default)))

def getbool(setting, default=False, section=DEFAULT_SECTION, additional_lookup={}):
  """Gets a boolean value for a setting. It uses the `get` under the hood so the same
  rules applies.

  Args:
    setting (str): Name of the configuration option
    default (bool): Fallback value
    section (str): Section to look in
    additional_lookup (dict): Additional dictionary to look in

  Returns:
    bool: Value of the setting

  """

  v = get(setting, section=section, additional_lookup=additional_lookup)

  return config._convert_to_boolean(v) if v else default

def getint(setting, default=0, section=DEFAULT_SECTION, additional_lookup={}):
  """Gets a int value for a setting. It uses the `get` under the hood so the same
  rules applies.

  Args:
    setting (str): Name of the configuration option
    default (int): Fallback value
    section (str): Section to look in
    additional_lookup (dict): Additional dictionary to look in

  Returns:
    int: Value of the setting

  """

  v = get(setting, section=section, additional_lookup=additional_lookup)

  return int(v) if v else default

def getfloat(setting, default=0.0, section=DEFAULT_SECTION, additional_lookup={}):
  """Gets a float value for a setting. It uses the `get` under the hood so the same
  rules applies.

  Args:
    setting (str): Name of the configuration option
    default (float): Fallback value
    section (str): Section to look in
    additional_lookup (dict): Additional dictionary to look in

  Returns:
    float: Value of the setting

  """

  v = get(setting, section=section, additional_lookup=additional_lookup)

  return float(v) if v else default

def getlist(setting, default=[], section=DEFAULT_SECTION, additional_lookup={}):
  """Gets a list for a setting. It will split values separated by a comma.
  
  It uses the `get` under the hood so the same rules applies.

  Args:
    setting (str): Name of the configuration option
    default (list): Fallback value
    section (str): Section to look in
    additional_lookup (dict): Additional dictionary to look in

  Returns:
    list: Value of the setting

  """

  v = get(setting, section=section, additional_lookup=additional_lookup)

  return v.split(',') if v else default

def getpath(setting, default=None, section=DEFAULT_SECTION, additional_lookup={}):
  """Gets an absolute path for a setting.
  
  It uses the `get` under the hood so the same rules applies.

  Args:
    setting (str): Name of the configuration option
    default (str): Fallback value
    section (str): Section to look in
    additional_lookup (dict): Additional dictionary to look in

  Returns:
    str: Value of the setting

  """

  v = get(setting, default, section=section, additional_lookup=additional_lookup)

  return os.path.abspath(v) if v else None
