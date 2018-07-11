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
    interp = Interpreter()
    client = Client()
    handlers = {
      'lights_on': MagicMock(),
      'lights_off': MagicMock(),
    }
    interp.intents = list(handlers.keys())
    interp.parse = MagicMock(return_value=[
      Intent('lights_on'),
      Intent('lights_off')
    ])
    
    agt = Agent(interp, client, handlers)
    agt.parse('turn lights on and off')

    handlers['lights_on'].assert_called_once()
    agt.done() # Since we use a mock, we should call it ourselves
    handlers['lights_off'].assert_called_once()

  def test_ask(self):
    interp = Interpreter()
    client = Client()
    client.ask = MagicMock()
    client.done = MagicMock()
    handlers = {
      'should_ask': lambda r: r.agent.ask('a_slot', 'Please fill the slot'),
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

    client.ask.assert_called_once_with(choices=None, slot='a_slot', text='Please fill the slot')
    client.done.assert_called_once()
    self.assertEqual(STATE_ASK, agt.state)    

    handlers['should_ask'] = lambda r: self.assertEqual('a value', r.intent.slot('a_slot').first().value)

    agt.parse('Parse slot should be called')
    interp.parse_slot.assert_called_once_with('should_ask', 'a_slot', 'Parse slot should be called')