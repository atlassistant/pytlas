from sure import expect
from pytlas.interpreters.slot import UnitValue
from pytlas.testing import create_skill_agent
import os
from .swear_jar import swear_jar, SwearJar

agent = create_skill_agent(os.path.dirname(__file__))

class TestSwearJar:

  def test_it_should_have_correct_default_values(self):
    j = SwearJar()

    expect(j.balance).to.equal(0)
    expect(j.unit).to.be.empty

    expect(str(j)).to.equal('nothing')

  def test_it_should_be_able_to_add_money_to_it(self):
    j = SwearJar()

    j.add(UnitValue(10, '$'))

    expect(j.balance).to.equal(10)
    expect(j.unit).to.equal('$')
    expect(str(j)).to.equal('10$')

  def test_it_should_complain_when_adding_different_units(self):
    j = SwearJar()
    
    j.add(UnitValue(10, '$'))

    expect(lambda: j.add(UnitValue(5, '€'))).to.throw(ArithmeticError)

class TestAddToSwearJar:

  def setup(self):
    agent.model.reset()
    swear_jar.reset()

  def test_it_should_add_money_to_the_swear_jar_when_given(self):
    agent.parse('add 20 dollars to the swear jar')

    on_answer = agent.model.on_answer.get_call()

    expect(on_answer.text).to.equal('Alright! 20$ have been added to the jar!')

  def test_it_should_request_money_when_not_given(self):
    agent.parse("i've been a bad guy")

    on_ask = agent.model.on_ask.get_call()

    expect(on_ask.slot).to.equal('money')
    expect(on_ask.text).to.be.within([
      'How many bucks should I add?',
      'How bad did you do?',
    ])

    agent.parse('fifty dollars')

    on_answer = agent.model.on_answer.get_call()

    expect(on_answer.text).to.equal('Alright! 50$ have been added to the jar!')

class TestGetSwearJarBalance:

  def setup(self):
    agent.model.reset()
    swear_jar.reset()

  def test_it_should_returns_the_correct_balance(self):
    agent.parse('how many dollars in the swear jar')

    on_answer = agent.model.on_answer.get_call()

    expect(on_answer.text).to.equal('You got nothing in the swear jar')
    
    agent.parse('add 11 dollars to the jar')
    agent.parse('drop 20 dollars in the jar')

    agent.model.reset()

    agent.parse('how many dollars in the swear jar')

    on_answer = agent.model.on_answer.get_call()

    expect(on_answer.text).to.equal('You got 31$ in the swear jar')