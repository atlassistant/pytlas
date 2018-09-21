import importlib, os, logging, sys, threading
from types import ModuleType
from watchgod import watch

"""A list of allowed language resources to be loaded.
"""
LOAD_LANGUAGES = None

def restrict_load_languages(languages):
  """Set allowed language ressources to be loaded.

  Args:
    languages (list): List of language codes to allow

  """

  global LOAD_LANGUAGES

  LOAD_LANGUAGES = languages

def should_load_resources(language_code):
  """Determines if resources for the given language should be loaded. It will help
  keep only necessary stuff and avoid allocating space for unneeded resources.

  Args:
    language_code (str): Language to check

  Returns:
    bool: True if it should be loaded, false otherwise

  """

  global LOAD_LANGUAGES

  if LOAD_LANGUAGES == None:
    LOAD_LANGUAGES = list(filter(None, os.environ.get('PYTLAS_LOAD_LANGUAGES', '').split(',')))

  return not LOAD_LANGUAGES or language_code in LOAD_LANGUAGES

def _reload(module):
  """Recursively reloads a module. It only works for simple scenario but it may be suitable for pytlas ;).

  Args:
    module (ModuleType): Module to reload

  """

  importlib.reload(module)

  for attr_name in dir(module):
    attr = getattr(module, attr_name)

    if isinstance(attr, ModuleType):
      _reload(attr)

def _watch(directory):
  logging.info('Watching for file changes in "%s"' % directory)

  for changes in watch(directory):
    for change in changes:
      file_path = change[1]
      module_name = os.path.split(os.path.relpath(file_path, directory))[0]
      module = sys.modules.get(module_name)

      logging.debug('Changes in file "%s" cause "%s" module (re)load' % (file_path, module_name))
      
      if module:
        logging.info('Reloading module "%s"' % module_name)

        try:
          _reload(module)
        except:
          logging.warning('Reloading failed for "%s"' % module_name)
      else:
        logging.info('Importing module "%s"' % module_name)

        try:
          importlib.import_module(module_name)
        except ImportError:
          logging.error ('Could not import skill "%s"' % module_name)

def import_skills(directory, auto_reload=False):
  """Import skills inside the givne directory.

  Args:
    directory (str): Directory in which skills are contained
    auto_reload (bool): Sets to True if you want to watch for file changes, it should be used only for development purposes

  """

  logging.debug('Importing skills from "%s"' % directory)

  sys.path.append(directory)

  for skill_folder in os.listdir(directory):
    try:
      importlib.import_module(skill_folder)
      logging.debug ('Imported skill "%s"' % skill_folder)
    except ImportError:
      logging.error ('Could not import skill "%s"' % skill_folder)

  if auto_reload:
    threading.Thread(target=_watch, args=(directory,), daemon=True).start()