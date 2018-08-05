pytlas
======

Python 3 assistant made to be super simple to setup!

Installation
------------

pip
~~~

.. code-block:: bash

  $ pip install pytlas

source
~~~~~~

.. code-block:: bash

  $ git clone https://github.com/atlassistant/pytlas.git
  $ cd pytlas
  $ python setup.py install

  or

  $ pip install -e ."[snips]"

Usage
-----

.. code-block:: python

  # pytlas is fairly easy to understand.
  # It will take raw user inputs, parse them and call appropriate handlers with
  # parsed slots. It will also manage the conversation states so skills can ask
  # for user inputs if they need to.

  from pytlas import Agent, intent
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
    # or the `ask` method if we need more user input. Here we are joining on each
    # slot `value` because a slot can have multiple values.
    
    request.agent.answer('Turning lights on in %s' % ', '.join([v.value for v in request.intent.slot('room')]))

    # When using the `answer` method, you should call the `done` method as well. This is
    # useful because a skill could communicate multiple answers at different intervals
    # (ie. when fetching the information elsewhere).

    return request.agent.done()

  if __name__ == '__main__':
    
    # The last piece is the `Interpreter`. This is the part responsible for human
    # language parsing. It parses raw human sentences into something more useful for
    # the program.
    #
    # Each interpreter as its own training format so here we are loading the snips 
    # interpreter with needed files from this directory.

    interpreter = SnipsInterpreter('.')
    interpreter.fit_as_needed()
    
    # The `Agent` exposes some handlers used to communicate with the outside world.

    agent = Agent(interpreter, 
      on_answer=lambda text, cards: print (text),
      on_ask=lambda slot, text, choices: print (text)
    )

    # With this next line, this is what happenned:
    #
    # - The message is parsed by the `SnipsInterpreter`
    # - A 'lights_on' intents is retrieved and contains 'kitchen' as the 'room' slot value
    # - Since the `Agent` is asleep, it will transition to the 'lights_on' state
    # - Transitioning to this state call the appropriate handler (at the beginning of this file)
    # - 'Turning lights on in kitchen' is printed to the terminal by the `on_answer` delegate defined above
    # - `done` is called by the skill so the agent transitions back to the 'asleep' state

    agent.parse('turn the lights on in the kitchen please')

Testing
-------

.. code-block:: bash

  $ cd tests/
  $ python -m unittest -v
