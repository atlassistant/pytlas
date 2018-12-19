.. _meta:

Meta
====

When working with **pytlas**, you may find metadata in different places.

Especialy in:

- The agent `__init__`, `answer`, `ask` and `parse` methods,
- The `Intent` class

Those metadata represents any non consumed keyword parameters. They are pretty useful when you need to provide additional information but should never be considered mandatory.

Here is a code example for a skill:

.. code-block:: python

  from pytlas import intent

  @intent('get_weather')
  def on_weather(r):
    lat = r.intent.meta.get('latitude')
    lng = r.intent.meta.get('longitude')

    if lat and lng:
      # Search using the user position
    else:
      name = r.intent.slot('city').first().value

      if not name:
        return r.agent.ask('city', 'For which city?')

      # Search using a city name
    
    return r.agent.done()

With this definition, if I call the `parse` method with some meta, it will handle my position, else, it will fallback to search the weather for a city:

.. code-block:: python
  
  from pytlas import Agent

  agent = Agent() # In the real world, you should provide an interpreter and a client

  # Meta here will be added to the parsed intent
  agent.parse("What's the weather like", latitude=49, longitude=1)

  # Will fallback to the city one
  agent.parse("What's the weather like in Paris")