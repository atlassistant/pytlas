import unittest

snips_imported = True

try:
  from pytlas.interpreters.snips import SnipsInterpreter
except ImportError:
  snips_imported = False

def snips_available(func):
  """Check if snips is imported before executing the test
  """

  def new(*args, **kwargs):
    if not snips_imported:
      return args[0].skipTest('snips could not be imported')

    return func(*args, **kwargs)

  return new
    

class SnipsTests(unittest.TestCase):

  @snips_available
  def test_parse(self):
    pass

  @snips_available
  def test_parse_slot(self):
    pass