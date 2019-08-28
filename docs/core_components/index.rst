Core components
===============

In order to develop for pytlas, you should understand how core components fit
together to make it understand and call your handlers. If you only want to
develop your own skills, you can omit this section and go to :ref:`skills`.

The general command flow looks like this:

- The user says **will it rain tomorrow**,
- The user **agent** uses its internal **interpreter** to extract the user intent and slots based on its training data,
- The **agent** call the **skill** handler registered for this specific intent if any,
- The **skill** has now the opportunity to answer or ask something to the user in order to fulfil his request and the agent will use the attached **client** to communicate back with the user.

.. toctree::
  :maxdepth: 2
  :caption: Going deeper

  understanding
  handling
  conversing
  settings
  meta
