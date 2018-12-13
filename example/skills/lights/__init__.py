from pytlas import register_training, register_translations
from .skill import *
import json, os

def read_file(path):
  with open(os.path.join(os.path.dirname(__file__), path)) as fp:
    return fp.read()

def parse_json(path):
  return json.loads(read_file(path))

register_translations ('fr', lambda: parse_json('lights.fr.json'))
register_training ('en', lambda: read_file('lights.en.dsl'))
register_training ('fr', lambda: read_file('lights.fr.dsl'))
