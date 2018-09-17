from pytlas.skill import intent
from pytlas.training import training

@training('en')
def en_data(): return """
%[get_forecast]
  will it be sunny in @[location] at @[date#at]
  what's the weather like in @[location] on @[date#on]
  will it rain in @[location] @[date]
  what kind of weather should I expect at @[date#at] in @[location]
  what will be the weather on @[date#on] in @[location]
  tell me if it is going to rain @[date] in @[location]
  will it rain in @[location] and @[location] @[date]

~[los angeles]
  la

@[date](type=snips/datetime)
  tomorrow
  today
  this evening

@[date#at]
  the end of the day
  nine o'clock

@[date#on]
  tuesday
  monday

@[location]
  ~[los angeles]
  paris
  rio de janeiro
  tokyo
  london
  tel aviv
  paris
  new york

"""

@intent('get_forecast')
def on_forecast(req):
  cities = req.intent.slot('location')
  date = req.intent.slot('date').first().value

  if not date:
    return req.agent.ask('date', 'For when?')

  if not cities:
    return req.agent.ask('location', 'For where?')
    
  req.agent.answer('Checking weather for %s and %s' % (', '.join(c.value for c in cities), date))

  return req.agent.done()