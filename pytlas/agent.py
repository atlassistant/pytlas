import logging, uuid
from pytlas.request import Request
from pytlas.utils import get_package_name_from_module, keep_one, strip_format, find_match
from pytlas.localization import get_translations
from pytlas.interpreters.intent import Intent
from pytlas.interpreters.slot import SlotValue
from pytlas.skill import handlers as skill_handlers
from pytlas.hooks import trigger, ON_AGENT_CREATED, ON_AGENT_DESTROYED
from transitions import Machine, MachineError

# Silent the transitions logger
logging.getLogger('transitions').setLevel(logging.WARNING)

STATE_PREFIX = '__'
STATE_SUFFIX = '__'
STATE_ASLEEP = STATE_PREFIX + 'asleep' + STATE_SUFFIX
STATE_CANCEL = STATE_PREFIX + 'cancel' + STATE_SUFFIX
STATE_FALLBACK = STATE_PREFIX + 'fallback' + STATE_SUFFIX
STATE_ASK = STATE_PREFIX + 'ask' + STATE_SUFFIX
CONTEXT_SEPARATOR = '/'

def is_builtin(state):
  """Checks if the given state is a builtin one.
  
  Args:
    state (str): State to check

  Returns:
    bool: True if it's a builtin state, false otherwise

  """

  return state.startswith(STATE_PREFIX) and state.endswith(STATE_SUFFIX) if state else False

def build_scopes(intents, include_cancel_state=True):
  """Build all scopes given an intents list. It will create a dict which contains
  association between a context and available scopes.

  Scopes are intents which could be triggered from a particular context. They will be given
  to the interpreter to restrict the list of intents to be parsed. That's why STATE_CANCEL is
  always added to every scopes if include_cancel_state is set to True.

  Args:
    intents (list): List of intents
    include_cancel_state (bool): Should builtin state cancel be always added?

  Returns:
    dict: Dictionary mapping each context to a list of available scopes

  """

  scopes = {
    # represents the root scopes, ie. when not in a specific context
    None: [STATE_CANCEL] if include_cancel_state else [], 
  }

  for intent in intents:
    try:
      last_idx = intent.rindex(CONTEXT_SEPARATOR)
      root = intent[:last_idx]

      if root not in scopes:
        scopes[root] = [STATE_CANCEL] if include_cancel_state else []

      scopes[root].append(intent)
    except:
      scopes[None].append(intent)

  return scopes

