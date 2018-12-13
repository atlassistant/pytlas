from sure import expect
from pytlas.skill_data import SkillData

TEST_PACKAGE = 'atlassistant__weather'
TEST_NAME = 'weather'
TEST_DESCRIPTION = 'Give weather forecasts'
TEST_VERSION = '1.1.0'
TEST_AUTHOR = 'Julien LEICHER'
TEST_HOMEPAGE = 'https://julien.leicher.me'
TEST_SETTINGS = ['A_SETTING']

class TestSkillData:

  def test_it_should_contain_package_as_the_name_if_not_defined(self):
    data = SkillData(package=TEST_PACKAGE)

    expect(data.name).to.equal(data.package)

  def test_it_should_print_correctly(self):
    data = SkillData(
      package=TEST_PACKAGE,
      name=TEST_NAME,
      description=TEST_DESCRIPTION,
      version=TEST_VERSION,
      homepage=TEST_HOMEPAGE,
      author=TEST_AUTHOR,
      settings=TEST_SETTINGS)
    
    expect(str(data)).to.equal("""%s - v%s
  description: %s
  homepage: %s
  author: %s
  package: %s
  settings: %s
""" % (TEST_NAME, TEST_VERSION, TEST_DESCRIPTION, TEST_HOMEPAGE, TEST_AUTHOR, TEST_PACKAGE, TEST_SETTINGS))