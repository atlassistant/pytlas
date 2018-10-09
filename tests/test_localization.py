from sure import expect
from unittest.mock import patch, mock_open
from pytlas.localization import translations, register, module_translations

@translations ('fr', 'amodule')
def some_translations(): return {
  'hi': 'bonjour',
  'bye': 'au revoir',
}

class TestLocalization:

  def test_it_should_be_imported_with_the_decorator(self):
    expect(module_translations).to.have.key('amodule')
    expect(module_translations['amodule']).to.have.key('fr')
    expect(module_translations['amodule']['fr']['hi']).to.equal('bonjour')
    expect(module_translations['amodule']['fr']['bye']).to.equal('au revoir')

  def test_it_should_be_imported_with_the_register_function_with_dict(self):
    register ('en', {
      'hi': 'hello',
      'bye': 'see ya!',
    }, 'amodule')

    expect(module_translations).to.have.key('amodule')
    expect(module_translations['amodule']).to.have.key('en')
    expect(module_translations['amodule']['en']['hi']).to.equal('hello')
    expect(module_translations['amodule']['en']['bye']).to.equal('see ya!')

  def test_it_should_be_imported_with_the_register_function_with_filepath(self):
    with patch('builtins.open') as mock:
      mock_open(mock, """
{
  "hi": "buongiorno",
  "bye": "arrivederci"
}
""")

      with patch('pytlas.utils.get_module_path', return_value='/home/pytlas/amodule') as mock_module_path:
        register('it', './a_path', 'amodule')

        expect(module_translations).to.have.key('amodule')
        expect(module_translations['amodule']).to.have.key('it')
        expect(module_translations['amodule']['it']['hi']).to.equal('buongiorno')
        expect(module_translations['amodule']['it']['bye']).to.equal('arrivederci')
