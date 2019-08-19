.. _handling:

Handling
========

The handling domain enables skills to register their data such as **meta**, **handlers** and **translations**.

This is where you, as a developer, will spend most your time, see :ref:`skills` for more info.

Basically, it's just a python module which uses `pytlas` decorators to register some specific components on the running environment.

Handlers store
--------------

Handlers are register on an instance of an `HandlersStore`, mostly using the `intent` decorator.

.. autoclass:: pytlas.handling.HandlersStore
  :members:

Metas store
-----------

Skill meta are registered on a `MetasStore`, mostly using the `meta` decorator.

.. autoclass:: pytlas.handling.MetasStore
  :members:

Translations store
------------------

Translations are registered on a `TranslationsStore` instance, mostly using the `translations` decorator.

.. autoclass:: pytlas.handling.TranslationsStore
  :members: