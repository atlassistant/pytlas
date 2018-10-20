from pytlas import intent, training, translations, Card
import requests, re

@training('en')
def en_data(): return """
%[__cancel__]
  cancel
  abandon the command

%[greet]
  hey
  hi
  hello
  hey there
  good morning
  good evening
"""

@training('fr')
def fr_data(): return """
%[__cancel__]
  annule
  annuler
  abandonne la commande

%[greet]
  hey
  salut
  bonjour
  coucou
  bonsoir
"""

@translations('fr')
def fr_translations(): return {
  'Yes': 'Oui',
  'No': 'Non',
  'An error occured': 'Une erreur est survenue',
  'Would you like me to search for "%s"?': 'Voulez-vous que je recherche "%s" ?',
  'No results found': 'Aucun résultat trouvé',
  'Here it is': 'Et voilà',
  'Command aborted': 'Commande annulée',
  'Hello 🖐️! What can I do for you?': "Salut 🖐️ ! Qu'est ce que je peux faire pour toi ?",
  'Hi 🖐️! How can I help you?': "Hey 🖐️ ! Comment puis-je t'aider ?",
  'Hey 🖐️! What are you looking for?': "Bonjour 👋 ! Que souhaites tu faire ?",
}

@intent('greet')
def greet(req):
  req.agent.answer([
    req._('Hello 🖐️! What can I do for you?'),
    req._('Hi 🖐️! How can I help you?'),
    req._('Hey 🖐️! What are you looking for?'),
  ])

  return req.agent.done()

@intent('__cancel__')
def cancel(req):
  req.agent.answer(req._('Command aborted'))

  return req.agent.done()

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
      results = res.json()['data']['result']['items']

      if len(results) > 0:
        r.agent.answer(r._('Here it is'), cards=[create_result_card(r, d) for d in results])
      else:
        r.agent.answer(r._('No results found'))
    else:
      r.agent.answer(r._('An error occured'))

  return r.agent.done()

cleanr = re.compile('<.*?>')

def remove_html_tags(raw_html):
  return re.sub(cleanr, '', raw_html)

def create_result_card(request, data):
  title = remove_html_tags(data.get('title'))
  desc = remove_html_tags(data.get('desc'))
  link = data.get('url')

  return Card(title, desc, header_link=link)
