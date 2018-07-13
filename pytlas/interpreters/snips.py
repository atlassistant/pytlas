import os, json
from .interpreter import Interpreter, compute_checksum
from .intent import Intent
from .slot import SlotValue
from snips_nlu import load_resources, SnipsNLUEngine, __version__
from snips_nlu.builtin_entities import BuiltinEntityParser, is_builtin_entity

class SnipsInterpreter(Interpreter):
  """Wraps the snips-nlu stuff to provide valuable informations to an agent.
  """

  def __init__(self, training_filepath, output_directory):
    """Instantiates a new Snips interpreter.

    Args:
      training_filepath (str): Path to the training file
      output_directory (str): Directory where to put computed file and checksum

    """

    super(SnipsInterpreter, self).__init__(training_filepath)

    self._output_directory = output_directory
    self._engine = None
    self._entity_parser = None

  def fit_as_needed(self):
    self._logger.info('Using "snips v%s"' % __version__)

    training_filename, _ = os.path.splitext(os.path.basename(self.training_filepath))
    checksum_filepath = os.path.join(self._output_directory, training_filename + '.checksum')
    output_filepath = os.path.join(self._output_directory, training_filename + '.trained.json')

    training_checksum = None
    computed_checksum = None

    # Computes training checksum first
    with open(self.training_filepath) as f:
      training_str = f.read()
      training_checksum = compute_checksum(training_str)
      training_data = json.loads(training_str)

      self.lang = training_data.get('language', 'en')
      load_resources(self.lang)

    try:
      with open(checksum_filepath) as f:
        computed_checksum = f.read()
    except FileNotFoundError:
      pass

    if training_checksum == computed_checksum and os.path.isfile(output_filepath):
      self._logger.info('Checksums matched, loading engine from "%s"' % output_filepath)

      with open(output_filepath) as f:
        self._engine = SnipsNLUEngine.from_dict(json.load(f))
    else:
      self._logger.info('Checksum has changed, retraining the engine from "%s"' % self.training_filepath)

      self._engine = SnipsNLUEngine()
      self._engine.fit(training_data)

      with open(output_filepath, mode='w') as f:
        json.dump(self._engine.to_dict(), f)

      with open(checksum_filepath, mode='w') as f:
        f.write(computed_checksum)

    self._entity_parser = BuiltinEntityParser(self.lang)
    self.intents = list(self._engine._dataset_metadata.get('slot_name_mappings', {}).keys())

  def parse(self, msg):
    # TODO manage multiple intents in the same sentence

    parsed = self._engine.parse(msg)

    if parsed['intent'] == None:
      return []

    slots = {}

    for slot in parsed['slots']:
      name = slot['slotName']
      parsed_slot = slot['value']
      value = SlotValue(parsed_slot.get('value'), **parsed_slot)

      if name in slots:
        slots[name].append(value)
      else:
        slots[name] = [value]

    return [
      Intent(parsed['intent']['intentName'], **slots),
    ]