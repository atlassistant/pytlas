import os
from sure import expect
from unittest.mock import patch
from pytlas.handling.importers import import_skills, import_or_reload


class TestImporters:

    def test_it_should_not_raise_error_when_skills_folder_does_not_exist(self):
        import_skills('/does/not/exists')

    def test_it_should_not_explode_when_importing_a_module_with_errors(self):
        import_or_reload('a_non_existant_module')

    def test_it_should_import_skills_in_a_directory_correctly(self):
        with patch('pytlas.training') as train_mock:
            with patch('pytlas.intent') as intent_mock:
                import_skills(os.path.join(os.path.dirname(__file__), '../__skills'))

                expect(train_mock.call_count).to.equal(2)
                expect(intent_mock.call_count).to.equal(2)
