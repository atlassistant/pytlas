from sure import expect
from pytlas.store import Store

class TestStore:

  def test_it_should_be_named_and_expose_a_logger(self):
    s = Store('test')

    expect(s.name).to.equal('test')
    expect(s._logger.name).to.equal('test')

  def test_it_should_be_populated_with_initial_data(self):
    s = Store('test')
    expect(s._data).to.be.empty

    s = Store('test', { 'some': 'data' })
    expect(s._data).to.equal({ 'some': 'data' })

  def test_it_should_reset_to_its_initial_data(self):
    s = Store('test', { 'initial': 'data' })
    s._data['another'] = 'value'
    s._data['and'] = 'one more'

    s.reset()

    expect(s._data).to.equal({ 'initial': 'data' })