from pytlas import intent

@intent('lights_on')
def turn_on(req):
  room = req.intent.slot('rooms').first().value

  if not room:
    return req.agent.ask('rooms', 'Which room?')
  
  print ('Hello from turn on')
  print (req.intent.slot('rooms').first().value)
  
  return req.agent.done()

@intent('lights_off')
def turn_off(req):
  print ('Hello from turn off')
  print (req.intent.slot('rooms').first().value)
  
  return req.agent.done()