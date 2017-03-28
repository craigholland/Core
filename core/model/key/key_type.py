"""Fundamental Identifier across apps, namespaces, and kinds."""

import base64
import calendar
import datetime
import os
import re
import string
import time
import urlparse
import enum
import collections

class Key1(object):
  __EXPECTED_KWARGS_DEF= {
    'id': {
      'aliases': 'uid',
      'def': '<str>, Encoded identifier unique across all apps, namespaces, and kinds.'
    },
    'reference': {
      'aliases': 'ref',
      'def': '<Key object>, A related Parent (ancestor) Key.'
    },
    'app': '<App object>, Instance representative of a particular App.',
    'namespace': '<Namespace object>, Instance representative of a particular Namespace.',
    'kind': '<Kind object>, Instance representative of a particular Kind.'
  }

  def __init__(self, **kwargs):
    """
    id: str (required)
    reference: obj (opt)
    app: obj (opt)
    namespace: obj (opt)
    kind: obj (opt)
    """

    self._id = None
    self._reference = None
    self._app = None
    self._nspace = None
    self._kind = None


att_visibility_options = ['hidden', 'aliased', 'normal']
class AttributeFieldVisibility(enum.Enum):

  NORMAL = 0
  ALIASED = 1
  HIDDEN = 2


class KeyAttributeMetaMeta(type):
  def __new__(cls, name, parents, dct):
    if 'visibility' not in dct:
      dct['visibility'] = AttributeFieldVisibility.NORMAL

    if 'field_type' not in dct:
      dct['field_type'] = str

    if 'default' not in dct:
      dct['default'] = None

    return super(KeyAttributeMetaMeta, cls).__new__(cls, name, parents, dct)

  def __init__(self, name, parents, dct):
    super(KeyAttributeMetaMeta, self).__init__(name, parents, dct)



class KeyAttributeMeta(type):

  def __new__(cls, name, parents, dct):
    # Set Defaults
    dct['_value'] = KeyAttributeMetaMeta('_value', (type,), {})
    dct['_valuetype'] = KeyAttributeMetaMeta('_valuetype', (type,), {})
    return super(KeyAttributeMeta, cls).__new__(cls, name, parents, dct)

class Key(object):
  __metaclass__ = KeyAttributeMeta

  def __init__(self, **kwargs):
    self.test1 = KeyAttributeMetaMeta()
    self.test2='hi'
    # self._value = None
    # self._valuetype = None
    # self._required = False
    # self._mutable = False
    # self._lockable = False
    # self._aliases = None
    # self._def = None
    # self._set = False
    # self._valid = False


Key_Attributes = collections.OrderedDict({
    'id': {
        'required': True,
        'mutable': False,
        'lockable': True,
        'aliases': 'uid',
        'def': '<str>, Encoded identifier unique across all apps, namespaces, and kinds.'
    },
    'reference': {
        'required': False,
        'mutable': True,
        'lockable': True,
        'aliases': 'ref',
        'def': '<Key object>, A related Parent (ancestor) Key.'
    },
    'app': {
        'required': False,
        'mutable': True,
        'lockable': True,
        'aliases': '',
        'def': '<App object>, Instance representative of a particular App.'
    },
    'namespace': {
        'required': False,
        'mutable': True,
        'lockable': True,
        'aliases': '',
        'def': '<Namespace object>, Instance representative of a particular Namespace.'
    },
    'kind': {
        'required': False,
        'mutable': True,
        'lockable': True,
        'aliases': '',
        'def': '<Kind object>, Instance representative of a particular Kind.'
    }
})

KeyNTuple = collections.namedtuple('KeyBase', [x for x in Key_Attributes.keys()])
TemplateKey = KeyNTuple(*[None for x in Key_Attributes.keys()])

class KeyBase(KeyNTuple):



  def __new__(cls, *args, **kwargs):
    # Get OrderedDict seq.

    seq = TemplateKey._asdict()
    for k in seq.keys():
      seq[k] = None

    # Process kwargs first.
    for k, v in kwargs.iteritems():
      if k in seq.keys():
        seq[k] = v
      else:
        for s in Key_Attributes.keys():
          aliases = s['aliases']
          if aliases and k in aliases:
            seq[s] = v

    # Process args next
    for arg in args:
      for k in seq.keys():
        if seq[k] is None:
          seq[k] = arg
          break

    self = super(KeyBase, cls).__new__(cls, **seq)
    return self

  @classmethod
  def find(cls, id):
    """Return Key by id input."""
    pass

  @property
  def isInitialized(self):
    for k, v in Key_Attributes.iteritems():
      if v['required']:
        if not getattr(self, k):
          return False
    return True

  def get(self):
    """Look up specific entity represented by Key and return entity."""
    pass

  def update(self, **kwargs):
    filtered_kwargs = {}
    for k, v in kwargs.iteritems():
      if k in Key_Attributes.keys():
        if Key_Attributes[k]['mutable']:
          if not Key_Attributes[k]['lockable'] or getattr(self, k) is None:
            filtered_kwargs[k] = v
          else:
            raise ValueError('%s is a locked field.' % k)
        else:
          raise ValueError('%s is an immutable field.' % k)
      else:
        raise ValueError('Got unexpected field names: %s' % k)

    return self._replace(filtered_kwargs)
