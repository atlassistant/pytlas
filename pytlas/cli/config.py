from configparser import ConfigParser
from functools import wraps
import logging, os

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
OPT_GRAPH = 'graph'

CONFIG_SECTION = 'pytlas'
CONFIG_DEFAULT_FILENAME = 'pytlas.conf'

config = ConfigParser()

# Needed because when loading the config file, logging has not been configured yet
config_loaded_from_path = None

# Represents default parameters value
config[CONFIG_SECTION] = {
  OPT_LANG: OPT_LANG_DEFAULT,
  OPT_SKILLS: OPT_SKILLS_DEFAULT,
}

def write_config(f):
  """Simple decorator used to write each argument value to the config
  if they're set and call the wrapped func without arguments.

  """

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
        config.set(CONFIG_SECTION, k, str(v))

    return f()
  
  return func

def log_configuration():
  """Logs configuration values using the standard logging library.
  """

  if config_loaded_from_path:
    logging.info('Configuration loaded from "%s"' % config_loaded_from_path)

  result = """Configuration:

"""

  for (k, v) in config[CONFIG_SECTION].items():
    result += ("""\t%s: %s
""") % (k, v)

  logging.debug(result)

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