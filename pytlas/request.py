import uuid

class Request:
  """Tiny wrapper which represents a request sent to a skill handler.
  """
  
  def __init__(self, agent, intent):
    self.agent = agent
    self.intent = intent
    
    self.lang = self.agent._interpreter.lang
    self.id = uuid.uuid4().hex