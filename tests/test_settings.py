from sure import expect
from unittest.mock import patch, mock_open
from configparser import NoOptionError
from pytlas.settings import write_to_settings, config, DEFAULT_SECTION, SETTING_DEFAULT_REPO_URL, \
  SETTING_SKILLS, DEFAULT_SETTING_SKILLS, DEFAULT_SETTING_DEFAULT_REPO_URL, get, set as set_setting, \
  load, getbool, getint, getfloat, getlist, getpath
import os

class TestSettings:

  def test_it_should_load_settings_from_a_path(self):
    conf = """
[some_section]
some_key=some_value
"""
    conf_path = '/a/path/to/a/file.conf'

    with patch('builtins.open', mock_open(read_data=conf)):
      expect(get('some_key', section='some_section')).to.be.none

      load(conf_path)

      expect(get('some_key', section='some_section')).to.equal('some_value')

  def test_it_should_set_the_setting_even_if_the_section_does_not_exists_yet(self):
    set_setting('my_key', 'a value', section='my_section')

    expect(config.get('my_section', 'my_key')).to.equal('a value')

  def test_it_should_return_default_settings(self):
    expect(config.get(DEFAULT_SECTION, SETTING_SKILLS)).to.equal(DEFAULT_SETTING_SKILLS)
    expect(config.get(DEFAULT_SECTION, SETTING_DEFAULT_REPO_URL)).to.equal(DEFAULT_SETTING_DEFAULT_REPO_URL)

  def test_it_should_write_to_settings_correctly_with_the_decorator(self):
    
    @write_to_settings()
    def a_method():
      pass

    expect(lambda: config.get(DEFAULT_SECTION, 'a_setting_key')).to.throw(NoOptionError)

    a_method(a_setting_key='a value') # pylint: disable=E1123

    expect(config.get(DEFAULT_SECTION, 'a_setting_key')).to.equal('a value')

  def test_it_should_retrieve_a_string_value(self):
    set_setting('key', 'value', section='strings')

    expect(get('key', section='strings')).to.equal('value')

  def test_it_should_returns_the_default_if_not_found(self):
    expect(get('a key', default='a value')).to.equal('a value')

  def test_it_should_returns_the_one_in_additional_lookup_first(self):
    d = {
      'PYTLAS_A_KEY': 'an additional value',
    }

    expect(get('a key', default='a value', additional_lookup=d)).to.equal('an additional value')

  def test_it_should_retrieve_the_env_var_which_takes_precedence_if_any(self):
    
    set_setting('a_key', 'a value', section='envs')

    expect(get('a_key', section='envs')).to.equal('a value')

    os.environ['ENVS_A_KEY'] = 'an env value'

    expect(get('a_key', section='envs')).to.equal('an env value')

    expect(get('a_key', section='envs', additional_lookup={
      'ENVS_A_KEY': 'an added env value',
    })).to.equal('an added env value')

  def test_it_should_returns_a_boolean_when_asked_to(self):
    r = getbool('a key', section='bools')
    expect(r).to.be.a(bool)
    expect(r).to.be.false

    set_setting('a key', 1, section='bools')

    r = getbool('a key', section='bools')
    expect(r).to.be.a(bool)
    expect(r).to.be.true

    set_setting('another key', True, section='bools')

    r = getbool('another key', section='bools')
    expect(r).to.be.a(bool)
    expect(r).to.be.true

    expect(getbool('another key', section='bools', additional_lookup={
      'BOOLS_ANOTHER_KEY': 'True',
    })).to.be.true

  def test_it_should_returns_an_int_when_asked_to(self):
    r = getint('a key', section='ints')
    expect(r).to.be.a(int)
    expect(r).to.equal(0)

    set_setting('a key', 1337, section='ints')

    r = getint('a key', section='ints')
    expect(r).to.be.a(int)
    expect(r).to.equal(1337)

    expect(getint('a key', section='ints', additional_lookup={
      'INTS_A_KEY': '42',
    })).to.equal(42)

  def test_it_should_returns_a_float_when_asked_to(self):
    r = getfloat('a key', section='floats')
    expect(r).to.be.a(float)
    expect(r).to.equal(0.0)

    set_setting('a key', 1337.2, section='floats')

    r = getfloat('a key', section='floats')
    expect(r).to.be.a(float)
    expect(r).to.equal(1337.2)

    expect(getfloat('a key', section='floats', additional_lookup={
      'FLOATS_A_KEY': '42.2',
    })).to.equal(42.2)

  def test_it_should_returns_a_list_of_str_when_asked_to(self):
    r = getlist('a key', section='lists')
    expect(r).to.be.a(list)
    expect(r).to.be.empty

    set_setting('a key', ['one', 'two'], section='lists')

    r = getlist('a key', section='lists')
    expect(r).to.be.a(list)
    expect(r).to.equal(['one', 'two'])

    expect(getlist('a key', section='lists', additional_lookup={
      'LISTS_A_KEY': 'a,b,c',
    })).to.equal(['a', 'b', 'c'])

  def test_it_should_returns_an_absolute_path_when_asked_to(self):
    r = getpath('a key', section='paths')
    expect(r).to.be.none

    r = getpath('a key', 'default/path', section='paths')
    expect(r).to.equal(os.path.abspath('default/path'))

    set_setting('a key', 'something', section='paths')

    r = getpath('a key', section='paths')
    expect(r).to.equal(os.path.abspath('something'))

    expect(getpath('a key', section='paths', additional_lookup={
      'PATHS_A_KEY': 'var/data',
    })).to.equal(os.path.abspath('var/data'))
