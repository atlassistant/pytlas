from sure import expect
from pytlas.skill import intent, register, handlers, meta, register_metadata, module_metas

@intent('an_intent')
def a_handler(r):
  return r.agent.done()

@meta('pkg')
def some_meta(): return {
  'name': 'a skill',
}

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

  def test_it_should_have_meta_imported_with_the_decorator(self):
    expect(module_metas).to.have.key('pkg')
    expect(module_metas['pkg']).to.equal(some_meta)

  def test_it_should_have_meta_imported_with_the_register_function(self):
    
    def another_meta():
      return {
        'name': 'another skill',
      }
    
    register_metadata(another_meta, 'another_pkg')

    expect(module_metas).to.have.key('another_pkg')
    expect(module_metas['another_pkg']).to.equal(another_meta)
