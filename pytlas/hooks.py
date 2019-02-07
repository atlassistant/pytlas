from pytlas.utils import get_caller_package_name
import logging

ON_AGENT_CREATED = 'on_agent_created'
ON_AGENT_DESTROYED = 'on_agent_destroyed'

# Contains hooks handlers
hooks = {
  ON_AGENT_CREATED: [],
  ON_AGENT_DESTROYED: [],
}

def trigger(hook, *args, **kwargs):
  """Trigger a hook with given arguments.

  Args:
    hook (str): Hook name to trigger
  
  """

  handlers = hooks.get(hook)

  if handlers:
    for handler in handlers:
      handler(*args, **kwargs)

def register(name, func, package=None):
  """Register a hook handler.

  Args:
    name (str): Hook name to listen for
    func (func): Function to call upon hook trigger
    package (str): Optional package name (usually __package__), if not given pytlas will try to determine it based on the call stack

  """

  package = package or get_caller_package_name()

  if name not in hooks:
    logging.warning('Not a valid hook name: "%s"' % name)
  else:
    hooks[name].append(func)
    logging.info('Registered "%s.%s" handler for hook "%s"' % (package, func.__name__, name))

def on_agent_created(package=None):
  """Decorator applied to a function that should be called when an agent is created

  Args:
    package (str): Optional package name (usually __package__), if not given pytlas will try to determine it based on the call stack

  """

  def new(func):
    register(ON_AGENT_CREATED, func, package or get_caller_package_name() or func.__module__)
    return func

  return new

def on_agent_destroyed(package=None):
  """Decorator applied to a function that should be called when an agent is destroyed

  Args:
    package (str): Optional package name (usually __package__), if not given pytlas will try to determine it based on the call stack

  """

  def new(func):
    register(ON_AGENT_DESTROYED, func, package or get_caller_package_name() or func.__module__)
    return func

  return new