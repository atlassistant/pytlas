from pytlas.understanding.training import GLOBAL_TRAININGS
from pytlas.handling.localization import GLOBAL_TRANSLATIONS
from pytlas.ioutils import read_file
from .skill import *
import json

GLOBAL_TRANSLATIONS.register('fr', lambda: json.loads(read_file('lights.fr.json', relative_to=__file__)))
GLOBAL_TRAININGS.register('en', lambda: read_file('lights.en.dsl', relative_to=__file__))
GLOBAL_TRAININGS.register('fr', lambda: read_file('lights.fr.dsl', relative_to=__file__))
