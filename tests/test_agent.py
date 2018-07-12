import unittest, logging
from unittest.mock import MagicMock
from pytlas import Agent
from pytlas.agent import STATE_ASK
from pytlas.clients import Client
from pytlas.interpreters import Interpreter, Intent, SlotValue

class AgentTests(unittest.TestCase):

  def test_simple_intent(self):
    interp = Interpreter()
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

    interp = Interpreter()
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

    interp = Interpreter()
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

    called = False

    def final_handler(r):
      nonlocal request, called
      self.assertEqual(r.id, request.id)
      self.assertEqual('a value', r.intent.slot('a_slot').first().value)
      called = True

    handlers['should_ask'] = final_handler

    agt.parse('Parse slot should be called')
    interp.parse_slot.assert_called_once_with('should_ask', 'a_slot', 'Parse slot should be called')
    self.assertTrue(called)