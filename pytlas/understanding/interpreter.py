# pylint: disable=C0111

import logging
import hashlib
import json
import pychatl.adapters as adapters
from pychatl import parse, merge
from pytlas.understanding.slot import SlotValue
from pytlas.understanding.training import GLOBAL_TRAININGS


def compute_checksum(data):
    """Generates a checksum from a raw string or object.

    If the given data is not a string, a json representation will be used.

    Args:
      data (str): Raw string to compute checksum for

    Returns:
      str: Computed checksum

    """

    if not isinstance(data, str):
        data = json.dumps(data, sort_keys=True)

    return hashlib.sha256(data.encode('utf-8')).hexdigest()


class Interpreter:
    """Base class for pytlas interpreters. They should convert human language to
    a more code friendly result: Intent and SlotValue.

    """

    def __init__(self, name, lang, cache_directory=None, trainings_store=None):
        """Instantiates a new interpreter.

        Args:
          name (str): Name of the interpreter
          lang (str): Language understood by this interpreter
          cache_directory (str): Optional directory to put cache data
          trainings_store (TrainingsStore): Optional trainings store used when fitting the engine

        """
        self._logger = logging.getLogger(name)
        self._trainings = trainings_store or GLOBAL_TRAININGS

        self.lang = lang
        self.name = name
        self.intents = []
        self.cache_directory = cache_directory

    def load_from_cache(self):
        """Loads the interpreter from the cache directory.
        """
        pass # pylint: disable=W0107

    def fit(self, data):
        """Fit the interpreter with given data.

        Args:
          data (dict): Training data

        """
        self._logger.debug(data)

    def fit_from_skill_data(self, skills=None): # pylint: disable=R1710
        """Fit the interpreter with every training data registered in the inner TrainingsStore.

        Args:
          skills (list of str): Optional list of skill names from which we should retrieve
            training data. Used to handle context understanding.

        """
        filtered_module_trainings = self._trainings.all(self.lang)

        if skills:
            filtered_module_trainings = {
                k: v for (k, v) in filtered_module_trainings.items() if k in skills}

        self._logger.info(
            'Merging skill training data from "%d" modules', len(filtered_module_trainings))

        data = {}
        sorted_trainings = sorted(filtered_module_trainings.items(),
                                  key=lambda x: x[0])

        for (module, training_dsl) in sorted_trainings:
            if training_dsl:
                try:
                    data = merge(data, parse(training_dsl))
                except Exception as err: # pylint: disable=W0703
                    self._logger.error(
                        'Could not parse "%s" training data: "%s"', module, err)
            else:
                self._logger.warning('No training data found for "%s"', module)

        try:
            data = getattr(adapters, self.name)(data, language=self.lang)
        except AttributeError:
            return self._logger.critical(
                'No post-processors found on pychatl for this interpreter!')

        self.fit(data)

    def fit_from_file(self, path):
        """Fit the interpreter from a training file path.

        Args:
          path (str): Path to the training file

        """
        self._logger.info('Training interpreter with file "%s"', path)

        with open(path, encoding='utf-8') as file:
            self.fit(json.load(file))

    def parse_slot(self, intent, slot, msg): # pylint: disable=W0613,R0201
        """Parses the given raw message to extract a slot matching given criterias.

        Args:
          intent (str): Name of the current intent
          slot (str): Name of the current slot to extract
          msg (str): Raw message to parse

        Returns:
          list of SlotValue: Slot values extracted

        """
        # Default is to wrap the raw msg in a SlotValue
        return [SlotValue(msg)]

    def parse(self, msg, scopes=None): # pylint: disable=W0613,R0201
        """Parses the given raw message and returns parsed intents.

        Args:
          msg (str): Message to parse
          scopes (list of str): Optional list of scopes used to restrict parsed intents

        Returns:
          list of Intent: Parsed intents

        """
        return []