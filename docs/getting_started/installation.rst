Installation
============

There's multiple way to install pytlas. You're free to pick the one that better fit your needs.

.. note::

  Whatever installation you choose, you may need additional setup related to the interpreter you have decided to use. See `Choosing your interpreter`_ below for more information.

  In the following examples, pytlas is installed with the extra require **snips** which is the official interpreter used by pytlas.

From pypi
---------

.. code:: bash

  $ pip install pytlas[snips]

.. note::

  The `[snips]` mention here represents an extra require and will download `snips_nlu` for you.

From source
-----------

.. code:: bash

  $ git clone https://github.com/atlassistant/pytlas.git
  $ cd pytlas
  $ pip install -e .[snips]

Choosing your interpreter
-------------------------

in order to understand natural language, pytlas is backed by **interpreters** which may need additional installation steps.

snips
~~~~~

The official interpreter supported use the fantastic `snips-nlu <https://github.com/snipsco/snips-nlu>`_ python library.

.. warning::

  On a Raspberry PI, you may have trouble getting `snips-nlu` to install correctly. A more complete docs will come soon for this particular case.

Given the language you want your assistant to understand, you may need to `download additional resources <https://github.com/snipsco/snips-nlu#language-resources>`_ using the following command:

.. code:: bash

  $ snips-nlu download en

to download only needed english resources or:

.. code:: bash

  $ snips-nlu download-all-languages

to download all language resources.