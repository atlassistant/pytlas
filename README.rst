pytlas |travis| |cover| |pypi| |rtd| |license|
==============================================

.. |travis| image:: https://travis-ci.org/atlassistant/pytlas.svg?branch=master
    :target: https://travis-ci.org/atlassistant/pytlas

.. |cover| image:: https://codecov.io/gh/atlassistant/pytlas/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/atlassistant/pytlas

.. |pypi| image:: https://badge.fury.io/py/pytlas.svg
    :target: https://badge.fury.io/py/pytlas

.. |rtd| image:: https://readthedocs.org/projects/pytlas/badge/?version=latest
    :target: https://pytlas.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |license| image:: https://img.shields.io/badge/License-GPL%20v3-blue.svg
    :target: https://www.gnu.org/licenses/gpl-3.0

An open-source 🤖💬 Python 3 assistant library built for people and made to be super easy to setup and understand.

**pytlas** translates natural language sentence into python skills you can easily define yourself. It makes it really easy to develop your own Google Assistant, Alexa or whatever but runs on **your device** with **your trusted code** and **no connection** to obscure servers.

🌊 Want to get your feet wet? Have a look at the `example/skills` folder to see how it works!

📚 Want to go further and develop your own skill? Let's visit the `latest documentation <https://pytlas.readthedocs.io>`_ and share your work!

Quick start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

  $ pip install pytlas[snips] # Gets the latest release from pypi
  $ git clone https://github.com/atlassistant/pytlas && cd pytlas && pip install -e .[snips] # or directly from source

Testing
~~~~~~~

*When `pytest` is also installed, it may cause some tests to fail, so make sure it is not installed with `pip uninstall -y pytest` or use venv*

.. code-block:: bash

  $ git clone https://github.com/atlassistant/pytlas && cd pytlas
  $ pip install -e .[snips,test]
  $ python -m nose --with-doctest --with-coverage --cover-package=pytlas

Linting
~~~~~~~

.. code-block:: bash

  $ pylint pytlas setup.py # in the root directory

Contributing
------------

Contributions are **welcome**! **pytlas** is being developed my spare time so every help is greatly appreciated to push this project further.

I have ideas!
~~~~~~~~~~~~~

Don't hesitate to submit them in the repo and we'll see what can be done.

I have skills & time!
~~~~~~~~~~~~~~~~~~~~~

Great, have a look at `the github project page <https://github.com/atlassistant/pytlas/projects/1>`_ to see the big plans for upcoming releases or fix unresolved issues to start.

I have money!
~~~~~~~~~~~~~

.. |liberapay| image:: https://liberapay.com/assets/widgets/donate.svg
    :target: https://liberapay.com/YuukanOO/donate

If you want to donate to help me find more time to work on **pytlas** and similar projects, you can support me on liberapay |liberapay|, thanks ❤️!
