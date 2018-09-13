import unittest
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