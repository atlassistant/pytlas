from sure import expect
from pytlas.conversing.agent import STATE_PREFIX, STATE_SUFFIX, is_builtin

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
