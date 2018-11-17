from sure import expect
from pytlas.card import Card

class TestCard:
  
  def test_it_should_handle_header_and_text_correctly(self):
    card = Card('An **header**', 'The *text* content')

    expect(card.header).to.equal('An **header**')
    expect(card.raw_header).to.equal('An header')

    expect(card.text).to.equal('The *text* content')
    expect(card.raw_text).to.equal('The text content')

    expect(card.__str__()).to.equal('An header (None) - The text content')

  def test_it_should_handle_subhead_correctly(self):
    card = Card('', '', subhead='A **subhead**')

    expect(card.subhead).to.equal('A **subhead**')
    expect(card.raw_subhead).to.equal('A subhead')