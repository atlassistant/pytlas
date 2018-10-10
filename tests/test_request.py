from sure import expect
from datetime import datetime
from pytlas.agent import Agent
from pytlas.interpreters import Interpreter
from pytlas.request import Request, AgentProxy

class TestRequest:

  def setup(self):
    self.interpreter = Interpreter('test', 'fr')
    self.agent = Agent(self.interpreter)

  def teardown(self):
    pass

  def test_it_should_have_a_unique_id(self):
    r = Request(self.agent, None)
    r2 = Request(self.agent, None)

    expect(r.id).to_not.be.none
    expect(r2.id).to_not.be.none
    expect(r.id).to_not.equal(r2.id)

  def test_it_should_have_the_same_language_as_the_interpreter(self):
    r = Request(self.agent, None)

    expect(r.lang).to.equal(self.interpreter.lang)

  def test_it_should_be_able_to_translate_text_in_the_interpreter_language(self):
    r = Request(self.agent, None, {
      'a text': 'un texte',
    })

    expect(r._('a text')).to.equal('un texte')
    expect(r._('not found')).to.equal('not found')

  def test_it_should_be_able_to_format_a_date_according_to_the_language(self):
    r = Request(self.agent, None)
    d = datetime(2018, 9, 25, 8, 30)

    expect(r._d(d)).to.equal('25 sept. 2018 à 08:30:00')
    expect(r._d(d, date_only=True)).to.equal('25 sept. 2018')
    expect(r._d(d, time_only=True)).to.equal('08:30:00')
    expect(r._d(d, format='full', date_only=True)).to.equal('mardi 25 septembre 2018')

  def test_it_should_not_call_agent_methods_if_not_the_current_request(self):
    r = Request(self.agent, None)

    expect(r.agent).to.be.an(AgentProxy)
    expect(r.agent.ask).to_not.equal(self.agent.ask)

    self.agent._request = Request(self.agent, None)
    expect(r.agent.ask).to_not.equal(self.agent.ask)
    expect(r.agent.ask).to.equal(r.agent.empty_func)
    expect(r.agent.done).to.equal(r.agent.empty_func)
    expect(r.agent.answer).to.equal(r.agent.empty_func)
    expect(r.agent.meta).to.equal(self.agent.meta)

  def test_it_should_call_agent_methods_if_the_current_request(self):
    r = Request(self.agent, None)

    expect(r.agent.ask).to_not.equal(self.agent.ask)

    self.agent._request = r
    expect(r.agent.ask).to.equal(self.agent.ask)
