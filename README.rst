pytlas |travis| |pypi| |license|
================================

.. |travis| image:: https://travis-ci.org/atlassistant/pytlas.svg?branch=master
    :target: https://travis-ci.org/atlassistant/pytlas

.. |pypi| image:: https://badge.fury.io/py/pytlas.svg
    :target: https://badge.fury.io/py/pytlas

.. |license| image:: https://img.shields.io/badge/License-GPL%20v3-blue.svg
    :target: https://www.gnu.org/licenses/gpl-3.0

An open-source 🤖 assistant library built for people and made to be super easy to setup and understand.

I first started to develop `atlas <https://github.com/atlassistant/atlas>`_ but I have finally decided to develop a library that everyone could embed in their own program with simple python code.

I have ditched the **MQTT** part to keep things super simple to understand.

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

  $ pip install -e .[snips]

⚠️ If you want to use `snips-nlu` as the backend, you would have to download needed resources with as per `the documentation <https://github.com/snipsco/snips-nlu#language-resources>`_:

.. code-block:: bash

  $ snips-nlu download en

Usage
-----

From the terminal
~~~~~~~~~~~~~~~~~

This line will start the pytlas command prompt with training data from `example/` and skills in the `example/skills/` directory. Every python file in the `example/skills/` will be imported by the CLI so handlers will be registered and called when appropriate.

.. code-block:: bash

  $ pytlas -t example -s example/skills

From code
~~~~~~~~~

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

    # Train the interpreter if training data has changed, else it will be loaded
    # from the cache directory.

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

    agent.parse('turn the lights on in kitchen please')

Testing
-------

.. code-block:: bash

  $ cd tests/
  $ python -m unittest -v
