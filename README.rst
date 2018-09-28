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

  $ pip install pytlas[snips]

source
~~~~~~

.. code-block:: bash

  $ git clone https://github.com/atlassistant/pytlas.git
  $ cd pytlas
  $ python setup.py install

  or

  $ pip install -e .[snips]

Additional resources
~~~~~~~~~~~~~~~~~~~~

⚠️ If you want to use `snips-nlu` as the backend (which is the default), you would have to download needed resources with the following command as per `the documentation <https://github.com/snipsco/snips-nlu#language-resources>`_ where `en` is the language code you plan to use :

.. code-block:: bash

  $ snips-nlu download en

or

.. code-block:: bash

  $ snips-nlu download-all-languages

to download all languages resources.

Usage
-----

From the terminal
~~~~~~~~~~~~~~~~~

pytlas include a basic CLI interface to interact with the system.

This line will start the pytlas command prompt with skills located in the `example/skills/` directory. It will load all data and fit the engine before starting the prompt.

.. code-block:: bash

  $ pytlas -s example/skills -v

From code
~~~~~~~~~

Here is a snippet which cover the basics of using pytlas inside your own program :

.. code-block:: python

  # pytlas is fairly easy to understand.
  # It will take raw user inputs, parse them and call appropriate handlers with
  # parsed slots. It will also manage the conversation states so skills can ask
  # for user inputs if they need to.

  from pytlas import Agent, intent, training
  from pytlas.interpreters.snips import SnipsInterpreter

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
    turn lights on in the @[room]
    lights on in @[room] please
    turn on the lights in @[room]
    turn the lights on in @[room]
    enlight me in @[room]

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

    interpreter = SnipsInterpreter('en')

    # Train the interpreter using training data register with the `training` decorator
    # or `pytlas.training.register` function.

    interpreter.fit_from_skill_data()
    
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
    # - 'Turning lights on in kitchen, bedroom' is printed to the terminal by the `on_answer` delegate defined above
    # - `done` is called by the skill so the agent transitions back to the 'asleep' state

    agent.parse('turn the lights on in kitchen and in bedroom please')

Creating a skill
----------------

Skill are reusable piece of code that you can share with others and do the actual job. You can have a skill that fetch weather forecasts, another one that talks with your home connected components, that's entirely up to you!

Skills are self-contained and composed of 3 specific components:

- Training data: examples of how to trigger specific intents from natural language, defined in a tiny Domain Specific Language not tied to a particular NLU engine,
- Translations: simple key/value pair used by your skill for different languages,
- Intent handlers: Python code called when a specific intent has been parsed by `pytlas`

Have a look at the `example/skills` folder to see how it works.

Testing
-------

You should install test's dependencies first with the command:

.. code-block:: bash

  $ pip install -e .[snips,test]

.. code-block:: bash

  $ python -m nose --with-doctest -v
