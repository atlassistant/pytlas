import unittest
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
    pass

  def test_register(self):
    pass