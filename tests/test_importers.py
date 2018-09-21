import unittest, os
from pytlas.importers import should_load_resources, restrict_load_languages

class ImportersTests(unittest.TestCase):

  def test_should_load_resources(self):
    restrict_load_languages([])
    self.assertTrue(should_load_resources('fr'))

    restrict_load_languages(['en', 'it'])
    self.assertFalse(should_load_resources('fr'))
    self.assertTrue(should_load_resources('en'))
    self.assertTrue(should_load_resources('it'))

    restrict_load_languages([]) # Reset it for other tests
