# pytlas is fairly easy to understand.
# It will take raw user inputs, parse them and call appropriate handlers with
# parsed slots.

from pytlas import Agent, Client, intent
from pytlas.interpreters.snips import SnipsInterpreter

# Here we are registering a function (with the intent decorator) as an handler 
# for the intent 'lights_on'.
#
# So when a user input will be parsed as a 'lights_on' intent, this handler will
# be called with a special `Request` object which contains the agent (which triggered
# this handler) and the intent with its slots.

@intent('lights_on')
def on_intent_lights_on(request):
  
  # With the request object, we can communicate back with the `answer` method
  # or the `ask` method if we need more user input.
  
  request.agent.answer('Turning lights on in %s' % request.intent.slot('room').first().value)

  # When using the `answer` method, you should call the `done` method as well. This is
  # useful because a skill could communicate multiple answers at different intervals
  # (ie. when fetching the information elsewhere).

  return request.agent.done()

# Communication is done with a special object called a `Client`. When a skill wants to
# reply to the user, it will use the client tied to the agent instance which initially
# parsed the raw message.

class BasicClient(Client):

  def __init__(self, interpreter):
    
    # The `Agent` is the core of pytlas. It manages the conversation state with a
    # state machine and call appropriate handlers when needed.

    self._agent = Agent(interpreter, self)

  def parse(self, msg):
    self._agent.parse(msg)

  def answer(self, text, cards):
    print (text)

if __name__ == '__main__':
  
  # The last piece is the `Interpreter`. This is the part responsible for human
  # language parsing. It parses raw human sentences into something more useful for
  # the program.
  #
  # Each interpreter as its own training format so here we are loading needed files from
  # this directory.

  interpreter = SnipsInterpreter('.')
  interpreter.fit_as_needed()
  
  client = BasicClient(interpreter)

  # With this next line, this is what happenned:
  #
  # - The message is parsed by the `SnipsInterpreter`
  # - A 'lights_on' intents is retrieved and contains 'kitchen' as the 'room' slot value
  # - Since the `Agent` is asleep, it will transition to the 'lights_on' state
  # - Transitioning to this state call the appropriate handler (at the beginning of this file)
  # - 'Turning lights on in kitchen' is printed to the terminal by the `BasicClient#answer` method defined above
  # - `done` is called by the skill so the agent transitions back to the 'asleep' state

  client.parse('turn the lights on in the kitchen please')