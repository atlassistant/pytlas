import os
from sure import expect
from pytlas.testing import create_skill_agent

# Testing a pytlas skill is easy.
# Start by instantiating an agent trained only for this skill.

agent = create_skill_agent(os.path.dirname(__file__), lang='en')


class TestHooverSkill:

    def setup(self):
        # Between each tests, resets the model mock so calls are dismissed and we
        # start on a fresh state.
        # This will be usefull when you have more than one test method :)
        agent.model.reset()

    def test_it_should_start_vacuuming(self):
        # Now, try to trigger our skill
        agent.parse('start vacuum cleaner')

        # And make assertions about how the model (the part between pytlas and the end user)
        # as answered: https://pytlas.readthedocs.io/en/latest/writing_skills/testing.html#writing-tests
        call = agent.model.on_answer.get_call()
        expect(call.text).to.equal('Vacuuming started')
        expect(call.skill).to.equal('vacuum')
        expect(call.action).to.equal('start')

    def test_it_should_stop_vacuuming(self):
        # Now, try to trigger our skill
        agent.parse('stop vacuum cleaner')

        # And make assertions about how the model (the part between pytlas and the end user)
        # as answered: https://pytlas.readthedocs.io/en/latest/writing_skills/testing.html#writing-tests
        call = agent.model.on_answer.get_call()
        expect(call.text).to.equal('End of vacuuming, return to dock')
        expect(call.skill).to.equal('vacuum')
        expect(call.action).to.equal('stop')
