# pylint: disable=missing-module-docstring

import logging
from copy import deepcopy


class Store: # pylint: disable=too-few-public-methods
    """Basic class to store configuration data for this library. Data will be
    stores in the `_data` property but chidren should implements getter/setter tied
    to their domain.

    It also exposes a logger instance in `_logger` to be used by chidren.
    """

    def __init__(self, name: str, initial_data: dict = None) -> None:
        """Creates a new store instance.

        Args:
          name (str): Name of the store
          initial_data (dict): Initial data to populate the store with

        """
        self.name = name
        self._initial_data = initial_data or {}
        self._logger = logging.getLogger(self.name)
        self.reset()

    def reset(self) -> None:
        """Reset the store data to the initial value provided at construction.
        """
        self._data = deepcopy(self._initial_data)

    def _set(self, value: object, *names: str) -> None:
        """Safely sets the given value in the nested path.

        Args:
            value (any): Value to set
            names (list of str): Path parts

        """
        cur = self._data

        for name in names[:-1]:
            if name not in cur:
                cur[name] = {}
            cur = cur[name]

        cur[names[-1]] = value
