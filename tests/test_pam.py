from sure import expect
from unittest.mock import patch
from pytlas.skill import register, register_metadata
from pytlas.pam import get_installed_skills
from pytlas.skill_data import SkillData

class TestPam:

  def test_it_should_retrieve_installed_skills_from_handlers(self):
    register('get_weather', lambda r: r.agent.done(), 'atlassistant__weather1')

    with patch('pytlas.pam.get_package_name_from_module', return_value='atlassistant__weather1'):
      r = get_installed_skills('fr')

      expect(r).to.have.length_of(1)

      data = r[0]

      expect(data).to.be.a(SkillData)
      expect(data.name).to.equal('atlassistant/weather1')
      expect(data.version).to.equal('?.?.?')

  def test_it_should_list_installed_skill_metadata_when_available(self):

    def get_meta(_): return {
      'name': 'weather',
      'version': '1.0.0',
    }

    register('get_weather', lambda r: r.agent.done(), 'atlassistant__weather2')
    register_metadata(get_meta, 'atlassistant__weather2')

    with patch('pytlas.pam.get_package_name_from_module', return_value='atlassistant__weather2'):
      r = get_installed_skills('fr')

      expect(r).to.have.length_of(1)

      data = r[0]

      expect(data).to.be.a(SkillData)
      expect(data.name).to.equal('weather')
      expect(data.package).to.equal('atlassistant/weather2')
      expect(data.version).to.equal('1.0.0')

  def test_it_should_localize_installed_skill_metadata_when_available(self):
    pass