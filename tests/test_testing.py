from sure import expect
from pytlas.agent import Agent
from pytlas.card import Card
from pytlas.testing import AttrDict, ModelMock, AgentModelMock, create_skill_agent
import os

class TestAttrDict:
  
  def test_it_should_expose_keys_as_attributes(self):
    d = AttrDict({
      'one': 1,
      'two': 2,
    })

    expect(d.one).to.equal(1)
    expect(d.two).to.equal(2)
    expect(lambda: d.three).to.throw(AttributeError)

class TestModelMock:

  def test_it_should_take_argument_names_into_account(self):
    m = ModelMock().has_arguments_mapping(['one', 'two'])

    m(1, 2, three=3)
    m(4, 5, three=6)

    call = m.get_call()

    expect(call).to.be.a(AttrDict)
    expect(call.one).to.equal(1)
    expect(call.two).to.equal(2)
    expect(call.three).to.equal(3)

    call = m.get_call(1)

    expect(call).to.be.a(AttrDict)
    expect(call.one).to.equal(4)
    expect(call.two).to.equal(5)
    expect(call.three).to.equal(6)

    expect(lambda: m.get_call(2)).to.throw(AssertionError)

class TestAgentModelMock:

  def test_it_should_contains_on_answer_handler(self):
    m = AgentModelMock()

    m.on_answer('This is a text', cards=[Card('Card header', 'Card text')], a_meta='a meta value')

    call = m.on_answer.get_call()

    expect(call.text).to.equal('This is a text')
    expect(call.cards).to.have.length_of(1)
    expect(call.cards[0].header).to.equal('Card header')
    expect(call.cards[0].text).to.equal('Card text')
    expect(call.a_meta).to.equal('a meta value')

  def test_it_should_contains_on_ask_handler(self):
    m = AgentModelMock()

    m.on_ask('room', 'Which rooms?', choices=['kitchen', 'bedroom'], a_meta='a meta value')

    call = m.on_ask.get_call()

    expect(call.slot).to.equal('room')
    expect(call.text).to.equal('Which rooms?')
    expect(call.choices).to.equal(['kitchen', 'bedroom'])
    expect(call.a_meta).to.equal('a meta value')

  def test_it_should_contains_on_context_handler(self):
    m = AgentModelMock()

    m.on_context('new_context')

    call = m.on_context.get_call()

    expect(call.context_name).to.equal('new_context')

  def test_it_should_contains_on_done_handler(self):
    m = AgentModelMock()

    m.on_done(True)

    call = m.on_done.get_call()

    expect(call.require_input).to.be.true

  def test_it_should_contains_on_thinking_handler(self):
    m = AgentModelMock()

    m.on_thinking()

    m.on_thinking.assert_called_once_with()

  def test_it_should_be_able_to_reset_all_mocks_count(self):
    m = AgentModelMock()

    m.on_answer()
    m.on_ask()
    m.on_context()
    m.on_done()
    m.on_thinking()

    m.on_answer.assert_called_once()
    m.on_ask.assert_called_once()
    m.on_context.assert_called_once()
    m.on_done.assert_called_once()
    m.on_thinking.assert_called_once()

    m.reset()

    m.on_answer.assert_not_called()
    m.on_ask.assert_not_called()
    m.on_context.assert_not_called()
    m.on_done.assert_not_called()
    m.on_thinking.assert_not_called()

def get_skill_folder(skill_name):
  return os.path.join(os.path.dirname(__file__), 'skills', skill_name)

class TestCreateSkillAgent:

  def test_it_should_instantiate_an_agent_for_the_targeted_skill_only(self):
    agt = create_skill_agent(get_skill_folder('alpha'))

    expect(agt).to.be.an(Agent)
    expect(agt._handlers).to.have.length_of(1)
    expect(agt._handlers).to.contain('alpha')
    expect(agt._interpreter.intents).to.have.length_of(1)
    expect(agt._interpreter.intents).to.contain('alpha')

    agt = create_skill_agent(get_skill_folder('bravo'))

    expect(agt._handlers).to.have.length_of(1)
    expect(agt._handlers).to.contain('bravo')
    expect(agt._interpreter.intents).to.have.length_of(1)
    expect(agt._interpreter.intents).to.contain('bravo')

  def test_it_should_load_additional_skills_too(self):
    # Will import both skills
    agt1 = create_skill_agent(get_skill_folder('alpha'))
    agt2 = create_skill_agent(get_skill_folder('bravo'))

    agt = create_skill_agent(get_skill_folder('alpha'), additional_skills=['bravo'])

    expect(agt._handlers).to.have.length_of(2)
    expect(agt._handlers).to.contain('alpha')
    expect(agt._handlers).to.contain('bravo')

    expect(agt._interpreter.intents).to.have.length_of(2)
    expect(agt._interpreter.intents).to.contain('alpha')
    expect(agt._interpreter.intents).to.contain('bravo')

  def test_it_should_contain_an_agent_model_mock(self):
    agt = create_skill_agent(get_skill_folder('alpha'))

    agt.parse('trigger alpha')

    expect(agt.model).to.be.an(AgentModelMock)

    call = agt.model.on_answer.get_call()

    expect(call.text).to.equal('Hello from alpha!')