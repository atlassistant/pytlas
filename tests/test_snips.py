import unittest, datetime
from unittest.mock import patch, mock_open

snips_imported = True

try:
  from pytlas.interpreters.snips import SnipsInterpreter
except ImportError:
  snips_imported = False

def snips_available(func):
  """Check if snips is imported before executing the test
  """

  def new(*args, **kwargs):
    if not snips_imported:
      return args[0].skipTest('snips could not be imported')

    return func(*args, **kwargs)

  return new
    

class SnipsTests(unittest.TestCase):

  @snips_available
  def test_with_no_training_file(self):
    interp = SnipsInterpreter('', False)
    interp.fit_as_needed()

  @snips_available
  def test_not_fitted(self):
    interp = SnipsInterpreter('', False)

    self.assertFalse(interp.is_ready)
    self.assertEqual([], interp.parse('a message'))

  @snips_available
  def test_parse(self):
    interp = SnipsInterpreter('./../example', False)
    interp.fit_as_needed()

    self.assertTrue(interp.is_ready)
    self.assertEqual(3, len(interp.intents))

    intents = interp.parse('will it rain in Paris and London today')

    self.assertEqual(1, len(intents))

    intent = intents[0]

    self.assertEqual(2, len(intent.slots))
    self.assertEqual(1, len(intent.slot('date')))
    self.assertTrue(datetime.datetime.now().date().isoformat() in intent.slot('date').first().value)
    self.assertEqual(2, len(intent.slot('city')))

    city_values = [i.value for i in intent.slot('city')]

    self.assertTrue('paris' in city_values)
    self.assertTrue('london' in city_values)

  @snips_available
  def test_parse_slot(self):
    interp = SnipsInterpreter('./../example', False)
    interp.fit_as_needed()

    slots = interp.parse_slot('get_forecast', 'date', 'on today')

    self.assertEqual(1, len(slots))
    self.assertTrue(datetime.datetime.now().date().isoformat() in slots[0].value)

    slots = [s.value for s in interp.parse_slot('lights_on', 'room', 'kitchen and bedroom')]

    self.assertEqual(2, len(slots))
    self.assertTrue('kitchen' in slots)
    self.assertTrue('bedroom' in slots)
