# pylint: disable=C0111

import logging
from copy import deepcopy


class Store: # pylint: disable=R0903
    """Basic class to store configuration data for this library. Data will be
    stores in the `_data` property but chidren should implements getter/setter tied
    to their domain.

    It also exposes a logger instance in `_logger` to be used by chidren.
    """

    def __init__(self, name, initial_data=None):
        """Creates a new store instance.

        Args:
          name (str): Name of the store
          initial_data (dict): Initial data to populate the store with

        """
        self.name = name
        self._initial_data = initial_data or {}
        self._logger = logging.getLogger(self.name)
        self.reset()

    def reset(self):
        """Reset the store data to the initial value provided at construction.
        """
        self._data = deepcopy(self._initial_data)
