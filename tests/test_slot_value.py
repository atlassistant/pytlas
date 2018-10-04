from sure import expect
from datetime import datetime
from pytlas.interpreters.slot import SlotValue

class TestSlotValue:

  def test_it_should_give_the_value(self):
    v = SlotValue('kitchen')

    expect(v.value).to.equal('kitchen')

  def test_it_should_have_meta(self):
    v = SlotValue('kitchen', type='room', another='meta')

    expect(v.meta).to.have.length_of(2)
    expect(v.meta).to.have.key('type')
    expect(v.meta).to.have.key('another')
    expect(v.meta['type']).to.equal('room')
    expect(v.meta['another']).to.equal('meta')

  def test_it_should_parse_the_value_as_date(self):
    v = SlotValue('2018-09-22 00:00:00 +02:00').value_as_date

    expect(v).to.be.a(datetime)
    expect(v.year).to.equal(2018)
    expect(v.month).to.equal(9)
    expect(v.day).to.equal(22)

  def test_it_should_returns_none_when_value_is_none(self):
    v = SlotValue(None).value_as_date

    expect(v).to.be.none
  
  def test_it_should_returns_none_when_value_is_not_a_valid_date(self):
    v = SlotValue('212fzekl').value_as_date
    
    expect(v).to.be.none
