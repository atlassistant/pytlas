from pytlas import intent, training, translations, Card
from datetime import datetime
from dateutil.parser import parse as dateParse 
import requests

# These entity will be shared among training data since it's not language specific

locations = """
@[location]
  los angeles
  paris
  rio de janeiro
  tokyo
  london
  tel aviv
  paris
  new york
  saint-étienne du rouvray
"""

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

@[date](snips:type=snips/datetime)
  tomorrow
  today
  this evening

@[date#at]
  the end of the day
  nine o'clock

@[date#on]
  tuesday
  monday

""" + locations

@training('fr')
def fr_data(): return """
%[get_forecast]
  va t-il ~[weather_conditions] @[date] sur @[location]
  quel temps va t-il faire à @[location] @[date]
  dis moi s'il va ~[weather_conditions] @[date] à @[location]
  donne moi la météo de @[date] à @[location]
  quel sera la météo sur @[location] @[date]
  est-ce qu'il va ~[weather_conditions] à @[location] @[date]

~[weather_conditions]
  faire beau
  pleuvoir
  y'avoir du vent
  faire nuageux

@[date](snips:type=snips/datetime)
  demain
  aujourd'hui
  ce week-end
  ce soir
  jeudi
  demain matin

""" + locations

@translations('fr')
def fr_translations(): return {
  'For where?': 'Pour quel emplacement ?',
  'Checking weather for %s on %s': "Je recherche la météo sur %s pour le %s",
  'You must provide an OPENWEATHER_APPID': "Vous devez fournir la clé OPENWEATHER_APPID",
  'Here what I found for %s!': "Voici ce que j'ai trouvé pour %s",
  'No results found': "Aucun résultat trouvé",
}

# Maps between openweather icon keys and emojis
emojis_map = {
  '01': '☀️',
  '02': '⛅',
  '03': '☁️',
  '04': '☁️',
  '09': '🌧️',
  '10': '🌧️',
  '11': '🌩️',
  '13': '🌨️',
  '50': '🌫️',
}

# Maps between openweather units and associated symbol
units_map = {
  'metric': '°C',
  'imperial': '°F',
}

@intent('get_forecast')
def on_forecast(req):
  appid = req.agent.meta.get('OPENWEATHER_APPID')
  units = req.agent.meta.get('OPENWEATHER_UNITS', 'metric')

  if not appid:
    req.agent.answer(req._('You must provide an OPENWEATHER_APPID'))
    return req.agent.done()

  city = req.intent.slot('location').first().value
  date = req.intent.slot('date').first().value_as_date or datetime.utcnow()

  if not city:
    return req.agent.ask('location', req._('For where?'))

  forecasts = fetch_forecasts(city, date, appid, req.lang, units)

  if len(forecasts) > 0:
    req.agent.answer(req._('Here what I found for %s!') % city, cards=[create_forecast_card(req, d, units) for d in forecasts])
  else:
    req.agent.answer(req._('No results found'))

  return req.agent.done()

def create_forecast_card(req, data, unit):
  w = data['weather'][0]
  temps = '{min}{unit} - {max}{unit}'.format(unit=units_map.get(unit), min=int(data['main']['temp_min']), max=int(data['main']['temp_max']))

  return Card('%s %s' % (emojis_map.get(w['icon'][:-1]), w['description'].capitalize()), temps, req._d(data['date']))

def fetch_forecasts(city, date, appid, lang, units):
  r = requests.get('https://api.openweathermap.org/data/2.5/forecast?q=%s&units=%s&lang=%s&appid=%s' 
    % (city, units, lang, appid))

  def concerned_date(data):
    parsed_date = dateParse(data.get('dt_txt'))
    data['date'] = parsed_date # Keep it!

    return parsed_date.date() == date.date()

  return list(filter(concerned_date, r.json().get('list', [])))