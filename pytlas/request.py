import uuid, logging

class AgentProxy:
  """Returns an agent proxy to silent down some methods (ask, answer and done) for skills
  that has been canceled. This is easier that running in subprocess and work well.

  So a skill may launch its own async task in a thread and reply back with the agent when it's done
  and if the user has cancel the action, its reply will be silented by this proxy.

  """

  def __init__(self, request, agent):
    self._request = request
    self._agent = agent
    self._silent_methods = ['ask', 'answer', 'done']

  def empty_func(self, *args, **kwargs):
    pass

  def __getattr__(self, attr):
    if self._agent._is_current_request(self._request) or attr not in self._silent_methods:
      return getattr(self._agent, attr)

    logging.debug('Silented "%s" call from the stub' % attr)
    return self.empty_func

class Request:
  """Tiny wrapper which represents a request sent to a skill handler.
  """
  
  def __init__(self, agent, intent, module_translations={}):
    self.intent = intent
    self.id = uuid.uuid4().hex
    self.agent = AgentProxy(self, agent)

    self._module_translations = module_translations

  def _(self, text):
    """Gets the translated value of the given text.

    Args:
      text (str): Text to translate

    Returns:
      str: Translated text or source text if no translation has been found

    """

    return self._module_translations.get(text, text)