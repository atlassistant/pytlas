import logging, argparse, sys
from .loader import import_skills
from .localization import import_translations
from .interpreters.dummy import DummyInterpreter
from .clients.prompt import PromptClient

def main():
  logging.basicConfig(level=logging.DEBUG)

  parser = argparse.ArgumentParser()
  parser.set_defaults(
    skill_dir='skills'
  )

  parser.add_argument('-s', '--skill_dir', help='Specifies the directory containing python skills')

  args = parser.parse_args(sys.argv[1:])

  import_skills(args.skill_dir)
  import_translations(args.skill_dir)

  PromptClient(DummyInterpreter()).cmdloop()