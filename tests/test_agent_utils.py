import unittest
from pytlas.interpreters import SlotValue
from pytlas.agent import STATE_PREFIX, find_matches, is_builtin, keep_one

class AgentUtilsTests(unittest.TestCase):

  def test_find_matches(self):
    choices = ['kitchen', 'bedroom', 'living room']
    values = [SlotValue('kitch'), SlotValue('bedoorm'), SlotValue('nothing here')]

    matched = list(find_matches(choices, values))

    self.assertEqual(2, len(matched))

    matched_values = [m.value for m in matched]

    self.assertTrue('kitchen' in matched_values)
    self.assertTrue('bedroom' in matched_values)

  def test_is_builtin(self):
    self.assertTrue(is_builtin(STATE_PREFIX + 'something'))
    self.assertFalse(is_builtin('something'))

  def test_keep_one(self):
    self.assertEqual('a text', keep_one('a text'))

    v = ['a text', 'another text']
    r = keep_one(v)

    self.assertIsInstance(r, str)
    self.assertTrue(r in v)