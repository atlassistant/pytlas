import logging, argparse, sys, re, cmd, os
from colorlog import ColoredFormatter, escape_codes
from pytlas.importers import import_skills, restrict_load_languages
from pytlas.agent import Agent
from pytlas.version import __version__

class CustomFormatter(ColoredFormatter):
  """Custom formatter used to highlight every words wrapped in quotes.
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

def install_logs(verbose, debug=False):
  """Install a custom colored formatter in the root logger.

  Args:
    verbose (bool): Verbose output?
    debug (bool): Debug output?

  """

  log = logging.getLogger()
  formatter = CustomFormatter()
  stream = logging.StreamHandler()
  stream.setLevel(logging.DEBUG)
  stream.setFormatter(formatter)

  log.addHandler(stream)
  log.setLevel(logging.DEBUG if debug else logging.INFO if verbose else logging.WARNING)

class Prompt(cmd.Cmd):
  intro = 'pytlas prompt v%s (type exit to leave)' % __version__
  prompt = '> '

  def __init__(self, agent, parse_message=None):
    super(Prompt, self).__init__()

    self._agent = agent
    self._agent.on_ask = self.ask
    self._agent.on_answer = self.answer
    self._agent.on_done = self.done
    self._exit_on_done = False

    if parse_message:
      self._exit_on_done = True
      self._agent.parse(parse_message)
  
  def done(self):
    if self._exit_on_done and not self._agent._request:
      sys.exit()

  def ask(self, slot, text, choices, **meta):
    print (text)

    if choices:
      for choice in choices:
        print ('\t-' + choice)

  def answer(self, text, cards, **meta):
    print (text)

    if cards:
      for card in cards:
        print (card)

  def do_exit(self, msg):
    return True

  def default(self, msg):
    self._agent.parse(msg)

def main():
  parser = argparse.ArgumentParser(description='An open-source 🤖 assistant library built for people and made to be super easy to setup and understand.')
  
  parser.set_defaults(
    lang='en',
    skills='skills',
    cache=None,
    verbose=False,
    debug=False,
    watch=False,
    dry=False,
    parse=None,
  )

  parser.add_argument('training_file', type=str, nargs='?', help='If given, the interpreter will be fit with this file instead of skill data')
  parser.add_argument('--version', action='version', version='%(prog)s v' + __version__)
  parser.add_argument('-s', '--skills', type=str, help='Specifies the directory containing pytlas skills (default to skills/')
  parser.add_argument('-c', '--cache', type=str, help='Path to the directory where engine cache will be outputted')
  parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
  parser.add_argument('-l', '--lang', type=str, help='Lang of the interpreter to use')
  parser.add_argument('--parse', type=str, help='Parse the given message immediately and exits when the skill is done')
  parser.add_argument('--debug', action='store_true', help='Debug mode')
  parser.add_argument('--dry', action='store_true', help='Dry run, will not load the interactive prompt')
  parser.add_argument('--watch', action='store_true', help='Reload on skill files change')

  args = parser.parse_args(sys.argv[1:])

  install_logs(args.verbose, args.debug)

  restrict_load_languages([args.lang])
  import_skills(args.skills, args.watch)

  try:
    from .interpreters.snips import SnipsInterpreter
    
    interpreter = SnipsInterpreter(args.lang, args.cache)

    if args.training_file:
      interpreter.fit_from_file(args.training_file)
    else:
      interpreter.fit_from_skill_data()

    if not args.dry:
      Prompt(Agent(interpreter, **os.environ), args.parse).cmdloop()
  except ImportError:
    logging.critical('Could not import the "snips" interpreter, is "snips-nlu" installed?') 
