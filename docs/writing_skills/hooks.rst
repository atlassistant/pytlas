.. _hooks:

Hooks
=====

Hooks represents lifecycle events your skill can listen to. At the moment, only 2 hooks are available:

.. py:function:: on_agent_created(agent)

  This hook will be called when an agent is first created. It enables you to make additional setup stuff on your skill part. It will receive one argument which is the created agent.

.. py:function:: on_agent_destroyed(agent)

  This hook will be called when an agent is destroyed. It will receive one argument which is the destroyed agent.