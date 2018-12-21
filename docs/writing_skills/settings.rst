Settings
========

Settings provides a basic handling of providing configuration variable to the user.

When you use the `pytlas repl`, you can provide a config file that will be parsed using `ConfigParser <https://docs.python.org/3/library/configparser.html>`_. If an environment variable matching `SECTION_SETTING` is available, it will override the config file value.

`pytlas.settings` also provides a wide range of methods to retrieve configuration values casted to a particular type.

.. code-block:: python

  from pytlas import settings

  # Get a string
  settings.get('openweather_key', 'a default value', section='pytlas.weather')

  # If you have exported the env PYTLAS_WEATHER_OPENWEATHER_KEY=apikey, then this
  # function will returns "apikey"

  # Arguments are the same for other helpers
  # settings.getint
  # settings.getfloat
  # settings.getlist
  # settings.getbool
  # settings.getpath

  # You can also programatically set a setting
  settings.set('a key', 'your value', section='pytlas.weather')