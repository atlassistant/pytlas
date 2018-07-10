import logging
from .request import Request
from transitions import Machine

PREFIX = 'pytlas/'
STATE_ASLEEP = PREFIX + 'asleep'
STATE_CANCEL = PREFIX + 'cancel'
STATE_ASK = PREFIX + 'ask'

class Agent:

  def __init__(self, interpreter, client, handlers={}, **kwargs):
    self._logger = logging.getLogger(self.__class__.__name__.lower())
    self._interpreter = interpreter
    self._client = client
    self._handlers = handlers
    self._intents_queue = []
    self._request = None
    self._asked_slot = None

    # Contains all metadata tied to this particular instance
    # This will be added to the Request object before sending it
    self._meta = kwargs

    self._machine = None
    self._init_state_machine()

  def _init_state_machine(self):
    states = [STATE_ASLEEP, STATE_ASK, STATE_CANCEL] + self._interpreter.intents
    self._machine = Machine(model=self, states=states, initial=STATE_ASLEEP)

    self._logger.info('Instantiated agent with %s states: %s' % (len(states), ', '.join(states)))

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

      self._logger.info('💬 New "%s" conversation started with id %s' % (intent.name, self._request.id))

      self._handlers[intent.name](self._request)

    self.end()

  def _process_next_intent(self):
    if len(self._intents_queue) > 0:
      self.process(self._intents_queue.pop(0))

  def _go(self, state, **kwargs):
    pass

  def ask(self, slot, text):
    """Ask something to the user.
    """

    self._go(STATE_ASK, slot=slot, text=text)

  def answer(self, text):
    """Answer something to the user.
    """

    self._client.answer(text)

  def end(self):
    """Ends a conversation, means nothing would come from the skill anymore and
    it does not require user inputs. This is especially useful when you are showing
    an activity indicator.

    """

    if not self._asked_slot:
      self._logger.info('Conversation ended')
      self._request = None
      self._client.end()
      self._process_next_intent()