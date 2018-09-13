import importlib, os, logging, sys

def import_skills(directory, auto_reload=False):
  """Import skills inside the givne directory.

  Args:
    directory (str): Directory in which skills are contained
    auto_reload (bool): Sets to True if you want to watch for file changes

  """

  logging.debug('Importing skills from "%s"' % directory)

  sys.path.append(directory)

  for skill_folder in os.listdir(directory):
    try:
      importlib.import_module(skill_folder)
      logging.debug ('Imported skill "%s"' % skill_folder)
    except ImportError:
      logging.error ('Could not import skill "%s"' % skill_folder)

  # TODO auto reloading