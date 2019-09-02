.. _settings:

Settings
========

Settings provides a facility to enable developers to retrieve settings value.

The `pytlas.settings` module exposes a `SettingsStore` class and a global
instance of this class in its `CONFIG` property.

The `SettingsStore` read settings from 3 sources:

- A `ConfigParser <https://docs.python.org/3/library/configparser.html>`_ instance
- System environment variables
- `additional_lookup` property used at construction

So when you request a value from a store object for a section **pytlas** and
a key **my_setting**, it will first try to find a key in `additional_lookup`
matching `PYTLAS_MY_SETTING`, if not found, it will look for the same key in
the OS environment variables and if it's still can't find a match, it will look
in the `ConfigParser` instance for the section and the key provided.

This order make it easy to override config file settings by using environment
variables or, as seen below, using agent metadata.

The store also provides a wide range of methods to retrieve configuration
values casted to a particular type.

.. code-block:: python

  from pytlas import intent
  from pytlas.settings import CONFIG

  # Load a setting file
  CONFIG.load_from_file('file/path/pytlas.ini')

  # Get a string
  CONFIG.get('openweather_key', 'a default value', section='pytlas.weather')

  # If you have exported the env PYTLAS_WEATHER_OPENWEATHER_KEY=apikey, then this
  # function will returns "apikey"

  # Arguments are the same for other helpers
  # CONFIG.getint
  # CONFIG.getfloat
  # CONFIG.getlist
  # CONFIG.getbool
  # CONFIG.getpath

  # You can also programatically set a setting
  CONFIG.set('a key', 'your value', section='pytlas.weather')

  @intent('my_intent')
  def my_handler(r):
    # Inside an handler, you can use the `agent.settings` property which is a `SettingsStore`
    # instance extending the global one with the agent metadata.
    #
    # It is useful to allow agent to override some settings such as api keys.
    #
    # The following line will returns the settings from agent meta first, if not found,
    # from env variables and if still not found, from the loaded config file.
    r.agent.settings.get('openweather_key', 'a default value', section='pytlas.weather')
