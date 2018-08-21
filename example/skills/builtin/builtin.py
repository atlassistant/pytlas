from pytlas import intent

@intent('__fallback__')
def fallback(r):
  r.agent.answer('Searching...')

  return r.agent.done()
