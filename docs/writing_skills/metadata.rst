Metadata
========

Metadata are entirely optional and are mostly use by the tiny skill manager of pytlas.

It gives some additional informations about a skill.

.. code-block:: python

  from pytlas import meta, translations

  # Here the function register will be called with a function used to translate
  # a string.

  @meta()
  def register(_): return {
    'name': _('lights'),
    'description': _('Control some lights'),
    'version': '1.0.0',
    'author': 'Julien LEICHER',
  }

  @translations('fr')
  def fr_translations(): return {
    'lights': 'lumières',
    'Control some lights': 'Contrôle des lumières',
  }