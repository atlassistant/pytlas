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

An open-source 🤖💬 python 3 assistant library built for people and made to be super easy to setup and understand.

I first started to develop `atlas <https://github.com/atlassistant/atlas>`_ but I have finally decided to develop a library that everyone could embed in their own program with simple python code.

Want to get your feet wet? Have a look at the `example/skills` folder to see how it works!

Documentation
-------------

The documentation is hosted on readthedocs here `https://pytlas.readthedocs.io <https://pytlas.readthedocs.io>`_. It still needs some improvement so don't hesitate to help me!

Testing
-------

.. code-block:: bash

  $ pip install -e .[snips,test]
  $ python -m nose --with-doctest -v --with-coverage --cover-package=pytlas
