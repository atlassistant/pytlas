Migrating
=========

Sometimes, things should be broken for the well being of the library. This is
where you will find such changes to help you update your code accordingly.

From 4.* to 5.0.0
-----------------

Version 5.0.0 is a big overhaul of how things are layed out in the library and
as such introduce a lot of breaking changes if you use the library directly.

If all you do is `from pytlas import training, translations, intent, meta`,
then you're good to go, nothing has changed, otherwise, keep reading.

The new structure follow a more domain centric approach:

- **understanding**: Contains interpreters, intent, slots and training stuff
- **handling**: Contains handlers, localization, importers and related stuff
- **conversing**: Contains agent and request
- **supporting**: Contains the skills manager
- **testing**: Contains tests related stuff

The **pytlas** root module now only exposes the most common stuff to make more
easy for newcomers to use the library. Each submodules also has a public
api represented by the `__init__.py` file.

Access to settings
~~~~~~~~~~~~~~~~~~

.. code-block:: python

  # WAS
  from pytlas.settings import get, getbool # And other getters

  # NOW
  from pytlas.settings import CONFIG # Represents the global configuration
  
  # And access it like this
  # CONFIG.get CONFIG.getbool

  # From a skill, you can now use the agent settings which inherits from the global
  # configuration and override keys with the agent metadata.
  @intent('my-skill')
  def my_skill(request):
    request.agent.settings.get('api', section='openweather')

Registering without decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since the prefered approach is to use the decorators, direct register are not
exposed in the main `__init__.py` and should be imported only when needed.

.. code-block:: python

  # WAS
  from pytlas.skill import register as register_intent, register_metadata
  from pytlas.localization  import register as register_translations
  from pytlas.training import register as register_training
  from pytlas.hooks import register as register_hook
  # DOES NOT EXIST ANYMORE, use NOW imports
  from pytlas import register_intent, register_metadata, register_translations, register_training, register_hook

  # NOW
  from pytlas.handling.skill import GLOBAL_HANDLERS, GLOBAL_METAS
  from pytlas.handling.hooks import GLOBAL_HOOKS
  from pytlas.handling.localization import GLOBAL_TRANSLATIONS
  from pytlas.understanding.training import GLOBAL_TRAININGS

  # And use the `register` method on those global stores (ie. GLOBAL_HANDLERS.register)

Utils
~~~~~

Utilities methods have been splitted by functions:

- `pytlas.datautils`: Data related helpers
- `pytlas.ioutils`: Input/output helpers
- `pytlas.pkgutils`: Package related helpers

and `read_file` as been updated:

.. code-block:: python

  # WAS
  from pytlas.utils import read_file
  read_file('data.dsl', relative_to_file=__file__)

  # NOW
  from pytlas.ioutils import read_file
  # relative_to_file is now relative_to and accept a folder too
  read_file('data.dsl', relative_to=__file__)

Testing
~~~~~~~

`ModelMock.get_call()` now returns the last call by default.

Managing skills from code
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

  # WAS
  from pytlas.pam import get_loaded_skills, install_skills, update_skills, uninstall_skills

  # NOW
  from pytlas.supporting import SkillsManager

  s = SkillsManager('your_skills_directory')
  loaded_skills = s.get()
  s.install('atlassistant/pytlas-weather', 'another/skill')
  s.update('atlassistant/pytlas-weather', 'another/skill')
  s.uninstall('atlassistant/pytlas-weather', 'another/skill')
