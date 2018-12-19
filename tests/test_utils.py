import os
from sure import expect
from unittest.mock import patch, mock_open
from pytlas.utils import find_match, keep_one, read_file

class TestFindMatch:

  def setup(self):
    self.choices = ['kitchen', 'bedroom', 'living room']

  def test_it_find_one_match_when_multiple_choices_matches(self):
    expect(find_match(self.choices, 'room')).to.equal('bedroom')

  def test_it_find_match_when_it_has_typo(self):
    expect(find_match(self.choices, 'bedoorm')).to.equal('bedroom')

  def test_it_find_match_when_word_not_complete(self):
    expect(find_match(self.choices, 'kitch')).to.equal('kitchen')

  def test_it_find_nothing_when_there_is_no_match(self):
    expect(find_match(self.choices, 'nothing here')).to.be.none

  def test_it_find_nothing_if_value_is_empty(self):
    expect(find_match(self.choices, None)).to.be.none

class TestKeepOne:

  def test_it_returns_the_given_value_if_not_an_array(self):
    expect(keep_one('a value')).to.equal('a value')

  def test_it_returns_one_of_given_value_if_its_an_array(self):
    values = ['a value', 'another value', 'something more']

    expect(keep_one(values)).to.be.within(values)

class TestReadFile:

  def test_it_should_raise_an_exception_when_errors_not_ignored(self):
    expect(lambda: read_file('something')).to.throw(Exception)

  def test_it_should_not_raise_exception_when_errors_ignored(self):
    expect(read_file('something', ignore_errors=True)).to.be.none

  def test_it_should_read_the_file_correctly(self):
    with patch('builtins.open', mock_open(read_data='some content')) as mopen:
      expect(read_file('somepath')).to.equal('some content')

      mopen.assert_called_once_with('somepath', encoding='utf-8')

  def test_it_should_read_the_file_relative_to_another_one(self):
    with patch('builtins.open', mock_open(read_data='some content')) as mopen:
      expect(read_file('somepath', relative_to_file='/home/julien/pytlas/a.file')).to.equal('some content')

      mopen.assert_called_once_with('/home/julien/pytlas%ssomepath' % os.path.sep, encoding='utf-8')
      