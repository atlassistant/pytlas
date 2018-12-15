from sure import expect
from pytlas.localization import translations, register, module_translations, get_translations
import pytlas.settings as settings

settings.set(settings.SETTING_LANG, []) # Allow all languages to be loaded

@translations ('fr', 'amodule')
def some_translations(): return {
  'hi': 'bonjour',
  'bye': 'au revoir',
}

class TestLocalization:

  def test_it_should_be_imported_with_the_decorator(self):
    expect(module_translations).to.have.key('amodule')
    expect(module_translations['amodule']).to.have.key('fr')

    r = module_translations['amodule']['fr']()

    expect(r['hi']).to.equal('bonjour')
    expect(r['bye']).to.equal('au revoir')

  def test_it_should_evaluate_translations_correctly(self):

    register('it', lambda: {
      'hi': 'ciao',
      'bye': 'addio',
    }, 'amodule')

    t = get_translations('it')

    expect(t).to.have.key('amodule')
    expect(t['amodule']).to.have.key('hi')
    expect(t['amodule']['hi']).to.equal('ciao')
    expect(t['amodule']).to.have.key('bye')
    expect(t['amodule']['bye']).to.equal('addio');

  def test_it_should_be_imported_with_the_register_function_with_dict(self):

    register('en', lambda: {
      'hi': 'hello',
      'bye': 'see ya!',
    }, 'amodule')

    expect(module_translations).to.have.key('amodule')
    expect(module_translations['amodule']).to.have.key('en')

    r = module_translations['amodule']['en']()

    expect(r['hi']).to.equal('hello')
    expect(r['bye']).to.equal('see ya!')
