from pytlas import intent

def turn_lights(req, on):
  rooms = req.intent.slot('rooms')

  if not rooms:
    return req.agent.ask('rooms', [
      req._('For which rooms?'),
      req._('Which rooms Sir?'),
      req._('Please specify some rooms'),
    ])

  req.agent.answer(req._('Turning lights %s in %s') % ('on' if on else 'off', ', '.join(room.value for room in rooms)))

  return req.agent.done()

@intent('lights_on')
def turn_on(req):
  return turn_lights(req, True)

@intent('lights_off')
def turn_off(req):
  return turn_lights(req, False)