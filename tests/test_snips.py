import datetime, os
from dateutil.parser import parse as dateParse
from dateutil.relativedelta import relativedelta
from sure import expect
from pytlas.interpreters import Intent, SlotValue, SlotValues
from pytlas.interpreters.slot import UnitValue

try:
  from pytlas.interpreters.snips import SnipsInterpreter, get_entity_value
  
  # Train the interpreter once to speed up tests
  fitted_interpreter = SnipsInterpreter('en')
  fitted_interpreter.fit_from_file(os.path.join(os.path.dirname(__file__), 'training.json'))

  cached_interpreter = SnipsInterpreter('en', os.path.join(os.path.dirname(__file__), 'snips_interpreter_cache'))
  cached_interpreter.load_from_cache()

  # Each test method will be run on a freshly fitted engine and on a cached one to be sure
  # there is no particular cases
  interpreters = [fitted_interpreter, cached_interpreter]

  class TestSnipsInterpreter:

    def test_it_should_returns_empty_results_when_not_fitted(self):
      i = SnipsInterpreter('en')

      expect(i.is_ready).to.be.false
      expect(i.parse('a message')).to.be.empty
      expect(i.parse_slot('get_forecast', 'date', 'tomorrow')).to.be.empty

    def it_should_contains_intents_defined_in_the_dataset(self, interpreter):
      expect(interpreter.is_ready).to.be.true
      expect(interpreter.intents).to.have.length_of(3)
      expect(interpreter.intents).to.contain('lights_on')
      expect(interpreter.intents).to.contain('lights_off')
      expect(interpreter.intents).to.contain('get_forecast')

    def test_it_should_contains_intents_defined_in_the_dataset(self):
      for interpreter in interpreters:
        yield self.it_should_contains_intents_defined_in_the_dataset, interpreter

    def it_should_returns_an_empty_array_when_no_intent_has_been_found(self, interpreter):
      intents = interpreter.parse('yolo')

      expect(intents).to.be.empty

    def test_it_should_returns_an_empty_array_when_no_intent_has_been_found(self):
      for interpreter in interpreters:
        yield self.it_should_returns_an_empty_array_when_no_intent_has_been_found, interpreter

    def it_should_parse_an_intent_with_slots_correctly(self, interpreter):
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
      expect(date.first().value).to.be.a(datetime.datetime)
      expect(date.first().value.isoformat()).to.contain(datetime.datetime.now().date().isoformat())

      location = intent.slot('location')
      expect(location).to.be.a(SlotValues)
      expect(location).to.have.length_of(2)

      locations = [i.value for i in location]
      expect(locations).to.contain('paris')
      expect(locations).to.contain('london')

    def test_it_should_parse_an_intent_with_slots_correctly(self):
      for interpreter in interpreters:
        yield self.it_should_parse_an_intent_with_slots_correctly, interpreter

    def it_should_parse_intent_with_date_range_correctly(self, interpreter):
      intents = interpreter.parse('will it rain from september 3 2018 to september 5 2018')

      expect(intents).to.have.length_of(1)

      intent = intents[0]
      expect(intent.name).to.equal('get_forecast')
      expect(intent.slots).to.have.length_of(1)
      expect(intent.slot('date')).to.have.length_of(1)

      date_value = intent.slot('date').first().value

      expect(date_value).to.be.a(tuple)
      expect(date_value).to.have.length_of(2)
      expect(date_value[0]).to.be.a(datetime.datetime)
      expect(date_value[0].isoformat().startswith('2018-09-03T00:00:00')).to.be.true

      expect(date_value[1]).to.be.a(datetime.datetime)
      expect(date_value[1].isoformat().startswith('2018-09-06T00:00:00')).to.be.true
    
    def test_it_should_parse_intent_with_date_range_correctly(self):
      for interpreter in interpreters:
        yield self.it_should_parse_intent_with_date_range_correctly, interpreter

    def it_should_parse_builtin_slot_correctly(self, interpreter):
      slots = interpreter.parse_slot('get_forecast', 'date', 'today')

      expect(slots).to.have.length_of(1)

      slot = slots[0]

      expect(slot.value).to.be.a(datetime.datetime)
      expect(slot.value.isoformat()).to.contain(datetime.datetime.now().date().isoformat())
      expect(slot.meta['value']['kind']).to.equal('InstantTime')

    def test_it_should_parse_builtin_slot_correctly(self):
      for interpreter in interpreters:
        yield self.it_should_parse_builtin_slot_correctly, interpreter

    def it_should_parse_builtin_slot_range_correctly(self, interpreter):
      slots = interpreter.parse_slot('get_forecast', 'date', 'from the third of september 2018 to the fifth of september 2018')

      expect(slots).to.have.length_of(1)

      slot = slots[0]
      date_value = slot.value

      expect(date_value).to.be.a(tuple)
      expect(date_value).to.have.length_of(2)
      expect(date_value[0]).to.be.a(datetime.datetime)
      expect(date_value[0].isoformat().startswith('2018-09-03T00:00:00')).to.be.true

      expect(date_value[1]).to.be.a(datetime.datetime)
      expect(date_value[1].isoformat().startswith('2018-09-06T00:00:00')).to.be.true

    def test_it_should_parse_builtin_slot_range_correctly(self):
      for interpreter in interpreters:
        yield self.it_should_parse_builtin_slot_range_correctly, interpreter

    def it_should_parse_custom_extensible_slot_correctly(self, interpreter):
      slots = interpreter.parse_slot('get_forecast', 'location', 'Strasbourg')

      expect(slots).to.have.length_of(1)
      expect(slots[0].value).to.equal('Strasbourg')

    def test_it_should_parse_custom_extensible_slot_correctly(self):
      for interpreter in interpreters:
        yield self.it_should_parse_custom_extensible_slot_correctly, interpreter

    def it_should_parse_custom_slot_correctly(self, interpreter):
      slots = [s.value for s in interpreter.parse_slot('lights_on', 'room', 'kitchen and bedroom')]

      expect(slots).to.have.length_of(2)
      expect(slots).to.equal(['kitchen', 'bedroom'])

    def test_it_should_parse_custom_slot_correctly(self):
      for interpreter in interpreters:
        yield self.it_should_parse_custom_slot_correctly, interpreter

    def it_should_parse_custom_slot_with_synonyms_correctly(self, interpreter):
      slots = [s.value for s in interpreter.parse_slot('lights_on', 'room', 'kitchen and cellar please')]

      expect(slots).to.have.length_of(2)
      expect(slots).to.equal(['kitchen', 'basement'])

    def test_it_should_parse_custom_slot_with_synonyms_correctly(self):
      for interpreter in interpreters:
        yield self.it_should_parse_custom_slot_with_synonyms_correctly, interpreter

    def it_should_parse_unknown_slot_correctly(self, interpreter):
      slots = interpreter.parse_slot('get_forecast', 'something', 'given value expected')

      expect(slots).to.have.length_of(1)
      expect(slots[0].value).to.equal('given value expected')

    def test_it_should_parse_unknown_slot_correctly(self):
      for interpreter in interpreters:
        yield self.it_should_parse_unknown_slot_correctly, interpreter

  class TestSnipsGetEntityValue:
    """Tests returns of the NLU concerning slots. See https://github.com/snipsco/snips-nlu-ontology#results-examples
    """

    def test_it_should_handle_amount_of_money(self):
      r = get_entity_value({
        'kind': 'AmountOfMoney',
        'value': 10.05,
        'precision': 'Approximate',
        'unit': '€',
      })

      expect(r).to.be.a(UnitValue)
      expect(r.value).to.equal(10.05, epsilon=0.01)
      expect(r.unit).to.equal('€')

    def test_it_should_handle_temperature(self):
      r = get_entity_value({
        'kind': 'Temperature',
        'value': 23.5,
        'unit': 'celsius',
      })

      expect(r).to.be.a(UnitValue)
      expect(r.value).to.equal(23.5, epsilon=0.01)
      expect(r.unit).to.equal('celsius')
    
    def test_it_should_handle_instant_time(self):
      r = get_entity_value({
        'kind': 'InstantTime',
        'value': '2017-06-13 18:00:00 +02:00',
        'grain': 'Hour',
        'precision': 'Exact',
      })

      expected = dateParse('2017-06-13 18:00:00 +02:00')

      expect(r).to.be.a(datetime.datetime)
      expect(r).to.equal(expected)

    def test_it_should_handle_time_interval(self):
      r = get_entity_value({
        'kind': 'TimeInterval',
        'from': '2017-06-07 18:00:00 +02:00',
        'to': '2017-06-08 00:00:00 +02:00',
      })

      expected_from = dateParse('2017-06-07 18:00:00 +02:00')
      expected_to = dateParse('2017-06-08 00:00:00 +02:00')

      expect(r).to.be.a(tuple)
      expect(r[0]).to.equal(expected_from)
      expect(r[1]).to.equal(expected_to)

    def test_it_should_handle_duration(self):
      r = get_entity_value({
        'kind': 'Duration',
        'years': 1,
        'quarters': 0,
        'months': 3,
        'weeks': 2,
        'days': 6,
        'hours': 10,
        'minutes': 30,
        'seconds': 59,
        'precision': 'Exact',
      })

      expected_delta = relativedelta(
        years=1,
        months=3,
        weeks=2,
        days=6,
        hours=10,
        minutes=30,
        seconds=59
      )

      expect(r).to.be.a(relativedelta)
      expect(r).to.equal(expected_delta)

    def test_it_should_handle_number(self):
      r = get_entity_value({
        'kind': 'Number',
        'value': 42.2,
      })

      expect(r).to.equal(42.2, epsilon=0.01)

    def test_it_should_handle_ordinal(self):
      r = get_entity_value({
        'kind': 'Ordinal',
        'value': 2,
      })

      expect(r).to.equal(2)

    def test_it_should_handle_percentage(self):
      r = get_entity_value({
        'kind': 'Percentage',
        'value': 20.0,
      })

      expect(r).to.equal(0.2, epsilon=0.01)

    def test_it_should_handle_music_album(self):
      r = get_entity_value({
        'kind': 'MusicAlbum',
        'value': 'Discovery'
      })

      expect(r).to.equal('Discovery')
    
    def test_it_should_handle_music_artist(self):
      r = get_entity_value({
        'kind': 'MusicArtist',
        'value': 'Daft Punk'
      })

      expect(r).to.equal('Daft Punk')

    def test_it_should_handle_music_track(self):
      r = get_entity_value({
        'kind': 'MusicTrack',
        'value': 'Harder Better Faster Stronger'
      })

      expect(r).to.equal('Harder Better Faster Stronger')

    def test_it_should_handle_custom(self):
      r = get_entity_value({
        'kind': 'Custom',
        'value': 'kitchen'
      })

      expect(r).to.equal('kitchen')

except ImportError:
  print ('snips_nlu could not be imported, tests will be skipped')
