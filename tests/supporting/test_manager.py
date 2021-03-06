import os
import subprocess
from unittest.mock import patch, call, mock_open
from sure import expect
from pytlas.__about__ import __version__, __title__
from pytlas.supporting import SkillsManager
from pytlas.handling import HandlersStore, MetasStore, Meta, TranslationsStore


class TestSkillsManager:

    def test_it_should_list_currently_loaded_skills_without_meta(self):
        def an_handler():
            pass

        h = HandlersStore()
        h.register('intent1', an_handler, package='skm_skill')
        m = MetasStore()

        s = SkillsManager('skills', handlers_store=h, metas_store=m)
        metas = s.get()
        expect(metas).to.have.length_of(1)

        meta = metas[0]
        expect(meta).to.be.a(Meta)
        expect(meta.name).to.equal('skm_skill')
        expect(meta.version).to.equal('?.?.?')
        expect(meta.package).to.equal('skm_skill')

    def test_it_should_list_currently_loaded_skills_with_meta(self):
        def an_handler():
            pass

        h = HandlersStore()
        h.register('intent1', an_handler, package='skm_skill')
        m = MetasStore()
        m.register(lambda _: {
            'name': _('Support skill'),
            'version': '1.0.0',
        }, package='skm_skill')

        s = SkillsManager('skills', handlers_store=h, metas_store=m)
        metas = s.get()
        expect(metas).to.have.length_of(1)

        meta = metas[0]
        expect(meta).to.be.a(Meta)
        expect(meta.name).to.equal('Support skill')
        expect(meta.version).to.equal('1.0.0')
        expect(meta.package).to.equal('skm_skill')

    def test_it_should_list_currently_loaded_skills_with_meta_and_localize(self):
        def an_handler():
            pass

        h = HandlersStore()
        h.register('intent1', an_handler, package='skm_skill')
        t = TranslationsStore()
        t.register('fr', lambda: {
            'Support skill': 'Fonctions de support',
        }, package='skm_skill')
        m = MetasStore(translations_store=t)
        m.register(lambda _: {
            'name': _('Support skill'),
            'version': '1.0.0',
        }, package='skm_skill')

        s = SkillsManager('skills', lang='fr', handlers_store=h, metas_store=m)
        metas = s.get()
        expect(metas).to.have.length_of(1)

        meta = metas[0]
        expect(meta).to.be.a(Meta)
        expect(meta.name).to.equal('Fonctions de support')
        expect(meta.version).to.equal('1.0.0')
        expect(meta.package).to.equal('skm_skill')

    def test_it_should_uninstall_skills_correctly(self):
        s = SkillsManager('skills')
        p = os.path.abspath('skills')

        with patch('os.path.isdir', return_value=True):
            with patch('pytlas.supporting.manager.rmtree') as rmtree_mock:
                succeeded, failed = s.uninstall(
                    'a/skill', 'another__one', 'https://github.com/a/third')

                expect(succeeded).to.equal(
                    ['a/skill', 'another/one', 'a/third'])
                expect(failed).to.be.empty

                expect(rmtree_mock.call_count).to.equal(3)
                rmtree_mock.assert_has_calls([
                    call(os.path.join(p, 'a__skill')),
                    call(os.path.join(p, 'another__one')),
                    call(os.path.join(p, 'a__third')),
                ])

    def test_it_should_complain_when_removing_a_skill_that_is_not_installed(self):
        s = SkillsManager('skills')

        with patch('os.path.isdir', return_value=False):
            succeeded, failed = s.uninstall(
                'a/skill', 'another__one', 'https://github.com/a/third')

            expect(failed).to.equal(['a/skill', 'another/one', 'a/third'])
            expect(succeeded).to.be.empty

    def test_it_should_complain_when_an_error_occured_when_removing_a_skill(self):
        s = SkillsManager('skills')
        p = os.path.abspath('skills')

        with patch('os.path.isdir', return_value=True):
            with patch('pytlas.supporting.manager.rmtree') as rmtree_mock:
                rmtree_mock.side_effect = Exception('An error!')

                succeeded, failed = s.uninstall(
                    'a/skill', 'another__one', 'https://github.com/a/third')

                expect(failed).to.equal(['a/skill', 'another/one', 'a/third'])
                expect(succeeded).to.be.empty

                expect(rmtree_mock.call_count).to.equal(3)
                rmtree_mock.assert_has_calls([
                    call(os.path.join(p, 'a__skill')),
                    call(os.path.join(p, 'another__one')),
                    call(os.path.join(p, 'a__third')),
                ])

    def test_it_should_update_skills_correctly(self):
        s = SkillsManager('skills')
        p = os.path.abspath('skills')

        with patch('os.path.isdir', return_value=True):
            with patch('os.path.isfile', return_value=False):
                with patch('subprocess.check_output') as sub_mock:
                    succeeded, failed = s.update(
                        'a/skill', 'another__one', 'https://github.com/a/third')

                    expect(succeeded).to.equal(
                        ['a/skill', 'another/one', 'a/third'])
                    expect(failed).to.be.empty

                    expect(sub_mock.call_count).to.equal(3)
                    sub_mock.assert_has_calls([
                        call(['git', 'pull'], cwd=os.path.join(
                            p, 'a__skill'), stderr=subprocess.STDOUT),
                        call(['git', 'pull'], cwd=os.path.join(
                            p, 'another__one'), stderr=subprocess.STDOUT),
                        call(['git', 'pull'], cwd=os.path.join(
                            p, 'a__third'), stderr=subprocess.STDOUT),
                    ])

    def test_it_should_install_dependencies_when_updating(self):
        s = SkillsManager('skills')
        p = os.path.abspath('skills')

        with patch('os.path.isdir', return_value=True):
            with patch('os.path.isfile', return_value=True):
                with patch('builtins.open', mock_open(read_data='')):
                    with patch('subprocess.check_output') as sub_mock:
                        succeeded, failed = s.update('my/skill')

                        expect(succeeded).to.equal(['my/skill'])
                        expect(failed).to.be.empty

                        expect(sub_mock.call_count).to.equal(2)
                        sub_mock.assert_has_calls([
                            call(['git', 'pull'], cwd=os.path.join(
                                p, 'my__skill'), stderr=subprocess.STDOUT),
                            call(['pip', 'install', '-r', 'requirements.txt'],
                                cwd=os.path.join(p, 'my__skill'), stderr=subprocess.STDOUT),
                        ])

    def test_it_should_update_all_skills_if_no_one_provided(self):
        s = SkillsManager('skills')

        with patch('os.listdir', return_value=['one', 'two']):
            with patch('os.path.isdir', return_value=True):
                with patch('subprocess.check_output') as sub_mock:
                    succeeded, failed = s.update()

                    expect(succeeded).to.equal(['one', 'two'])
                    expect(failed).to.be.empty

    def test_it_should_complain_when_updating_unknown_skills(self):
        s = SkillsManager('skills')

        with patch('os.path.isdir', return_value=False):
            succeeded, failed = s.update(
                'a/skill', 'another__one', 'https://github.com/a/third')

            expect(failed).to.equal(['a/skill', 'another/one', 'a/third'])
            expect(succeeded).to.be.empty

    def test_it_should_complain_when_update_failed(self):
        s = SkillsManager('skills')

        with patch('os.path.isdir', return_value=True):
            with patch('subprocess.check_output',
                       side_effect=subprocess.CalledProcessError(42, 'cmd')) as sub_mock:
                succeeded, failed = s.update(
                    'a/skill', 'another__one', 'https://github.com/a/third')

                expect(failed).to.equal(['a/skill', 'another/one', 'a/third'])
                expect(succeeded).to.be.empty

    def test_it_should_install_skills_and_their_dependencies(self):
        s = SkillsManager('skills')
        p = os.path.abspath('skills')

        with patch('subprocess.check_output') as sub_mock:
            with patch('os.path.isfile', return_value=True):
                with patch('builtins.open', mock_open(read_data='')):
                    succeeded, failed = s.install(
                        'a/skill', 'https://gitlab.com/a/third')

                    expect(succeeded).to.equal(['a/skill', 'a/third'])
                    expect(failed).to.be.empty

                    expect(sub_mock.call_count).to.equal(4)
                    sub_mock.assert_has_calls([
                        call(['git', 'clone', 'https://github.com/a/skill',
                            os.path.join(p, 'a__skill')], stderr=subprocess.STDOUT),
                        call(['pip', 'install', '-r', 'requirements.txt'],
                            cwd=os.path.join(p, 'a__skill'), stderr=subprocess.STDOUT),
                        call(['git', 'clone', 'https://gitlab.com/a/third',
                            os.path.join(p, 'a__third')], stderr=subprocess.STDOUT),
                        call(['pip', 'install', '-r', 'requirements.txt'],
                            cwd=os.path.join(p, 'a__third'), stderr=subprocess.STDOUT),
                    ])
    
    def test_it_should_not_allow_installation_of_incompatible_skills(self):
        s = SkillsManager('skills')
        p = os.path.abspath('skills')

        incompatible_version_spec = f'{__title__}[snips]~={int(__version__[0]) - 1}.0'

        with patch('subprocess.check_output') as sub_mock:
            with patch('os.path.isfile', return_value=True):
                with patch('builtins.open', mock_open(read_data=f'{incompatible_version_spec}\n\nrequests~=2.22')):
                    with patch('pytlas.supporting.manager.rmtree') as rm_mock:
                        succeeded, failed = s.install('incompatible/skill')

                        expect(succeeded).to.be.empty
                        expect(failed).to.equal(['incompatible/skill'])
                        rm_mock.assert_called_once_with(os.path.join(p, 'incompatible__skill'), ignore_errors=True)

    def test_it_should_allow_installation_of_compatible_skills(self):
        s = SkillsManager('skills')
        p = os.path.abspath('skills')

        compatible_version_spec = f'{__title__}[snips]~={__version__[0]}.0'

        with patch('subprocess.check_output') as sub_mock:
            with patch('os.path.isfile', return_value=True):
                with patch('builtins.open', mock_open(read_data=f'{compatible_version_spec}\n\nrequests~=2.22')):
                    succeeded, failed = s.install('incompatible/skill')

                    expect(failed).to.be.empty
                    expect(succeeded).to.equal(['incompatible/skill'])

    def test_it_should_complain_when_install_failed_and_cleanup_skill_folder(self):
        s = SkillsManager('skills')

        with patch('subprocess.check_output',
                   side_effect=subprocess.CalledProcessError(42, 'cmd')) as sub_mock:
            with patch('os.path.isfile', return_value=True):
                with patch('pytlas.supporting.manager.rmtree') as rm_mock:
                    succeeded, failed = s.install('my/skill')

                    expect(failed).to.equal(['my/skill'])
                    expect(succeeded).to.be.empty
                    rm_mock.assert_called_once_with(os.path.abspath('skills/my__skill'), ignore_errors=True)

    def test_it_should_update_skills_when_it_already_exists(self):
        s = SkillsManager('skills')
        p = os.path.abspath('skills')

        with patch('os.path.isdir', return_value=True):
            with patch('subprocess.check_output') as sub_mock:
                succeeded, failed = s.install('a/skill')

                expect(succeeded).to.equal(['a/skill'])
                expect(failed).to.be.empty

                expect(sub_mock.call_count).to.equal(1)
                sub_mock.assert_called_once_with(['git', 'pull'], cwd=os.path.join(
                    p, 'a__skill'), stderr=subprocess.STDOUT)
