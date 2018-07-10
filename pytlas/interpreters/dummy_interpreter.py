from .interpreter import Interpreter
from .slot import SlotValue
from .intent import Intent

class DummyInterpreter(Interpreter):
  
  def parse(self, msg):
    return [
      Intent('lights_on', rooms=[SlotValue('kitchen')]),
    ]