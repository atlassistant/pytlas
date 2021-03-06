import os
from unittest.mock import patch, mock_open, call
from configparser import ConfigParser
from sure import expect
from pytlas.settings import SettingsStore, write_to_store, CONFIG


class TestSettingsStore:

    def test_it_should_use_the_given_configparser_instance_if_any(self):
        c = ConfigParser()
        c['my_section'] = {'my_key': 'a value'}
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
        c['priority'] = {'a key': 'from config'}

        s = SettingsStore(config=c, additional_lookup={
            'PRIORITY_A_KEY': 'from additional data',
        })

        expect(s.get('a key', section='priority')
               ).to.equal('from additional data')
        del s._data['PRIORITY_A_KEY']
        expect(s.get('a key', section='priority')).to.equal('from env')
        del os.environ['PRIORITY_A_KEY']
        expect(s.get('a key', section='priority')).to.equal('from config')

    def test_it_should_load_settings_from_a_path(self):
        s = SettingsStore()
        expect(s.get('some_key', section='some_section')).to.be.none
        s.load_from_file(os.path.join(os.path.dirname(__file__), '__test.conf'))
        expect(s.get('some_key', section='some_section')).to.equal('some_value')
        expect(s._loaded_from_path).to.equal(os.path.abspath(os.path.join(
            os.path.dirname(__file__), '__test.conf')))

    def test_it_should_set_the_setting_even_if_the_section_does_not_exists_yet(self):
        s = SettingsStore()
        s.set('my_key', 'a value', section='my_section')
        expect(s.get('my_key', section='my_section')).to.equal('a value')
        expect(s._data.get('MY_SECTION_MY_KEY')).to.equal('a value')
        

    def test_it_should_keep_track_of_manually_set_settings(self):
        s = SettingsStore()
        s.set('my_key', 'a value', section='my_section')
        s.set('my_key', 'a value', section='my_section')
        s.set('another_key', 'a value', section='my_section')
        expect(s._overriden_by_set).to.equal({
            'my_section': set(['my_key', 'another_key']),
        })

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

        s._data['BOOLS_ANOTHER_KEY'] = 'True'
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

        s._data['INTS_A_KEY'] = '42'
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

        s._data['FLOATS_A_KEY'] = '42.2'
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

        s._data['LISTS_A_KEY'] = 'a,b,c'
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

        s._data['PATHS_A_KEY'] = 'var/data'
        expect(s.getpath('a key', section='paths')).to.equal(
            os.path.abspath('var/data'))

    def test_it_should_leave_absolute_path_as_it(self):
        s = SettingsStore(additional_lookup={
            'PATHS_A_KEY': os.path.abspath('skills'),
        })
        s.load_from_file(os.path.abspath('my_pytlas/pytlas.ini'))
        expect(s.getpath('a key', section='paths')).to.equal(
            os.path.abspath('skills'))

    def test_it_should_compute_a_path_relative_to_the_loaded_config_one(self):
        s = SettingsStore(additional_lookup={
            'PATHS_A_KEY': '../skills',
        })
        s.load_from_file(os.path.abspath('my_pytlas/pytlas.ini'))
        expect(s.getpath('a key', section='paths')).to.equal(
            os.path.abspath('my_pytlas/../skills'))

    def test_it_should_convert_all_settings_to_a_dict_representation(self):
        s = SettingsStore(additional_lookup={
            'A_SETTING': 'with a string value',
            'ANOTHER_ONE': '42',
        })
        s.load_from_file(os.path.join(os.path.dirname(__file__), '__test.conf'))

        expect(s.to_dict()).to.equal({
            'A_SETTING': 'with a string value',
            'ANOTHER_ONE': '42',
            'SOME_SECTION_SOME_KEY': 'some_value'
        })
    
    def test_it_should_write_the_store_to_a_file(self):
        s = SettingsStore(additional_lookup={
            'A_SETTING': 'with a string value',
            'SOME_SECTION_SOME_KEY': '42',
        })
        s.load_from_file(os.path.join(os.path.dirname(__file__), '__test.conf'))
        s.set('my_value', '1337', section='weather')

        with patch('builtins.open', mock_open()) as mopen:
            s.write_to_file('a/file/path.ini')

            mopen().write.assert_has_calls([
                call('[some_section]\n'),
                call('some_key=42\n'),
                call('\n'),
                call('[weather]\n'),
                call('my_value=1337\n'),
                call('\n'),
            ])



class TestWriteToStore:

    def teardown(self):
        CONFIG.reset()

    def test_it_should_write_args_to_global_store(self):
        @write_to_store()
        def a_method(one, two):
            expect(one).to.equal('one value')
            expect(two).to.equal('two value')

        expect(CONFIG.get('one')).to.be.none

        a_method(one='one value', two='two value')

        expect(CONFIG.get('one')).to.equal('one value')
        expect(CONFIG.get('two')).to.equal('two value')

    def test_it_should_write_args_to_given_store(self):
        s = SettingsStore()

        @write_to_store(store=s)
        def a_method(three):
            expect(three).to.equal('three value')

        expect(s.get('three')).to.be.none

        a_method(three='three value')

        expect(s.get('three')).to.equal('three value')
        expect(CONFIG.get('three')).to.be.none

    def test_it_should_write_args_to_given_section(self):
        s = SettingsStore()

        @write_to_store(section='custom_section', store=s)
        def a_method(four):
            expect(four).to.equal('four value')

        expect(s.get('four', section='custom_section')).to.be.none

        a_method(four='four value')

        expect(s.get('four', section='custom_section')).to.equal('four value')
