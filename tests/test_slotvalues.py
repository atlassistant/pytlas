import unittest
from pytlas.interpreters import SlotValue, SlotValues

class SlotValuesTests(unittest.TestCase):
  
  def test_slot_value(self):
    v = SlotValue('kitchen')

    self.assertEqual('kitchen', v.value)

  def test_slot_value_meta(self):
    v = SlotValue('kitchen', entity='rooms')

    self.assertEqual('rooms', v.meta['entity'])

  def test_slot_values_empty(self):

    v = SlotValues()

    self.assertTrue(v.is_empty())

    v1 = SlotValue('kitchen')
    v2 = SlotValue('bedroom')

    v.append(v1)
    v.append(v2)

    self.assertFalse(v.is_empty())

  def test_slot_values_first(self):

    v = SlotValues()

    self.assertIsNotNone(v.first())
    self.assertEqual(None, v.first().value)

    v.append(SlotValue('kitchen'))
    v.append(SlotValue('bedroom'))
    v.append(SlotValue('living room'))

    self.assertEqual('kitchen', v.first().value)

  def test_slot_values_last(self):

    v = SlotValues()

    self.assertIsNotNone(v.last())
    self.assertEqual(None, v.last().value)

    v.append(SlotValue('kitchen'))
    v.append(SlotValue('bedroom'))
    v.append(SlotValue('living room'))

    self.assertEqual('living room', v.last().value)