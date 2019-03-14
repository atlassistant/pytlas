Metadata
========

Metadata are entirely optional and are mostly use by the tiny skill manager of pytlas to list loaded skills with associated informations.

As a best practice however, you must include it in your skill to provide at least a description of what your skill do and what settings are expected.

.. code-block:: python

  from pytlas import meta, translations

  # Here the function register will be called with a function used to translate
  # a string.
  # If you prefer, you can also returns a `pytlas.skill.Meta` instance.

  @meta()
  def register(_): return {
    'name': _('lights'),
    'description': _('Control some lights'),
    'version': '1.0.0',
    'author': 'Julien LEICHER',
    'settings': ['LIGHTS_SETTING_ONE'],
  }

  @translations('fr')
  def fr_translations(): return {
    'lights': 'lumières',
    'Control some lights': 'Contrôle des lumières',
  }