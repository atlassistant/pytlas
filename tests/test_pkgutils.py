import os, sys, pytlas.understanding
from sure import expect
from pytlas.pkgutils import get_module_path, get_package_name_from_module, \
  get_caller_package_name

class TestGetModulePath:

  def test_it_should_provide_a_module_path(self):
    expect(get_module_path('pytlas.understanding')).to.equal(sys.modules['pytlas.understanding'].__path__[0])

  def test_it_should_fallback_to_the_current_working_directory(self):
    expect(get_module_path('pytlas.pkgutils')).to.equal(os.getcwd())

class TestGetPackageNameFromModule:

  def test_it_should_provide_the_package_name(self):
    expect(get_package_name_from_module('pytlas.understanding')).to.equal('pytlas')

class TestGetCallerPackageName:

  def test_it_should_retrieve_the_caller_package_name(self):
    expect(get_caller_package_name()).to.equal('nose')