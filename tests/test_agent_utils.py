import unittest
from pytlas.interpreters import SlotValue
from pytlas.agent import STATE_PREFIX, STATE_SUFFIX, find_match, is_builtin, keep_one

class AgentUtilsTests(unittest.TestCase):

  def test_find_match(self):
    choices = ['kitchen', 'bedroom', 'living room']

    self.assertEqual('kitchen', find_match(choices, 'kitch'))
    self.assertEqual('bedroom', find_match(choices, 'bedoorm'))
    self.assertIsNone(find_match(choices, 'nothing here'))

  def test_is_builtin(self):
    self.assertTrue(is_builtin(STATE_PREFIX + 'something' + STATE_SUFFIX))
    self.assertFalse(is_builtin('something'))

  def test_keep_one(self):
    self.assertEqual('a text', keep_one('a text'))

    v = ['a text', 'another text']
    r = keep_one(v)

    self.assertIsInstance(r, str)
    self.assertTrue(r in v)