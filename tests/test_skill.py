from sure import expect
from pytlas.skill import intent, register, handlers

@intent('an_intent')
def a_handler(r):
  return r.agent.done()

class TestSkill:

  def test_it_should_be_imported_with_the_decorator(self):
    expect(handlers).to.have.key('an_intent')
    expect(handlers['an_intent']).to.equal(a_handler)

  def test_it_should_be_imported_with_the_register_function(self):

    def another_handler(r):
      return r.agent.done()

    register('another_intent', another_handler)

    expect(handlers).to.have.key('another_intent')
    expect(handlers['another_intent']).to.equal(another_handler)
