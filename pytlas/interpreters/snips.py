import os, json, shutil
from .interpreter import Interpreter, compute_checksum
from .intent import Intent
from .slot import SlotValue
from snips_nlu import load_resources, SnipsNLUEngine, __version__
from snips_nlu.builtin_entities import BuiltinEntityParser, is_builtin_entity

class SnipsInterpreter(Interpreter):
  """Wraps the snips-nlu stuff to provide valuable informations to an agent.
  """

  def __init__(self, training_directory, persist=True):
    """Instantiates a new Snips interpreter.

    Args:
      training_directory (str): Path where training and trained files are placed
      persist (bool): True if trained engine should be persisted

    """

    super(SnipsInterpreter, self).__init__(training_directory)

    self._engine = None
    self._entity_parser = None
    self._persist = persist

  def fit_as_needed(self):
    self._logger.info('Using "snips v%s"' % __version__)

    cache_directory = os.path.join(self.training_directory, 'cache')
    training_filepath = os.path.join(self.training_directory, 'training.json')
    checksum_filepath = os.path.join(cache_directory, 'training.checksum')

    training_checksum = None
    computed_checksum = None

    # Computes training checksum first
    with open(training_filepath) as f:
      training_str = f.read()
      training_checksum = compute_checksum(training_str)
      training_data = json.loads(training_str)

      self.lang = training_data.get('language', 'en')

    try:
      with open(checksum_filepath) as f:
        computed_checksum = f.read()
    except FileNotFoundError:
      pass

    if training_checksum == computed_checksum:
      self._logger.info('Checksums matched, loading engine from "%s"' % cache_directory)
      self._engine = SnipsNLUEngine.from_path(cache_directory) 
    else:
      shutil.rmtree(cache_directory, ignore_errors=True)

      self._logger.info('Checksum has changed, retraining the engine from "%s"' % self.training_directory)
      
      load_resources(self.lang)

      self._engine = SnipsNLUEngine()
      self._engine.fit(training_data)

      if self._persist:
        self._logger.info('Persisting trained engine to "%s"' % cache_directory)
        self._engine.persist(cache_directory)

        with open(checksum_filepath, mode='w') as f:
          f.write(training_checksum)

    self._entity_parser = BuiltinEntityParser(self.lang)
    self.intents = list(self._engine._dataset_metadata.get('slot_name_mappings', {}).keys())

  def parse(self, msg):
    # TODO manage multiple intents in the same sentence

    parsed = self._engine.parse(msg)

    print (json.dumps(parsed, indent=2))

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
    return super(SnipsInterpreter, self).parse_slot(intent, slot, msg)