import logging
from .slot import SlotValue

class Interpreter:

  def __init__(self):
    self._logger = logging.getLogger(self.__class__.__name__.lower())
    
    self.lang = None
    self.intents = []
  
  def fit_as_needed(self):
    pass

  def parse_slot(self, intent, slot, msg):
    return [SlotValue(msg)] # Default is to wrap the raw msg in a SlotValue

  def parse(self, msg):
    return []