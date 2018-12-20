.. _handler:

Handler
=======

Handlers are python code that will be executed when an intent has been recognized.

Your handler will received one and only arguments, a :ref:`request` instance which represents the agent and the context for which your handler is being called.

Getting started
---------------

.. note::

  The agent in the :ref:`request` is a proxy which maps to an :ref:`agents`.

Here the basic code you need to have. Calling `request.agent.done` is mandatory to inform the agent that it should returns to its asleep state.

.. code-block:: python

  from pytlas import intent

  # Remember we have defined this handler in the training section with %[lights_on]

  @intent('lights_on')
  def my_handler(request):
    return request.agent.done()

Retrieving slots
----------------

Remember, slots are like function arguments that has been extracted by the interpreter.

.. code-block:: python

  from pytlas import intent

  # Remember we have defined a slot @[room] in training sentences

  @intent('lights_on')
  def my_handler(request):
    rooms = request.intent.slot('room')

    # When you retrieve a slot, it's always a list since you can have multiple occurences of an entity in the same sentence

    first = rooms.first()
    last = rooms.last()

    # first and last are SlotValue object, if you want to retrieve their value you should use the `value` property

    return request.agent.done()

Answering
---------

When you need to show something to the user, you should use the `answer` method.

.. code-block:: python

  from pytlas import intent

  @intent('lights_on')
  def my_handler(request):
    room = request.intent.slot('room').first().value

    # Turn the lights on !

    # And say it to the user

    request.agent.answer('Turning lights on in %s' % room)

    return request.agent.done()

Asking
------

When you need some informations or slot have not been extracted in the original sentence, you can ask the user to fill them.

.. code-block:: python

  from pytlas import intent

  @intent('lights_on')
  def my_handler(request):
    room = request.intent.slot('room')

    if not room:
      # Here we ask the user to fill the 'room' slot. That's the only case when you don't
      # need to call done yourself.
      return request.agent.ask('room', 'Which room?')

    request.agent.answer('Turning lights on in %s' % room)

    return request.agent.done()
