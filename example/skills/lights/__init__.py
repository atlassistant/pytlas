from pytlas import register_training, register_translations
from .skill import *

register_translations ('fr', './lights.fr.json')
register_training ('en', './lights.dsl')
