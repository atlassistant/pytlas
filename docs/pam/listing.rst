Listing skills
==============

Those methods will list all currently loaded skills with informations taken from the `@meta()` decorator in skills definitions when it founds them.

From CLI
--------

.. code-block:: bash

  $ pytlas skills list

From code
---------

.. code-block:: python

  from pytlas.supporting import get_loaded_skills

  # Will returns an array of `pytlas.skill.Meta`
  skills = get_loaded_skills('en')
