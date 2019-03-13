from sure import expect
from pytlas.testing import AttrDict, ModelMock

class TestAttrDict:
  
  def test_it_should_expose_keys_as_attributes(self):
    d = AttrDict({
      'one': 1,
      'two': 2,
    })

    expect(d.one).to.equal(1)
    expect(d.two).to.equal(2)
    expect(lambda: d.three).to.throw(AttributeError)

class TestModelMock:

  def test_it_should_take_argument_names_into_account(self):
    m = ModelMock().has_arguments_mapping(['one', 'two'])

    m(1, 2, three=3)
    m(4, 5, three=6)

    call = m.get_call()

    expect(call).to.be.a(AttrDict)
    expect(call.one).to.equal(1)
    expect(call.two).to.equal(2)
    expect(call.three).to.equal(3)

    call = m.get_call(1)

    expect(call).to.be.a(AttrDict)
    expect(call.one).to.equal(4)
    expect(call.two).to.equal(5)
    expect(call.three).to.equal(6)

    expect(lambda: m.get_call(2)).to.throw(AssertionError)
