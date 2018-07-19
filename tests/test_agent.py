import unittest, logging
from unittest.mock import MagicMock
from pytlas import Agent
from pytlas.agent import STATE_ASK, STATE_CANCEL, STATE_ASLEEP, STATE_FALLBACK
from pytlas.clients import Client
from pytlas.interpreters import Interpreter, Intent, SlotValue

class AgentTests(unittest.TestCase):

  def test_simple_intent(self):
    interp = Interpreter('test')
    client = Client()
    handlers = {
      'lights_on': MagicMock(),
      'lights_off': MagicMock(),
    }
    interp.intents = list(handlers.keys())
    interp.parse = MagicMock(return_value=[
      Intent('lights_on')
    ])

    agt = Agent(interp, client, handlers)
    agt.parse('turn lights on')

    handlers['lights_on'].assert_called_once()
    handlers['lights_off'].assert_not_called()

  def test_multiple_intents(self):

    lights_on_request = None
    lights_off_request = None

    def lights_on(r):
      nonlocal lights_on_request
      lights_on_request = r

    def lights_off(r):
      nonlocal lights_off_request
      lights_off_request = r

    interp = Interpreter('test')
    client = Client()
    handlers = {
      'lights_on': lights_on,
      'lights_off': lights_off,
    }
    interp.intents = list(handlers.keys())
    interp.parse = MagicMock(return_value=[
      Intent('lights_on'),
      Intent('lights_off')
    ])
    
    agt = Agent(interp, client, handlers)
    agt.parse('turn lights on and off')

    self.assertIsNotNone(lights_on_request)
    self.assertIsNone(lights_off_request)
    self.assertEqual('lights_on', agt.state)

    agt.done() # Since we use a mock, we should call it ourselves

    self.assertIsNotNone(lights_off_request)
    self.assertEqual('lights_off', agt.state)

    self.assertNotEqual(lights_on_request.id, lights_off_request.id)

  def test_ask(self):
    
    request = None

    def handler(r):
      nonlocal request
      request = r
      r.agent.ask('a_slot', 'Please fill the slot')

    interp = Interpreter('test')
    client = Client()
    client.ask = MagicMock()
    client.done = MagicMock()
    handlers = {
      'should_ask': handler,
    }
    interp.intents = list(handlers.keys())
    interp.parse = MagicMock(return_value=[
      Intent('should_ask'),
    ])
    interp.parse_slot = MagicMock(return_value=[
      SlotValue('a value'),
    ])

    agt = Agent(interp, client, handlers)
    agt.parse('You should ask for a slot')

    client.ask.assert_called_once_with('a_slot', 'Please fill the slot', None)
    client.done.assert_called_once()
    self.assertEqual(STATE_ASK, agt.state)

    assertion_success = False

    def final_handler(r):
      nonlocal request, assertion_success

      assertion_success = r.id == request.id and r.intent.slot('a_slot').first().value == 'a value'

    handlers['should_ask'] = final_handler

    agt.parse('Parse slot should be called')
    interp.parse_slot.assert_called_once_with('should_ask', 'a_slot', 'Parse slot should be called')

    self.assertTrue(assertion_success)

  def test_ask_with_choices(self):

    assertion_success = False
    choices = ['kitchen', 'living room', 'bedroom']

    def handler(r):
      nonlocal assertion_success

      rooms = r.intent.slot('rooms')

      if not rooms:
        return r.agent.ask('rooms', 'Choose a room in one of those', choices)

      assertion_success = len(rooms) == 2 and all([r.value in choices for r in rooms])

      return r.agent.done()
    
    client = Client()
    client.ask = MagicMock()
    handlers = {
      'lights_on': handler,
    }
    interp = Interpreter('test')
    interp.intents = list(handlers.keys())
    interp.parse = MagicMock(return_value=[
      Intent('lights_on'),
    ])
    interp.parse_slot = MagicMock(return_value=[
      SlotValue('kitch'),
      SlotValue('living one'),
    ])

    agt = Agent(interp, client, handlers)
    agt.parse('turn the lights on')

    client.ask.assert_called_once_with('rooms', 'Choose a room in one of those', choices)
    self.assertEqual(STATE_ASK, agt.state)
    self.assertEqual(choices, agt._choices)

    agt.parse('would not be took into account in those tests')

    self.assertTrue(assertion_success)

  def test_cancel(self):
    client = Client()
    handlers = {
      'lights_on': lambda r: r.agent.ask('rooms', 'Please specify a room'),
    }
    interp = Interpreter('test')
    interp.intents = list(handlers.keys())
    interp.parse = MagicMock(return_value=[
      Intent('lights_on'),
    ])

    agt = Agent(interp, client, handlers)
    agt.parse('turn lights on')

    self.assertEqual(STATE_ASK, agt.state)

    interp.parse = MagicMock(return_value=[
      Intent(STATE_CANCEL),
    ])

    agt.parse('cancel')

    self.assertEqual(STATE_ASLEEP, agt.state)
    self.assertIsNone(agt._choices)
    self.assertIsNone(agt._request)
    self.assertIsNone(agt._asked_slot)

  def test_fallback(self):

    assertion_success = False

    def handler(r):
      nonlocal assertion_success

      assertion_success = r.intent.slot('text').first().value == 'something not catched'

    client = Client()
    handlers = {
      STATE_FALLBACK: handler,
    }
    interp = Interpreter('test')
    interp.intents = list(handlers.keys())
    interp.parse = MagicMock(return_value=[])

    agt = Agent(interp, client, handlers)
    agt.parse('something not catched')

    self.assertTrue(assertion_success)