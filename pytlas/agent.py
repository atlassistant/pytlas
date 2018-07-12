import logging, random
from .request import Request
from .skill import handlers as skill_handlers
from transitions import Machine, MachineError

logging.getLogger('transitions').setLevel(logging.WARNING)

STATE_PREFIX = 'pytlas/'
STATE_ASLEEP = STATE_PREFIX + 'asleep'
STATE_CANCEL = STATE_PREFIX + 'cancel'
STATE_FALLBACK = STATE_PREFIX + 'fallback'
STATE_ASK = STATE_PREFIX + 'ask'

def is_builtin(state):
  """Checks if the given state is a builtin one.
  
  Args:
    state (str): State to check

  Returns:
    bool: True if it's a builtin state, false otherwise

  """

  return state.startswith(STATE_PREFIX)

def keep_one(value):
  """Keeps only one element if value is a list.

  Args:
    value (str, list): Value to check

  Returns:
    str: Random value in the given list if it's a list, else the given value

  """

  if type(value) is list:
    return random.choice(value)

  return value

class Agent:
  """Manages a conversation with a client.

  Conversation state is represented by a finite state machine. It handle ask states
  when the skill needs more information and trigger appropriate handler upon intent
  parsing.

  """

  def __init__(self, interpreter, client, handlers=None, **kwargs):
    self._logger = logging.getLogger(self.__class__.__name__.lower())
    self._interpreter = interpreter
    self._client = client
    self._handlers = handlers or skill_handlers

    self._intents_queue = []
    self._request = None
    self._asked_slot = None
    self._choices = None
    
    self.meta = kwargs

    self._machine = None
    self._init_state_machine()

  def _init_state_machine(self):
    intents = [i for i in self._interpreter.intents if not is_builtin(i)]
    states = [STATE_ASLEEP, STATE_ASK, STATE_FALLBACK, STATE_CANCEL] + intents
    
    self._machine = Machine(
      model=self, 
      states=states, 
      send_event=True,
      before_state_change=self._log_transition,
      initial=STATE_ASLEEP)

    self._logger.info('Instantiated agent with %s states: %s' % (len(states), ', '.join(states)))

    # Go to the asleep state from anywhere except the ask state
    self._machine.add_transition(
      STATE_ASLEEP, 
      [STATE_CANCEL, STATE_FALLBACK] + intents,
      STATE_ASLEEP,
      after=self.end_conversation)

    # Go to the cancel state from anywhere except the asleep state
    self._machine.add_transition(
      STATE_CANCEL,
      [STATE_ASK, STATE_FALLBACK] + intents,
      STATE_CANCEL,
      after=None)

    # Go to the ask state from every intents
    self._machine.add_transition(
      STATE_ASK,
      [STATE_FALLBACK] + intents,
      STATE_ASK,
      after=self._on_asked)

    # And go to intents state from asleep or ask states
    for intent in [STATE_FALLBACK] + intents:
      self._machine.add_transition(
        intent,
        [STATE_ASLEEP, STATE_ASK],
        intent,
        after=self._on_intent)

  def _log_transition(self, e):
    dest = e.transition.dest
    msg = '⚡ %s: %s -> %s' % (e.event.name, e.transition.source, dest)

    if dest == STATE_ASK:
      msg += ' (slot: {slot}, choices: {choices})'.format(**e.kwargs)

    self._logger.info(msg)

  def _is_valid(self, data, required_keys=[]):
    if not all(elem in data and data[elem] != None for elem in required_keys):
      self._log.warning('One of required keys are not present or its value is equal to None in the data, required keys were %s' % required_keys)
      return False

    return True

  def parse(self, msg):
    """Parse a raw message.
    """

    self._logger.info('Parsing sentence "%s"' % msg)

    intents = self._interpreter.parse(msg)

    # TODO: handle cancel one

    if self.state == STATE_ASK:
      values = self._interpreter.parse_slot(self._request.intent.name, self._asked_slot, msg)
      
      self._request.intent.update_slots(**{ self._asked_slot: values })
      self._logger.info('Updated slot "%s" with values %s' % (self._asked_slot, [str(v) for v in values]))
      self.go(self._request.intent.name, intent=self._request.intent)
    else:
      self._logger.info('%s intent(s) found: %s' % (len(intents), ', '.join([str(i) for i in intents])))

      self._intents_queue.extend(intents)

      if self.state == STATE_ASLEEP:
        self._process_next_intent()

  def _process_intent(self, intent):
    self._logger.info('Processing intent %s' % intent)
    
    if intent.name not in self._handlers:
      self._logger.error('No handler found for the intent "%s"' % intent.name)
      self.done()
    else:
      if (self._request == None or self._request.intent != intent):
        self._request = Request(self, intent)
        self._logger.info('💬 New "%s" conversation started with id %s' % (intent.name, self._request.id))
      
      try:
        self._handlers[intent.name](self._request) # Thread? Or nope
      except Exception as err:
        self._logger.error(err.msg)

  def _on_intent(self, event):
    if not self._is_valid(event.kwargs, ['intent']):
      return self.done()

    self._process_intent(event.kwargs.get('intent'))

  def _on_asked(self, event):
    if not self._is_valid(event.kwargs, ['slot', 'text']):
      return self.done()

    text = keep_one(event.kwargs.get('text'))
    slot = event.kwargs.get('slot')
    choices = event.kwargs.get('choices')

    self._asked_slot = slot
    self._choices = choices

    self._client.ask(slot, text, choices)

  def _process_next_intent(self):
    if len(self._intents_queue) > 0:
      intent = self._intents_queue.pop(0)

      self.go(intent.name, intent=intent)

  def go(self, state, **kwargs):
    """Try to move the state machine to the given state.

    Args:
      state (str): Desired state
      kwargs (dict): Arguments

    """

    try:
      self.trigger(state, **kwargs) # pylint: disable=E1101
    except MachineError as err:
      self._logger.error('Could not trigger "%s": %s' % (state, err))

  def ask(self, slot, text, choices=None):
    """Ask something to the user.
    """

    self._client.done()
    self.go(STATE_ASK, slot=slot, text=text, choices=choices)

  def answer(self, text):
    """Answer something to the user.
    """

    self._client.answer(keep_one(text))

  def done(self):
    """Done should be called by skills when they are done with their stuff. It enables
    threaded scenarii. When asking something to the user, you should not call this method!

    """

    self.go(STATE_ASLEEP)

  def end_conversation(self, event=None):
    """Ends a conversation, means nothing would come from the skill anymore and
    it does not require user inputs. This is especially useful when you are showing
    an activity indicator.

    """

    self._logger.info('Conversation %s has ended' % self._request.id)
    self._request = None
    self._asked_slot = None
    self._choices = None
    self._client.done()
    self._process_next_intent()