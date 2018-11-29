from configparser import ConfigParser
from functools import wraps

OPT_VERBOSE = 'verbose'
OPT_DEBUG = 'debug'
OPT_LANG = 'lang'
OPT_LANG_DEFAULT = 'en'
OPT_SKILLS = 'skills'
OPT_SKILLS_DEFAULT = 'skills'
OPT_CACHE = 'cache'
OPT_DRY = 'dry'
OPT_PARSE = 'parse'
OPT_WATCH = 'watch'
OPT_TRAINING_FILE = 'training_file'

CONFIG_SECTION = 'pytlas'
CONFIG_FILENAME = 'pytlas.conf'

# Represents default parameters value
config = ConfigParser()
config[CONFIG_SECTION] = {}

def write_config(f):
  """Simple decorator used to write each argument value to the config
  if they're set and call the wrapped func without arguments.

  """

  @wraps(f)
  def func(**kwargs):
    # Config is a specific key used to read the config from a file
    conf = kwargs.get('config')

    if conf:
      config.read(conf)

    # And then, for each argument, write its value in the config object
    for (k, v) in kwargs.items():
      if v:
        config.set(CONFIG_SECTION, k, str(v))

    f()
  
  return func

def get(name, default=None):
  """Gets a configuration value.

  Args:
    name (str): Name of the configuration option
    default (object): Fallback value

  Returns:
    str: Value of the option

  """

  return config.get(CONFIG_SECTION, name, fallback=default)

def getboolean(name, default=False):
  """Gets a boolean value for a configuration value.

  Args:
    name (str): Name of the configuration option
    default (bool): Fallback value

  Returns:
    bool: Value of the option

  """
  
  return config.getboolean(CONFIG_SECTION, name, fallback=default)