.. _installation:

Installation
============

There's multiple way to install pytlas. You're free to pick the one that better fit your needs.

.. note::

  Whatever installation you choose, you may need additional setup related to the interpreter you have decided to use. See `Choosing your interpreter`_ below for more information.

  In the following examples, pytlas is installed with the extra require **snips** which is the official interpreter used by pytlas.

.. warning::

  On a Raspberry PI, if you wish to install `snips`, you will have to follow the `instructions here <https://github.com/snipsco/snips-nlu-parsers/tree/develop/python#other-platforms>`_ to install `rust` and `setuptools_rust` before running below commands.

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

In order to understand natural language, pytlas is backed by :ref:`interpreter` which may need additional installation steps.

.. _installation_snips:

snips
~~~~~

The official interpreter use the fantastic `snips-nlu <https://github.com/snipsco/snips-nlu>`_ python library.

Given the language you want your assistant to understand, it will need to download additional resources. Fortunately, you don't have to do it manually since `v5.0.0`, pytlas will automatically try to download them when fitting the interpreter with a language it doesn't know already.
