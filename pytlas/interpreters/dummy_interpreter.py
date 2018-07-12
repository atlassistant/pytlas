from .interpreter import Interpreter
from .slot import SlotValue
from .intent import Intent
from ..skill import handlers

class DummyInterpreter(Interpreter):

  def __init__(self):
    super(DummyInterpreter, self).__init__()

    self.lang = 'fr'
    self.intents = list(handlers.keys())
  
  def parse_slot(self, intent, slot, msg):
    return [
      SlotValue(msg),
    ]

  def parse(self, msg):
    return [
      Intent('lights_on'),
    ]