from pytlas import intent

@intent('lights_on')
def turn_on(req):
  print (req.intent.slot('rooms').first().value)

@intent('lights_off')
def turn_off(req):
  print (req.intent.slot('rooms').first().value)