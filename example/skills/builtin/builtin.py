from pytlas import intent, training

@training('en')
def en_data(): return """
%[__cancel__]
  cancel
  abandon the command
"""

@training('fr')
def fr_data(): return """
%[__cancel__]
  annule
  annuler
  abandonne la commande
"""

@intent('__fallback__')
def fallback(r):
  r.agent.answer('Searching for "%s" ...' % r.intent.slot('text').first().value)

  return r.agent.done()
