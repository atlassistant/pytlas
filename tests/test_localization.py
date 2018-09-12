import unittest
from unittest.mock import patch, mock_open
from pytlas.loaders import list_translations, import_translations
from pytlas.localization import translations

class LocalizationTests(unittest.TestCase):

  @patch('glob.glob')
  def test_list_translations(self, glob_mock):
    glob_mock.return_value = ['lights.fr.json', 'lights.en.json']
    
    translations = list(list_translations('a_directory'))

    self.assertEqual(2, len(translations))

  @patch('glob.glob')
  @patch('builtins.open')
  def test_import_translations(self, open_mock, glob_mock):
    files = {
      'lights.fr.json': """
{
  "on": "allumer",
  "off": "éteindre"
}
""",
      'lights.en.json': """
      {
        "on": "on",
        "off": "off"
      }
""",
      'weather.fr.json': """
      {
        "weather": "météo",
        "sunny": "ensoleillé"
      }
"""
    }
    
    glob_mock.return_value = list(files.keys())
    open_mock.side_effect = [
      mock_open(read_data=files['lights.fr.json']).return_value,
      mock_open(read_data=files['lights.en.json']).return_value,
      mock_open(read_data=files['weather.fr.json']).return_value,
    ]

    import_translations('a directory')

    self.assertEqual(2, len(translations.keys()))
    self.assertEqual(2, len(translations['lights']))
    self.assertEqual(1, len(translations['weather']))
    
    self.assertIn('fr', translations['lights'])
    self.assertIn('en', translations['lights'])
    self.assertIn('fr', translations['weather'])

    self.assertEqual('météo', translations['weather']['fr']['weather'])
    self.assertEqual('éteindre', translations['lights']['fr']['off'])