from pytlas.understanding.training import global_trainings
from pytlas.handling.localization import global_translations
from pytlas.ioutils import read_file
from .skill import *
import json

global_translations.register('fr', lambda: json.loads(read_file('lights.fr.json', relative_to_file=__file__)))
global_trainings.register('en', lambda: read_file('lights.en.dsl', relative_to_file=__file__))
global_trainings.register('fr', lambda: read_file('lights.fr.dsl', relative_to_file=__file__))
