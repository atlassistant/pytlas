import logging, argparse, sys
from colorlog import ColoredFormatter
from .loader import import_skills
from .localization import import_translations
from .interpreters.dummy import DummyInterpreter
from .clients.prompt import PromptClient

def main():
  # Sets up the colored logger
  log = logging.getLogger()
  log.setLevel(logging.DEBUG)

  formatter = ColoredFormatter('%(log_color)s %(levelname)s %(reset)-8s %(bold_black)s%(message)s', 
    log_colors={
      'DEBUG': 'green',
      'INFO': 'black,bg_cyan',
      'WARNING': 'black,bg_yellow',
      'ERROR': 'black,bg_red',
    })
  stream = logging.StreamHandler()

  stream.setLevel(logging.DEBUG)
  stream.setFormatter(formatter)

  log.addHandler(stream)

  parser = argparse.ArgumentParser()
  parser.set_defaults(
    skill_dir='skills'
  )

  parser.add_argument('-s', '--skill_dir', help='Specifies the directory containing python skills')

  args = parser.parse_args(sys.argv[1:])

  import_skills(args.skill_dir)
  import_translations(args.skill_dir)

  PromptClient(DummyInterpreter()).cmdloop()