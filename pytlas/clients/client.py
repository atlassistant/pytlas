class Client:
  """Base interface for a client to implement.
  """

  def ask(self, slot, text, choices):
    pass

  def answer(self, text):
    pass

  def done(self):
    pass