.. _hooks:

Hooks
=====

Hooks represents lifecycle events your skill can listen to. At the moment, only 2 hooks are available as decorators.

.. code-block:: python

  from pytlas import on_agent_created, on_agent_destroyed

  @on_agent_created()
  def do_some_setup_for(agent):
    # It will be called on agent startup so you have a change to do some
    # stuff in your skill.
    print (agent.meta)

  @on_agent_destroyed()
  def do_some_cleanup_for(agent):
    # It will be called upon agent destruction.
    print ('Some cleanup stuff could go here!')
