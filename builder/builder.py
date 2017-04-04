"""Methods and Classes providing functionality for Builder mechanism."""

"""
Builder() is a "class factory" that creates classes
"""

class BaseMeta(object):
    def _check(self, attr, value):
        if attr in self.defaults:
            if not isinstance(value, self.defaults[attr]):
                raise TypeError('%s cannot be %s' % (attr, type(value)))
        else:
            self.defaults[attr] = type(value)
    def __setattr__(self, attr, value):
        self._check(attr, value)
        super(BaseMeta, self).__setattr__(attr, value)

class Meta(type):
    def __new__(meta, name, bases, dict):
        cls = type.__new__(meta, name, (BaseMeta,) + bases, dict)
        cls.defaults = {name: type(value) for name, value in dict.items()}
        return cls

class BaseModel(object):
    __metaclass__ = Meta
    # Shared Model methods.
    pass


class ModelDef(object):
    height = int
    width = int
    path = str
    size = float


class MyModel(BaseModel):
  _DEFINITION = ModelDef()

  def __init__(self, **kwargs):
    for k,v in kwargs:
      self[k] = v

