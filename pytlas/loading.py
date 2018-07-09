import os, glob, sys

def list_skills(directory):
  for path in glob.glob('%s/*.py' % directory):
    name, _ = os.path.splitext(os.path.basename(path))
    yield name

def import_skills(directory):
  plugins = list_skills(directory)

  sys.path.extend([directory])

  for p in plugins:
    __import__(p)
