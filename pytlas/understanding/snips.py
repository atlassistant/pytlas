# pylint: disable=missing-module-docstring,fixme

import os
import sys
import subprocess
from typing import List
import importlib
import pkg_resources
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse as parse_date
from snips_nlu import SnipsNLUEngine, __version__
from snips_nlu.resources import load_resources
from snips_nlu.constants import ENTITIES, AUTOMATICALLY_EXTENSIBLE, RESOLVED_VALUE, \
    ENTITY_KIND, ENTITY, RES_VALUE, RES_RAW_VALUE, RES_INTENT, RES_INTENT_NAME, RES_SLOTS, \
    RES_SLOT_NAME
from snips_nlu.entity_parser.builtin_entity_parser import is_builtin_entity
import snips_nlu.default_configs as snips_confs
from pytlas.understanding.intent import Intent
from pytlas.understanding.training import TrainingsStore
from pytlas.understanding.slot import SlotValue, UnitValue
from pytlas.understanding.interpreter import Interpreter, compute_checksum
from pytlas.ioutils import read_file, rmtree


def get_entity_value(data: dict) -> object:
    """Try to retrieve a flat value from a parsed snips entity.

    It will try to convert the parsed slot value to a python representation:

      - for Duration, it will returns a `dateutil.relativedelta` object
      - for AmountOfMoney and Temperature, it returns a `pytlas.interpreters.slot.UnitValue`
      - for Percentage, a float between 0 and 1
      - for InstantTime, a `datetime.datetime` object,
      - for TimeInterval, a tuple of `datetime.datetime` objects,
      - for anything else, a string

    Args:
      data (dict): Entity data

    Returns:
      any: A python object which match the slot value kind

    """
    kind = data.get('kind')

    if kind == 'Duration': # pylint: disable=no-else-return
        return relativedelta(
            days=data.get('days'),
            hours=data.get('hours'),
            minutes=data.get('minutes'),
            months=data.get('months'),
            seconds=data.get('seconds'),
            weeks=data.get('weeks'),
            years=data.get('years'),
        )
    elif kind in ('AmountOfMoney', 'Temperature'):
        return UnitValue(data.get('value'), data.get('unit'))
    elif kind == 'Percentage':
        return data.get('value') / 100.0
    elif kind == 'InstantTime':
        return parse_date(data.get('value'))
    elif kind == 'TimeInterval':
        return (parse_date(data.get('from')), parse_date(data.get('to')))

    return data.get('value')


