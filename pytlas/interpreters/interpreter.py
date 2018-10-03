import logging, hashlib, os, json
from pytlas.interpreters.slot import SlotValue
from pytlas.training import module_trainings
from pychatl.utils import deep_update
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
    data = json.dumps(data)

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

  def fit_from_skill_data(self):
    """Fit the interpreter with every training data registered in the system.
    """

    self._logger.info('Merging skill training data from "%d" modules' % len(module_trainings))

    data = {}

    for (module, module_data) in module_trainings.items():
      lang_data = module_data.get(self.lang)

      if lang_data:
        data = deep_update(data, lang_data)
      else:
        self._logger.warning('Skill "%s" does not seem to have training data for the lang "%s"' % (module, self.lang))

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
    return [SlotValue(msg)] # Default is to wrap the raw msg in a SlotValue

  def parse(self, msg):
    return []