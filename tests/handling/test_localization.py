from sure import expect
from pytlas.handling.localization import translations, TranslationsStore, global_translations

class TestLocalization:

  def teardown(self):
    global_translations.reset()

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

  def test_it_should_be_imported_with_the_decorator_in_the_given_store(self):
    s = TranslationsStore()

    @translations ('fr', store=s, package='amodule')
    def some_translations(): return {
      'hi': 'bonjour',
      'bye': 'au revoir',
    }

    expect(s._data).to.equal({
      'amodule': {
        'fr': some_translations,
      },
    })

  def test_it_should_be_imported_with_the_decorator_in_the_global_store_if_not_provided(self):
    @translations ('fr', package='amodule')
    def some_translations(): return {
      'hi': 'bonjour',
      'bye': 'au revoir',
    }

    expect(global_translations._data).to.equal({
      'amodule': {
        'fr': some_translations,
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

    expect(s.all('it')).to.equal({
      'amodule': {
        'hi': 'ciao',
        'bye': 'addio',
      },
    })

    expect(s.all('fr')).to.equal({
      'amodule': {
        'hi': 'bonjour',
        'bye': 'au revoir',
      },
    })

  def test_it_should_retrieve_all_translations_for_a_particular_package(self):
    s = TranslationsStore()
    s.register('fr', lambda: {
      'hi': 'salut',
      'bye': 'à plus',
    }, 'mymodule')
    s.register('fr', lambda: {
      'hi': 'bonjour',
      'bye': 'au revoir',
    }, 'amodule')

    expect(s.get('mymodule', 'fr')).to.equal({
      'hi': 'salut',
      'bye': 'à plus',
    })

    expect(s.get('mymodule', 'it')).to.be.empty