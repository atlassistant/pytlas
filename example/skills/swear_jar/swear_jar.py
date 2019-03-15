from pytlas import training, intent

class SwearJar:
  """Tiny class to represents the global swear jar shared amoung all users.
  """

  def __init__(self):
    self.reset()

  def __str__(self):
    if not self.balance:
      return 'nothing'

    return '%.2g%s' % (self.balance, self.unit)
  
  def reset(self):
    self.balance = 0.0
    self.unit = ''

  def add(self, money):
    self.balance += money.value
    
    if not self.unit:
      self.unit = money.unit
    elif self.unit != money.unit:
      raise ArithmeticError

swear_jar = SwearJar()

@training('en')
def en_training_data(): return """
%[add_to_swear_jar]
  add @[money] to the swear jar
  i've been a bad boy
  i am a bad boy
  drop @[money] in the swear jar

%[get_swear_jar_balance]
  give me the current jar balance
  what's the swear jar balance
  how many dollars in the swear jar

@[money](type=amountOfMoney)
  two dollars
  fifty dollars
"""

@intent('add_to_swear_jar')
def on_add_to_swear_jar(req):
  amount_to_add = req.intent.slot('money').first().value

  if not amount_to_add:
    return req.agent.ask('money', [
      req._('How many bucks should I add?'),
      req._('How bad did you do?'),
    ])

  swear_jar.add(amount_to_add)

  req.agent.answer(req._('Alright! %s have been added to the jar!') % amount_to_add)

  return req.agent.done()

@intent('get_swear_jar_balance')
def on_get_swear_jar_balance(req):
  req.agent.answer(req._('You got %s in the swear jar') % swear_jar)

  return req.agent.done()