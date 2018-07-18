import json
from pytlas import intent

@intent('get_forecast')
def on_forecast(req):
  cities = req.intent.slot('city')

  for city in cities:
    print (city.value)
    print (city.meta)

  print (req.intent.slot('date').first().value)
    
  return req.agent.done()