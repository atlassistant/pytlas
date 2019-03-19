from pytlas import Agent, __version__
from pytlas.cli.prompt import Prompt
from pytlas.cli.utils import install_logs
from pytlas.importers import import_skills
from pytlas.pam import get_loaded_skills, install_skills, uninstall_skills, update_skills
import click, logging, os, pytlas.settings as settings

def instantiate_and_fit_interpreter(): # pragma: no cover
  import_skills(settings.getpath(settings.SETTING_SKILLS), settings.getbool(settings.SETTING_WATCH))

  try:
    from pytlas.interpreters.snips import SnipsInterpreter
    
    interpreter = SnipsInterpreter(settings.get(settings.SETTING_LANG), settings.getpath(settings.SETTING_CACHE))

    training_file = settings.getpath(settings.SETTING_TRAINING_FILE)

    if training_file:
      interpreter.fit_from_file(training_file)
    else:
      interpreter.fit_from_skill_data()

    return interpreter
  except ImportError:
    logging.critical('Could not import the "snips" interpreter, is "snips-nlu" installed?') 

def instantiate_agent_prompt(sentence=None): # pragma: no cover
  interpreter = instantiate_and_fit_interpreter()

  Prompt(Agent(interpreter, transitions_graph_path=settings.getpath(settings.SETTING_GRAPH_FILE), **os.environ), parse_message=sentence).cmdloop()

@click.group()
@click.version_option(__version__)
@click.option('--config', default=settings.DEFAULT_FILENAME, help='Path to the configuration file')
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')
@click.option('--debug', is_flag=True, help='Debug mode')
@click.option('-l', '--lang', help='Lang of the interpreter to use', default=settings.DEFAULT_LANG)
@click.option('-s', '--skills', type=click.Path(), help='Specifies the directory containing pytlas skills')
@click.option('-c', '--cache', type=click.Path(), help='Path to the directory where engine cache will be outputted')
@click.option('-g', '--graph', type=click.Path(), help='Output the transitions graph to the given path')
@settings.write_to_settings()
def main(): # pragma: no cover
  """An open-source 🤖 assistant library built for people and made to be super easy to setup and understand.
  """
  
  install_logs(settings.getbool(settings.SETTING_VERBOSE), settings.getbool(settings.SETTING_DEBUG))

@main.group(invoke_without_command=True)
@click.option('--watch', is_flag=True, help='Reload on skill files change')
@click.argument('training_file', type=click.Path(), nargs=1, required=False)
@settings.write_to_settings()
def repl(): # pragma: no cover
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

  import_skills(settings.getpath(settings.SETTING_SKILLS))

  for skill_data in get_loaded_skills(settings.getlist(settings.SETTING_LANG)[0]):
    click.echo(skill_data)

@skills.command('add')
@click.argument('skills', nargs=-1, required=True)
def add_skills(skills): # pragma: no cover
  """Add given skills to your instance.
  """

  install_skills(settings.getpath(settings.SETTING_SKILLS), click.echo, *skills)

@skills.command('update')
@click.argument('skills', nargs=-1)
def update_skills_command(skills): # pragma: no cover
  """Update given skills for this instance. If no skills are defined, they will be all updated.
  """
  
  update_skills(settings.getpath(settings.SETTING_SKILLS), click.echo, *skills)

@skills.command('remove')
@click.argument('skills', nargs=-1, required=True)
def remove_skills(skills): # pragma: no cover
  """Remove given skills from your instance.
  """

  uninstall_skills(settings.getpath(settings.SETTING_SKILLS), click.echo, *skills)