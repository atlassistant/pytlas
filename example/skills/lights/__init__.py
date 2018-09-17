from pytlas.localization import register
from pytlas.training import register as register_training
from .skill import *

register ('fr', './lights.fr.json')
register_training ('fr', './lights.dsl')
