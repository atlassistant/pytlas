from pytlas import intent, training, translations, Card
import requests, re

@training('en')
def en_data(): return """
%[__cancel__]
  cancel
  abandon the command
"""

@training('fr')
def fr_data(): return """
%[__cancel__]
  annule
  annuler
  abandonne la commande
"""

@translations('fr')
def fr_translations(): return {
  'Yes': 'Oui',
  'No': 'Non',
  'Would you like me to search for "%s"?': 'Voulez-vous que je recherche "%s" ?',
  'No results found': 'Aucun résultat trouvé',
  'Here it is': 'Et voilà',
}

@intent('__fallback__')
def fallback(r):
  term = r.intent.slot('text').first().value
  search_confirmed = r.intent.slot('search_confirmed').first().value
  yes = r._('Yes')
  no = r._('No')

  if not search_confirmed:
    return r.agent.ask('search_confirmed', r._('Would you like me to search for "%s"?') % term, [yes, no])

  if search_confirmed == yes:
    res = requests.get('https://api.qwant.com/egp/search/web', 
      params={ 'q': term }, 
      headers={
        'user-agent': 'Mozilla/5.0 (Windows NT x.y; rv:10.0) Gecko/20100101 Firefox/10.0',
      })

    if res.ok:
      r.agent.answer(r._('Here it is'), cards=[create_result_card(r, d) for d in res.json()['data']['result']['items']])
    else:
      r.agent.answer(r._('No results found'))

  return r.agent.done()

cleanr = re.compile('<.*?>')

def remove_html_tags(raw_html):
  return re.sub(cleanr, '', raw_html)

def create_result_card(request, data):
  title = remove_html_tags(data.get('title'))
  desc = remove_html_tags(data.get('desc'))

  return Card(title, desc)