class SnipsInterpreter(Interpreter):
    """Wraps the snips-nlu stuff to provide valuable informations to an agent.
    """

    def __init__(self,
                 lang: str,
                 cache_directory: str = None,
                 trainings_store: TrainingsStore = None) -> None:
        """Instantiates a new Snips interpreter.

        Args:
          lang (str): Language used for this interpreter (ie. en, fr, ...)
          cache_directory (str): Path where training and trained files are placed
          trainings_store (TrainingsStore): Optional trainings store used when fitting the engine

        """
        super(SnipsInterpreter, self).__init__(
            'snips', lang, cache_directory, trainings_store)

        self._engine = None
        self._slot_mappings = {}
        self._entities = {}

    def _configure(self) -> None:
        self._slot_mappings = self._engine.dataset_metadata.get(
            'slot_name_mappings', {})
        self._entities = self._engine.dataset_metadata.get(ENTITIES, {})

        self.intents = list(self._slot_mappings.keys())

    def load_from_cache(self) -> None:
        self._logger.info('Loading engine from "%s"', self.cache_directory)
        self._engine = SnipsNLUEngine.from_path(self.cache_directory)
        self._configure()

    def _check_and_install_resources_package(self) -> None:
        resource_pkg_name = f'snips_nlu_{self.lang}'

        if not importlib.util.find_spec(resource_pkg_name):
            self._logger.info(
                'Could not import resource package "%s", attempting installation',
                resource_pkg_name)

            try:
                subprocess.run([sys.executable, '-m', 'snips_nlu', 'download',
                                self.lang], check=True, stdout=subprocess.PIPE)
                self._logger.info(
                    'Successfuly downloaded "%s"!', resource_pkg_name)
                # Reload resources (used by snips to determine if resources are installed)
                importlib.reload(pkg_resources)
            except:  # pragma: no cover pylint: disable=W0702
                self._logger.warning(
                    'Looks like it fails, you may have to do it manually with: '\
                    '"python -m snips_nlu download %s"',
                    self.lang)

        return resource_pkg_name

    def fit(self, data: dict) -> None:
        super().fit(data)

        data_lang = data.get('language')

        if data_lang != self.lang:  # pragma: no cover
            self._logger.warning(
                'Training language "%s" and interpreter language "%s" do not match,'\
                'things could go badly',
                data_lang, self.lang)

        self._logger.info('Fitting using "snips v%s"', __version__)

        checksum = compute_checksum(data)
        cached_checksum = None

        # Try to load the used checksum
        if self.cache_directory:
            cached_checksum_path = os.path.join(
                self.cache_directory, 'trained.checksum')
            cached_checksum = read_file(
                cached_checksum_path, ignore_errors=True)

        if not cached_checksum:
            self._logger.debug('Checksum file not found')

        if checksum == cached_checksum:
            self.load_from_cache()
        else:
            config = None

            try:
                self._logger.info(
                    'Importing default configuration for language "%s"', self.lang)
                config = getattr(snips_confs, 'CONFIG_%s' % self.lang.upper())
            except AttributeError:
                self._logger.warning(
                    'Could not import default configuration, it will use the generic one instead')

            resource_pkg_name = self._check_and_install_resources_package()

            self._engine = SnipsNLUEngine(
                config, resources=load_resources(resource_pkg_name))
            self._engine.fit(data)

            if self.cache_directory:  # pragma: no cover
                self._logger.info(
                    'Persisting trained engine to "%s"', self.cache_directory)

                # Make sure the cache directory has been cleaned out
                rmtree(self.cache_directory, ignore_errors=True)

                self._engine.persist(self.cache_directory)

                with open(cached_checksum_path, mode='w') as file:
                    file.write(checksum)

            self._configure()

    @property
    def is_ready(self) -> bool:
        """Returns true if the interpreter is ready.

        Returns:
          bool: Ready or not

        """
        return self._engine and self._engine.fitted

    def parse(self, msg: str, scopes: List[str] = None) -> List[Intent]:
        if not self.is_ready:
            return []

        # TODO manage multiple intents in the same sentence

        parsed = self._engine.parse(msg, intents=scopes)

        if not parsed[RES_INTENT][RES_INTENT_NAME]:
            return []

        slots = {}

        for slot in parsed[RES_SLOTS]:
            name = slot[RES_SLOT_NAME]
            parsed_slot = slot[RES_VALUE]
            value = SlotValue(get_entity_value(parsed_slot), **slot)

            if name in slots:
                slots[name].append(value)
            else:
                slots[name] = [value]

        return [
            Intent(parsed[RES_INTENT][RES_INTENT_NAME], **slots),
        ]

    def parse_slot(self, intent: str, slot: str, msg: str) -> List[SlotValue]:
        if not self.is_ready:
            return []

        # Here I still use my own method to parse slots because it gives better
        # results in my benchmarks.
        #
        # However, we should keep an eye on https://github.com/snipsco/snips-nlu/pull/724
        # for when it becomes relevant. For now get_slots returns less results than this
        # homemade method below.

        entity_label = self._slot_mappings.get(intent, {}).get(slot)

        # No label, just returns the given value
        if not entity_label:
            return [SlotValue(msg)]

        result = []

        # If it's a builtin entity, try to parse it
        if is_builtin_entity(entity_label):
            parsed = self._engine.builtin_entity_parser.parse(
                msg, [entity_label])

            for slot_data in parsed:
                # Here we move some keys to keep the returned meta consistent with the parse above
                # We are checking if `rawValue` is already present because snips-nlu seems to keep
                # a cache so to avoid mutating the same dict twice, we check again this added key.

                if RES_RAW_VALUE not in slot_data:
                    slot_data[RES_RAW_VALUE] = slot_data[RES_VALUE]
                    slot_data[RES_VALUE] = slot_data[RESOLVED_VALUE]
                    slot_data[ENTITY] = slot_data[ENTITY_KIND]

                result.append(SlotValue(get_entity_value(
                    slot_data[RES_VALUE]), **slot_data))
        else:
            parsed = self._engine.custom_entity_parser.parse(
                msg, [entity_label])

            # The custom parser did not found a match and it's extensible? Just returns the value
            if not parsed and self._entities.get(entity_label, {})[AUTOMATICALLY_EXTENSIBLE]:
                return [SlotValue(msg)]

            for slot_data in parsed:
                if RES_RAW_VALUE not in slot_data:
                    slot_data[RES_RAW_VALUE] = slot_data[RES_VALUE]
                    slot_data[RES_VALUE] = {
                        'kind': 'Custom',
                        RES_VALUE: slot_data[RESOLVED_VALUE],
                    }
                    slot_data[ENTITY] = slot_data[ENTITY_KIND]

                result.append(SlotValue(get_entity_value(
                    slot_data[RES_VALUE]), **slot_data))

        return result
