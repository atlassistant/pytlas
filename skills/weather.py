from pytlas import intent

@intent('get_forecast')
def on_forecast(req):
  print('Youhouuuu')
  return req.agent.done()