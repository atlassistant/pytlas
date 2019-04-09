import logging, hashlib, os, json
from pytlas.interpreters.slot import SlotValue
from pytlas.training import get_training_data
from pychatl.utils import deep_update
from pychatl import parse
import pychatl.postprocess as postprocessors

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

  def __init__(self, name, lang, cache_directory=None):
    self._logger = logging.getLogger(name)
    
    self.lang = lang
    self.name = name
    self.intents = []
    self.cache_directory = cache_directory

  def load_from_cache(self):
    """Loads the interpreter from the cache directory.
    """

    pass

  def fit(self, data):
    """Fit the interpreter with given data.
    
    Args:
      data (dict): Training data

    """

    pass

  def fit_from_skill_data(self, skills=None):
    """Fit the interpreter with every training data registered in the system.

    Args:
      skills (list of str): Optional list of skill names from which we should retrieve training data.
    
    """

    filtered_module_trainings = get_training_data(self.lang)

    if skills:
      filtered_module_trainings = { k: v for (k, v) in filtered_module_trainings.items() if k in skills }

    self._logger.info('Merging skill training data from "%d" modules' % len(filtered_module_trainings))

    data = {}
    sorted_trainings = sorted(filtered_module_trainings.items(), 
      key=lambda x: x[0])

    for (module, training_dsl) in sorted_trainings:
      if training_dsl:
        try:
          data = deep_update(data, parse(training_dsl))
        except Exception as e:
          self._logger.error('Could not parse "%s" training data: "%s"' % (module, e))
      else:
        self._logger.warning('No training data found for "%s"' % module)
      
    try:
      data = getattr(postprocessors, self.name)(data, language=self.lang)
    except AttributeError:
      return self._logger.critical('No post-processors found on pychatl for this interpreter!')

    self.fit(data)

  def fit_from_file(self, path):
    """Fit the interpreter from a training file path.

    Args:
      path (str): Path to the training file

    """

    self._logger.info('Training interpreter with file "%s"' % path)

    with open(path, encoding='utf-8') as f:
      self.fit(json.load(f))

  def parse_slot(self, intent, slot, msg):
    """Parses the given raw message to extract a slot matching given criterias.

    Args:
      intent (str): Name of the current intent
      slot (str): Name of the current slot to extract
      msg (str): Raw message to parse

    Returns:
      list of SlotValue: Slot values extracted

    """

    return [SlotValue(msg)] # Default is to wrap the raw msg in a SlotValue

  def parse(self, msg, scopes=None):
    """Parses the given raw message and returns parsed intents.

    Args:
      msg (str): Message to parse
      scopes (list of str): Optional list of scopes used to restrict parsed intents
    
    Returns:
      list of Intent: Parsed intents
    
    """

    return []