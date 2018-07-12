import unittest
from pytlas.request import Request

class RequestTests(unittest.TestCase):

  def test_id(self):
    
    r = Request(None, None)

    self.assertIsNotNone(r.id)

  def test_translations(self):

    r = Request(None, None, {
      'a text': 'un texte',
    })

    self.assertEqual('un texte', r._('a text'))
    self.assertEqual('not found', r._('not found'))