import json, glob, os, logging

# Represents translations by module/lang
translations = {}

def list_translations(directory):
  """List translations files in the given directory.

  Args:
    directory (str): Directory which contain translation files

  Returns:
    generator: List of translation file paths

  """

  return glob.glob('%s/**/*.*.json' % directory)

def import_translations(directory):
  """Import translations in the global translations object.

  Args:
    directory (str): Directory containing translation files

  """

  logging.debug('Importing translations from "%s"' % directory)

  for translation_path in list_translations(directory):
    name_with_lang, _ = os.path.splitext(os.path.basename(translation_path))
    module, lang_ext = os.path.splitext(name_with_lang)
    lang = lang_ext[1:]

    if module not in translations:
      translations[module] = {}

    if lang not in translations[module]:
      translations[module][lang] = {}

    # Here we extend translations to avoid conflicts
    with open(translation_path, encoding='utf-8') as f:
      translations[module][lang].update(json.load(f))
