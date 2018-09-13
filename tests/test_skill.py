import unittest
from pytlas.skill import intent, register, handlers

@intent('an_intent')
def a_handler(r):
  return r.agent.done()

def another_handler(r):
  return r.agent.done()

class SkillTests(unittest.TestCase):
  
  def test_decorator(self):
    self.assertTrue('an_intent' in handlers)
    self.assertEqual(handlers['an_intent'], a_handler)

  def test_register(self):
    register('another_intent', another_handler)

    self.assertTrue('another_intent' in handlers)
    self.assertEqual(handlers['another_intent'], another_handler)
