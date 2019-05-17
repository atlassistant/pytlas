.. pytlas documentation master file, created by
   sphinx-quickstart on Fri Dec  7 12:50:34 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

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

pytlas is an open-source 🤖💬 **python 3** assistant library built for people and made to be super easy to setup and understand.

Its goal is to make easy to **map natural language sentences** to **python function handlers**. It also manages a conversation with the help of a finite state machine.

Ever wanted to develop your own Alexa, Siri or Google Assistant and host it yourself? This is possible!

.. warning::

    **pytlas** being a library, it does not handle speech recognition and synthesis. It only handles text inputs. If you want it to be able to interact with the voice, you must write a :ref:`client` which will call the library internally.

.. toctree::
  :maxdepth: 2
  :caption: Contents

  getting_started/index
  writing_skills/index
  pam/index
  core_components/index

