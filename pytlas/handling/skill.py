# pylint: disable=C0111

from pytlas.settings import DEFAULT_SECTION
from pytlas.pkgutils import get_caller_package_name
from pytlas.store import Store
from pytlas.handling.localization import GLOBAL_TRANSLATIONS


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


class Meta: # pylint: disable=R0902
    """Represents a single skill metadata. It's used primarly for skill listing and
    comprehensive help on how your assistant can help you.
    """

    # pylint: disable=W0102,R0913

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
        self.settings = [setting if isinstance(
            setting, Setting) else Setting.from_value(setting) for setting in settings]
        self.package = None  # Represents the module which defines this meta

    # pylint: enable=W0102,R0913

    def __eq__(self, value):
        if not isinstance(value, self.__class__):
            return False
        return self.name == value.name and self.media == value.media \
            and self.description == value.description and self.version == value.version \
            and self.author == value.author and self.homepage == value.homepage

    def __str__(self):
        data = self.__dict__.copy()
        data['settings'] = ', '.join([str(s) for s in data['settings']])

        return """{name} - v{version}
  description: {description}
  homepage: {homepage}
  author: {author}
  settings: {settings}
""".format(**data)


class MetasStore(Store):
    """Hold skill metadatas.
    """

    def __init__(self, translations_store=None, data=None):
        """Instantiates a new store.

        Args:
          translations_store (TranslationsStore): Optional translations store to use
          data (dict): Optional initial data to use

        """
        super().__init__('meta', data or {})
        self._translations = translations_store or GLOBAL_TRANSLATIONS

    def _apply_meta_func(self, package, func, translations): # pylint: disable=R0201
        result = func(lambda k: translations.get(k, k))

        if not isinstance(result, Meta):
            result = Meta(**result)

        result.package = package

        return result

    def all(self, lang):
        """Retrieve all registered meta in the given language.

        Args:
          lang (str): Language to use

        Returns:
          list of Meta: Registered Meta

        """
        metas = []
        translations = self._translations.all(lang)

        for pkg, meta_func in self._data.items():
            pkg_translations = translations.get(pkg, {})
            metas.append(self._apply_meta_func(
                pkg, meta_func, pkg_translations))

        return metas

    def get(self, package, lang):
        """Retrieve a meta for the given package.

        Args:
          package (str): Package name to retrieve
          lang (str): Lang for which you want to retrieve the skill Meta

        Returns:
          Meta: Meta instance or None if not found

        """
        meta_func = self._data.get(package)

        if not meta_func:
            return None

        translations = self._translations.get(package, lang)
        return self._apply_meta_func(package, meta_func, translations)

    def register(self, func, package=None):
        """Register skill package metadata

        Args:
          func (func): Function which will be called with a function to translate
            strings using the package translations at runtime
          package (str): Optional package name (usually __package__), if not given
            pytlas will try to determine it based on the call stack

        """
        package = package or get_caller_package_name()

        self._data[package] = func
        self._logger.info('Registered "%s.%s" metadata', package, func.__name__)


# Global skill metadata store
GLOBAL_METAS = MetasStore()


def meta(store=None, package=None):
    """Decorator used to register skill metadata.

    Args:
      store (MetasStore): Store to use for registration, defaults to the global one
      package (str): Optional package name (usually __package__), if not given
        pytlas will try to determine it based on the call stack

    """
    ms = store or GLOBAL_METAS # pylint: disable=C0103

    def new(func):
        ms.register(func, package or get_caller_package_name()
                    or func.__module__)
        return func

    return new


class HandlersStore(Store):
    """Holds skill handlers.
    """

    def __init__(self, data=None):
        """Instantiates a new store.

        Args:
          data (dict): Optional initial data to use

        """
        super().__init__('handl', data or {})

    def get(self, intent_name):
        """Try to retrieve the handler associated with a particular intent.

        Args:
          intent_name (str): Intent to search

        Returns:
          callable: Handler if found, None otherwise

        """
        return self._data.get(intent_name)

    def register(self, intent_name, func, package=None):
        """Register an intent handler.

        Args:
          intent_name (str): Name of the intent to handle
          func (callable): Handler to be called when the intent is triggered
          package (str): Optional package name (usually __package__), if not given
            pytlas will try to determine it based on the call stack

        """
        package = package or get_caller_package_name() or func.__module__

        self._data[intent_name] = func
        self._logger.info('Registered "%s.%s" which should handle "%s" intent',
                          package, func.__name__, intent_name)


# Global handlers store
GLOBAL_HANDLERS = HandlersStore()


def intent(intent_name, store=None, package=None):
    """Decorator used to register an intent handler.

    Args:
      intent_name (str): Name of the intent to handle
      package (str): Optional package name (usually __package__), if not given
        pytlas will try to determine it based on the call stack

    """
    hs = store or GLOBAL_HANDLERS # pylint: disable=C0103

    def new(func):
        hs.register(intent_name, func,
                    package or get_caller_package_name() or func.__module__)
        return func

    return new
