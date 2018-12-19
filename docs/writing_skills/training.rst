.. _training:

Training
========

Training data allow your skill to define which sentences will trigger specific intents so you must provide enough data for it to understand patterns.

.. note::

  You should define training data in all languages that you wish to support in your skill.

It uses a specific **interpreter agnostic format** called `pychatl <https://github.com/atlassistant/pychatl>`_ that I also maintain. Its goal is to be easy to write and read by humans.

This tiny DSL will be transformed to a format understandable by your interpreter of choice.

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

Where `%[lights_on]` and `%[lights_off]` define intents, `@[room]` is an entity and `~[basement]` is a synonym.