from sure import expect
from pytlas.agent import STATE_PREFIX, STATE_SUFFIX, find_match, is_builtin, keep_one

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

class TestIsBuiltIn:

  def test_it_is_builtin_if_it_start_with_prefix_and_end_with_suffix(self):
    expect(is_builtin(STATE_PREFIX + 'something' + STATE_SUFFIX)).to.be.true

  def test_it_is_not_builtin_if_it_doesnt_start_with_prefix(self):
    expect(is_builtin('something' + STATE_SUFFIX)).to.be.false

  def test_it_is_not_builtin_if_it_doesnt_end_with_suffix(self):
    expect(is_builtin(STATE_PREFIX + 'something')).to.be.false

  def test_it_is_not_builtin_if_its_none(self):
    expect(is_builtin(None)).to.be.false

  def test_it_is_not_builtin_if_its_empty(self):
    expect(is_builtin('')).to.be.false

class TestKeepOne:

  def test_it_returns_the_given_value_if_not_an_array(self):
    expect(keep_one('a value')).to.equal('a value')

  def test_it_returns_one_of_given_value_if_its_an_array(self):
    values = ['a value', 'another value', 'something more']

    expect(keep_one(values)).to.be.within(values)
