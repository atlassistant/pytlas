import os, glob, sys

def list_skills(directory):
  """List skills in the given directory.

  Args:
    directory (str): Directory in which we should retrieve skills

  """

  for path in glob.glob('%s/*.py' % directory):
    name, _ = os.path.splitext(os.path.basename(path))
    yield name

def import_skills(directory):
  """Import skills inside the givne directory.

  Args:
    directory (str): Directory in which python skills are contained

  """

  plugins = list_skills(directory)

  sys.path.extend([directory])

  for p in plugins:
    __import__(p)
