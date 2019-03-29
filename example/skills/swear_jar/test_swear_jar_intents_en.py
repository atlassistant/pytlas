from sure import expect
from pytlas.testing import create_skill_agent
from .swear_jar import swear_jar
import os

# Le helper `create_skill_agent` nous permet de construire un agent pytlas pour 
# le skill contenu dans ce répertoire avec un SnipsInterpreter déjà entrainé.
agent = create_skill_agent(os.path.dirname(__file__), lang='en')

class TestAddToSwearJarInEnglish:

  # Ici, on reset les informations nécessaires pour que chaque tests s'éxécute
  # de manière isolé.
  def setup(self):
    agent.model.reset()
    swear_jar.reset()

  def test_it_should_add_money_to_the_swear_jar_when_given(self):
    agent.parse('add 20 dollars to the swear jar')

    # Le model passé à l'agent est un mock avec quelques utilitaires comme le 
    # get_call sur le différents événements levés par la librairie (cf. doc)
    # qui nous permet de récupérer l'appel effectué et de pouvoir effectuer
    # des assertions
    on_answer = agent.model.on_answer.get_call()

    expect(on_answer.text).to.equal('20$ have been added to the jar')
    expect(swear_jar.balance.value).to.equal(20)

  def test_it_should_request_money_when_not_given(self):
    agent.parse("i've been a bad guy")

    on_ask = agent.model.on_ask.get_call()

    expect(on_ask.slot).to.equal('money')
    expect(on_ask.text).to.equal('How many bucks should I add to the jar?')

    agent.parse('fifty dollars')

    on_answer = agent.model.on_answer.get_call()

    expect(on_answer.text).to.equal('50$ have been added to the jar')
    expect(swear_jar.balance.value).to.equal(50)

class TestGetSwearJarBalanceInEnglish:

  def setup(self):
    agent.model.reset()
    swear_jar.reset()

  def test_it_should_returns_the_correct_balance(self):
    agent.parse('how many dollars in the swear jar')

    on_answer = agent.model.on_answer.get_call()

    expect(on_answer.text).to.equal('The swear jar is empty')
    
    agent.parse('add 11 dollars to the jar')
    agent.parse('drop 20 dollars in the jar')

    # On reset manuellement pour que le prochain `get_call` nous retourne
    # le dernier appel
    agent.model.reset()

    agent.parse('how many dollars in the swear jar')

    on_answer = agent.model.on_answer.get_call()

    expect(on_answer.text).to.equal('There is 31$ in the swear jar')