from pytlas import Agent, __version__
from pytlas.cli.prompt import Prompt
from pytlas.cli.utils import install_logs
from pytlas.cli.config import get, getboolean, write_config, log_configuration, \
  CONFIG_DEFAULT_FILENAME, OPT_VERBOSE, OPT_DEBUG, OPT_LANG, OPT_SKILLS, OPT_CACHE, \
  OPT_WATCH, OPT_TRAINING_FILE, OPT_PARSE, OPT_WATCH, OPT_DRY
from pytlas.importers import restrict_load_languages, import_skills
from pytlas.skills_manager import get_installed_skills, install_skills, uninstall_skills
import click, logging, os

@click.group()
@click.version_option(__version__)
@click.option('--config', default=CONFIG_DEFAULT_FILENAME, help='Path to the configuration file')
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')
@click.option('--debug', is_flag=True, help='Debug mode')
@click.option('-l', '--lang', help='Lang of the interpreter to use')
@click.option('-s', '--skills', type=click.Path(), help='Specifies the directory containing pytlas skills')
@click.option('-c', '--cache', type=click.Path(), help='Path to the directory where engine cache will be outputted')
@write_config
def main():
  """An open-source 🤖 assistant library built for people and made to be super easy to setup and understand.
  """
  
  install_logs(getboolean(OPT_VERBOSE), getboolean(OPT_DEBUG))
  log_configuration()

  restrict_load_languages([ get(OPT_LANG) ])

@main.group(invoke_without_command=True)
@click.option('--parse', help='Parse the given message immediately and exits when the skill is done')
@click.option('--dry', is_flag=True, help='Dry run, will not load the interactive prompt')
@click.option('--watch', is_flag=True, help='Reload on skill files change')
@click.argument('training_file', type=click.Path(), nargs=1, required=False)
@write_config
def repl():
  """Start a REPL session to interact with your assistant.
  """

  import_skills(get(OPT_SKILLS), getboolean(OPT_WATCH))

  try:
    from pytlas.interpreters.snips import SnipsInterpreter
    
    interpreter = SnipsInterpreter(get(OPT_LANG), get(OPT_CACHE))

    training_file = get(OPT_TRAINING_FILE)

    if training_file:
      interpreter.fit_from_file(training_file)
    else:
      interpreter.fit_from_skill_data()

    if not getboolean(OPT_DRY):
      Prompt(Agent(interpreter, **os.environ), get(OPT_PARSE)).cmdloop()
  except ImportError:
    logging.critical('Could not import the "snips" interpreter, is "snips-nlu" installed?') 

@main.group()
def skills():
  """Manage skills for this pytlas instance.

  Under the hood, it uses git to clone and update skills so it must be installed and available in your path.
  """

  pass

@skills.command('list')
def list_skills():
  """List installed skills for this instance.
  """

  import_skills(get(OPT_SKILLS))

  for skill_data in get_installed_skills(get(OPT_LANG)):
    click.echo(skill_data)

@skills.command('add')
@click.argument('skills', nargs=-1, required=True)
def add_skills(skills):
  """Add given skills to your instance.
  """

  install_skills(get(OPT_SKILLS), click.echo, *skills)

@skills.command('remove')
@click.argument('skills', nargs=-1, required=True)
def remove_skills(skills):
  """Remove given skills from your instance.
  """

  uninstall_skills(get(OPT_SKILLS), click.echo, *skills)