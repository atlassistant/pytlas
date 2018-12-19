Agent
=====

An agent represent the interface between the user and loaded skills. It maintain the conversation state and use an underlying interpreter to understand the user.

The agent is the entry point which will take raw user inputs with its `parse` method.

Entry point
-----------

.. py:function:: parse(msg, **meta)

   This method will use the agent :ref:`interpreter` to extract intents and slots from the raw message given by the user.

.. note::

  More information on :ref:`meta`.

When an intent has been found, it will try to find an handler for this specific intent and call it. It will then manage the conversation, handle cancel and fallback intents and communicate back to the user using its internal :ref:`client`.

From a skill
------------

From a skill perspective, here are the method you will use.

.. py:function:: answer(text, cards=None, **meta)

  Answer something to the user.

.. py:function:: ask(slot, text, choices=None, **meta)

  Ask for a slot value to the user.

.. py:function:: done(require_input=False)

  Inform the agent that a skill has done its work and it should returns in its asleep state.

.. py:function:: context(context_name)

  Change the current :ref:`context`.