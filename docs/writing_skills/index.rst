.. _skills:

Writing skills
==============

Writing a skill for **pytlas** is as easy as creating a python module, writing some code that use `pytlas` members and putting it in the skills directory of your instance.

There's only two parts that your skill should always define to make it work, :ref:`training` and :ref:`handler`.

.. note::

  For the rest of this section, I assumed you have created a new folder (that's your skill name) in your instance skills directory (`skills/` subdirectory by default) and created an `__init__.py` file inside it that makes this folder an importable python module.

.. toctree::
  :maxdepth: 2
  :caption: Contents

  training
  handler
  translations
  metadata
  settings