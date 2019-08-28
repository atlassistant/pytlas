from sure import expect
from pytlas.understanding import UnitValue
from .swear_jar import SwearJar

class TestSwearJar:

  def test_it_should_be_empty_when_created(self):
    j = SwearJar()

    expect(j.balance).to.be.none

  def test_it_should_add_money_correctly(self):
    j = SwearJar()
    j.add(UnitValue(5, '€'))
    j.add(UnitValue(10, '€'))

    expect(str(j.balance)).to.equal('15€')

  def test_it_should_reset_correctly(self):
    j = SwearJar()
    j.add(UnitValue(5, '€'))
    j.reset()

    expect(j.balance).to.be.none
