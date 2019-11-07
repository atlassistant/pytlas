.. _training:

Training
========

You should always start by defining example sentences of how a user might
trigger your code. The :ref:`interpreter` will use them to train and extract
meaningful content on unknown inputs.

It allows your skill to define which sentences will trigger specific intents so
you must provide enough data for it to understand patterns.

.. note::

  You should define training data in all languages that you wish to support in your skill.

.. warning::

  At runtime, all trainings will be merged into a single dictionary. So don't forget
  to namespace your intents and entities when that makes sense.

Format
------

It uses a specific **interpreter agnostic format** called `chatl <https://github.com/atlassistant/chatl>`_ that I also maintain. Its goal is to be easy to write and read by humans.

This tiny DSL will be transformed to a format understandable by your
interpreter of choice.

So, going back to our skill, let's define some training data:

.. code-block:: python

  from pytlas import training

  @training('en')
  def my_data(): return """
  %[lights_on]
    turn the @[room]'s lights on would you
    turn lights on in the @[room]
    lights on in @[room] please
    turn on the lights in @[room]
    turn the lights on in @[room]
    enlight me in @[room]

  %[lights_off]
    turn the @[room]'s lights off would you
    turn lights off in the @[room]
    lights off in @[room] please
    turn off the lights in @[room]
    turn the lights off in @[room]

  ~[basement]
    cellar

  @[room](extensible=false)
    living room
    kitchen
    bedroom
    ~[basement]
  """

Where `%[lights_on]` and `%[lights_off]` define intents, `@[room]` is an
entity and `~[basement]` is a synonym.

Builtin intents
---------------

pytlas does not ship with training data at all. There's currently one intent
which needs data: `__cancel__`. You should provide training data to recognize
this intent, something as simple as this:

.. code-block:: python

  from pytlas import training

  @training('en')
  def en_data(): return """
  %[__cancel__]
    cancel
    abandon the command
  """

Best practices
--------------

Here is some thoughts about making great training data:

* Use lowercase
* Avoid punctuation
* Give at least 10 sentences per intent
* Provide variety in your samples (with or without slots defined for example)
* Use optional synonyms (with ~[your synonym?] in intents)
