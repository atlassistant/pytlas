from sure import expect
import logging
from unittest.mock import MagicMock
from pytlas import Agent
from pytlas.agent import STATE_ASK, STATE_CANCEL, STATE_ASLEEP, STATE_FALLBACK
from pytlas.card import Card
from pytlas.interpreters import Interpreter, Intent, SlotValue

last_request = None

def on_cancel(r):
  """greet handler which call agent.answer with 'Cancelled'.
  """

  global last_request
  last_request = r

  r.agent.answer('Cancelled')

  return r.agent.done()

def on_fallback(r):
  """on_fallback handler which call agent.answer with 'Searching for <text slot value>'.
  """
  
  global last_request
  last_request = r

  r.agent.answer('Searching for ' + r.intent.slot('text').first().value)

  return r.agent.done()

def on_block(r):
  """block handler which does not call agent.done so it freeze transitions.
  """

  pass

def on_greet(r):
  """greet handler which call agent.answer with 'Hello you!'.
  """

  global last_request
  last_request = r

  r.agent.answer('Hello you!')

  return r.agent.done(True)

def on_with_meta(r):
  """with_meta handler which call agent.ask and agent.answer with meta:
  
  When asking for the name slot, it will include special_meta='something'
  When answering, it will include trigger_listening=True
  """

  if not r.intent.slot('name'):
    return r.agent.ask('name', 'Whom?', special_meta='something')

  r.agent.answer('Hello **%s**' % r.intent.slot('name').first().value, trigger_listening=True)

  return r.agent.done()

def on_lights_on(r):
  """lights_on handler which call agent.answer with 'Turning lights on in <room slot value>'.
  """

  global last_request
  last_request = r

  room = r.intent.slot('room')

  if not room:
    return r.agent.ask('room', 'Which ones?', choices=['kitchen', 'living room', 'bedroom'])

  r.agent.answer('Turning lights on in ' + room.first().value)

  return r.agent.done()

def on_get_forecast(r):
  """get_forecast handler which requires date and city slots and answer with
  'Looking in <city slot value> for <date slot value>'
  """

  global last_request
  last_request = r

  date = r.intent.slot('date').first().value
  city = r.intent.slot('city').first().value

  if not date:
    return r.agent.ask('date', 'When?')

  if not city:
    return r.agent.ask('city', 'Where?')

  r.agent.answer('Looking in %s for %s' % (city, date), cards=[Card(city, date)])

  return r.agent.done()

