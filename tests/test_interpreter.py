from sure import expect
from unittest.mock import MagicMock
from pytlas.interpreters import Interpreter
from pytlas.training import register

class TestInterpreter:

  def setup(self):
    self.interpreter = Interpreter('snips', 'en')
    self.interpreter.fit = MagicMock()

    register('en', """
@[interpreter_module1_entity]
  an entity
  another entity
""", 'interpreter_module1')

    register('en', """
@[interpreter_module2_entity]
  an entity
  another entity
""", 'interpreter_module2')

  def test_it_should_returns_nothing_when_parsing(self):
    expect(self.interpreter.parse('A message')).to.be.empty

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