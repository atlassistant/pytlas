import os, json, shutil
from .interpreter import Interpreter, compute_checksum
from .intent import Intent
from .slot import SlotValue
from snips_nlu import load_resources, SnipsNLUEngine, __version__
from snips_nlu.builtin_entities import BuiltinEntityParser, is_builtin_entity
from fuzzywuzzy import process
# from snips_nlu.default_configs import CONFIG_EN

class SnipsInterpreter(Interpreter):
  """Wraps the snips-nlu stuff to provide valuable informations to an agent.
  """

  def __init__(self, training_directory, persist=True):
    """Instantiates a new Snips interpreter.

    Args:
      training_directory (str): Path where training and trained files are placed
      persist (bool): True if trained engine should be persisted

    """

    super(SnipsInterpreter, self).__init__('snips', training_directory)

    self._engine = None
    self._entity_parser = None
    self._persist = persist

  def fit_as_needed(self):
    self._logger.info('Using "snips v%s"' % __version__)

    training_checksum = None
    cached_checksum = None

    # Try to computes training checksum first
    try:
      with open(self.training_filepath) as f:
        training_str = f.read()
        training_checksum = compute_checksum(training_str)
        training_data = json.loads(training_str)

        self.lang = training_data['language']
    except FileNotFoundError:
      # No training file, do nothing
      self._logger.warning('No training file found, engine will be not fitted!')

      training_checksum = None
      training_data = None
      self.lang = 'en'

    # Try to open the cached checksum
    try:
      with open(self.checksum_filepath) as f:
        cached_checksum = f.read()
    except FileNotFoundError:
      self._logger.debug('Checksum file not found')

    # If they matched, load the engine from the cache directory
    if training_checksum and training_checksum == cached_checksum:
      self._logger.info('Checksums matched, loading engine from "%s"' % self.cache_directory)
      self._engine = SnipsNLUEngine.from_path(self.cache_directory) 
    else:
      # Else retrain it
      self._logger.info('Checksum has changed, retraining the engine from "%s"' % self.training_directory)
      
      load_resources('snips_nlu_%s' % self.lang)

      self._engine = SnipsNLUEngine()

      # If we have training data, fit the engine
      if training_data:
        self._engine.fit(training_data)

      # If we want to cache our engine, do it now!
      if self._persist:
        self._logger.info('Persisting trained engine to "%s"' % self.cache_directory)
        
        shutil.rmtree(self.cache_directory, ignore_errors=True)

        self._engine.persist(self.cache_directory)

        if training_checksum:
          with open(self.checksum_filepath, mode='w') as f:
            f.write(training_checksum)

    self._entity_parser = BuiltinEntityParser(self.lang)

    if self._engine._dataset_metadata:
      self._slot_mappings = self._engine._dataset_metadata.get('slot_name_mappings', {})
      self._entities = self._engine._dataset_metadata.get('entities', {})
    else:
      self._slot_mappings = {}
      self._entities = {}

    self.intents = list(self._slot_mappings.keys())

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

    if parsed['intent'] == None:
      return []

    slots = {}

    for slot in parsed['slots']:
      name = slot['slotName']
      parsed_slot = slot['value']
      value = SlotValue(parsed_slot.get('value'), **slot)

      if name in slots:
        slots[name].append(value)
      else:
        slots[name] = [value]

    return [
      Intent(parsed['intent']['intentName'], **slots),
    ]

  def parse_slot(self, intent, slot, msg):
    if not self.is_ready:
      return []

    entity_label = self._slot_mappings.get(intent, {}).get(slot)

    if entity_label:
      # If it's a builtin entity, try to parse it
      if is_builtin_entity(entity_label):
        parsed = self._entity_parser.parse(msg)

        if parsed:
          return [SlotValue(parsed[0]['entity'].get('value'), **parsed[0])]
        else:
          # If the parsing has failed, the user should reiterate
          return []
      else:
        entity = self._entities.get(entity_label)

        # Not automatically extensible, try to fuzzy match it
        if entity and entity['automatically_extensible'] == False:
            choices = set(entity['utterances'].values()) # TODO use keys instead for synonyms
            results = process.extractBests(msg, choices, score_cutoff=60)
            
            return [SlotValue(r[0]) for r in results]

    return super(SnipsInterpreter, self).parse_slot(intent, slot, msg)