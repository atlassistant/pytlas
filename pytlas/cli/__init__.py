from pytlas import Agent, __version__
from pytlas.cli.prompt import Prompt
from pytlas.cli.utils import install_logs
from pytlas.importers import restrict_load_languages, import_skills
import click, logging, os

@click.group()
@click.version_option(__version__)
@click.option('-v', '--verbose', default=False, is_flag=True, help='Verbose output')
@click.option('--debug', default=False, is_flag=True, help='Debug mode')
@click.option('-l', '--lang', default='en', help='Lang of the interpreter to use')
@click.option('-s', '--skills', default='skills', type=click.Path(), help='Specifies the directory containing pytlas skills (default to skills/)')
@click.option('-c', '--cache', default=None, type=click.Path(), help='Path to the directory where engine cache will be outputted')
@click.pass_context
def main(ctx, verbose, debug, lang, skills, cache):
  """An open-source 🤖 assistant library built for people and made to be super easy to setup and understand.
  """

  install_logs(verbose, debug)
  restrict_load_languages([lang])

@main.group(invoke_without_command=True)
@click.option('--parse', help='Parse the given message immediately and exits when the skill is done')
@click.option('--dry', default=False, is_flag=True, help='Dry run, will not load the interactive prompt')
@click.option('--watch', default=False, is_flag=True, help='Reload on skill files change')
@click.argument('training_file', type=click.Path(), nargs=1, required=False)
@click.pass_context
def repl(ctx, parse, dry, watch, training_file):
  """Start a REPL session to interact with your assistant.
  """

  import_skills(ctx.parent.params.get('skills'), watch)

  try:
    from pytlas.interpreters.snips import SnipsInterpreter
    
    interpreter = SnipsInterpreter(ctx.parent.params.get('lang'), ctx.parent.params.get('cache'))

    if training_file:
      interpreter.fit_from_file(training_file)
    else:
      interpreter.fit_from_skill_data()

    if not dry:
      Prompt(Agent(interpreter, **os.environ), parse).cmdloop()
  except ImportError:
    logging.critical('Could not import the "snips" interpreter, is "snips-nlu" installed?') 

@main.group()
def skills():
  """Manage skills for this pytlas instance.
  """

  pass

@skills.command('list')
def list_skills():
  """List installed skills for this instance.
  """

  pass