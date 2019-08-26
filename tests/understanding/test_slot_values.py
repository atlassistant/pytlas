from sure import expect
from pytlas.understanding import SlotValue, SlotValues


class TestSlotValues:

    def test_it_should_convert_raw_values_to_slot_value(self):
        v = SlotValues(['kitchen', 'bedroom'])

        expect(v).to.have.length_of(2)
        expect(v[0]).to.be.a(SlotValue)
        expect(v[0].value).to.equal('kitchen')

        expect(v[1]).to.be.a(SlotValue)
        expect(v[1].value).to.equal('bedroom')

    def test_it_should_convert_raw_value_to_list(self):
        v = SlotValues('kitchen')

        expect(v).to.have.length_of(1)
        expect(v[0]).to.be.a(SlotValue)
        expect(v[0].value).to.equal('kitchen')

    def test_it_should_be_empty(self):
        v = SlotValues()

        expect(v.is_empty()).to.be.true

    def test_it_should_not_be_empty(self):
        v = SlotValues('kitchen')

        expect(v.is_empty()).to.be.false

    def test_it_should_give_the_first_value_when_there_is_one(self):
        v = SlotValues(['kitchen', 'bedroom']).first()

        expect(v).to.be.a(SlotValue)
        expect(v.value).to.equal('kitchen')

    def test_it_should_give_an_empty_first_value_when_there_is_no_value(self):
        v = SlotValues().first()

        expect(v).to.be.a(SlotValue)
        expect(v.value).to.be.none

    def test_it_should_give_the_last_value_when_there_is_one(self):
        v = SlotValues(['kitchen', 'bedroom']).last()

        expect(v).to.be.a(SlotValue)
        expect(v.value).to.equal('bedroom')

    def test_it_should_give_an_empty_last_value_when_there_is_no_value(self):
        v = SlotValues().last()

        expect(v).to.be.a(SlotValue)
        expect(v.value).to.be.none
