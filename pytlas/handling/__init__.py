"""The handling domain exposes stuff to register python handlers, translations and
skill metadata in the system using provided decorators.
"""

from pytlas.handling.card import Card
from pytlas.handling.localization import translations, TranslationsStore
from pytlas.handling.skill import meta, intent, Meta, Setting, MetasStore, HandlersStore
