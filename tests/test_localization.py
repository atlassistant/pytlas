from sure import expect
from pytlas.localization import translations, TranslationsStore, global_translations

class TestLocalization:

  def teardown(self):
    global_translations.reset()

  def test_it_should_be_imported_with_the_decorator_in_the_given_store(self):
    s = TranslationsStore()

    @translations ('fr', store=s, package='amodule')
    def some_translations(): return {
      'hi': 'bonjour',
      'bye': 'au revoir',
    }

    expect(s._data).to.have.key('amodule')
    expect(s._data['amodule']).to.have.key('fr')

    r = s._data['amodule']['fr']()

    expect(r['hi']).to.equal('bonjour')
    expect(r['bye']).to.equal('au revoir')

  def test_it_should_be_imported_with_the_decorator_in_the_global_store_if_not_provided(self):
    @translations ('fr', package='amodule')
    def some_translations(): return {
      'hi': 'bonjour',
      'bye': 'au revoir',
    }

    expect(global_translations._data).to.have.key('amodule')
    expect(global_translations._data['amodule']).to.have.key('fr')

    r = global_translations._data['amodule']['fr']()

    expect(r['hi']).to.equal('bonjour')
    expect(r['bye']).to.equal('au revoir')

  def test_it_should_register_translations_correctly(self):
    s = TranslationsStore()
    f = lambda: {
      'hi': 'ciao',
      'bye': 'addio',
    }
    s.register('it', f, 'amodule')

    expect(s._data).to.equal({
      'amodule': {
        'it': f,
      },
    })
  
  def test_it_should_retrieve_all_translations_for_a_given_language(self):
    s = TranslationsStore()
    s.register('it', lambda: {
      'hi': 'ciao',
      'bye': 'addio',
    }, 'amodule')
    s.register('fr', lambda: {
      'hi': 'bonjour',
      'bye': 'au revoir',
    }, 'amodule')

    expect(s.get('it')).to.equal({
      'amodule': {
        'hi': 'ciao',
        'bye': 'addio',
      },
    })

    expect(s.get('fr')).to.equal({
      'amodule': {
        'hi': 'bonjour',
        'bye': 'au revoir',
      },
    })
