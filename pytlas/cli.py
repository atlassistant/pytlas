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
    super(CustomFormatter, self).__init__('%(log_color)s%(levelname)s%(reset)s\t%(name)s\t%(reset)s%(message)s', 
    log_colors={
      'DEBUG': 'green',
      'INFO': 'cyan',
      'WARNING': 'yellow',
      'ERROR': 'red',
    })

    self._pattern = re.compile('"(.*?)"')

  def format(self, record):
    msg = super(CustomFormatter, self).format(record)

    return self._pattern.sub(r'%s\1%s' % (escape_codes['cyan'], escape_codes['reset']), msg) + escape_codes['reset']

def install_logs(verbose=False):
  """Installs a custom formatter to color output logs.

  Args:
    verbose (bool): Verbose output

  """

  log = logging.getLogger()
  formatter = CustomFormatter()
  stream = logging.StreamHandler()
  stream.setLevel(logging.DEBUG)
  stream.setFormatter(formatter)

  log.addHandler(stream)

  if verbose:
    log.setLevel(logging.DEBUG)

def main():
  parser = argparse.ArgumentParser()
  parser.set_defaults(
    skills_dir='skills',
    training_file='training.json',
    output_dir='output',
  )

  parser.add_argument('-s', '--skills_dir', help='Specifies the directory containing python skills')
  parser.add_argument('-t', '--training_file', help='Path to the training file')
  parser.add_argument('-o', '--output_dir', help='Path to output directory for trained files')
  parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

  args = parser.parse_args(sys.argv[1:])

  install_logs(args.verbose)
  import_skills(args.skills_dir)
  import_translations(args.skills_dir)

  interpreter = DummyInterpreter()

  try:
    from .interpreters.snips import SnipsInterpreter
    interpreter = SnipsInterpreter(args.training_file, args.output_dir)
  except ImportError:
    logging.warning('Could not import the "snips" interpreter, is "snips-nlu" installed? Using a dummy interpreter instead')

  interpreter.fit_as_needed()

  PromptClient(interpreter).cmdloop()