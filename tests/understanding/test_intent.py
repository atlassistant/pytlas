from sure import expect
from pytlas.understanding import Intent, SlotValues, SlotValue

class TestIntent:

  def test_it_should_contains_the_intent_name(self):
    intent = Intent('get_forecast')

    expect(intent.name).to.be.equal('get_forecast')
    expect(intent.meta).to.be.empty
    expect(intent.slots).to.be.empty

  def test_it_should_parse_kwargs_as_slot_values(self):
    intent = Intent('get_forecast', date='today', city=['Paris', 'New York'])

    expect(intent.name).to.be.equal('get_forecast')
    expect(intent.slots).to.have.length_of(2)
    expect(intent.slots).to.have.key('date')
    expect(intent.slots).to.have.key('city')

    date = intent.slot('date')

    expect(date).to.be.a(SlotValues)
    expect(date).to.have.length_of(1)
    expect(date.first().value).to.equal('today')

    city = intent.slot('city')

    expect(city).to.be.a(SlotValues)
    expect(city).to.have.length_of(2)
    expect(city.first().value).to.equal('Paris')
    expect(city.last().value).to.equal('New York')
