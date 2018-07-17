import logging, hashlib
from .slot import SlotValue

def compute_checksum(data):
  """Generates a checksum from a raw string.
  
  Args:
    data (str): Raw string to compute checksum for

  Returns:
    str: Computed checksum

  """

  return hashlib.sha256(data.encode('utf-8')).hexdigest()

class Interpreter:
  """Base class for pytlas interpreters. They should convert human language to
  a more code friendly result: Intent and SlotValue.

  """

  def __init__(self, training_directory=None):
    self._logger = logging.getLogger(self.__class__.__name__.lower())
    
    self.lang = None
    self.intents = []
    self.training_directory = training_directory
  
  def fit_as_needed(self):
    """Fit the interpreter if it's needed (ie. the checksum does not match).
    """

    pass

  def parse_slot(self, intent, slot, msg):
    return [SlotValue(msg)] # Default is to wrap the raw msg in a SlotValue

  def parse(self, msg):
    return []