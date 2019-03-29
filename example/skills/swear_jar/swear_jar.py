from pytlas import training, intent, translations

@training('fr')
def french_data(): return """
%[add_to_swear_jar]
  j'ai été vulgaire
  j'ai été un vilain garçon
  ajoute @[money] au bocal à jurons
  ajoute @[money] au bocal
  mets @[money] dans le bocal à jurons

%[get_swear_jar_balance]
  à combien s'élève le bocal
  combien y'a t-il d'euros dans le bocal
  peux-tu me donner le montant du bocal
  quel est le montant du bocal

@[money](type=amountOfMoney)
  deux euros
  10 euros
"""

@training('en')
def english_data(): return """
%[add_to_swear_jar]
  i've been a bad boy
  i was mean
  i was vulgar
  add @[money] to the swear jar
  add @[money] to the jar
  drop @[money] in the swear jar

%[get_swear_jar_balance]
  what's in the swear jar
  how many dollars in the jar
  can you give me the current swear jar balance
  what's the jar balance

@[money](type=amountOfMoney)
  two dollars
  10 dollars
"""

class SwearJar:
  def __init__(self):
    self.reset()
  
  def reset(self):
    self.balance = None
    
  def add(self, value):
    if not self.balance:
      self.balance = value
    else:
      self.balance += value

@translations('fr')
def french_translations(): return {
  'How many bucks should I add to the jar?': 'Combien dois-je ajouter au bocal ?',
  '%s have been added to the jar': '%s ont été ajoutés au bocal',
  'There is %s in the swear jar': "Il y'a %s dans le bocal à jurons",
  'The swear jar is empty': 'Le bocal à jurons est vide',
}

# Comme notre bocal sera le même pour tout le monde, on l'instantie ici (on ne gérera pas la persistance dans cet exemple)
swear_jar = SwearJar()

@intent('add_to_swear_jar')
def on_add_to_swear_jar(request):
  # On récupère le montant à ajouter en allant chercher le paramètre `money` défini dans les jeux d'exemples
  amount_to_add = request.intent.slot('money').first().value
  
  # Si pas de montant défini, alors on demande à l'utilisateur de le préciser et l'handler sera de nouveau appelé
  # avec la valeur modifiée
  if not amount_to_add:
    return request.agent.ask('money', request._('How many bucks should I add to the jar?'))
  
  swear_jar.add(amount_to_add)
  
  # On informe l'utilisateur de ce qui s'est passé
  request.agent.answer(request._('%s have been added to the jar') % amount_to_add)
  
  # Et enfin, on fait signe à pytlas que le skill a terminé de traiter l'intention
  return request.agent.done()
  
@intent('get_swear_jar_balance')
def on_get_swear_jar_balance(request):
  if not swear_jar.balance:
    request.agent.answer(request._('The swear jar is empty'))
  else:
    request.agent.answer(request._('There is %s in the swear jar') % swear_jar.balance)

  return request.agent.done()