Managing skills
===============

The pytlas `SkillsManager` class make it easy to add, update and remove skills to and from your pytlas skills directory.

.. note::

  Since it uses `git` internally to manage skills retrieval and updates, the command should be available in your environment when executing all commands listed below.

Using the CLI
-------------

Listing
~~~~~~~

List all loaded skills metadata and tries to translate them.

.. code-block:: bash

  $ pytlas skills list

Installing
~~~~~~~~~~

Install one or more skills from a git repository. If you use a relative name such as `owner/repo`, it will be resolved as `https://github.com/owner/repo` but you can use an absolute URL such as `https://gitlab.com/owner/repo`.

.. code-block:: bash

  $ pytlas skills add atlassistant/pytlas-weather atlassistant/pytlas-help

Updating
~~~~~~~~

Updates one, more, or all skills.

.. code-block:: bash

  $ pytlas skills update atlassistant/pytlas-weather atlassistant/pytlas-help
  $ pytlas skills update # Will try to update all skills in the skills directory

Removing
~~~~~~~~

Remove one or more skills.

.. code-block:: bash

  $ pytlas skills remove atlassistant/pytlas-weather atlassistant/pytlas-help

Using the SkillsManager class
-----------------------------

.. autoclass:: pytlas.supporting.SkillsManager
  :members: