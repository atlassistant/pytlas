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
  def test_not_fitted(self):
    interp = SnipsInterpreter('en')

    self.assertFalse(interp.is_ready)
    self.assertEqual([], interp.parse('a message'))

  @snips_available
  def test_parse(self):
    interp = SnipsInterpreter('en')
    interp.fit_from_file('./training.json')

    self.assertTrue(interp.is_ready)
    self.assertEqual(3, len(interp.intents))

    intents = interp.parse('will it rain in Paris and London today')

    self.assertEqual(1, len(intents))

    intent = intents[0]

    self.assertEqual(2, len(intent.slots))
    self.assertEqual(1, len(intent.slot('date')))
    self.assertTrue(datetime.datetime.now().date().isoformat() in intent.slot('date').first().value)
    self.assertEqual(2, len(intent.slot('location')))

    location_values = [i.value for i in intent.slot('location')]

    self.assertTrue('paris' in location_values)
    self.assertTrue('london' in location_values)

  @snips_available
  def test_parse_intent_date_range(self):
    interp = SnipsInterpreter('en')
    interp.fit_from_file('./training.json')

    intents = interp.parse('will it rain between from the third of september 2018 to the fifth of september 2018')

    self.assertEqual(1, len(intents))

    intent = intents[0]

    self.assertEqual('get_forecast', intent.name)

    self.assertEqual(1, len(intent.slots))
    self.assertEqual(1, len(intent.slot('date')))

    slot = intent.slot('date').first()
    date_value = slot.value

    self.assertTrue(date_value.startswith('2018-09-03 00:00:00'))
    self.assertEqual('TimeInterval', slot.meta.get('value', {}).get('kind'))
    self.assertTrue(slot.meta.get('value', {}).get('from', '').startswith('2018-09-03 00:00:00'))
    self.assertTrue(slot.meta.get('value', {}).get('to', '').startswith('2018-09-06 00:00:00'))

  @snips_available
  def test_parse_slot_date_range(self):
    interp = SnipsInterpreter('en')
    interp.fit_from_file('./training.json')

    slots = interp.parse_slot('get_forecast', 'date', 'from the third of september 2018 to the fifth of september 2018')

    self.assertEqual(1, len(slots))

    slot = slots[0]

    self.assertTrue(slot.value.startswith('2018-09-03 00:00:00'))
    self.assertEqual('TimeInterval', slot.meta.get('value', {}).get('kind'))
    self.assertTrue(slot.meta.get('value', {}).get('from', '').startswith('2018-09-03 00:00:00'))
    self.assertTrue(slot.meta.get('value', {}).get('to', '').startswith('2018-09-06 00:00:00'))

  @snips_available
  def test_parse_slot(self):
    interp = SnipsInterpreter('en')
    interp.fit_from_file('./training.json')

    slots = interp.parse_slot('get_forecast', 'date', 'on today')

    self.assertEqual(1, len(slots))
    self.assertTrue(datetime.datetime.now().date().isoformat() in slots[0].value)

    slots = [s.value for s in interp.parse_slot('lights_on', 'room', 'kitchen and bedroom')]

    self.assertEqual(2, len(slots))
    self.assertTrue('kitchen' in slots)
    self.assertTrue('bedroom' in slots)

  @snips_available
  def test_parse_slot_with_synonym(self):
    interp = SnipsInterpreter('en')
    interp.fit_from_file('./training.json')

    slots = [s.value for s in interp.parse_slot('lights_on', 'room', 'kitchen and cellar')]
    self.assertEqual(2, len(slots))
    self.assertTrue('kitchen' in slots)
    self.assertTrue('basement' in slots)
