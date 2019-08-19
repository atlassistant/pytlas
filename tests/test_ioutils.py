import os
from sure import expect
from unittest.mock import mock_open, patch
from pytlas.ioutils import read_file

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