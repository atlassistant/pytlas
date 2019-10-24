# pylint: disable=missing-module-docstring

from typing import Callable
from pytlas.pkgutils import get_caller_package_name
from pytlas.store import Store

ON_AGENT_CREATED = 'on_agent_created'
ON_AGENT_DESTROYED = 'on_agent_destroyed'


class HooksStore(Store):
    """Holds registered hooks and provide a way to trigger them.
    """

    def __init__(self, data: dict = None) -> None:
        """Instantiates a new store.

        Args:
          data (dict): Optional initial data to use

        """
        super().__init__('hooks', data or {
            ON_AGENT_CREATED: [],
            ON_AGENT_DESTROYED: [],
        })

    def register(self, name: str, func: Callable, package: str = None) -> None:
        """Register a new handler for the given hook.

        Args:
          name (str): Name of the hook to register to
          func (callable): Function to call upon hook trigger
          package (str): Optional package name (usually __package__), if not given
            pytlas will try to determine it based on the call stack

        """
        pkg = package or get_caller_package_name()

        if name not in self._data:
            self._logger.warning(
                '"%s" doesn\'t look like a valid hook name, dismissing', name)
        else:
            self._data[name].append(func)
            self._logger.info(
                'Registered "%s.%s" handler for hook "%s"',
                pkg, func.__name__, name)

    def trigger(self, name: str, *args, **kwargs) -> None:
        """Trigger a hook with given arguments.

        Args:
          name (str): Hook name to trigger
          args (any): Variadic args
          kwargs (dict): Keyword args

        """
        handlers = self._data.get(name)

        if handlers:
            for handler in handlers:
                handler(*args, **kwargs)


# Contains global hooks handlers
GLOBAL_HOOKS = HooksStore()


def on_agent_created(store: HooksStore = None, package: str = None) -> None:
    """Decorator applied to a function that should be called when an agent is created

    Args:
      store (HooksStore): Store to use for registration, defaults to the global one
      package (str): Optional package name (usually __package__), if not given pytlas
        will try to determine it based on the call stack

    """
    hs = store or GLOBAL_HOOKS # pylint: disable=invalid-name

    def new(func):
        hs.register(ON_AGENT_CREATED, func,
                    package or get_caller_package_name() or func.__module__)
        return func

    return new


def on_agent_destroyed(store: HooksStore = None, package: str = None) -> None:
    """Decorator applied to a function that should be called when an agent is destroyed

    Args:
      store (HooksStore): Store to use for registration, defaults to the global one
      package (str): Optional package name (usually __package__), if not given pytlas
        will try to determine it based on the call stack

    """
    s = store or GLOBAL_HOOKS # pylint: disable=invalid-name

    def new(func):
        s.register(ON_AGENT_DESTROYED, func,
                   package or get_caller_package_name() or func.__module__)
        return func

    return new
