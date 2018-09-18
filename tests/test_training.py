import unittest
from unittest.mock import patch, mock_open
from pytlas.training import register, training, module_trainings

@training ('en', 'amodule')
def en_data(): return """
%[get_forecast]
  will it rain in @[city]

@[city]
  paris
  london
"""

class TrainingTests(unittest.TestCase):

  def test_decorator(self):
    self.assertTrue('amodule' in module_trainings)
    self.assertTrue('en' in module_trainings['amodule'])
    self.assertEqual(1, len(module_trainings['amodule']['en']['intents']))
    self.assertEqual(1, len(module_trainings['amodule']['en']['entities']))

  def test_register(self):
    register ('fr', """
%[some_intent]
  with training data

%[another one]
  with another data

@[and_entity]
  with some value
""", 'amodule')

    self.assertTrue('amodule' in module_trainings)
    self.assertTrue('fr' in module_trainings['amodule'])
    self.assertEqual(2, len(module_trainings['amodule']['fr']['intents']))
    self.assertEqual(1, len(module_trainings['amodule']['fr']['entities']))

    with patch('builtins.open') as mock:
      mock_open(mock, """
%[some_intent]
  with training data

%[another one]
  with another data

@[and_entity]
  with some value
""")

      with patch('pytlas.utils.get_module_path', return_value='/home/pytlas/amodule'):
        with patch('os.path.isfile', return_value=True):
          register('it', './a_path', 'amodule')

          self.assertTrue('amodule' in module_trainings)
          self.assertTrue('it' in module_trainings['amodule'])
          self.assertEqual(2, len(module_trainings['amodule']['it']['intents']))
          self.assertEqual(1, len(module_trainings['amodule']['it']['entities']))