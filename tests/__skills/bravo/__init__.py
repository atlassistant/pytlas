from pytlas import training, intent

@training('en')
def bravo_training():
  return """
%[bravo]
  start bravo
  bravo one
  trigger bravo handler
"""

@intent('bravo')
def bravo_handler(r):
  r.agent.answer('Hello from bravo!')

  return r.agent.done()