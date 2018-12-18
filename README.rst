pytlas |travis| |coveralls| |pypi| |rtd| |license|
==================================================

.. |travis| image:: https://travis-ci.org/atlassistant/pytlas.svg?branch=master
    :target: https://travis-ci.org/atlassistant/pytlas

.. |coveralls| image:: https://coveralls.io/repos/github/atlassistant/pytlas/badge.svg?branch=master
    :target: https://coveralls.io/github/atlassistant/pytlas?branch=master

.. |pypi| image:: https://badge.fury.io/py/pytlas.svg
    :target: https://badge.fury.io/py/pytlas

.. |rtd| image:: https://readthedocs.org/projects/pytlas/badge/?version=latest
    :target: https://pytlas.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |license| image:: https://img.shields.io/badge/License-GPL%20v3-blue.svg
    :target: https://www.gnu.org/licenses/gpl-3.0

⚠️ **You're reading the develop README.** For the last published version documentation, `please click here <https://github.com/atlassistant/pytlas/tree/43bda4ea9936c414a77aafdc803144dcbaa50672>`_.

An open-source 🤖💬 python 3 assistant library built for people and made to be super easy to setup and understand.

I first started to develop `atlas <https://github.com/atlassistant/atlas>`_ but I have finally decided to develop a library that everyone could embed in their own program with simple python code.

Documentation
-------------

The documentation is being actively re-written to `https://pytlas.readthedocs.io <https://pytlas.readthedocs.io>`_, that's the next big step before the V3 release!

Creating a skill
~~~~~~~~~~~~~~~~

Skill are reusable piece of code that you can share with others and do the actual job. You can have a skill that fetch weather forecasts, another one that talks with your home connected components, that's entirely up to you!

Skills are self-contained and composed of 3 specific components:

- Training data: examples of how to trigger specific intents from natural language, defined in a tiny Domain Specific Language not tied to a particular NLU engine,
- Translations: simple key/value pair used by your skill for different languages,
- Intent handlers: Python code called when a specific intent has been parsed by `pytlas`

Have a look at the `example/skills` folder to see how it works.

Testing
-------

.. code-block:: bash

  $ pip install -e .[snips,test]
  $ python -m nose --with-doctest -v --with-coverage --cover-package=pytlas
