import datetime, os
from sure import expect
from pytlas.interpreters import Intent, SlotValue, SlotValues

try:
  from pytlas.interpreters.snips import SnipsInterpreter
  
  # Train the interpreter once to speed up tests
  interpreter = SnipsInterpreter('en')
  interpreter.fit_from_file(os.path.join(os.path.dirname(__file__), 'training.json'))

  class TestSnipsInterpreter:

    def test_it_should_returns_empty_results_when_not_fitted(self):
      i = SnipsInterpreter('en')

      expect(i.is_ready).to.be.false
      expect(i.parse('a message')).to.be.empty
      expect(i.parse_slot('get_forecast', 'date', 'tomorrow')).to.be.empty

    def test_it_should_contains_intents_defined_in_the_dataset(self):
      expect(interpreter.is_ready).to.be.true
      expect(interpreter.intents).to.equal(['lights_on', 'lights_off', 'get_forecast'])

    def test_it_should_parse_an_intent_with_slots_correctly(self):
      intents = interpreter.parse('will it rain in Paris and London today')

      expect(intents).to.be.a(list)
      expect(intents).to.have.length_of(1)

      intent = intents[0]
      expect(intent.name).to.equal('get_forecast')
      expect(intent).to.be.an(Intent)
      expect(intent.slots).to.be.a(dict)
      expect(intent.slots).to.have.length_of(2)

      date = intent.slot('date')
      expect(date).to.be.a(SlotValues)
      expect(date).to.have.length_of(1)
      expect(date.first().value).to.contain(datetime.datetime.now().date().isoformat())

      location = intent.slot('location')
      expect(location).to.be.a(SlotValues)
      expect(location).to.have.length_of(2)

      locations = [i.value for i in location]
      expect(locations).to.contain('paris')
      expect(locations).to.contain('london')

    def test_it_should_parse_intent_with_date_range_correctly(self):
      intents = interpreter.parse('will it rain between from the third of september 2018 to the fifth of september 2018')

      expect(intents).to.have.length_of(1)

      intent = intents[0]
      expect(intent.name).to.equal('get_forecast')
      expect(intent.slots).to.have.length_of(1)
      expect(intent.slot('date')).to.have.length_of(1)

      slot = intent.slot('date').first()
      date_value = slot.value

      expect(date_value.startswith('2018-09-03 00:00:00')).to.be.true
      expect(slot.meta['value']['kind']).to.equal('TimeInterval')
      expect(slot.meta['value']['from'].startswith('2018-09-03 00:00:00')).to.be.true
      expect(slot.meta['value']['to'].startswith('2018-09-06 00:00:00')).to.be.true
    
    def test_it_should_parse_builtin_slot_correctly(self):
      slots = interpreter.parse_slot('get_forecast', 'date', 'today')

      expect(slots).to.have.length_of(1)

      slot = slots[0]

      expect(slot.value).to.contain(datetime.datetime.now().date().isoformat())
      expect(slot.meta['value']['kind']).to.equal('InstantTime')

    def test_it_should_parse_builtin_slot_range_correctly(self):
      slots = interpreter.parse_slot('get_forecast', 'date', 'from the third of september 2018 to the fifth of september 2018')

      expect(slots).to.have.length_of(1)

      slot = slots[0]

      expect(slot.value.startswith('2018-09-03 00:00:00')).to.be.true
      expect(slot.meta['value']['kind']).to.equal('TimeInterval')
      expect(slot.meta['value']['from'].startswith('2018-09-03 00:00:00')).to.be.true
      expect(slot.meta['value']['to'].startswith('2018-09-06 00:00:00')).to.be.true

    def test_it_should_parse_custom_extensible_slot_correctly(self):
      slots = interpreter.parse_slot('get_forecast', 'location', 'Strasbourg')

      expect(slots).to.have.length_of(1)
      expect(slots[0].value).to.equal('Strasbourg')

    def test_it_should_parse_custom_slot_correctly(self):
      slots = [s.value for s in interpreter.parse_slot('lights_on', 'room', 'kitchen and bedroom')]

      expect(slots).to.have.length_of(2)
      expect(slots).to.equal(['kitchen', 'bedroom'])

    def test_it_should_parse_custom_slot_with_synonyms_correctly(self):
      slots = [s.value for s in interpreter.parse_slot('lights_on', 'room', 'kitchen and cellar please')]

      expect(slots).to.have.length_of(2)
      expect(slots).to.equal(['kitchen', 'basement'])

    def test_it_should_parse_unknown_slot_correctly(self):
      slots = interpreter.parse_slot('get_forecast', 'something', 'given value expected')

      expect(slots).to.have.length_of(1)
      expect(slots[0].value).to.equal('given value expected')

except ImportError:
  print ('snips_nlu could not be imported, tests will be skipped')
