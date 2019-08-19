"""datautils provides helper methods to deals with pytlas specific data.
"""

import random
from pytlas.settings import config, SETTING_ALLOWED_LANGUAGES
from fuzzywuzzy import process
from markdown import markdown
from bs4 import BeautifulSoup

def keep_one(value):
  """Keeps only one element if value is a list.

  Args:
    value (str, list): Value to check

  Returns:
    str: Random value in the given list if it's a list, else the given value

  """
  if isinstance(value, list):
    return random.choice(value)

  return value

def strip_format(value):
  """Removes any markdown format from the source to returns a raw string.

  Args:
    value (str): Input value which may contains format characters
  
  Returns:
    str: Raw value without format characters
  
  Examples:
    >>> strip_format('contains **bold** text here')
    'contains bold text here'

    >>> strip_format('nothing fancy here')
    'nothing fancy here'

    >>> strip_format(None)

  """
  if not value:
    return None

  html = markdown(value)

  # If nothing has changed, don't rely on BeautifulSoup since this is not needed
  if html == value:
    return value

  return BeautifulSoup(html, 'html.parser').get_text()

def find_match(choices, value):
  """Find element that fuzzy match the available choices.

  Args:
    choices (list): Available choices
    value (str): Raw value to fuzzy match

  Returns:
    str: matched text in given choices

  """
  match = process.extractOne(value, choices, score_cutoff=60)

  return match[0] if match else None

def should_load_resources(language_code):
  """Determines if resources for the given language should be loaded. It will help
  keep only necessary stuff and avoid allocating space for unneeded resources.

  Args:
    language_code (str): Language to check

  Returns:
    bool: True if it should be loaded, false otherwise

  """
  langs = config.getlist(SETTING_ALLOWED_LANGUAGES)

  return not langs or language_code in langs