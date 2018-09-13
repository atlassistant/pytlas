from pytlas.skill import intent

@intent('__fallback__')
def fallback(r):
  r.agent.answer('Searching for "%s" ...' % r.intent.slot('text').first().value)

  return r.agent.done()
