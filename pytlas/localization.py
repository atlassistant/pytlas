import json, glob, os

# Represents translations by module/lang
translations = {}

def list_translations(directory):
  """List translations files in the given directory.

  Args:
    directory (str): Directory which contain translation files

  Returns:
    generator: List of translation file paths

  """

  for path in glob.glob('%s/*.*.json' % directory):
    yield path

def import_translations(directory):
  """Import translations in the global translations object.

  Args:
    directory (str): Directory containing translation files

  """

  for translation_path in list_translations(directory):
    name_with_lang, _ = os.path.splitext(os.path.basename(translation_path))
    module, lang = os.path.splitext(name_with_lang)

    if module not in translations:
      translations[module] = {}

    with open(translation_path) as f:
      translations[module][lang[1:]] = json.load(f)