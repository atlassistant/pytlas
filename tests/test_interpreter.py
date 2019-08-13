from sure import expect
from unittest.mock import MagicMock
from pytlas.interpreters import Interpreter
from pytlas.training import TrainingsStore, global_trainings

class TestInterpreter:

  def setup(self):
    t = TrainingsStore({
      'interpreter_module1': {
        'en': lambda: """
@[interpreter_module1_entity]
  an entity
  another entity
""",
      },
      'interpreter_module2': {
        'en': lambda: """
@[interpreter_module2_entity]
  an entity
  another entity
""",
      },
    })
    self.interpreter = Interpreter('snips', 'en', trainings_store=t)
    self.interpreter.fit = MagicMock()

  def test_it_should_returns_nothing_when_parsing(self):
    expect(self.interpreter.parse('A message')).to.be.empty

  def test_it_should_do_nothing_when_loading_from_cache(self):
    expect(self.interpreter.load_from_cache()).to.be.none

  def test_it_should_returns_a_generic_slot_value_when_parsing_slot(self):
    slots = self.interpreter.parse_slot('an_intent', 'a slot', 'a message')

    expect(slots).to.have.length_of(1)
    expect(slots[0].value).to.equal('a message')

  def test_it_should_fit_from_all_skills_when_no_filters_is_provided(self):
    self.interpreter.fit_from_skill_data()

    data = self.interpreter.fit.call_args[0][0]

    expect(data['entities']).to.have.key('interpreter_module1_entity')
    expect(data['entities']).to.have.key('interpreter_module2_entity')

  def test_it_should_fit_only_from_given_skill_names(self):
    self.interpreter.fit_from_skill_data(['interpreter_module2'])

    data = self.interpreter.fit.call_args[0][0]

    expect(data['entities']).to.not_have.key('interpreter_module1_entity')
    expect(data['entities']).to.have.key('interpreter_module2_entity')

  def test_it_should_ignore_package_without_data_when_fitting(self):
    t = TrainingsStore({
      'module1': {
        'fr': lambda: """
%[intent_module1]
  avec quelques données
""",
      },
      'module2': {
        'en': lambda: """
%[intent_module2]
  with some data
""",
      },
    })
    interpreter = Interpreter('snips', 'en', trainings_store=t)
    interpreter.fit = MagicMock()
    interpreter.fit_from_skill_data()

    data = interpreter.fit.call_args[0][0]

    expect(data['intents']).to.have.key('intent_module2')
    expect(data['intents']).to_not.have.key('intent_module1')
  
  def test_it_should_ignore_package_with_invalid_data_when_fitting(self):
    t = TrainingsStore({
      'module1': {
        'en': lambda: """
parsing will fail here
""",
      },
      'module2': {
        'en': lambda: """
%[intent_module2]
  with some data
""",
      },
    })
    interpreter = Interpreter('snips', 'en', trainings_store=t)
    interpreter.fit = MagicMock()
    interpreter.fit_from_skill_data()

    data = interpreter.fit.call_args[0][0]

    expect(data['intents']).to.have.key('intent_module2')
    expect(data['intents']).to_not.have.key('intent_module1')

  def test_it_should_fail_when_no_processor_could_be_found_for_the_interpreter(self):
    t = TrainingsStore({
      'module1': {
        'fr': lambda: """
%[intent_module1]
  avec quelques données
""",
      },
      'module2': {
        'en': lambda: """
%[intent_module2]
  with some data
""",
      },
    })
    interpreter = Interpreter('unknown', 'en', trainings_store=t)
    interpreter.fit = MagicMock()

    interpreter.fit_from_skill_data()
    interpreter.fit.assert_not_called()