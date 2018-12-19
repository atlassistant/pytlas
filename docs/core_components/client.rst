.. _client:

Client
======

A client is a thin layer used by an agent to communicate with the user. It can be anything such as a tiny CLI (as the one provided), a WebSocket server or a connected speaker.

When provided to an agent, some specific members will be called by the agent on specific lifecycle events:

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