class TestAgent:
  """For those tests, the interpreter.parse is always mocked because there is no interpreter
  such as snips. It only tests transitions and state management.
  """

  def setup(self):
    self.on_answer = MagicMock()
    self.on_ask = MagicMock()
    self.on_done = MagicMock()
    self.on_thinking = MagicMock()

    self.handlers = {
      'greet': on_greet,
      'get_forecast': on_get_forecast,
      'lights_on': on_lights_on,
      'block': on_block,
      'with_meta': on_with_meta,
      STATE_CANCEL: on_cancel,
      STATE_FALLBACK: on_fallback,
    }
    self.interpreter = Interpreter('test', 'en')
    self.interpreter.intents = list(self.handlers.keys()) + ['intent_without_handler']
    self.agent = Agent(self.interpreter, model=self, handlers=self.handlers)

  def test_it_should_queue_string_as_intent(self):
    self.agent.queue_intent('greet')

    expect(last_request.intent.name).to.equal('greet')
    self.on_answer.assert_called_once_with('Hello you!', None, raw_text='Hello you!')
    self.on_done.assert_called_once_with(True)
    expect(self.agent.state).to.equal(STATE_ASLEEP)

  def test_it_should_queue_string_and_kwargs_as_intent_with_slot_values(self):
    self.agent.queue_intent('greet', name='Julien')

    self.on_answer.assert_called_once()
    self.on_done.assert_called_once_with(True)
    
    expect(last_request.intent.name).to.equal('greet')
    expect(last_request.intent.slots).to.have.length_of(1)
    expect(last_request.intent.slot('name').first().value).to.equal('Julien')
    expect(self.agent.state).to.equal(STATE_ASLEEP)

  def test_it_should_trigger_intent(self):
    self.agent.queue_intent(Intent('greet'))

    expect(last_request.intent.name).to.equal('greet')
    self.on_answer.assert_called_once_with('Hello you!', None, raw_text='Hello you!')
    self.on_done.assert_called_once_with(True)
    self.on_thinking.assert_called_once()
    expect(self.agent.state).to.equal(STATE_ASLEEP)

  def test_it_should_handle_simple_intent(self):
    self.interpreter.parse = MagicMock(return_value=[Intent('greet')])

    self.agent.parse('hello')

    self.on_answer.assert_called_once_with('Hello you!', None, raw_text='Hello you!')
    self.on_done.assert_called_once_with(True)
    expect(self.agent.state).to.equal(STATE_ASLEEP)

  def test_it_should_have_cards(self):
    self.interpreter.parse = MagicMock(return_value=[Intent('get_forecast', date='tomorrow', city='rouen')])

    self.agent.parse('will it rain in rouen tomorrow')

    self.on_answer.assert_called_once()

    call_args = self.on_answer.call_args[0]
    expect(call_args).to.have.length_of(2)
    expect(call_args[0]).to.equal('Looking in rouen for tomorrow')
    expect(call_args[1]).to.be.a(list)
    expect(call_args[1]).to.have.length_of(1)
    expect(call_args[1][0].header).to.equal('rouen')
    expect(call_args[1][0].text).to.equal('tomorrow')

  def test_it_should_handle_multiple_intents(self):
    self.interpreter.parse = MagicMock(return_value=[
      Intent('greet'), 
      Intent('block'), 
      Intent('lights_on', room='kitchen'),
    ])

    self.agent.parse('hello, can you turn the lights on in kitchen')

    self.on_answer.assert_called_once_with('Hello you!', None, raw_text='Hello you!')
    self.on_done.assert_called_once_with(True)
    expect(self.on_thinking.call_count).to.equal(2) # One for greet, the other for block

    greet_id = last_request.id

    expect(self.agent.state).to.equal('block')

    # Since the block intent does not call it to test it more easily, call the agent.done now to process the next intent
    self.agent.done()

    self.on_answer.assert_called_with('Turning lights on in kitchen', None, raw_text='Turning lights on in kitchen')

    expect(self.on_done.call_count).to.equal(3)
    expect(self.on_thinking.call_count).to.equal(3)
    expect(last_request.id).to_not.equal(greet_id)
    expect(self.agent.state).to.equal(STATE_ASLEEP)

  def test_it_should_add_parse_meta_to_intent_meta(self):
    greet_intent = Intent('greet')
    lights_intent = Intent('lights_on', room='kitchen')

    self.interpreter.parse = MagicMock(return_value=[
      greet_intent,
      lights_intent,
    ])

    self.agent.parse('hello, can you turn the lights on in kitchen', latitude=49.44, longitude=1.09)

    expect(greet_intent.meta).to.equal({ 'latitude': 49.44, 'longitude': 1.09 })
    expect(lights_intent.meta).to.equal({ 'latitude': 49.44, 'longitude': 1.09 })
    expect(last_request.intent.meta).to.equal({ 'latitude': 49.44, 'longitude': 1.09 })
  
  def test_it_should_do_nothing_and_returns_to_the_asleep_state_when_no_handler_was_found(self):
    self.interpreter.parse = MagicMock(return_value=[Intent('intent_without_handler')])

    self.agent.parse('an intent without a handler')

    self.on_done.assert_called_once_with(False)
    expect(self.agent.state).to.equal(STATE_ASLEEP)

  def test_it_should_be_in_the_ask_state_when_a_skill_ask_for_slot(self):
    self.interpreter.parse = MagicMock(return_value=[Intent('get_forecast')])

    self.agent.parse('will it be sunny')

    initial_request_id = last_request.id

    self.on_ask.assert_called_once_with('date', 'When?', None, raw_text='When?')
    self.on_done.assert_called_once_with(True)
    self.on_answer.assert_not_called()
    expect(self.agent.state).to.equal(STATE_ASK)

    self.agent.parse('tomorrow')

    expect(last_request.intent.slot('date').first().value).to.equal('tomorrow')
    self.on_ask.assert_any_call('city', 'Where?', None, raw_text='Where?')
    expect(self.on_done.call_count).to.equal(2)
    self.on_answer.assert_not_called()
    expect(self.agent.state).to.equal(STATE_ASK)

    self.agent.parse('rouen')

    expect(last_request.intent.slot('city').first().value).to.equal('rouen')
    self.on_answer.assert_called_once()
    expect(self.on_answer.call_args[0][0]).to.equal('Looking in rouen for tomorrow')
    expect(self.agent.state).to.equal(STATE_ASLEEP)
    expect(self.on_done.call_count).to.equal(3)
    expect(last_request.id).to.equal(initial_request_id)

  def test_it_should_match_on_choices_when_asking_with_choices(self):
    self.interpreter.parse = MagicMock(return_value=[Intent('lights_on')])

    self.agent.parse('turn the lights on')

    self.on_ask.assert_called_once_with('room', 'Which ones?', ['kitchen', 'living room', 'bedroom'], raw_text='Which ones?')
    expect(self.agent.state).to.equal(STATE_ASK)

    self.agent.parse('in the living room')

    self.on_answer.assert_called_with('Turning lights on in living room', None, raw_text='Turning lights on in living room')
    expect(self.on_done.call_count).to.equal(2)

  def test_it_should_cancel_intent_when_cancel_is_caught(self):
    self.interpreter.parse = MagicMock(return_value=[Intent('lights_on')])

    self.agent.parse('turn the lights on')

    expect(self.agent.state).to.equal(STATE_ASK)

    self.interpreter.parse = MagicMock(return_value=[Intent(STATE_CANCEL)])

    self.agent.parse('cancel')

    self.on_answer.assert_called_once_with('Cancelled', None, raw_text='Cancelled')
    expect(self.agent.state).to.equal(STATE_ASLEEP)

  def test_it_should_pass_ask_meta_to_the_handler(self):
    self.interpreter.parse = MagicMock(return_value=[Intent('with_meta')])

    self.agent.parse('trigger with_meta handler')

    self.on_ask.assert_called_once_with('name', 'Whom?', None, raw_text='Whom?', special_meta='something')

  def test_it_should_pass_answer_meta_to_the_handler(self):
    self.interpreter.parse = MagicMock(return_value=[Intent('with_meta', name='Julien')])

    self.agent.parse('trigger with_meta handler')

    self.on_answer.assert_called_once_with('Hello **Julien**', None, raw_text='Hello Julien', trigger_listening=True)

  def test_it_should_call_the_fallback_intent_when_no_matching_intent_could_be_found(self):
    self.agent.parse('should go in fallback')

    self.on_answer.assert_called_once_with('Searching for should go in fallback', None, raw_text='Searching for should go in fallback')
    self.on_done.assert_called_once_with(False)
    expect(self.agent.state).to.equal(STATE_ASLEEP)
    expect(last_request.intent.name).to.equal(STATE_FALLBACK)
    expect(last_request.intent.slots).to.have.length_of(1)
    expect(last_request.intent.slot('text').first().value).to.equal('should go in fallback')

  def test_it_should_handle_interpreter_changes_with_build(self):
    expect(self.agent._machine.states).to_not.contain('something_else')

    self.interpreter.intents.append('something_else')

    self.agent.build()

    expect(self.agent._machine.states).to.contain('something_else')

