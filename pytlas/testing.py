import os, sys
from unittest.mock import MagicMock
from pytlas.importers import import_or_reload
from pytlas.agent import Agent
from pytlas.skill import handlers
from pytlas.utils import get_root_package_name
from pytlas.interpreters.snips import SnipsInterpreter

class AttrDict(dict):
  """Simple object to access dict keys like attributes.
  """

  def __getattr__(self, name):
    try:
      return self[name]
    except KeyError:
      raise AttributeError

class ModelMock(MagicMock):
  """Represents a particular mocking object used to make assertions easier on the
  agent model.
  """

  def has_arguments_mapping(self, mapping):
    """Adds arguments names to this instance to be able to test against them. Maybe
    there is a better way to handle it, I don't know yet.

    Args:
      mapping (list of str): List of keys in the order of arguments

    """

    self._args_map = mapping
    return self

  def get_call(self, number=0):
    """Retrieve call args for the given call number. With this tiny method, you can
    call a mock multiple times and assert against a specific one.

    It will returns an AttrDict which contains each argument name and their respective value
    so order is not an issue.

    Args:
      number (int): Call order

    Returns:
      AttrDict: AttrDict with argument names as keys

    """

    try:
      c = self.call_args_list[number][0]
    except IndexError:
      raise AssertionError('Mock has been called less than %d times!' % number)

    r = AttrDict()

    for (i, arg) in enumerate(c):
      try:
        r[self._args_map[i]] = arg
      except IndexError:
        pass

    for (k, v) in self.call_args_list[number][1].items():
      r[k] = v

    return r

class AgentModelMock:
  """Represents an agent model targeted at testing skills easily.
  """

  def __init__(self):
    self.on_answer = ModelMock().has_arguments_mapping(['text', 'cards'])
    self.on_ask = ModelMock().has_arguments_mapping(['slot', 'text', 'choices'])
    self.on_done = ModelMock().has_arguments_mapping(['require_input'])
    self.on_context = ModelMock().has_arguments_mapping(['context_name'])
    self.on_thinking = ModelMock().has_arguments_mapping([])

  def reset(self):
    """Resets all magic mocks calls. Basically, you should call it in your test
    setup method to make sure each instance starts from a fresh state.
    """

    self.on_answer.reset_mock()
    self.on_ask.reset_mock()
    self.on_done.reset_mock()
    self.on_context.reset_mock()
    self.on_thinking.reset_mock()

def create_skill_agent(skill_folder, lang='en', additional_skills=[]):
  """Create an agent specifically targeted at the specified skill folder. It makes
  it easy to write skill tests using a specific mock object as the Agent model.

  It will spawn a SnipsInterpreter and fit data only for the skill being tested.

  Args:
    skill_folder (str): Absolute path of the skill folder to be tested
    lang (str): Optional language used by the interpreter
    additional_skills (list of str): Additional skills to be loaded and interpreted
  
  Returns:
    Agent: Agent with a specific mock model to make assertions simplier

  """

  import_path = os.path.dirname(skill_folder)
  skill_name = os.path.basename(skill_folder)

  # Start by importing the skill
  if import_path not in sys.path:
    sys.path.append(import_path)

  import_or_reload(skill_name)

  # And instantiate an interpreter
  skills_to_load = [skill_name] + additional_skills

  interpreter = SnipsInterpreter(lang)
  interpreter.fit_from_skill_data(skills_to_load)

  # Filter handlers for targeted skill only
  valid_handlers = { k: v for (k, v) in handlers.items() if get_root_package_name(v.__module__) in skills_to_load }

  return Agent(interpreter, model=AgentModelMock(), handlers=valid_handlers)