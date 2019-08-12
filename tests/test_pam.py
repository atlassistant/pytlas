from sure import expect
from unittest.mock import patch
from pytlas.skill import global_handlers, global_metas, Meta
from pytlas.localization import global_translations
from pytlas.pam import get_loaded_skills, install_skills, update_skills, uninstall_skills

class TestPam:

  def teardown(self):
    global_translations.reset()
    global_handlers.reset()
    global_metas.reset()

  def test_it_should_retrieve_installed_skills_from_handlers(self):
    global_handlers.register('get_weather', lambda r: r.agent.done(), 'atlassistant__weather1')

    with patch('pytlas.pam.get_package_name_from_module', return_value='atlassistant__weather1'):
      r = get_loaded_skills('fr')

      expect(r).to.have.length_of(1)

      data = r[0]

      expect(data).to.be.a(Meta)
      expect(data.name).to.equal('atlassistant/weather1')
      expect(data.version).to.equal('?.?.?')

  def test_it_should_list_installed_skill_metadata_when_available(self):

    def get_meta(_): return {
      'name': 'weather',
      'version': '1.0.0',
    }

    global_handlers.register('get_weather', lambda r: r.agent.done(), 'atlassistant__weather2')
    global_metas.register(get_meta, 'atlassistant__weather2')

    with patch('pytlas.pam.get_package_name_from_module', return_value='atlassistant__weather2'):
      r = get_loaded_skills('fr')

      expect(r).to.have.length_of(1)

      data = r[0]

      expect(data).to.be.a(Meta)
      expect(data.name).to.equal('weather')
      expect(data.version).to.equal('1.0.0')

  def test_it_should_localize_installed_skill_metadata_when_available(self):
    
    def get_meta(_): return {
      'name': _('weather'),
    }

    global_handlers.register('get_weather', lambda r: r.agent.done(), 'atlassistant__weather3')
    global_metas.register(get_meta, 'atlassistant__weather3')
    global_translations.register('fr', lambda: {
      'weather': 'météo',
    }, 'atlassistant__weather3')

    with patch('pytlas.pam.get_package_name_from_module', return_value='atlassistant__weather3'):
      r = get_loaded_skills('fr')

      expect(r).to.have.length_of(1)

      data = r[0]

      expect(data).to.be.a(Meta)
      expect(data.name).to.equal('météo')

  def test_it_should_install_skill_from_relative_name(self):
    with patch('subprocess.check_output', return_value='') as subprocess_mock:
      with patch('pytlas.pam.install_dependencies_if_needed') as dep_mock:
        r = install_skills('/home/pytlas/skills', 'https://github.com/', None, 'atlassistant/weather')
        
        expect(r).to.have.length_of(1)
        expect(r).to.contain('atlassistant/weather')

        cmd = subprocess_mock.call_args[0][0]

        expect(cmd).to.contain('git')
        expect(cmd).to.contain('clone')
        expect(cmd).to.contain('https://github.com/atlassistant/weather')

        dep_mock.assert_called_once()
  
  def test_it_should_install_skill_from_relative_name_with_custom_repo_url(self):
    with patch('subprocess.check_output', return_value='') as subprocess_mock:
      with patch('pytlas.pam.install_dependencies_if_needed') as dep_mock:
        r = install_skills('/home/pytlas/skills', 'https://gitlab.com/', None, 'atlassistant/weather')
        
        expect(r).to.have.length_of(1)
        expect(r).to.contain('atlassistant/weather')

        cmd = subprocess_mock.call_args[0][0]

        expect(cmd).to.contain('git')
        expect(cmd).to.contain('clone')
        expect(cmd).to.contain('https://gitlab.com/atlassistant/weather')

        dep_mock.assert_called_once()

  def test_it_should_install_dependencies_if_needed_upon_installation(self):
    with patch('subprocess.check_output', return_value='') as subprocess_mock:
      with patch('os.path.isfile', return_value=True):
        r = install_skills('/home/pytlas/skills', 'https://github.com/', None, 'atlassistant/weather')
        
        expect(r).to.have.length_of(1)
        expect(r).to.contain('atlassistant/weather')
        
        # Should have been called twice, once for the clone, and the other for the pip install
        expect(subprocess_mock.call_count).to.equal(2)
        
        cmd = subprocess_mock.call_args[0][0]

        expect(cmd).to.contain('pip')
        expect(cmd).to.contain('install')
        expect(cmd).to.contain('-r')
        expect(cmd).to.contain('requirements.txt')

  def test_it_should_install_skill_from_absolute_url(self):
    with patch('subprocess.check_output', return_value='') as subprocess_mock:
      r = install_skills('/home/pytlas/skills', 'https://github.com/', None, 'https://git.somewhere/atlassistant/weather')
      
      expect(r).to.have.length_of(1)
      expect(r).to.contain('https://git.somewhere/atlassistant/weather')

      cmd = subprocess_mock.call_args[0][0]

      expect(cmd).to.contain('git')
      expect(cmd).to.contain('clone')
      expect(cmd).to.contain('https://git.somewhere/atlassistant/weather')

  def test_it_should_update_skill_when_already_available(self):
    with patch('subprocess.check_output', return_value='') as subprocess_mock:
      with patch('os.path.isdir', return_value=True):
        with patch('pytlas.pam.update_skills', return_value=['atlassistant/weather']) as update_mock:
          r = install_skills('/home/pytlas/skills', 'https://github.com/', None, 'atlassistant/weather')

          expect(r).to.have.length_of(1)
          expect(r).to.contain('atlassistant/weather')

          update_mock.assert_called_once_with('/home/pytlas/skills', None, 'atlassistant/weather')

  def test_it_should_update_all_skills_if_no_defined(self):
    with patch('subprocess.check_output', return_value='') as subprocess_mock:
      with patch('os.path.isdir', return_value=True):
        with patch('os.listdir', return_value=['atlassistant__weather', 'atlassistant__builtin']):
          r = update_skills('/home/pytlas/skills')

          expect(r).to.have.length_of(2)
          expect(r).to.contain('atlassistant/weather')
          expect(r).to.contain('atlassistant/builtin')

          expect(subprocess_mock.call_count).to.equal(2)

  def test_it_should_update_correctly_a_skill(self):
    with patch('subprocess.check_output', return_value='') as subprocess_mock:
      with patch('os.path.isdir', return_value=True):
        with patch('pytlas.pam.install_dependencies_if_needed') as dep_mock:
          r = update_skills('/home/pytlas/skills', None, 'atlassistant/weather')

          expect(r).to.have.length_of(1)
          expect(r).to.contain('atlassistant/weather')

          cmd = subprocess_mock.call_args[0][0]

          expect(cmd).to.contain('git')
          expect(cmd).to.contain('pull')

          dep_mock.assert_called_once()

  def test_it_should_uninstall_skill_correctly(self):
    with patch('os.path.isdir', return_value=True):
      with patch('pytlas.pam.rmtree', return_value='') as rm_mock:
        r = uninstall_skills('/home/pytlas/skills', None, 'atlassistant/weather')
        
        expect(r).to.have.length_of(1)
        expect(r).to.contain('atlassistant/weather')

        rm_mock.assert_called_once()
