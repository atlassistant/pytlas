from pytlas import register_training, register_translations
from pytlas.utils import read_file
from .skill import *
import json

register_translations ('fr', lambda: json.loads(read_file('lights.fr.json', relative_to_file=__file__)))
register_training ('en', lambda: read_file('lights.en.dsl', relative_to_file=__file__))
register_training ('fr', lambda: read_file('lights.fr.dsl', relative_to_file=__file__))
