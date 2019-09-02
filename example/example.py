# pytlas is fairly easy to understand.
# It will take raw user inputs, parse them and call appropriate handlers with
# parsed slots values. It will also manage the conversation states so skills
# can ask for user inputs if they need to.

import os
from pytlas import Agent, intent, training
from pytlas.understanding.snips import SnipsInterpreter

# Here, we register a sentence as training data for the specified language
# Those training sample are written using a simple DSL named chatl. It make it
# back-end agnostic and is much more readable than raw dataset needed by NLU
# engines.
#
# Those data will be parsed by `pychatl` to output the correct dataset use for the fit
# part.

@training('en')
def en_data(): return """
%[lights_on]
  turn the @[room]'s lights on would you
  turn lights on in the @[room] and @[room]
  lights on in @[room] and @[room] please
  turn on the lights in @[room]
  turn the lights on in @[room]
  enlight me in @[room]
  lights on in @[room] and [room]

~[basement]
  cellar

@[room](extensible=false)
  living room
  kitchen
  bedroom
  ~[basement]

"""

# Here we are registering a function (with the intent decorator) as an handler
# for the intent 'lights_on'.
#
# So when a user input will be parsed as a 'lights_on' intent by the
# interpreter, this handler will be called with a special `Request` object
# which contains the agent (which triggered this handler) and the intent with
# its slots.

@intent('lights_on')
def on_intent_lights_on(request):
  
  # With the request object, we can communicate back with the `answer` method
  # or the `ask` method if we need more user input. Here we are joining on each
  # slot `value` because a slot can have multiple values.
  
  request.agent.answer('Turning lights on in %s' % ', '.join([v.value for v in request.intent.slot('room')]))

  # When using the `answer` method, you should call the `done` method as well. This is
  # useful because a skill could communicate multiple answers at different intervals
  # (ie. when fetching the information elsewhere).

  return request.agent.done()

class Client:
  """This client is used as a model for an agent. It will receive lifecycle events
  raised by the agent.
  """

  def on_answer(self, text, cards, **meta):
    print (text)

  def on_ask(self, slot, text, choices, **meta):
    print (text)

if __name__ == '__main__':
  
  # The last piece is the `Interpreter`. This is the part responsible for human
  # language parsing. It parses raw human sentences into something more useful for
  # the program.

  interpreter = SnipsInterpreter('en', cache_directory=os.path.join(os.path.dirname(__file__), 'cache'))

  # Train the interpreter using training data register with the `training` decorator
  # or `pytlas.training.register` function.

  interpreter.fit_from_skill_data()
  
  # The `Agent` uses the model given to call appropriate lifecycle hooks.

  agent = Agent(interpreter, model=Client())

  # With this next line, this is what happenned:
  #
  # - The message is parsed by the `SnipsInterpreter`
  # - A 'lights_on' intents is retrieved and contains 'kitchen' and 'bedroom' as the 'room' slot values
  # - Since the `Agent` is asleep, it will transition to the 'lights_on' state immediately
  # - Transitioning to this state call the appropriate handler (at the beginning of this file)
  # - 'Turning lights on in kitchen, bedroom' is printed to the terminal by the `Client.on_answer` defined above
  # - `done` is called by the skill so the agent transitions back to the 'asleep' state

  agent.parse('turn the lights on in kitchen and bedroom please')
