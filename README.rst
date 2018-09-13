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

Training
--------

In order for pytlas to understand you, you must train the interpreter. By default, only the `SnipsInterpreter` is available and should be train using its specific dataset format.

To generate this training dataset, you can use `chatito <https://github.com/rodrigopivi/Chatito>`_, `chatl <https://github.com/atlassistant/chatl>`_, `the snips-nlu dataset generation tool <https://snips-nlu.readthedocs.io/en/latest/tutorial.html#snips-dataset-format>`_ or any other tool of your choice.

Once you have that training json file, you should give the directory path of this file to the `SnipsInterpreter` constructor. So if you have put your file in `training/training.json`, you should instantiate the interpreter with `SnipsInterpreter('./training')`. It will make use of 3 paths:

- cache_directory (`./training/cache/`): This is where the trained engine will be put 
- training_filepath (`./training/training.json`): Path to the file used to train the model
- checksum_filepath (`./training/trained.checksum`): Generated checksum of the training file, this is used to avoid retraining the engine if training data hasn't changed between 2 runs

*TODO: split this category to make it more clear on where to put files*

Usage
-----

From the terminal
~~~~~~~~~~~~~~~~~

pytlas include a basic CLI interface to interact with the system.

This line will start the pytlas command prompt with training data from `example/` and skills in the `example/skills/` directory. Every python files in the `example/skills/` will be imported by the CLI so handlers will be registered and called when appropriate.

.. code-block:: bash

  $ pytlas -t example -s example/skills

From code
~~~~~~~~~

Here is a snippet which cover the basics of using pytlas inside your own program :

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

Creating a skill
----------------

Creating skills is fairly easy. You can look at the `example/skills/` folder but here is a simple explanation of how it works.

Every folder into the `<skills>` folder will be loaded as a python module. So let's say we want to create a new skill called `my_skill`. Go to the directory which contains your other skills and make a new directory `my_skill`. Inside this folder, create a new required `__init__.py` file that will be called when the skill is first imported :

.. code-block:: python

  from pytlas.skill import intent
  from pytlas.localization import translations

  # You can also use relative import if your skill contains multiple files
  # from .subfile import *

  @translations('fr')
  def fr_translations(): return {
    'hello': 'bonjour',
    'bye': 'au revoir',
  }

  @intent('on_some_intent_triggered')
  def my_handler(r):
    r.agent.answer(r._('hello'))

    # Put your logic here

    return r.agent.done() # See examples

And that's all you need to know to create and share your own skills!

Testing
-------

.. code-block:: bash

  $ cd tests/
  $ python -m unittest -v
