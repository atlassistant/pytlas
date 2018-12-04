from sure import expect
from pytlas.cli.config import write_config, get, getboolean, OPT_LANG, OPT_LANG_DEFAULT

class TestCli:
  
  def test_it_should_write_config_correctly(self):

    @write_config
    def some_func():
      # Using write_config, every parameters will be captured and written to the config object
      pass

    some_func(some_key='some value', verbose=True)

    expect(get('some_key')).to.equal('some value')
    expect(getboolean('verbose')).to.be.true
    expect(get(OPT_LANG)).to.equal(OPT_LANG_DEFAULT)

    some_func(lang='fr')

    expect(get(OPT_LANG)).to.equal('fr')