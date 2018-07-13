import logging, argparse, sys, re
from colorlog import ColoredFormatter, escape_codes
from .loader import import_skills
from .localization import import_translations
from .interpreters.dummy import DummyInterpreter
from .clients.prompt import PromptClient

class CustomFormatter(ColoredFormatter):
  """Custom formatter used to highlight every words wrapped by quotes.
  """

  def __init__(self):
    super(CustomFormatter, self).__init__('%(log_color)s %(levelname)s %(reset)s %(name)s %(bold_black)s%(message)s', 
    log_colors={
      'DEBUG': 'green',
      'INFO': 'black,bg_cyan',
      'WARNING': 'black,bg_yellow',
      'ERROR': 'black,bg_red',
    })

    self._pattern = re.compile('"(.*?)"')

  def format(self, record):
    msg = super(CustomFormatter, self).format(record)

    return self._pattern.sub(r'%s\1%s' % (escape_codes['cyan'], escape_codes['bold_black']), msg) + escape_codes['reset']

def main():
  # Sets up the colored logger
  log = logging.getLogger()
  formatter = CustomFormatter()
  stream = logging.StreamHandler()
  stream.setLevel(logging.DEBUG)
  stream.setFormatter(formatter)

  log.addHandler(stream)

  parser = argparse.ArgumentParser()
  parser.set_defaults(
    skills_dir='skills'
  )

  parser.add_argument('-s', '--skills_dir', help='Specifies the directory containing python skills')
  parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

  args = parser.parse_args(sys.argv[1:])

  if args.verbose:
    log.setLevel(logging.DEBUG)

  import_skills(args.skills_dir)
  import_translations(args.skills_dir)

  PromptClient(DummyInterpreter()).cmdloop()