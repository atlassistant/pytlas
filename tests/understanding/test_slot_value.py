from sure import expect
from pytlas.understanding import SlotValue, UnitValue


class TestSlotValue:

    def test_it_should_give_the_value(self):
        v = SlotValue('kitchen')

        expect(v.value).to.equal('kitchen')

    def test_it_should_have_meta(self):
        v = SlotValue('kitchen', type='room', another='meta')

        expect(v.meta).to.have.length_of(2)
        expect(v.meta).to.have.key('type')
        expect(v.meta).to.have.key('another')
        expect(v.meta['type']).to.equal('room')
        expect(v.meta['another']).to.equal('meta')


class TestUnitValue:

    def test_it_should_print_value_and_unit(self):
        v = UnitValue(20, '$')

        expect(str(v)).to.equal('20$')

    def test_it_should_keep_the_value_and_the_unit(self):
        v = UnitValue(20.4, '$')

        expect(v.value).to.equal(20.4)
        expect(v.unit).to.equal('$')

    def test_it_should_be_able_to_do_basic_arithmetic_with_values(self):
        v = UnitValue(20.4, '$')

        r = v + 14.5

        expect(r).to.be.a(UnitValue)
        expect(r.value).to.equal(34.9, epsilon=0.01)
        expect(r.unit).to.equal('$')

        r = v - 14.5

        expect(r).to.be.a(UnitValue)
        expect(r.value).to.equal(5.9, epsilon=0.01)
        expect(r.unit).to.equal('$')

        r = v * 2

        expect(r).to.be.a(UnitValue)
        expect(r.value).to.equal(40.8, epsilon=0.01)
        expect(r.unit).to.equal('$')

        r = v / 2

        expect(r).to.be.a(UnitValue)
        expect(r.value).to.equal(10.2, epsilon=0.01)
        expect(r.unit).to.equal('$')

    def test_it_should_be_able_to_do_basic_arithmetic_with_other_unit_value(self):
        v = UnitValue(20.4, '$')

        r = UnitValue(14.5, '$') + v

        expect(r).to.be.a(UnitValue)
        expect(r.value).to.equal(34.9, epsilon=0.01)
        expect(r.unit).to.equal('$')

        r = v - UnitValue(14.5, '$')

        expect(r).to.be.a(UnitValue)
        expect(r.value).to.equal(5.9, epsilon=0.01)
        expect(r.unit).to.equal('$')

        r = v * UnitValue(2, '$')

        expect(r).to.be.a(UnitValue)
        expect(r.value).to.equal(40.8, epsilon=0.01)
        expect(r.unit).to.equal('$')

        r = v / UnitValue(2, '$')

        expect(r).to.be.a(UnitValue)
        expect(r.value).to.equal(10.2, epsilon=0.01)
        expect(r.unit).to.equal('$')

    def test_it_should_be_able_to_compare_with_values(self):
        v = UnitValue(20.4, '$')

        expect(v).to.equal(20.4, epsilon=0.01)
        expect(v).to_not.equal(20.9, epsilon=0.01)
        expect(v > 10).to.be.true
        expect(v >= 25).to.be.false
        expect(v < 30).to.be.true
        expect(v <= 20).to.be.false

    def test_it_should_be_able_to_compare_with_other_unit_value(self):
        v = UnitValue(20.4, '$')

        expect(v).to.equal(UnitValue(20.4, '$'), epsilon=0.01)
        expect(v).to_not.equal(UnitValue(20.9, '$'), epsilon=0.01)
        expect(v > UnitValue(10, '$')).to.be.true
        expect(v >= UnitValue(25, '$')).to.be.false
        expect(v < UnitValue(30, '$')).to.be.true
        expect(v <= UnitValue(20, '$')).to.be.false

    def test_it_should_raise_arithmetic_error_if_not_the_same_unit(self):
        v = UnitValue(20.4, '$')
        other = UnitValue(4, '€')

        expect(lambda: v + other).to.throw(ArithmeticError)
        expect(lambda: v - other).to.throw(ArithmeticError)
        expect(lambda: v * other).to.throw(ArithmeticError)
        expect(lambda: v / other).to.throw(ArithmeticError)

    def test_it_should_returns_false_when_comparing_different_units(self):
        v = UnitValue(20.4, '$')
        other = UnitValue(4, '€')

        expect(v == other).to.be.false
        expect(v != other).to.be.false
        expect(v < other).to.be.false
        expect(v <= other).to.be.false
        expect(v > other).to.be.false
        expect(v >= other).to.be.false
