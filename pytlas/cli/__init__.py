from pytlas import Agent, __version__
from pytlas.cli.prompt import Prompt
from pytlas.cli.utils import install_logs
from pytlas.handling.importers import import_skills
from pytlas.settings import config, write_to_store
from pytlas.supporting import SkillsManager
import click, logging, os

SKILLS_DIR = 'skills_dir'
CACHE_DIR = 'cache_dir'
TRAINING_FILE = 'training_file'
REPO_URL = 'repo_url'
GRAPH_FILE = 'graph_file'
WATCH = 'watch'
LANGUAGE = 'language'
VERBOSE = 'verbose'
DEBUG = 'debug'

def instantiate_and_fit_interpreter(): # pragma: no cover
  import_skills(config.getpath(SKILLS_DIR), config.getbool(WATCH))

  try:
    from pytlas.understanding.snips import SnipsInterpreter
    
    interpreter = SnipsInterpreter(config.get(LANGUAGE), config.getpath(CACHE_DIR))

    training_file = config.getpath(TRAINING_FILE)

    if training_file:
      interpreter.fit_from_file(training_file)
    else:
      interpreter.fit_from_skill_data()

    return interpreter
  except ImportError:
    logging.critical('Could not import the "snips" interpreter, is "snips-nlu" installed?') 

def instantiate_agent_prompt(sentence=None): # pragma: no cover
  interpreter = instantiate_and_fit_interpreter()

  Prompt(Agent(interpreter, transitions_graph_path=config.getpath(GRAPH_FILE)), parse_message=sentence).cmdloop()

def instantiate_skill_manager(): # pragma: no cover
  return SkillsManager(config.getpath(SKILLS_DIR), config.get(LANGUAGE),
    default_git_url=config.get(REPO_URL))

def make_argname(name):
  """Tiny function to prepend "--" to a string.

  Args:
    name (str): Setting name

  Examples:
    >>> make_argname('language')
    '--language'

  """

  return f'--{name}'

@click.group()
@click.version_option(__version__)
@click.option('-c', '--config_file', type=click.Path(), help='Path to the configuration file')
@click.option('-v', make_argname(VERBOSE), is_flag=True, help='Verbose output')
@click.option(make_argname(DEBUG), is_flag=True, help='Debug mode')
@click.option('-l', make_argname(LANGUAGE), help='Lang of the interpreter to use')
@click.option('-s', make_argname(SKILLS_DIR), type=click.Path(), help='Specifies the directory containing pytlas skills')
@click.option(make_argname(CACHE_DIR), type=click.Path(), help='Path to the directory where engine cache will be outputted')
@click.option('-g', make_argname(GRAPH_FILE), type=click.Path(), help='Output the transitions graph to the given path')
@click.option(make_argname(REPO_URL), help='Repository URL to prepend when installing skills without an absolute URL')
@write_to_store()
def main(config_file, skills_dir, language, repo_url, **kwargs): # pragma: no cover
  """An open-source 🤖 assistant library built for people and made to be super easy to setup and understand.
  """

  if config_file:
    config.load_from_file(config_file)

  # Sets default settings value if not given in args or config file
  config.set(LANGUAGE, language or config.get(LANGUAGE, 'en'))
  config.set(SKILLS_DIR, skills_dir or config.get(SKILLS_DIR, os.getcwd()))
  config.set(REPO_URL, repo_url or config.get(REPO_URL, 'https://github.com/'))
  
  install_logs(config.get(VERBOSE), config.get(DEBUG))

@main.group(invoke_without_command=True)
@click.option(make_argname(WATCH), is_flag=True, help='Reload on skill files change')
@click.argument(make_argname(TRAINING_FILE), type=click.Path(), nargs=1, required=False)
@write_to_store()
def repl(**kwargs): # pragma: no cover
  """Start a REPL session to interact with your assistant.
  """

  instantiate_agent_prompt()

@main.command('parse')
@click.argument('sentence', required=True)
def parse(sentence): # pragma: no cover
  """Parse the given message immediately and exits when the skill is done.
  """

  instantiate_agent_prompt(sentence)

@main.command('train')
def train(): # pragma: no cover
  """Dry run, will not load the interactive prompt but only the fit part.
  """

  instantiate_and_fit_interpreter()

@main.group()
def skills(): # pragma: no cover
  """Manage skills for this pytlas instance.

  Under the hood, it uses git to clone and update skills so it must be installed and available in your path.
  """

  pass

@skills.command('list')
def list_skills(): # pragma: no cover
  """List installed skills for this instance.
  """
  import_skills(config.getpath(SKILLS_DIR))

  metas = instantiate_skill_manager().get()

  for meta in metas:
    click.echo(meta)

@skills.command('add')
@click.argument('skills', nargs=-1, required=True)
def add_skills(skills): # pragma: no cover
  """Add given skills to your instance.
  """
  succeeded, failed = instantiate_skill_manager().install(*skills)

  if succeeded:
    click.echo(f'Successfully installed skills: {", ".join(succeeded)}')

  if failed:
    click.echo(f'Failed to install skills: {", ".join(failed)}')

@skills.command('update')
@click.argument('skills', nargs=-1)
def update_skills_command(skills): # pragma: no cover
  """Update given skills for this instance. If no skills are defined, they will be all updated.
  """
  succeeded, failed = instantiate_skill_manager().update(*skills)

  if succeeded:
    click.echo(f'Successfully updated skills: {", ".join(succeeded)}')

  if failed:
    click.echo(f'Failed to update skills: {", ".join(failed)}')

@skills.command('remove')
@click.argument('skills', nargs=-1, required=True)
def remove_skills(skills): # pragma: no cover
  """Remove given skills from your instance.
  """
  succeeded, failed = instantiate_skill_manager().uninstall(*skills)

  if succeeded:
    click.echo(f'Successfully uninstalled skills: {", ".join(succeeded)}')

  if failed:
    click.echo(f'Failed to uninstall skills: {", ".join(failed)}')