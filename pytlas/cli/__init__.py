"""Exposes the tiny pytlas CLI used to easily interact with the system.
"""

# pylint: disable=missing-function-docstring,unused-argument,unnecessary-pass

import os
import logging
import click
from pytlas import Agent, __version__
from pytlas.cli.prompt import Prompt
from pytlas.cli.utils import install_logs
from pytlas.handling.importers import import_skills
from pytlas.settings import CONFIG, write_to_store
from pytlas.supporting import SkillsManager

SKILLS_DIR = 'skills_dir'
CACHE_DIR = 'cache_dir'
REPO_URL = 'repo_url'
GRAPH_FILE = 'graph_file'
WATCH = 'watch'
LANGUAGE = 'language'
VERBOSE = 'verbose'
DEBUG = 'debug'


def instantiate_and_fit_interpreter(training_file=None):  # pragma: no cover
    if not training_file:
        import_skills(CONFIG.getpath(SKILLS_DIR), CONFIG.getbool(WATCH))

    try:
        from pytlas.understanding.snips import SnipsInterpreter

        interpreter = SnipsInterpreter(
            CONFIG.get(LANGUAGE), CONFIG.getpath(CACHE_DIR))

        if training_file:
            interpreter.fit_from_file(training_file)
        else:
            interpreter.fit_from_skill_data()

        return interpreter
    except ImportError:
        logging.critical(
            'Could not import the "snips" interpreter, is "snips-nlu" installed?')


def instantiate_agent_prompt(sentence=None):  # pragma: no cover
    interpreter = instantiate_and_fit_interpreter()

    Prompt(Agent(interpreter, transitions_graph_path=CONFIG.getpath(
        GRAPH_FILE)), parse_message=sentence).cmdloop()


def instantiate_skill_manager():  # pragma: no cover
    return SkillsManager(CONFIG.getpath(SKILLS_DIR), CONFIG.get(LANGUAGE),
                         default_git_url=CONFIG.get(REPO_URL))


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
@click.option('-c', '--config_file', type=click.Path(), default='pytlas.ini', \
    help='Path to the configuration file (default to pytlas.ini')
@click.option('-v', make_argname(VERBOSE), is_flag=True, help='Verbose output')
@click.option(make_argname(DEBUG), is_flag=True, help='Debug mode')
@click.option('-l', make_argname(LANGUAGE), help='Lang of the interpreter to use')
@click.option('-s', make_argname(SKILLS_DIR), type=click.Path(), \
    help='Specifies the directory containing pytlas skills')
@click.option(make_argname(CACHE_DIR), type=click.Path(), \
    help='Path to the directory where engine cache will be outputted')
@click.option('-g', make_argname(GRAPH_FILE), type=click.Path(), \
    help='Output the transitions graph to the given path')
@click.option(make_argname(REPO_URL), \
    help='Repository URL to prepend when installing skills without an absolute URL')
@write_to_store()
def main(config_file, skills_dir, language, repo_url, **kwargs):  # pragma: no cover
    """An open-source 🤖 assistant library built for people and made to be super
    easy to setup and understand.
    """
    if os.path.isfile(config_file):
        CONFIG.load_from_file(config_file)

    # Sets default settings value if not given in args or config file
    CONFIG.set(LANGUAGE, language or CONFIG.get(LANGUAGE, 'en'))
    CONFIG.set(SKILLS_DIR, skills_dir or CONFIG.get(SKILLS_DIR, os.getcwd()))
    CONFIG.set(REPO_URL, repo_url or CONFIG.get(
        REPO_URL, 'https://github.com/'))

    install_logs(CONFIG.get(VERBOSE), CONFIG.get(DEBUG))


@main.group(invoke_without_command=True)
@click.option(make_argname(WATCH), is_flag=True, help='Reload on skill files change')
@write_to_store()
def repl(**kwargs):  # pragma: no cover
    """Start a REPL session to interact with your assistant.
    """
    instantiate_agent_prompt()


@main.command('parse')
@click.argument('sentence', required=True)
def parse(sentence):  # pragma: no cover
    """Parse the given message immediately and exits when the skill is done.
    """
    instantiate_agent_prompt(sentence)


@main.command('train')
@click.argument('training_file', type=click.Path(), nargs=1, required=False)
def train(training_file):  # pragma: no cover
    """Dry run, will not load the interactive prompt but only the fit part.
    """
    instantiate_and_fit_interpreter(training_file)


@main.group()
def skills():  # pragma: no cover
    """Manage skills for this pytlas instance.

    Under the hood, it uses git to clone and update skills so it must be installed
    and available in your path.
    """
    pass


@skills.command('list')
def list_skills():  # pragma: no cover
    """List installed skills for this instance.
    """
    import_skills(CONFIG.getpath(SKILLS_DIR))

    metas = instantiate_skill_manager().get()

    for meta in metas:
        click.echo(meta)


@skills.command('add')
@click.argument('names', nargs=-1, required=True)
def add_skills(names):  # pragma: no cover
    """Add given skills to your instance.
    """
    succeeded, failed = instantiate_skill_manager().install(*names)

    if succeeded:
        click.echo(f'Successfully installed skills: {", ".join(succeeded)}')

    if failed:
        click.echo(f'Failed to install skills: {", ".join(failed)}')


@skills.command('update')
@click.argument('names', nargs=-1)
def update_skills_command(names):  # pragma: no cover
    """Update given skills for this instance. If no skills are defined, they will be all updated.
    """
    succeeded, failed = instantiate_skill_manager().update(*names)

    if succeeded:
        click.echo(f'Successfully updated skills: {", ".join(succeeded)}')

    if failed:
        click.echo(f'Failed to update skills: {", ".join(failed)}')


@skills.command('remove')
@click.argument('names', nargs=-1, required=True)
def remove_skills(names):  # pragma: no cover
    """Remove given skills from your instance.
    """
    succeeded, failed = instantiate_skill_manager().uninstall(*names)

    if succeeded:
        click.echo(f'Successfully uninstalled skills: {", ".join(succeeded)}')

    if failed:
        click.echo(f'Failed to uninstall skills: {", ".join(failed)}')
