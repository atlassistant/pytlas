Translations
============

Translating a skill is pretty easy. It works the same as training data. You'll just have to use the decorator on a method which returns a dictionary representing keys and associated translations.

.. code-block:: python

  from pytlas import translations, intent

  @translations('fr')
  def my_translations(): return {
    'Turning lights on in %s': "J'allume les lumières dans %s",
  }

  # Training data are not shown here

  @intent('lights_on')
  def my_handler(request):
    room = request.intent.slot('room').first().value

    # Do something

    # Here, just use the `request._` to translate the string
    # If you wish to localize a date, we got you covered with the `request._d`

    request.agent.answer(request._('Turning lights on in %s') % room)

    return request.agent.done()