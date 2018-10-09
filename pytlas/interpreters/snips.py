import os, shutil
from pytlas.interpreters.interpreter import Interpreter, compute_checksum
from pytlas.interpreters.intent import Intent
from pytlas.interpreters.slot import SlotValue
from pytlas.utils import read_file
from snips_nlu import load_resources, SnipsNLUEngine, __version__
from snips_nlu.entity_parser.builtin_entity_parser import BuiltinEntityParser, is_builtin_entity
from fuzzywuzzy import process
import snips_nlu.default_configs as snips_confs

def get_entity_value(data):
  """Try to retrieve a flat value from a parsed snips entity.

  This is usefull for range where the `value` is not defined but `from` is.

  Args:
    data (dict): Entity data

  Returns:
    any: Flat value

  >>> get_entity_value({ 'value': 'a value', 'from': '2018-09-05' })
  'a value'

  >>> get_entity_value({ 'from': '2018-09-05' })
  '2018-09-05'

  """

  return data.get('value', data.get('from'))

def extract_synonyms_from_dataset(data):
  """Extract and flatten synonyms from the dataset. Needed since snips-nlu v0.17.0 which
  does not include entities utterances anymore.

  Args:
    data (dict): Training dataset

  Returns:
    dict: Flattened synonyms

  """

  result = {}

  for (entity_name, entity) in data.get('entities').items():
    result[entity_name] = {}

    for d in entity.get('data', []):
      v = d.get('value')
      result[entity_name][v] = v

      for synonym in d.get('synonyms', []):
        result[entity_name][synonym] = v

  return result

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
    self._entity_parser = BuiltinEntityParser.build(language=self.lang)
    self._slot_mappings = {}
    self._entities = {}
    self._entities_synonyms = {}

  def _configure(self):
    self._slot_mappings = self._engine._dataset_metadata.get('slot_name_mappings', {})
    self._entities = self._engine._dataset_metadata.get('entities', {})

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
    
    # Everything was ok, we can now extract synonyms from the dataset
    self._entities_synonyms = extract_synonyms_from_dataset(data)

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
      value = SlotValue(get_entity_value(parsed_slot), **slot)

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
          # Here we move some keys to keep the returned meta consistent with the parse above
          # We are checking if `rawValue` is already present because snips-nlu seems to keep
          # a cache so to avoid mutating the same dict twice, we check again this added key.

          slot_data = parsed[0]

          if 'rawValue' not in slot_data:
            slot_data['rawValue'] = slot_data['value']
            slot_data['value'] = slot_data['entity']
            slot_data['entity'] = slot_data['entity_kind']

          return [SlotValue(get_entity_value(slot_data['value']), **slot_data)]
        else:
          # If the parsing has failed, the user should reiterate
          return []
      else:
        entity = self._entities.get(entity_label)

        # Not automatically extensible, try to fuzzy match it
        if entity and entity['automatically_extensible'] == False:
            choices = set([k.lower() for k in self._entities_synonyms[entity_label].keys()])
            results = [self._entities_synonyms[entity_label][r[0]] for r in process.extractBests(msg, choices, score_cutoff=60)]
                        
            return [SlotValue(r) for r in results]

    return super(SnipsInterpreter, self).parse_slot(intent, slot, msg)