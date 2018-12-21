.. _context:

Context
=======

Context are important when dealing with complex skills. It allows you to define in which case your intent should be recognized.

In order to declare a context, you just to have to define your intent with `valid_context/your_intent` and use the `request.agent.context` method to switch at runtime. Here is an example.

.. code-block:: python

  from pytlas import training, intent

  @training('en')
  def en_training(): return """
  %[start_intent]
    start something right now
    please start a context
    let's dance

  %[started_intent/say]
    say something
    talk to me
  """

  @intent('start_intent')
  def start_handler(request):
    # This line will switch to the context `started_intent` which means that
    # the interpreter will now be able to recognize the `started_intent/say` intent
    # we define earlier.
    #
    # Till we switch to this context, `started_intent/say` could not be triggered.
    request.agent.context('started_intent')
    
    return request.agent.done()

  @intent('started_intent/say')
  def say(request)
    request.agent.answer('Hey!')

    # Switch to the root context which is the None one so this handler could not be triggered anymore
    request.agent.context(None)

    return request.agent.done()

  # You can also override builtin intents such as __fallback__ and __cancel__ for
  # your context.
  #
  # Here the fallback means every sentence not recognized by the interpreter when
  # in the `started_intent` context will trigger this handler.
  @intent('started_intent/__fallback__')
  def fallback(request):
    request.agent.answer('Looks like you said %s' % request.intent.slot('text').first().value)

    return request.agent.done()