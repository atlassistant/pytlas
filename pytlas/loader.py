from .skill import handlers
from watchgod import watch
import os, glob, sys, logging, threading, importlib

def _get_module_name(path):
  name, _ = os.path.splitext(os.path.basename(path))

  return name

def _watch(directory):
  logging.info('Watching for file changes in "%s"' % directory)
  
  for changes in watch(directory):
    for change in changes:
      module_name = _get_module_name(change[1])
      module = sys.modules.get(module_name)

      if module:
        for intent, func in list(handlers.items()):
          if func.__module__ == module_name:
            del handlers[intent]

        logging.info('Reloading module "%s"' % module_name)
        importlib.reload(module)
      else:
        logging.info('Importing module "%s"' % module_name)
        __import__(module_name)

def list_skills(directory):
  """List skills in the given directory.

  Args:
    directory (str): Directory in which we should retrieve skills

  Returns:
    generator: List of skill files

  """

  for path in glob.glob('%s/*.py' % directory):
    yield _get_module_name(path)

def import_skills(directory, auto_reload=False):
  """Import skills inside the givne directory.

  Args:
    directory (str): Directory in which python skills are contained
    auto_reload (bool): Sets to True if you want to watch for file changes

  """

  logging.debug('Importing skills from "%s"' % directory)

  plugins = list_skills(directory)

  sys.path.extend([directory])

  for p in plugins:
    __import__(p)

  if auto_reload:
    threading.Thread(target=_watch, args=(directory,), daemon=True).start()
