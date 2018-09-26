import unittest
from datetime import datetime
from pytlas.agent import Agent
from pytlas.interpreters import Interpreter
from pytlas.request import Request, AgentProxy

class RequestTests(unittest.TestCase):

  def test_id(self):
    
    r = Request(None, None)

    self.assertIsNotNone(r.id)

  def test_translations(self):

    r = Request(None, None, {
      'a text': 'un texte',
    })

    self.assertEqual('un texte', r._('a text'))
    self.assertEqual('not found', r._('not found'))

  def test_datetime_localizations(self):
    interp = Interpreter('test', 'fr')
    agt = Agent(interp)

    r = Request(agt, None)
    d = datetime(2018, 9, 25, 8, 30)

    self.assertEqual('25 sept. 2018 à 08:30:00', r._d(d))
    self.assertEqual('25 sept. 2018', r._d(d, date_only=True))
    self.assertEqual('08:30:00', r._d(d, time_only=True))
    self.assertEqual('mardi 25 septembre 2018', r._d(d, format='full', date_only=True))

  def test_agent_proxy(self):
    interp = Interpreter('test', 'en')
    agt = Agent(interp)

    r = Request(agt, None)

    self.assertIsInstance(r.agent, AgentProxy)
    self.assertNotEqual(r.agent.ask, agt.ask)

    agt._request = r
    self.assertEqual(r.agent.ask, agt.ask)

    agt._request = Request(agt, None)
    self.assertEqual(r.agent.ask, r.agent.empty_func) # Check redirect to empty func
    self.assertEqual(r.agent.done, r.agent.empty_func)
    self.assertEqual(r.agent.answer, r.agent.empty_func)
    self.assertEqual(r.agent.meta, agt.meta)