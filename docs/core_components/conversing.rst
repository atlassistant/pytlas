Conversing
==========

The conversing domain use the :ref:`understanding` and :ref:`handling` domains
to trigger python actions from parsed intents and maintain a conversation
state.

.. _agents:

Agent
-----

An agent represent the interface between the user and loaded skills. It
maintain the conversation state and use an underlying interpreter to understand
the user.

The agent is the entry point which will take raw user inputs with its `parse`
method and call loaded handlers as needed.

Entry point
~~~~~~~~~~~

.. automethod:: pytlas.conversing.Agent.parse

.. note::

  More information on :ref:`meta`.

When an intent has been found, it will try to find an handler for this specific
intent and call it. It will then manage the conversation, handle cancel and
fallback intents and communicate back to the user using its internal
:ref:`client`.

From a skill
~~~~~~~~~~~~

From a skill perspective, here are the method you will use.

.. automethod:: pytlas.conversing.Agent.answer
.. automethod:: pytlas.conversing.Agent.ask
.. automethod:: pytlas.conversing.Agent.done
.. automethod:: pytlas.conversing.Agent.context

.. _client:

Client
------

A client is a thin layer used by an agent to communicate with the user. It can
be anything such as a tiny CLI (as the one provided), a WebSocket server or a
connected speaker.

When provided to an agent (using its `model` property), some specific members
will be called by the agent on specific lifecycle events:

.. py:function:: on_answer(text, cards, raw_text, **meta)

  Called when the skill answer something to the user. *cards* is a list of `pytlas.Card` which represents informations that should be presented to the user if possible. Your client should always handle the `text` property at least.

.. py:function:: on_ask(slot, text, choices, raw_text, **meta)

  Called when the skill need some user inputs for the given *slot*. *choices* if set, represents a list of available choices.

.. py:function:: on_thinking()

  Called when the agent has called a skill which is handling the request.

.. py:function:: on_done(require_input)

  Called when a skill has done its work and the agent is going back to the asleep state.

.. py:function:: on_context(context_name)

  Called when the agent context has changed.
