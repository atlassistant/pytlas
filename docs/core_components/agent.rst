Agent
=====

An agent represent the interface between the user and loaded skills. It maintain the conversation state and use an underlying interpreter to understand the user.

The agent is the entry point which will take raw user inputs with its `parse` method.

.. py:function:: parse(msg, **meta)

   This method will use the agent :ref:`interpreter` to extract intents and slots from the raw message given by the user.

.. note::

  More information on :ref:`meta`.

When an intent has been found, it will try to find an handler for this specific intent and call it. It will then manage the conversation, handle cancel and fallback intents and communicate back to the user using its internal :ref:`client`.