import logging
from .request import Request

class Agent:

  def __init__(self, interpreter, client, handlers={}):
    self._logger = logging.getLogger(self.__class__.__name__.lower())
    self._interpreter = interpreter
    self._client = client
    self._handlers = handlers
    self._intents_queue = []
    self._request = None
    self._asked_slot = None

    self.lang = self._interpreter.lang
    self.conversation_id = None

  def parse(self, msg):
    """Parse a raw message.
    """

    self._logger.info('Parsing sentence "%s"' % msg)

    intents = self._interpreter.parse(msg)

    self._logger.info('%s intent(s) found: %s' % (len(intents), ', '.join([str(i) for i in intents])))

    self._intents_queue.extend(intents)
    self._process_next_intent()

  def process(self, intent):
    self._logger.info('Processing intent %s' % intent)
    
    if intent.name not in self._handlers:
      self._logger.error('No handler found for the intent "%s"' % intent.name)
    else:
      self._request = Request(self, intent)
      self._handlers[intent.name](self._request)
      self.end()

  def _process_next_intent(self):
    if len(self._intents_queue) > 0:
      self.process(self._intents_queue.pop(0))

  def ask(self):
    """Ask something to the user.
    """

    pass

  def answer(self):
    """Answer something to the user.
    """

    pass

  def end(self):
    """Ends a conversation, means nothing would come from the skill anymore and
    it does not require user inputs.

    """

    if not self._asked_slot:
      self._logger.info('Conversation ended')
      self._request = None
      self._process_next_intent()
      self._client.end()