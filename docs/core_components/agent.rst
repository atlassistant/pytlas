.. _agents:

Agent
=====

An agent represent the interface between the user and loaded skills. It maintain the conversation state and use an underlying interpreter to understand the user.

The agent is the entry point which will take raw user inputs with its `parse` method and call loaded handlers as needed.

Entry point
-----------

.. automethod:: pytlas.agent.Agent.parse

.. note::

  More information on :ref:`meta`.

When an intent has been found, it will try to find an handler for this specific intent and call it. It will then manage the conversation, handle cancel and fallback intents and communicate back to the user using its internal :ref:`client`.

From a skill
------------

From a skill perspective, here are the method you will use.

.. automethod:: pytlas.agent.Agent.answer
.. automethod:: pytlas.agent.Agent.ask
.. automethod:: pytlas.agent.Agent.done
.. automethod:: pytlas.agent.Agent.context
