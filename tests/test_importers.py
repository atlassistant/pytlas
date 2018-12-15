from sure import expect
from pytlas.importers import should_load_resources, import_skills
import pytlas.settings as settings

class TestImporters:

  def test_it_should_allow_load_resources_when_empty(self):
    settings.set(settings.SETTING_LANG, [])
    expect(should_load_resources('fr')).to.be.true

  def test_it_should_allow_load_resources(self):
    settings.set(settings.SETTING_LANG, ['en', 'it'])

    expect(should_load_resources('en')).to.be.true
    expect(should_load_resources('it')).to.be.true
    expect(should_load_resources('fr')).to.be.false

  def test_it_should_not_raise_error_when_skills_folder_does_not_exist(self):
    import_skills('/does/not/exists')
