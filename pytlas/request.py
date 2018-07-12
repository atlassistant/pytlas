import uuid

class Request:
  """Tiny wrapper which represents a request sent to a skill handler.
  """
  
  def __init__(self, agent, intent, module_translations={}):
    self.agent = agent
    self.intent = intent
    self.id = uuid.uuid4().hex

    self._module_translations = module_translations

  def _(self, text):
    """Gets the translated value of the given text.

    Args:
      text (str): Text to translate

    Returns:
      str: Translated text or source text if no translation has been found

    """

    return self._module_translations.get(text, text)