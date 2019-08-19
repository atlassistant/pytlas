import os, sys
from pytlas.pkgutils import get_root_package_name
from pytlas.conversing import Agent
from pytlas.handling import HandlersStore
from pytlas.handling.skill import global_handlers
from pytlas.handling.importers import import_or_reload
from pytlas.understanding.snips import SnipsInterpreter
from pytlas.testing.mock import AgentModelMock

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
  handlers = HandlersStore({ k: v for (k, v) in global_handlers._data.items() if get_root_package_name(v.__module__) in skills_to_load })

  return Agent(interpreter, model=AgentModelMock(), handlers_store=handlers)