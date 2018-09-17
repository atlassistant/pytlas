import unittest
from unittest.mock import patch, mock_open
from pytlas.localization import translations, register, module_translations

@translations ('fr', 'amodule')
def some_translations(): return {
  'hi': 'bonjour',
  'bye': 'au revoir',
}

class LocalizationTests(unittest.TestCase):

  def test_decorator(self):
    self.assertTrue('amodule' in module_translations)
    self.assertTrue('fr' in module_translations['amodule'])
    self.assertEqual('bonjour', module_translations['amodule']['fr']['hi'])
    self.assertEqual('au revoir', module_translations['amodule']['fr']['bye'])

  def test_register(self):
    register ('en', {
      'hi': 'hello',
      'bye': 'see ya!',
    }, 'amodule')

    self.assertTrue('amodule' in module_translations)
    self.assertTrue('en' in module_translations['amodule'])
    self.assertEqual('hello', module_translations['amodule']['en']['hi'])
    self.assertEqual('see ya!', module_translations['amodule']['en']['bye'])

    with patch('builtins.open') as mock:
      mock_open(mock, """
{
  "hi": "buongiorno",
  "bye": "arrivederci"
}
""")

      with patch('pytlas.utils.get_module_path', return_value='/home/pytlas/amodule') as mock_module_path:
        register('it', './a_path', 'amodule')

        self.assertTrue('amodule' in module_translations)
        self.assertTrue('it' in module_translations['amodule'])
        self.assertEqual('buongiorno', module_translations['amodule']['it']['hi'])
        self.assertEqual('arrivederci', module_translations['amodule']['it']['bye'])