from sure import expect
from pytlas.handling.importers import import_skills

class TestImporters:

  def test_it_should_not_raise_error_when_skills_folder_does_not_exist(self):
    import_skills('/does/not/exists')
