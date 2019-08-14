Stores
======

All data in pytlas are registered on `Store` classes which provides useful getters and setters. They are used everywhere when needing training data, translations, handlers and so on.

For each stores, there's a global property in the associated file used by decorators by default. It enables skills to register themselves to global stores on the running environment.

Here is the list of actual stores used in pytlas:

.. autoclass:: pytlas.skill.MetasStore
  :members:

.. autoclass:: pytlas.skill.HandlersStore
  :members:

.. autoclass:: pytlas.training.TrainingsStore
  :members:

.. autoclass:: pytlas.localization.TranslationsStore
  :members:

.. autoclass:: pytlas.settings.SettingsStore
  :members: