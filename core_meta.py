import collections

_MUTABLE_ATTRIBUTES = frozenset(['_message_definiton'])

class _CoreDefineClass(type):
    """Base Metaclass used to create defined classes."""
    __init = False

    def __init__(cls, type_name, bases, d):
        type.__init__(cls, type_name, bases, d)
        if cls.__bases__ != (object,):
            cls.__init = True

    def get_parent_definition(cls):
        """If this definition is contained within a parent, get it."""

        try:
            return cls._get_parent_definition()
        except AttributeError:
            return None

    def __setattr__(cls, name, value):
        """Attributes of Defined classes shouldn't be changed.

        Args:
            name: Class attribute name.
            value: value of attribute name."""

        if cls.__init and name not in _MUTABLE_ATTRIBUTES:
            http: // pydoc.net / Python / protorpc / 0.1
            .6
            .7 / protorpc.messages /



class Core(object):
    __metaclass__ = CoreMeta
