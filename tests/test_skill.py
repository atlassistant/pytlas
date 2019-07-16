from sure import expect
from pytlas.skill import intent, register, handlers, meta, register_metadata, module_metas, \
  Meta, Setting

@intent('an_intent')
def a_handler(r):
  return r.agent.done()

@meta('pkg')
def some_meta(): return {
  'name': 'a skill',
}

class TestMeta:

  def test_it_should_be_instantiable(self):
    m = Meta('lights', 
      description='Some lighting skill',
      author='Julien LEICHER',
      homepage='https://julien.leicher.me',
      media='https://somepic',
      version='1.0.0')

    expect(m.name).to.equal('lights')
    expect(m.description).to.equal('Some lighting skill')
    expect(m.author).to.equal('Julien LEICHER')
    expect(m.version).to.equal('1.0.0')
    expect(m.homepage).to.equal('https://julien.leicher.me')
    expect(m.media).to.equal('https://somepic')

  def test_it_should_convert_settings_strings_to_setting_object_if_needed(self):
    m = Meta('lights', settings=['lights.default', Setting('lights', 'other', int, 'A description')])

    expect(m.settings).to.have.length_of(2)
    expect(m.settings[0]).to.be.a(Setting)
    expect(m.settings[0].section).to.equal('lights')
    expect(m.settings[0].name).to.equal('default')

    expect(m.settings[1]).to.be.a(Setting)
    expect(m.settings[1].section).to.equal('lights')
    expect(m.settings[1].name).to.equal('other')
    expect(m.settings[1].type).to.equal(int)
    expect(m.settings[1].description).to.equal('A description')

  def test_it_should_print_correctly(self):
    m = Meta('lights', 
      description='Some lighting skill',
      author='Julien LEICHER',
      homepage='https://julien.leicher.me',
      media='https://somepic',
      version='1.0.0',
      settings=[Setting('lights', 'default')])
    
    expect(str(m)).to.equal("""lights - v1.0.0
  description: Some lighting skill
  homepage: https://julien.leicher.me
  author: Julien LEICHER
  settings: lights.default (str)
""")

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
