import logging
from pytlas.settings import DEFAULT_SECTION
from pytlas.utils import get_caller_package_name

handlers = {}

# Contains module metadatas functions. Why functions? Because we want to be able
# to translate them in the user language.
module_metas = {}

class Setting:
  """Represents a skill settings.
  """

  def __init__(self, section, name, data_type=str, description='No description provided'):
    """Instantiate a new setting.

    Args:
      section (str): Section in which this setting belongs
      name (str): Name of the settings
      data_type (type): Data type of the settings
      description (str): Optional description for this setting

    """

    self.name = name
    self.section = section
    self.description = description
    self.type = data_type

  @classmethod
  def from_value(cls, value):
    """Instantiate a setting from a string representation in the form section.name

    Args:
      value (str): String which represents the setting

    Returns:
      Setting: Setting instance

    Examples:
      >>> str(Setting.from_value('openweather.api_key'))
      'openweather.api_key (str)'
      >>> str(Setting.from_value('language'))
      'pytlas.language (str)'
      >>> Setting.from_value('pytlas.weather.api_key').section
      'pytlas.weather'

    """

    try:
      section, name = value.rsplit('.', 1)
    except ValueError:
      section, name = DEFAULT_SECTION, value

    return Setting(section, name)

  def __str__(self):
    return f'{self.section}.{self.name} ({self.type.__name__})'

class Meta:
  """Represents a single skill metadata. It's used primarly for skill listing and
  comprehensive help on how your assistant can help you.
  """

  def __init__(self, name=None, description='No description provided',
    version='?.?.?', author='', homepage='', media='', settings=[]):
    """Instantiate a new Metadata instance for a skill.

    Args:
      name (str): Name of the skill
      description (str): Description of what your skill is doing
      version (str): Version of the skill
      author (str): Author of the skill
      homepage (str): URL of the skill to submit issues or enhancements
      media (str): Logo representing your skill
      settings (list of str or list of Setting): Settings used by your skill

    """

    self.name = name
    self.media = media
    self.description = description
    self.version = version
    self.author = author
    self.homepage = homepage
    self.settings = [setting if isinstance(setting, Setting) else Setting.from_value(setting) for setting in settings]

  def __str__(self):
    data = self.__dict__
    data['settings'] = ', '.join([ str(s) for s in data['settings'] ])

    return """{name} - v{version}
  description: {description}
  homepage: {homepage}
  author: {author}
  settings: {settings}
""".format(**data)

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