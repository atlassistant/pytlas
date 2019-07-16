from sure import expect
from pytlas.importers import should_load_resources, import_skills
from pytlas.settings import config, SETTING_ALLOWED_LANGUAGES

class TestImporters:

  def teardown(self):
    # Restore the global loading settings
    config.set(SETTING_ALLOWED_LANGUAGES, [])

  def test_it_should_allow_load_resources_when_empty(self):
    config.set(SETTING_ALLOWED_LANGUAGES, [])
    expect(should_load_resources('fr')).to.be.true

  def test_it_should_allow_load_resources(self):
    config.set(SETTING_ALLOWED_LANGUAGES, ['en', 'it'])

    expect(should_load_resources('en')).to.be.true
    expect(should_load_resources('it')).to.be.true
    expect(should_load_resources('fr')).to.be.false

  def test_it_should_not_raise_error_when_skills_folder_does_not_exist(self):
    import_skills('/does/not/exists')
