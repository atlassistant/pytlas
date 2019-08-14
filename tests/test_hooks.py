from sure import expect
from unittest.mock import MagicMock
from pytlas.hooks import global_hooks, HooksStore, ON_AGENT_CREATED, ON_AGENT_DESTROYED, \
  on_agent_created, on_agent_destroyed

class TestHooks:

  def setup(self):
    self.on_created_handler = MagicMock()
    self.on_created_handler.__name__ = 'on_created_handler'
    self.on_created2_handler = MagicMock()
    self.on_created2_handler.__name__ = 'on_created2_handler'
    self.on_destroyed_handler = MagicMock()
    self.on_destroyed2_handler = MagicMock()

  def teardown(self):
    global_hooks.reset() # Resets global hooks just to be sure

  def test_it_should_register_hooks_correctly_with_the_register_method(self):
    h = HooksStore()
    h.register(ON_AGENT_CREATED, self.on_created_handler)
    h.register(ON_AGENT_CREATED, self.on_created2_handler)

    expect(h._data[ON_AGENT_CREATED]).to.have.length_of(2)
    expect(h._data[ON_AGENT_CREATED][0]).to.equal(self.on_created_handler)
    expect(h._data[ON_AGENT_CREATED][1]).to.equal(self.on_created2_handler)
    expect(h._data[ON_AGENT_DESTROYED]).to.have.length_of(0)

  def test_it_should_register_hooks_to_the_given_store_with_the_decorator(self):
    h = HooksStore()

    @on_agent_created(store=h)
    def my_func(*args, **kwargs):
      pass

    @on_agent_destroyed(store=h)
    def other_func(*args, **kwargs):
      pass

    expect(h._data[ON_AGENT_CREATED]).to.have.length_of(1)
    expect(h._data[ON_AGENT_DESTROYED]).to.have.length_of(1)

    expect(h._data[ON_AGENT_CREATED][0]).to.equal(my_func)
    expect(h._data[ON_AGENT_DESTROYED][0]).to.equal(other_func)

  def test_it_should_register_hooks_to_the_global_store_with_the_decorator(self):
    @on_agent_created()
    def my_func(*args, **kwargs):
      pass

    @on_agent_destroyed()
    def other_func(*args, **kwargs):
      pass

    expect(global_hooks._data[ON_AGENT_CREATED]).to.have.length_of(1)
    expect(global_hooks._data[ON_AGENT_DESTROYED]).to.have.length_of(1)

    expect(global_hooks._data[ON_AGENT_CREATED][0]).to.equal(my_func)
    expect(global_hooks._data[ON_AGENT_DESTROYED][0]).to.equal(other_func)

  def test_it_should_call_handlers_with_arguments_when_hook_triggered(self):
    h = HooksStore()
    h.register(ON_AGENT_CREATED, self.on_created_handler)
    h.register(ON_AGENT_CREATED, self.on_created2_handler)

    h.trigger(ON_AGENT_CREATED, 1, 2)

    self.on_created_handler.assert_called_once_with(1, 2)
    self.on_created2_handler.assert_called_once_with(1, 2)
    self.on_destroyed_handler.assert_not_called()
    self.on_destroyed2_handler.assert_not_called()