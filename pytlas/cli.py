import logging, argparse, sys, re, cmd
from colorlog import ColoredFormatter, escape_codes
from .importers import import_skills
from .interpreters.dummy import DummyInterpreter
from .agent import Agent
from .version import __version__

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

class Prompt(cmd.Cmd):
  intro = 'pytlas prompt v%s' % __version__
  prompt = '> '

  def __init__(self, agent):
    super(Prompt, self).__init__()

    self._agent = agent

    # Attach handlers
    self._agent.on_ask = self.ask
    self._agent.on_answer = self.answer
    self._agent.on_done = self.done
  
  def ask(self, slot, text, choices):
    print (text)

  def answer(self, text, cards):
    print (text)

  def done(self):
    pass

  def do_exit(self, msg):
    return True

  def default(self, msg):
    self._agent.parse(msg)

def install_logs(verbosity=logging.WARNING):
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
  log.setLevel(verbosity)

def create_parser():
  """Creates the parser that pytlas CLI internaly use.

  This is useful if you want to give the same options in your own program.

  Returns:
    ArgumentParser: Parser to use

  """
  parser = argparse.ArgumentParser()
  parser.set_defaults(
    skills_dir='skills',
    training_dir='training',
    verbose=False,
    debug=False,
    reload=False,
  )

  parser.add_argument('-s', '--skills_dir', help='Specifies the directory containing python skills')
  parser.add_argument('-t', '--training_dir', help='Path to the training directory')
  parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
  parser.add_argument('--debug', action='store_true', help='Debug mode')
  parser.add_argument('-r', '--reload', action='store_true', help='Reload on skill files change')

  return parser

def main():
  args = create_parser().parse_args(sys.argv[1:])

  verbosity = logging.WARNING

  if args.verbose:
    verbosity = logging.INFO
  
  if args.debug:
    verbosity = logging.DEBUG

  install_logs(verbosity)
  import_skills(args.skills_dir, args.reload)
  
  interpreter = DummyInterpreter()

  try:
    from .interpreters.snips import SnipsInterpreter
    interpreter = SnipsInterpreter(args.training_dir)
  except ImportError:
    logging.warning('Could not import the "snips" interpreter, is "snips-nlu" installed? Using a dummy interpreter instead') 

  interpreter.fit_as_needed()

  Prompt(Agent(interpreter)).cmdloop()