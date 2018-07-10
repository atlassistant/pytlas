import logging

class Interpreter:

  def __init__(self):
    self._logger = logging.getLogger(self.__class__.__name__.lower())
    
    self.lang = None
    self.intents = []
  
  def fit_as_needed(self):
    pass

  def parse(self, msg):
    return []