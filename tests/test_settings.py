from sure import expect
from pytlas.settings import SettingsStore, write_to_store, config
from configparser import ConfigParser
import os

class TestSettingsStore:

  def test_it_should_use_the_given_configparser_instance_if_any(self):
    c = ConfigParser()
    c['my_section'] = { 'my_key': 'a value' }
    s = SettingsStore(config=c)
    expect(s.get('my_key', section='my_section')).to.equal('a value')

  def test_it_should_use_additional_data_dict_when_given(self):
    s = SettingsStore(additional_lookup={
      'MY_SECTION_MY_KEY': 'a value',
    })

    expect(s.get('my_key', section='my_section')).to.equal('a value')

  def test_it_should_use_env_variables(self):
    s = SettingsStore()
    os.environ['ENVS_A_KEY'] = 'an env value'
    expect(s.get('a_key', section='envs')).to.equal('an env value')

  def test_it_should_look_in_additional_data_first_then_env_then_config(self):
    os.environ['PRIORITY_A_KEY'] = 'from env'
    
    c = ConfigParser()
    c['priority'] = { 'a key': 'from config' }
    
    s = SettingsStore(config=c, additional_lookup={
      'PRIORITY_A_KEY': 'from additional data',
    })

    expect(s.get('a key', section='priority')).to.equal('from additional data')
    del s.additional_lookup['PRIORITY_A_KEY']
    expect(s.get('a key', section='priority')).to.equal('from env')
    del os.environ['PRIORITY_A_KEY']
    expect(s.get('a key', section='priority')).to.equal('from config')

  def test_it_should_load_settings_from_a_path(self):
    s = SettingsStore()
    expect(s.get('some_key', section='some_section')).to.be.none
    s.load_from_file(os.path.join(os.path.dirname(__file__), 'test.conf'))
    expect(s.get('some_key', section='some_section')).to.equal('some_value')

  def test_it_should_set_the_setting_even_if_the_section_does_not_exists_yet(self):
    s = SettingsStore()
    s.set('my_key', 'a value', section='my_section')
    expect(s.get('my_key', section='my_section')).to.equal('a value')
    expect(s.additional_lookup.get('MY_SECTION_MY_KEY')).to.equal('a value')

  def test_it_should_retrieve_a_string_value(self):
    s = SettingsStore()
    s.set('key', 'value', section='strings')
    expect(s.get('key', section='strings')).to.equal('value')

  def test_it_should_returns_the_default_if_not_found(self):
    s = SettingsStore()
    expect(s.get('a key', default='a value')).to.equal('a value')

  def test_it_should_returns_a_boolean_when_asked_to(self):
    s = SettingsStore()
    r = s.getbool('a key', section='bools')
    expect(r).to.be.a(bool)
    expect(r).to.be.false

    s.set('a key', 1, section='bools')

    r = s.getbool('a key', section='bools')
    expect(r).to.be.a(bool)
    expect(r).to.be.true

    s.set('another key', True, section='bools')

    r = s.getbool('another key', section='bools')
    expect(r).to.be.a(bool)
    expect(r).to.be.true

    s.additional_lookup['BOOLS_ANOTHER_KEY'] = 'True'
    expect(s.getbool('another key', section='bools')).to.be.true

  def test_it_should_returns_an_int_when_asked_to(self):
    s = SettingsStore()
    r = s.getint('a key', section='ints')
    expect(r).to.be.a(int)
    expect(r).to.equal(0)

    s.set('a key', 1337, section='ints')

    r = s.getint('a key', section='ints')
    expect(r).to.be.a(int)
    expect(r).to.equal(1337)

    s.additional_lookup['INTS_A_KEY'] = '42'
    expect(s.getint('a key', section='ints')).to.equal(42)

  def test_it_should_returns_a_float_when_asked_to(self):
    s = SettingsStore()
    r = s.getfloat('a key', section='floats')
    expect(r).to.be.a(float)
    expect(r).to.equal(0.0)

    s.set('a key', 1337.2, section='floats')

    r = s.getfloat('a key', section='floats')
    expect(r).to.be.a(float)
    expect(r).to.equal(1337.2)

    s.additional_lookup['FLOATS_A_KEY'] = '42.2'
    expect(s.getfloat('a key', section='floats')).to.equal(42.2)

  def test_it_should_returns_a_list_of_str_when_asked_to(self):
    s = SettingsStore()
    r = s.getlist('a key', section='lists')
    expect(r).to.be.a(list)
    expect(r).to.be.empty

    s.set('a key', ['one', 'two'], section='lists')

    r = s.getlist('a key', section='lists')
    expect(r).to.be.a(list)
    expect(r).to.equal(['one', 'two'])

    s.additional_lookup['LISTS_A_KEY'] = 'a,b,c'
    expect(s.getlist('a key', section='lists')).to.equal(['a', 'b', 'c'])

  def test_it_should_returns_an_absolute_path_when_asked_to(self):
    s = SettingsStore()
    r = s.getpath('a key', section='paths')
    expect(r).to.be.none

    r = s.getpath('a key', 'default/path', section='paths')
    expect(r).to.equal(os.path.abspath('default/path'))

    s.set('a key', 'something', section='paths')

    r = s.getpath('a key', section='paths')
    expect(r).to.equal(os.path.abspath('something'))

    s.additional_lookup['PATHS_A_KEY'] = 'var/data'
    expect(s.getpath('a key', section='paths')).to.equal(os.path.abspath('var/data'))

class TestWriteToStore:

  def test_it_should_write_args_to_global_store(self):
    @write_to_store()
    def a_method(one, two):
      expect(one).to.equal('one value')
      expect(two).to.equal('two value')

    expect(config.get('one')).to.be.none

    a_method(one='one value', two='two value')

    expect(config.get('one')).to.equal('one value')
    expect(config.get('two')).to.equal('two value')

  def test_it_should_write_args_to_given_store(self):
    s = SettingsStore()

    @write_to_store(store=s)
    def a_method(three):
      expect(three).to.equal('three value')

    expect(s.get('three')).to.be.none

    a_method(three='three value')

    expect(s.get('three')).to.equal('three value')
    expect(config.get('three')).to.be.none

  def test_it_should_write_args_to_given_section(self):
    s = SettingsStore()

    @write_to_store(section='custom_section', store=s)
    def a_method(four):
      expect(four).to.equal('four value')

    expect(s.get('four', section='custom_section')).to.be.none

    a_method(four='four value')

    expect(s.get('four', section='custom_section')).to.equal('four value')
