.. _testing:

Testing your skill
==================

Once you have developed your skill, you should test it. You can launch the
pytlas repl and test it manually or (the prefered approach) use some code to
trigger agent state and make assertions about how your skill has answered.

In order to help you do the later approach, there's some utilities in the
`pytlas` package itself.

Let's consider this tiny skill:

.. code-block:: python

  from pytlas import training, intent

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

  @intent('lights_on')
  def on_lights_on(r):
    rooms = req.intent.slot('room')

    if not rooms:
      return req.agent.ask('room', 'For which rooms?')

    req.agent.answer('Turning lights on in %s' % ', '.join(room.value for room in rooms))

    return req.agent.done()

Writing tests
-------------

In order to make assertions, pytlas use the excellent `sure <https://github.com/gabrielfalcao/sure>`_ library so let's use them here too.

Now, let's create a file `test_lights.py` next to your skill python file.

.. warning::

  Since `create_skill_agent` uses the `SnipsInterpreter`, you must have `snips-nlu` installed and language resources too. See :ref:`installation_snips` for more informations.

.. code-block:: python

  from sure import expect
  from pytlas.testing import create_skill_agent
  import os

  # Let's instantiate an agent specifically designed to make assertions easier.
  # It will fit the data with the SnipsInterpreter so you have pretty much what
  # will be used in a real case scenario.
  agent = create_skill_agent(os.path.dirname(__file__))

  class TestLights:

    def setup(self):
      # Between each tests, resets the model mock so calls are dismissed and we
      # start on a fresh state.
      agent.model.reset()

    def test_it_should_answer_directly_when_room_is_given(self):
      agent.parse('Turn the lights on in the kitchen please')

      # Retrieve the last call on on_answer (you can also give an integer if you have multiple calls in your skill).
      # Here `agent.model.on_answer` is a `pytlas.testing.ModelMock` with some utilities to make assertions.
      on_answer = agent.model.on_answer.get_call()

      # And make assertions on argument names
      expect(on_answer.text).to.equal('Turning lights on in kitchen')

    def test_it_should_ask_for_room_when_no_one_is_given(self):
      agent.parse('Turn the lights on')

      on_ask = agent.model.on_ask.get_call()

      expect(on_ask.slot).to.equal('room')
      expect(on_ask.text).to.equal('For which rooms?')

      agent.parse('In the bedroom')

      on_answer = agent.model.on_answer.get_call()

      expect(on_answer.text).to.equal('Turning lights on in bedroom')

      # Since it inherits from `MagicMock`, you can use all methods to make assertions
      agent.model.on_done.assert_called()

Launching tests
---------------

In order to launch tests, pytlas uses `nose <https://nose.readthedocs.io/en/latest/>`_, so you may use it to test your skill too.

In your skill directory, just launch the following command:

.. code-block:: bash

  $ python -m nose
  ..
  ----------------------------------------------------------------------
  Ran 2 tests in 0.016s

  OK
