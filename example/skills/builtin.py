from pytlas import intent

@intent('pytlas__fallback')
def fallback(r):
  return r.agent.done()