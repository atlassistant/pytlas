from sure import expect
from pytlas.testing import create_skill_agent
import os

agent = create_skill_agent(os.path.dirname(__file__))

class TestLights:

  def setup(self):
    agent.model.reset()

  def test_it_should_turn_lights_on(self):
    agent.parse('Turn the lights on in kitchen please')

    call = agent.model.on_answer.get_call(0)

    expect(call.text).to.equal('Turning lights on in kitchen')

  def test_it_should_turn_lights_on_and_ask_for_rooms(self):
    agent.parse('Turn the lights on')

    call = agent.model.on_ask.get_call()

    expect(call.slot).to.equal('room')
    expect(call.text).to.be.within(['For which rooms?', 'Which rooms Sir?', 'Please specify some rooms'])
    expect(call.choices).to.be.none

    agent.parse('In the kitchen please')

    call = agent.model.on_answer.get_call()

    expect(call.text).to.equal('Turning lights on in kitchen')
