from pytlas.skill import intent

@intent('get_forecast')
def on_forecast(req):
  cities = req.intent.slot('location')
  date = req.intent.slot('date').first().value

  if not date:
    return req.agent.ask('date', 'For when?')
    
  req.agent.answer('Checking weather for %s and %s' % (', '.join(c.value for c in cities), date))

  return req.agent.done()