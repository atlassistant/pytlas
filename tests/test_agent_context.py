from sure import expect
from unittest.mock import MagicMock
from pytlas.interpreters import Interpreter, Intent, SlotValue
from pytlas.agent import Agent, build_scopes, STATE_CANCEL, STATE_FALLBACK, STATE_ASLEEP

def on_manage_list(r):
  r.agent.context('manage_list')

  return r.agent.done()

def on_rename_list(r):
  return r.agent.done()

def on_list_fallback(r):
  if 'list' not in r.agent.meta:
    r.agent.meta['list'] = []

  r.agent.meta['list'].append(r.intent.slot('text').first().value)

  return r.agent.done()

def on_close_list(r):
  r.agent.context(None)

  return r.agent.done()

def on_open_context(r):
  r.agent.context('open_context')

  return r.agent.done()

class TestAgentContext:

  def setup(self):
    self.on_context = MagicMock()

    self.handlers = {
      'manage_list': on_manage_list,
      'manage_list/rename': on_rename_list,
      'manage_list/close': on_close_list,
      'manage_list/' + STATE_FALLBACK: on_list_fallback,
      'open_context': on_open_context,
      'open_context/nested': MagicMock(),
    }

    self.interpreter = Interpreter('test', 'en')
    self.interpreter.intents = [i for i in self.handlers.keys() if STATE_FALLBACK not in i] + [STATE_CANCEL]
    self.agent = Agent(self.interpreter, handlers=self.handlers, model=self)

  def test_it_should_parse_scopes_correctly(self):
    intents = ['an intent', 'an intent/a sub intent', 'an intent/a sub intent/another one', 'one more']

    r = build_scopes(intents)

    expect(r).to.be.a(dict)
    expect(r).to.have.length_of(3)
    expect(r).to.have.key(None)
    expect(r).to.have.key('an intent')
    expect(r).to.have.key('an intent/a sub intent')

    scope = r[None]

    expect(scope).to.have.length_of(3)
    expect(scope).to.contain(STATE_CANCEL)
    expect(scope).to.contain('an intent')
    expect(scope).to.contain('one more')

    scope = r['an intent']

    expect(scope).to.have.length_of(2)
    expect(scope).to.contain(STATE_CANCEL)
    expect(scope).to.contain('an intent/a sub intent')

    scope = r['an intent/a sub intent']

    expect(scope).to.have.length_of(2)
    expect(scope).to.contain(STATE_CANCEL)
    expect(scope).to.contain('an intent/a sub intent/another one')

  def test_it_should_not_contains_the_cancel_scope_if_interpreter_does_not_understand_it(self):
    intents = ['an intent', 'an intent/a sub intent', 'an intent/a sub intent/another one', 'one more']

    r = build_scopes(intents, include_cancel_state=False)

    scope = r[None]

    expect(scope).to.have.length_of(2)
    expect(scope).to.contain('an intent')
    expect(scope).to.contain('one more')

    scope = r['an intent']

    expect(scope).to.have.length_of(1)
    expect(scope).to.contain('an intent/a sub intent')

    scope = r['an intent/a sub intent']

    expect(scope).to.have.length_of(1)
    expect(scope).to.contain('an intent/a sub intent/another one')

  def test_it_should_be_initialized_with_the_none_context(self):
    expect(self.agent.current_context).to.equal(None)
    expect(self.agent._available_scopes[None]).to.contain('manage_list')
    expect(self.agent._current_scopes).to.have.length_of(3)
    expect(self.agent._current_scopes).to.contain(STATE_CANCEL)
    expect(self.agent._current_scopes).to.contain('manage_list')
    expect(self.agent._current_scopes).to.contain('open_context')

  def test_it_should_handle_context_switching_from_a_skill(self):
    self.on_context.assert_called_once_with(None)
    self.on_context.reset_mock()

    self.interpreter.parse = MagicMock(return_value=[Intent('manage_list')])
    self.agent.parse('I want to manage a list')

    self.on_context.assert_called_once_with('manage_list')
    self.on_context.reset_mock()
    self.interpreter.parse.assert_called_once()

    call_args = self.interpreter.parse.call_args[0]
    expect(call_args).to.have.length_of(2)
    expect(call_args[0]).to.equal('I want to manage a list')
    expect(call_args[1]).to.be.a(list)
    expect(call_args[1]).to.have.length_of(3)
    expect(call_args[1]).to.contain(STATE_CANCEL)
    expect(call_args[1]).to.contain('manage_list')
    expect(call_args[1]).to.contain('open_context')

    self.interpreter.parse.reset_mock()

    expect(self.agent.current_context).to.equal('manage_list')
    expect(self.agent._current_scopes).to.have.length_of(3)
    expect(self.agent._current_scopes).to.contain(STATE_CANCEL)
    expect(self.agent._current_scopes).to.contain('manage_list/rename')
    expect(self.agent._current_scopes).to.contain('manage_list/close')

    self.interpreter.parse = MagicMock(return_value=[Intent('manage_list/close')])
    
    self.agent.parse('I am done with that list')

    self.on_context.assert_called_once_with(None)
    self.interpreter.parse.assert_called_once()

    call_args = self.interpreter.parse.call_args[0]
    expect(call_args).to.have.length_of(2)
    expect(call_args[0]).to.equal('I am done with that list')
    expect(call_args[1]).to.be.a(list)
    expect(call_args[1]).to.have.length_of(3)
    expect(call_args[1]).to.contain(STATE_CANCEL)
    expect(call_args[1]).to.contain('manage_list/rename')
    expect(call_args[1]).to.contain('manage_list/close')

    expect(self.agent.current_context).to.be.none

  def test_it_should_return_to_the_root_context_if_cancelled_and_not_specific_handler(self):
    self.interpreter.parse = MagicMock(return_value=[Intent('open_context')])

    self.agent.parse('Switch to a context')

    expect(self.agent.current_context).to.equal('open_context')

    self.interpreter.parse = MagicMock(return_value=[Intent(STATE_CANCEL)])

    self.agent.parse('Cancel')

    expect(self.agent.current_context).to.be.none
    expect(self.agent._current_scopes).to.have.length_of(3)
    expect(self.agent._current_scopes).to.contain(STATE_CANCEL)
    expect(self.agent._current_scopes).to.contain('manage_list')
    expect(self.agent._current_scopes).to.contain('open_context')

  def test_it_should_call_context_specific_handler_if_any_for_builtin_intents(self):
    self.interpreter.parse = MagicMock(return_value=[Intent('manage_list')])
    self.agent.parse('I want to manage a list')

    expect(self.agent.current_context).to.equal('manage_list')

    self.interpreter.parse = MagicMock(return_value=[])
    self.agent.parse('Buy some eggs')

    expect(self.agent.current_context).to.equal('manage_list')
    expect(self.agent.meta).to.have.key('list')
    expect(self.agent.meta['list']).to.contain('Buy some eggs')

    self.agent.parse('Buy milk too')

    expect(self.agent.current_context).to.equal('manage_list')
    expect(self.agent.meta).to.have.key('list')
    expect(self.agent.meta['list']).to.have.length_of(2)
    expect(self.agent.meta['list']).to.contain('Buy milk too')

  def test_it_should_not_be_able_to_transition_to_nested_state_if_not_in_the_context(self):
    self.handlers['manage_list/rename'] = MagicMock()

    self.agent.go('manage_list/rename', intent=Intent('manage_list/rename'))
    self.handlers['manage_list/rename'].assert_not_called()

    self.agent.go('manage_list', intent=Intent('manage_list'))
    self.agent.go('manage_list/rename', intent=Intent('manage_list/rename'))
    self.handlers['manage_list/rename'].assert_called_once()

  def test_it_should_create_attribute_on_the_agent_to_check_if_right_context(self):
    expect(callable(self.agent.is_in_manage_list_context)).to.be.true
    expect(self.agent.is_in_manage_list_context(None)).to.be.false
    self.agent.context('manage_list')
    expect(self.agent.is_in_manage_list_context(None)).to.be.true

    expect(callable(self.agent.is_in_open_context_context)).to.be.true
    expect(self.agent.is_in_open_context_context(None)).to.be.false
    self.agent.context('open_context')
    expect(self.agent.is_in_open_context_context(None)).to.be.true