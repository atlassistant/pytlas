from sure import expect
from pytlas.testing import create_skill_agent
from .swear_jar import swear_jar
import os

# Le helper `create_skill_agent` nous permet de construire un agent pytlas pour 
# le skill contenu dans ce répertoire avec un SnipsInterpreter déjà entrainé.
agents = [
  create_skill_agent(os.path.dirname(__file__), lang='en'),
  create_skill_agent(os.path.dirname(__file__), lang='fr'),
]

# Liste des chaînes utilisées dans les tests
strings = {
  'en': {
    'add_20_units': 'add 20 dollars to the swear jar',
    '20_units_added': '20$ have been added to the jar',
    'i_have_been_mean': "i've been a bad guy",
    'ask_how_many': 'How many bucks should I add to the jar?',
    'answer_50_units': 'fifty dollars',
    '50_units_added': '50$ have been added to the jar',
    'add_11_units': 'add 11 dollars to the jar',
    'drop_20_units': 'drop 20 dollars in the jar',
    'empty_jar': 'The swear jar is empty',
    'balance_is_31': 'There is 31$ in the swear jar',
    'ask_for_balance': 'how many dollars in the swear jar',
  },
  'fr': {
    'add_20_units': 'ajoute 20 € au bocal à jurons',
    '20_units_added': '20EUR ont été ajoutés au bocal',
    'i_have_been_mean': "j'ai été vilain",
    'ask_how_many': 'Combien dois-je ajouter au bocal ?',
    'answer_50_units': 'cinquante euros',
    '50_units_added': '50EUR ont été ajoutés au bocal',
    'add_11_units': 'ajoute 11 euros dans le bocal',
    'drop_20_units': 'met 20 euros dans le bocal',
    'empty_jar': 'Le bocal à jurons est vide',
    'balance_is_31': "Il y'a 31EUR dans le bocal à jurons",
    'ask_for_balance': "A combien s'élève le bocal à jurons",
  },
}

class TestAddToSwearJar:

  # Ici, on reset les informations nécessaires pour que chaque tests s'éxécute
  # de manière isolé.
  def setup(self):
    for agent in agents:
      agent.model.reset()
      
    swear_jar.reset()

  def it_should_add_money_to_the_swear_jar_when_given(self, agent):
    agent.parse(strings[agent._interpreter.lang]['add_20_units'])

    # Le model passé à l'agent est un mock avec quelques utilitaires comme le 
    # get_call sur le différents événements levés par la librairie (cf. doc)
    # qui nous permet de récupérer l'appel effectué et de pouvoir effectuer
    # des assertions
    on_answer = agent.model.on_answer.get_call()

    expect(on_answer.text).to.equal(strings[agent._interpreter.lang]['20_units_added'])
    expect(swear_jar.balance.value).to.equal(20)

  def test_it_should_add_money_to_the_swear_jar_when_given(self):
    for agent in agents:
      yield self.it_should_add_money_to_the_swear_jar_when_given, agent

  def it_should_request_money_when_not_given(self, agent):
    agent.parse(strings[agent._interpreter.lang]['i_have_been_mean'])

    on_ask = agent.model.on_ask.get_call()

    expect(on_ask.slot).to.equal('money')
    expect(on_ask.text).to.equal(strings[agent._interpreter.lang]['ask_how_many'])

    agent.parse(strings[agent._interpreter.lang]['answer_50_units'])

    on_answer = agent.model.on_answer.get_call()

    expect(on_answer.text).to.equal(strings[agent._interpreter.lang]['50_units_added'])
    expect(swear_jar.balance.value).to.equal(50)

  def test_it_should_request_money_when_not_given(self):
    for agent in agents:
      yield self.it_should_request_money_when_not_given, agent

class TestGetSwearJarBalance:

  def setup(self):
    for agent in agents:
      agent.model.reset()
    swear_jar.reset()

  def it_should_returns_the_correct_balance(self, agent):
    agent.parse(strings[agent._interpreter.lang]['ask_for_balance'])

    on_answer = agent.model.on_answer.get_call()

    expect(on_answer.text).to.equal(strings[agent._interpreter.lang]['empty_jar'])
    
    agent.parse(strings[agent._interpreter.lang]['add_11_units'])
    agent.parse(strings[agent._interpreter.lang]['drop_20_units'])

    # On reset manuellement pour que le prochain `get_call` nous retourne
    # le dernier appel
    agent.model.reset()

    agent.parse(strings[agent._interpreter.lang]['ask_for_balance'])

    on_answer = agent.model.on_answer.get_call()

    expect(on_answer.text).to.equal(strings[agent._interpreter.lang]['balance_is_31'])

  def test_it_should_returns_the_correct_balance(self):
    for agent in agents:
      yield self.it_should_returns_the_correct_balance, agent