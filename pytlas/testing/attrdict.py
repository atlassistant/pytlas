# pylint: disable=missing-module-docstring

class AttrDict(dict):
    """Simple object to access dict keys like attributes.
    """

    def __getattr__(self, name: str) -> object:
        try:
            return self[name]
        except KeyError:
            raise AttributeError
