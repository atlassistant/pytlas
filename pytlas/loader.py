from .skill import handlers
from watchgod import watch
import os, glob, sys, logging, threading, importlib

def _get_module_import_parts(path):
  module = os.path.basename(os.path.dirname(path))
  name, _ = os.path.splitext(os.path.basename(path))

  return (name, module)

def _get_module_path(path):
  return os.path.abspath(os.path.dirname(path))

def _watch(directory):
  logging.info('Watching for file changes in "%s"' % directory)

  for changes in watch(directory):
    for change in changes:
      name, module_name = _get_module_import_parts(change[1])
      module = sys.modules.get(name)

      if module:
        for intent, func in list(handlers.items()):
          if func.__module__ == module_name:
            del handlers[intent]

        logging.info('Reloading module "%s"' % module_name)

        try:
          importlib.reload(module)
        except:
          logging.warning('Reloading failed for "%s"' % module_name)
      else:
        logging.info('Importing module "%s"' % module_name)

        module_path = _get_module_path(change[1])

        if module_path not in sys.path:
          sys.path.append(module_path)

        __import__(name, fromlist=[module_name])

def list_skills(directory):
  """List skills in the given directory.

  Args:
    directory (str): Directory in which we should retrieve skills

  Returns:
    generator: List of skill files

  """

  for path in glob.glob('%s/**/*.py' % directory):
    yield path

def import_skills(directory, auto_reload=False):
  """Import skills inside the givne directory.

  Args:
    directory (str): Directory in which python skills are contained
    auto_reload (bool): Sets to True if you want to watch for file changes

  """

  logging.debug('Importing skills from "%s"' % directory)

  plugins = list(list_skills(directory))

  sys.path.extend(list(set([_get_module_path(p) for p in plugins])))

  for p in plugins:
    name, module = _get_module_import_parts(p)

    __import__(name, fromlist=[module])

  if auto_reload:
    threading.Thread(target=_watch, args=(directory,), daemon=True).start()
