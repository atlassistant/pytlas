import json
from pytlas import intent

@intent('get_forecast')
def on_forecast(req):
  cities = req.intent.slot('city')

  for city in cities:
    print (city.value)
    print (city.meta)
    
  return req.agent.done()