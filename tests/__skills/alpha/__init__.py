from pytlas import training, intent

@training('en')
def alpha_training():
  return """
%[alpha]
  start alpha
  alpha one
  trigger alpha handler
"""

@intent('alpha')
def alpha_handler(r):
  r.agent.answer('Hello from alpha!')
  
  return r.agent.done()