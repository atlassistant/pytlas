import json
from pytlas import intent

@intent('get_forecast')
def on_forecast(req):
  cities = req.intent.slot('city')
  date = req.intent.slot('date').first().value

  if not date:
    return req.agent.ask('date', 'For when?')
    
  return req.agent.done()