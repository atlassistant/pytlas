# pylint: disable=C0111

from pytlas.pkgutils import get_caller_package_name
from pytlas.datautils import should_load_resources
from pytlas.store import Store


class TranslationsStore(Store):
    """Translations store which holds all translations used by skills.
    """

    def __init__(self, data=None):
        """Instantiates a new store.

        Args:
          data (dict): Optional initial data to use

        """
        super().__init__('trans', data)

    def all(self, lang):
        """Retrieve all translations for all packages in the given language.

        Args:
          lang (str): Language for which we want translations

        Returns:
          dict: Dictionary of package => translations dict in the given language

        """
        return {k: v.get(lang, lambda: {})() for k, v in self._data.items()}

    def get(self, package, lang):
        """Retrieve all translations for a particular package.

        Args:
          package (str): Name of the package
          lang (str): Language to retrieve

        Returns:
          dict: Translations dictionary

        """
        return self._data.get(package, {}).get(lang, lambda: {})()

    def register(self, lang, func, package=None):
        """Register translations into the store.

        Args:
          lang (str): Language being loaded
          func (func): Function to call to load a dictionary of translations
          package (str): Optional package name (usually __package__), if not given
            pytlas will try to determine it based on the call stack

        """
        package = package or get_caller_package_name()

        if not should_load_resources(lang): # pragma: no cover
            self._logger.debug('Skipped "%s" translations for language "%s"',
                               package, lang)
        else:
            if package not in self._data:
                self._data[package] = {}

            self._data[package][lang] = func
            self._logger.info('Registered "%s.%s" translations for the lang "%s"',
                              package, func.__name__, lang)


# Global store instance
GLOBAL_TRANSLATIONS = TranslationsStore()


def translations(lang, store=None, package=None):
    """Decorator applied to a function that returns a dictionary to indicate translations.

    Args:
      lang (str): Lang of the translations
      store (TranslationsStore): Store to use for registration, defaults to the global one
      package (str): Optional package name (usually __package__), if not given pytlas
        will try to determine it based on the call stack

    """
    s = store or GLOBAL_TRANSLATIONS # pylint: disable=C0103

    def new(func):
        s.register(lang, func, package or get_caller_package_name()
                   or func.__module__)
        return func

    return new
