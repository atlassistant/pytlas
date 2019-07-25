.. _skills:

Writing skills
==============

Writing a skill for **pytlas** is as easy as creating a python module, writing some code that use `pytlas` members and putting it in the skills directory of your instance (when :ref:`using_repl`).

There's only two parts that your skill should always define to make it work, :ref:`training` and :ref:`handler`.

.. note::

  For the rest of this section, I assumed the following directory structure:

    .. code-block:: bash

      - skills/
        - your_awesome_skill/
          - __init__.py

  and we're going to work directly in the `__init__.py` file.

.. toctree::
  :maxdepth: 2
  :caption: Contents

  training
  handler
  testing
  translations
  metadata
  request
  hooks
  settings
  context