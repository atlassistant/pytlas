from sure import expect
from pytlas.testing import create_skill_agent
from .swear_jar import swear_jar
import os

agent = create_skill_agent(os.path.dirname(__file__), lang='fr')

class TestAddToSwearJarInFrench:

  def setup(self):
    agent.model.reset()
    swear_jar.reset()

  def test_it_should_add_money_to_the_swear_jar_when_given(self):
    agent.parse('ajoute 20 € au bocal à jurons')

    on_answer = agent.model.on_answer.get_call()

    expect(on_answer.text).to.equal('20EUR ont été ajoutés au bocal')
    expect(swear_jar.balance.value).to.equal(20)

  def test_it_should_request_money_when_not_given(self):
    agent.parse("J'ai été vilain")

    on_ask = agent.model.on_ask.get_call()

    expect(on_ask.slot).to.equal('money')
    expect(on_ask.text).to.equal('Combien dois-je ajouter au bocal ?')

    agent.parse('cinquante euros')

    on_answer = agent.model.on_answer.get_call()

    expect(on_answer.text).to.equal('50EUR ont été ajoutés au bocal')
    expect(swear_jar.balance.value).to.equal(50)

class TestGetSwearJarBalanceInFrench:

  def setup(self):
    agent.model.reset()
    swear_jar.reset()

  def test_it_should_returns_the_correct_balance(self):
    agent.parse("A combien s'élève le bocal à jurons")

    on_answer = agent.model.on_answer.get_call()

    expect(on_answer.text).to.equal('Le bocal à jurons est vide')
    
    agent.parse('ajoute 11 euros dans le bocal')
    agent.parse('met 20 euros dans le bocal')

    agent.model.reset()

    agent.parse("combien y'a t-il d'euros dans le bocal")

    on_answer = agent.model.on_answer.get_call()

    expect(on_answer.text).to.equal("Il y'a 31EUR dans le bocal à jurons")