from pytlas import intent, training

@training('en')
def en_training(): return """
%[create_scenario]
  create a scenario named @[name]
  create the scenario @[name]
  create a new scenario @[name]

%[scenario_creation/done]
  i'm done
  i have finished

@[name]
  good morning
  wake up
"""

@intent('create_scenario')
def create_scenario(r):
  name = r.intent.slot('name').first().value

  if not name:
    return r.agent.ask('name', r._("What's its name?"))
  
  r.agent.meta['current_scenario'] = {
    'name': name,
    'intents': [],
  }

  r.agent.answer(r._("Please give your instructions and say you're done to save the scenario"))

  r.agent.context('scenario_creation')

  return r.agent.done()

@intent('scenario_creation/__fallback__')
def append_intent(r):

  # TODO use the interpreter to parse the intent and slot and save that instead
  # to be able to call the queue_intent when executing a scenario
  r.agent.meta['current_scenario']['intents'].append(r.intent.slot('text').first().value)

  r.agent.answer(r._("What's next?"))

  return r.agent.done()

@intent('scenario_creation/done')
def save_scenario(r):
  c = r.agent.meta['current_scenario']

  r.agent.answer(r._('Alright, I have saved your %s scenario with %d intents') % (c['name'], len(c['intents'])))

  r.agent.context(None)

  return r.agent.done()