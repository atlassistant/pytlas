# pylint: disable=C0111

class AttrDict(dict):
    """Simple object to access dict keys like attributes.
    """

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError
