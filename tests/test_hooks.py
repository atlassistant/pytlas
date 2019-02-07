from sure import expect
from unittest.mock import MagicMock
from pytlas.hooks import hooks, trigger, on, register, ON_AGENT_CREATED, ON_AGENT_DESTROYED

class TestHooks:

  def setup(self):
    self.on_created_handler = MagicMock()
    self.on_created_handler.__name__ = 'on_created_handler'
    self.on_created2_handler = MagicMock()
    self.on_created2_handler.__name__ = 'on_created2_handler'
    self.on_destroyed_handler = MagicMock()
    self.on_destroyed2_handler = MagicMock()

    hooks[ON_AGENT_CREATED] = []
    hooks[ON_AGENT_DESTROYED] = []

  def test_it_should_register_hooks_correctly_with_the_register_method(self):
    register(ON_AGENT_CREATED, self.on_created_handler)
    register(ON_AGENT_CREATED, self.on_created2_handler)

    expect(hooks[ON_AGENT_CREATED]).to.have.length_of(2)
    expect(hooks[ON_AGENT_DESTROYED]).to.have.length_of(0)

  def test_it_should_register_hooks_with_the_decorator(self):

    @on(ON_AGENT_DESTROYED)
    def my_func(*args, **kwargs):
      pass

    expect(hooks[ON_AGENT_CREATED]).to.have.length_of(0)
    expect(hooks[ON_AGENT_DESTROYED]).to.have.length_of(1)

    expect(hooks[ON_AGENT_DESTROYED][0]).to.equal(my_func)

  def test_it_should_call_handlers_with_arguments_when_hook_triggered(self):
    register(ON_AGENT_CREATED, self.on_created_handler)
    register(ON_AGENT_CREATED, self.on_created2_handler)

    trigger(ON_AGENT_CREATED, 1, 2)

    self.on_created_handler.assert_called_once_with(1, 2)
    self.on_created2_handler.assert_called_once_with(1, 2)
    self.on_destroyed_handler.assert_not_called()
    self.on_destroyed2_handler.assert_not_called()