.. _handler:

Handler
=======

Handlers are python code that will be executed when an intent has been
recognized.

Your handler will received one and only arguments, a :ref:`request` instance
which represents the agent and the context for which your handler is being
called.

Getting started
---------------

.. note::

  The agent in the :ref:`request` is a proxy which maps to an :ref:`agents` so you have access to everything it exposes. Why a proxy you may ask? Because when the action is cancelled by the user, the request is invalidated so any call through the proxy will be dismissed.

Here the basic code you need to have. Calling `request.agent.done` is mandatory
to inform the agent that it should returns to its asleep state.

.. code-block:: python

  from pytlas import intent

  # Remember we have defined this handler in the training section with %[lights_on]

  @intent('lights_on')
  def my_handler(request):
    return request.agent.done()

.. _retrieving_slots:

Retrieving slots
----------------

Remember, slots are like function arguments that has been extracted by the
:ref:`interpreter`.

.. note::

  In a slot, the `value` property will give you back a representation of what have been parsed by the NLU engine in a meaningful way:

    - for durations, it will returns a `dateutil.relativedelta` object
    - for moneys and temperatures, it returns a `pytlas.understanding.UnitValue`
    - for percentages, a float between 0 and 1
    - for exact time, a `datetime.datetime` object,
    - for time ranges, a tuple of `datetime.datetime` objects representing the lower and upper bounds
    - for anything else, a string

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

When you need to show something to the user, you should use the `answer`
method.

.. code-block:: python

  from pytlas import intent

  @intent('lights_on')
  def my_handler(request):
    room = request.intent.slot('room').first().value

    # Turn the lights on !

    # And say it to the user

    request.agent.answer('Turning lights on in %s' % room)
    
    # You can also give the text parameter an array of strings.
    # If you do so, pytlas will choose one item randomly. This make it easy
    # to provide some variations for your skill handler.
    # request.agent.answer(['Turning lights on in %s' % room, 'Alright, lights on in %s' % room])

    return request.agent.done()

Asking
------

When you need some informations or slot have not been extracted in the original
sentence, you can ask the user to fill them. Once filled by the user, your
handler will be called again with the updated slots.

.. code-block:: python

  from pytlas import intent

  @intent('lights_on')
  def my_handler(request):
    room = request.intent.slot('room')

    if not room:
      # Here we ask the user to fill the 'room' slot. That's the only case when you don't
      # need to call done yourself.
      # Like in the answer text argument, the ask text argument also accept an array of strings and
      # pytlas will choose one randomly to provide to the user.
      return request.agent.ask('room', 'Which room?')

    request.agent.answer('Turning lights on in %s' % room)

    return request.agent.done()

Builtin intents
---------------

For now, there's only one builtin intent that you want to handle which is
`__fallback__`. It will be called if an intent has been recognized but no handler
have been found to fulfill the request.