class Agent:
  """Manages a conversation with a client.

  Conversation state is represented by a finite state machine. It handle ask states
  when the skill needs more information and trigger appropriate handler upon intent
  parsing.

  """

  def __init__(self, interpreter, model=None, handlers=None, transitions_graph_path=None, **meta):
    """Initialize an agent.

    When skills ask or answer something to the client, they can send markdown formatted text
    to enable rich text display. This markdown will not be processed by pytlas and should be handled
    by clients on their side.

    But as a convenience, a special meta will be added to `on_answer` and `on_ask` which is called
    `raw_text` and contains the text without any formatting.

    Args:
      interpreter (Interpreter): Interpreter used to convert human language to intents
      model (object): Model which will receive events raised by this agent instance
      handlers (dict): Dictionary of intent: handler to use. If no one is provided, all handlers registered will be used instead.
      transitions_graph_path (str): If pygraphviz is installed, where to output the transitions graph
      meta (dict): Every other properties will be made available through the self.meta property

    """

    self._logger = logging.getLogger(self.__class__.__name__.lower())
    self._interpreter = interpreter
    self._transitions_graph_path = transitions_graph_path

    self._on_ask = None
    self._on_answer = None
    self._on_done = None
    self._on_thinking = None
    self._on_context = None

    self._handlers = handlers if handlers != None else skill_handlers
    self._translations = get_translations(self._interpreter.lang)

    self._intents_queue = []
    self._request = None
    self._asked_slot = None
    self._choices = None
    self._available_scopes = {}
    self._current_scopes = None

    self.id = uuid.uuid4().hex
    self.model = model
    self.meta = meta
    self.current_context = None

    self._machine = None
    self.build()
    self.context(None)

    trigger(ON_AGENT_CREATED, self)

  def __del__(self):
    # Maybe we should use a finalizer instead
    trigger(ON_AGENT_DESTROYED, self)

  def _build_is_in_context_lambda(self, ctx):
    return lambda _: self.current_context == ctx

  def build(self):
    """Setup the state machine based on the interpreter available intents. This is
    especialy useful if you have trained the interpreter after creating this agent.

    This method is also called from the constructor.

    """

    # Ends the conversation if the machine already exists, just to make sure
    if self._machine:
      self.end_conversation()

    intents = [i for i in self._interpreter.intents if not is_builtin(i)]
    states = [STATE_ASLEEP, STATE_ASK, STATE_FALLBACK, STATE_CANCEL] + intents

    self._available_scopes = build_scopes(intents, STATE_CANCEL in self._interpreter.intents)

    MachineKlass = Machine
    kwargs = {} # Additional arguments to give to the machine

    if self._transitions_graph_path: # pragma: no cover
      try:
        import pygraphviz
        from transitions.extensions import GraphMachine
        
        MachineKlass = GraphMachine
        kwargs['show_conditions'] = True
      except:
        self._logger.error('Could not use a GraphMachine, is pygraphviz installed?')

    self._machine = MachineKlass(
      model=self, 
      states=states, 
      send_event=True,
      before_state_change=self._log_transition,
      initial=STATE_ASLEEP,
      **kwargs)

    self._logger.info('Instantiated agent with "%s" states: %s' % (len(states), ', '.join('"%s"' % s for s in states)))

    # Go to the asleep state from anywhere except the ask state
    self._machine.add_transition(
      STATE_ASLEEP, # trigger
      [STATE_FALLBACK, STATE_CANCEL] + intents, # source
      STATE_ASLEEP, # destination
      after=self.end_conversation)

    # Go to the cancel state from anywhere
    self._machine.add_transition(
      STATE_CANCEL,
      [STATE_ASLEEP, STATE_ASK, STATE_FALLBACK] + intents,
      STATE_CANCEL,
      after=self._on_cancel)

    # Go to the ask state from every intents
    # For now, you can't ask something from the cancel state...
    self._machine.add_transition(
      STATE_ASK,
      [STATE_FALLBACK] + intents,
      STATE_ASK,
      after=self._on_asked)

    # Fallback is treated as a common intent
    self._machine.add_transition(
      STATE_FALLBACK,
      [STATE_ASLEEP, STATE_ASK],
      STATE_FALLBACK,
      after=self._on_intent)

    for (ctx, ctx_intents) in self._available_scopes.items():
      conditions = None

      # If we need a specific context, create an attribute which will check
      # if we are in the right context as a condition
      if ctx:
        attr_name = 'is_in_%s_context' % ctx
        setattr(self, attr_name, self._build_is_in_context_lambda(ctx))
        conditions = [attr_name]

      for intent in ctx_intents:
        if intent != STATE_CANCEL:
          self._machine.add_transition(
            intent,
            [STATE_ASLEEP, STATE_ASK],
            intent,
            after=self._on_intent,
            conditions=conditions)

    if self._transitions_graph_path and getattr(self._machine, 'get_graph', None): # pragma: no cover
      self._logger.info('Writing graph to "%s"' % self._transitions_graph_path)
      self._machine.get_graph().draw(self._transitions_graph_path, prog='dot')

  @property
  def model(self):
    """Retrieve the model associated with this agent instance.

    Returns:
      object: The model

    """

    return self._model

  @model.setter
  def model(self, model):
    """Sets the model associated with this instance. It will pull handlers
    from the model attributes:

      - on_ask: Called when asking for user inputs
      - on_answer: Called when showing something to the user
      - on_thinking: Called when a skill has started working
      - on_done: Called when a skill has done its work
      - on_context: Called when the current context has changed

    Args:
      model (object): Object which will receive those events

    """

    self._model = model

    if self._model:
      self._on_ask = getattr(self._model, 'on_ask', None)
      self._on_answer = getattr(self._model, 'on_answer', None)
      self._on_done = getattr(self._model, 'on_done', None)
      self._on_thinking = getattr(self._model, 'on_thinking', None)
      self._on_context = getattr(self._model, 'on_context', None)

  def _log_transition(self, e):
    dest = e.transition.dest
    msg = '⚡ "%s": %s -> %s' % (e.event.name, e.transition.source, dest)

    if dest == STATE_ASK:
      msg += ' (slot: {slot}, choices: {choices})'.format(**e.kwargs)

    self._logger.info(msg)

  def _is_current_request(self, request):
    return self._request and self._request.id == request.id

  def _is_valid(self, data, required_keys=[]):
    if not all(elem in data and data[elem] != None for elem in required_keys):
      self._logger.warning('One of required keys are not present or its value is equal to None in the data, required keys were %s' % required_keys)
      return False

    return True

  def queue_intent(self, intent, **slots):
    """Queue the given intent and process it if the agent is asleep.
    
    Args:
      intent (str, Intent): Intent to process as soon as possible
      slots (dict): When intent is an str, parses those data as slot values

    """

    if isinstance(intent, str):
      intent = Intent(intent, **slots)

    self._intents_queue.append(intent)

    if self.state == STATE_ASLEEP: # pylint: disable=E1101
      self._process_next_intent()

  def parse(self, msg, **meta):
    """Parse a raw message.

    The interpreter will be used to determine which intent(s) has been formulated
    by the user and the state machine will move to the appropriate state calling
    the right skill handler.

    It will also handle some specific intents such as the cancel one and ask states.

    Args:
      msg (str): Raw message to parse
      meta (dict): Optional metadata to add to the request object

    """

    self._logger.info('Parsing sentence "%s"' % msg)

    intents = self._interpreter.parse(msg, self._current_scopes) or [Intent(STATE_FALLBACK, text=msg)]

    # Add meta to each parsed intents
    for intent in intents:
      intent.meta.update(meta)

    cancel_intent = next((i for i in intents if i.name == STATE_CANCEL), None)

    # Either way, extend the intent queue with new intents
    if self.state != STATE_ASK: # pylint: disable=E1101
      intents = [i for i in intents if i.name != STATE_CANCEL]

      self._logger.info('"%s" intent(s) found: %s' % (len(intents), ', '.join([str(i) for i in intents])))

      self._intents_queue.extend(intents)
    
    # If the user wants to cancel the current action, immediately go to the cancel state
    if cancel_intent: # pylint: disable=E1101
      self.go(STATE_CANCEL, intent=cancel_intent)
    else:
      if self.state == STATE_ASK: # pylint: disable=E1101

        # If choices are limited, try to extract a match
        if self._choices:
          msg = find_match(self._choices, msg)

        # Here msg will be None if choices could not be matched, so nothing should be done anymore
        if msg:
          values = self._interpreter.parse_slot(self._request.intent.name, self._asked_slot, msg)

          # Update slots and meta
          self._request.intent.update_slots(**{ self._asked_slot: values })
          self._request.intent.meta.update(meta)

          self._logger.info('Updated slot "%s" with values %s' % (self._asked_slot, ['"%s"' % v for v in values]))
        
        self.go(self._request.intent.name, intent=self._request.intent)
      elif self.state == STATE_ASLEEP: # pylint: disable=E1101
        self._process_next_intent()

  def _process_intent(self, intent):
    self._logger.info('Processing intent %s' % intent)

    handler = self._handlers.get(intent.name)

    # If we are in a context and the intent is a builtin one, check if the skill has a specific
    # handler registered, else fallback to the generic one
    if self.current_context and is_builtin(intent.name):
      handler = self._handlers.get(self.current_context + CONTEXT_SEPARATOR + intent.name, handler)
    
    if not handler:
      self._logger.warning('No handler found for the intent "%s"' % intent.name)
      self.done()
    else:
      if (self._request == None or self._request.intent != intent):
        # Creates the request and load module translations if any
        translations = self._translations.get(get_package_name_from_module(handler.__module__), {})

        self._logger.debug('Found "%s" translations matching the request' % len(translations))

        self._request = Request(self, intent, translations)
          
        self._logger.info('💬 New "%s" conversation started with id "%s"' % (intent.name, self._request.id))
      
      try:
        self._logger.debug('Calling handler "%s"' % handler)

        if self._on_thinking:
          self._on_thinking()

        handler(self._request)
      except Exception as err:
        self._logger.error(err)
        self.done() # Go back to the asleep state

  def _on_intent(self, event):
    if not self._is_valid(event.kwargs, ['intent']):
      return self.done()

    self._process_intent(**event.kwargs)

  def _on_cancel(self, event):
    self.context(None)
    self._on_intent(event)

  def _on_asked(self, event):
    if not self._is_valid(event.kwargs, ['slot', 'text']):
      return self.done()

    text = keep_one(event.kwargs.get('text'))
    slot = event.kwargs.get('slot')
    choices = event.kwargs.get('choices')

    self._asked_slot = slot
    self._choices = choices

    if self._on_ask:
      self._on_ask(slot, text, choices, raw_text=strip_format(text), **event.kwargs.get('meta'))

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
    except (MachineError, AttributeError) as err:
      self._logger.error('Could not trigger "%s": %s' % (state, err))

  def ask(self, slot, text, choices=None, **meta):
    """Ask something to the user.

    Args:
      slot (str): Name of the slot asked for
      text (str, list): Text to show to the user
      choices (list): List of available choices
      meta (dict): Any additional data to pass to the handler

    """

    if self._on_done:
      self._on_done(True)

    self.go(STATE_ASK, slot=slot, text=text, choices=choices, meta=meta)

  def answer(self, text, cards=None, **meta):
    """Answer something to the user.

    Args:
      text (str, list): Text to show to the user
      cards (list, Card): List of Card to show if any
      meta (dict): Any additional data to pass to the handler

    """

    if cards and not isinstance(cards, list):
      cards = [cards]

    if self._on_answer:
      t = keep_one(text)
      self._on_answer(t, cards, raw_text=strip_format(t), **meta)

  def done(self, require_input=False):
    """Done should be called by skills when they are done with their stuff. It enables
    threaded scenarii. When asking something to the user, you should not call this method!

    """

    self.go(STATE_ASLEEP, require_input=require_input)

  def context(self, context_name):
    """Switch the agent to the given context name. It will populates the list of reachable
    scopes so the interpreter will only parse intents defined in this scope.

    Args:
      context_name (str): Name of the context to switch to (None represents the root one)

    """

    self.current_context = context_name
    self._current_scopes = self._available_scopes.get(self.current_context, self._available_scopes.get(None))

    self._logger.info('Switched to the context "%s" with now "%d" understandable intents: %s' % 
      (self.current_context, len(self._current_scopes),  ', '.join('"%s"' % s for s in self._current_scopes)))

    if self._on_context:
      self._on_context(self.current_context)

  def end_conversation(self, event=None):
    """Ends a conversation, means nothing would come from the skill anymore and
    it does not require user inputs. This is especially useful when you are showing
    an activity indicator.

    """

    if self._request:
      self._logger.info('Conversation "%s" has ended' % self._request.id)

    self._request = None
    self._asked_slot = None
    self._choices = None

    if self._on_done:
      self._on_done(event.kwargs.get('require_input') if event else False)
      
    self._process_next_intent()
