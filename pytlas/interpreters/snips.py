import os, shutil
from pytlas.interpreters.interpreter import Interpreter, compute_checksum
from pytlas.interpreters.intent import Intent
from pytlas.interpreters.slot import SlotValue
from pytlas.utils import read_file
from snips_nlu import load_resources, SnipsNLUEngine, __version__
from snips_nlu.constants import ENTITIES, AUTOMATICALLY_EXTENSIBLE, RESOLVED_VALUE, \
  ENTITY_KIND, ENTITY, RES_VALUE, RES_RAW_VALUE, RES_INTENT, RES_INTENT_NAME, RES_SLOTS, \
  RES_SLOT_NAME
from snips_nlu.entity_parser.builtin_entity_parser import is_builtin_entity
import snips_nlu.default_configs as snips_confs

def get_entity_value(data):
  """Try to retrieve a flat value from a parsed snips entity.

  This is usefull for range where the `value` is not defined but `from` is.

  Args:
    data (dict): Entity data

  Returns:
    any: Flat value

  Example:
    >>> get_entity_value({ 'value': 'a value', 'from': '2018-09-05' })
    'a value'

    >>> get_entity_value({ 'from': '2018-09-05' })
    '2018-09-05'

  """

  return data.get(RES_VALUE, data.get('from'))

class SnipsInterpreter(Interpreter):
  """Wraps the snips-nlu stuff to provide valuable informations to an agent.
  """

  def __init__(self, lang, cache_directory=None):
    """Instantiates a new Snips interpreter.

    Args:
      lang (str): Language used for this interpreter (ie. en, fr, ...)
      cache_directory (str): Path where training and trained files are placed

    """

    super(SnipsInterpreter, self).__init__('snips', lang, cache_directory)

    self._engine = None
    self._slot_mappings = {}
    self._entities = {}

  def _configure(self):
    self._slot_mappings = self._engine._dataset_metadata.get('slot_name_mappings', {})
    self._entities = self._engine._dataset_metadata.get(ENTITIES, {})

    self.intents = list(self._slot_mappings.keys())

  def load_from_cache(self):
    self._logger.info('Loading engine from "%s"' % self.cache_directory)

    self._engine = SnipsNLUEngine.from_path(self.cache_directory)

    self._configure()

  def fit(self, data):
    data_lang = data.get('language')

    if data_lang != self.lang:
      self._logger.warning('Training language "%s" and interpreter language "%s" do not match, things could go badly' % (data_lang, self.lang))
    
    self._logger.info('Fitting using "snips v%s"' % __version__)

    checksum = compute_checksum(data)
    cached_checksum = None

    # Try to load the used checksum
    if self.cache_directory:
      cached_checksum_path = os.path.join(self.cache_directory, 'trained.checksum')
      cached_checksum = read_file(cached_checksum_path, ignore_errors=True)

    if not cached_checksum:
      self._logger.debug('Checksum file not found')

    if checksum == cached_checksum:
      self.load_from_cache()
    else:
      load_resources('snips_nlu_%s' % self.lang)

      config = None

      try:
        self._logger.info('Importing default configuration for language "%s"' % self.lang)
        config = getattr(snips_confs, 'CONFIG_%s' % self.lang.upper())
      except AttributeError:
        self._logger.warning('Could not import default configuration, it will use the generic one instead')

      self._engine = SnipsNLUEngine(config)
      self._engine.fit(data)

      if self.cache_directory:
        self._logger.info('Persisting trained engine to "%s"' % self.cache_directory)
        
        shutil.rmtree(self.cache_directory, ignore_errors=True)

        self._engine.persist(self.cache_directory)

        with open(cached_checksum_path, mode='w') as f:
          f.write(checksum)

      self._configure()

  @property
  def is_ready(self):
    """Returns true if the interpreter is ready.

    Returns:
      bool: Ready or not

    """

    return self._engine and self._engine.fitted

  def parse(self, msg):
    if not self.is_ready:
      return []

    # TODO manage multiple intents in the same sentence

    parsed = self._engine.parse(msg)

    if parsed[RES_INTENT] == None:
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

  def parse_slot(self, intent, slot, msg):
    if not self.is_ready:
      return []

    entity_label = self._slot_mappings.get(intent, {}).get(slot)

    # No label, just returns the given value
    if not entity_label:
      return [SlotValue(msg)]
      
    result = []

    # If it's a builtin entity, try to parse it
    if is_builtin_entity(entity_label):
      parsed = self._engine.builtin_entity_parser.parse(msg, [entity_label])

      for slot_data in parsed:
        # Here we move some keys to keep the returned meta consistent with the parse above
        # We are checking if `rawValue` is already present because snips-nlu seems to keep
        # a cache so to avoid mutating the same dict twice, we check again this added key.

        if RES_RAW_VALUE not in slot_data:
          slot_data[RES_RAW_VALUE] = slot_data[RES_VALUE]
          slot_data[RES_VALUE] = slot_data[ENTITY]
          slot_data[ENTITY] = slot_data[ENTITY_KIND]

        result.append(SlotValue(get_entity_value(slot_data[RES_VALUE]), **slot_data))
    else:
      parsed = self._engine.custom_entity_parser.parse(msg, [entity_label])

      # The custom parser did not found a match and it's extensible? Just returns the value
      if not parsed and self._entities.get(entity_label, {})[AUTOMATICALLY_EXTENSIBLE] == True:
        return [SlotValue(msg)]

      for slot_data in parsed:
        if RES_RAW_VALUE not in slot_data:
          slot_data[RES_RAW_VALUE] = slot_data[RES_VALUE]
          slot_data[RES_VALUE] = {
            'kind': 'Custom',
            RES_VALUE: slot_data[RESOLVED_VALUE],
          }
          slot_data[ENTITY] = slot_data[ENTITY_KIND]

        result.append(SlotValue(get_entity_value(slot_data[RES_VALUE]), **slot_data))

    return result