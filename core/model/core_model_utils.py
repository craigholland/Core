import collections
import sys
from core import core_utils
from core.core_error import *


class _NotEqualMixin(object):
  """Mix-in class that implements __ne__ in terms of __eq__."""

  def __ne__(self, other):
    """Implement self != other as not(self == other)."""
    eq = self.__eq__(other)
    if eq is NotImplemented:
      return NotImplemented
    return not eq


class _NestedCounter(object):
  """ A recursive counter for StructuredProperty deserialization.

  Deserialization has some complicated rules to handle StructuredPropertys
  that may or may not be empty. The simplest case is a leaf counter, where
  the counter will return the index of the repeated value that last had this
  leaf property written. When a non-leaf counter requested, this will return
  the max of all its leaf values. This is due to the fact that the next index
  that a full non-leaf property may be written to comes after all indices that
  have part of that property written (otherwise, a partial entity would be
  overwritten.

  Consider an evaluation of the following structure:
    class B(model.Model):
      c = model.IntegerProperty()
      d = model.IntegerProperty()

    class A(model.Model):
      b = model.StructuredProperty(B)

    class Foo(model.Model):
      # top-level model
      a = model.StructuredProperty(A, repeated=True)

    Foo(a=[A(b=None),
           A(b=B(c=1)),
           A(b=None),
           A(b=B(c=2, d=3))])

  This will result in a serialized structure:

  1) a.b   = None
  2) a.b.c = 1
  3) a.b.d = None
  4) a.b   = None
  5) a.b.c = 2
  6) a.b.d = 3

  The counter state should be the following:
     a | a.b | a.b.c | a.b.d
  0) -    -      -       -
  1) @1   1      -       -
  2) @2   @2     2       -
  3) @2   @2     2       2
  4) @3   @3     3       3
  5) @4   @4     4       3
  6) @4   @4     4       4

  Here, @ indicates that this counter value is actually a calculated value.
  It is equal to the MAX of its sub-counters.

  Counter values may get incremented multiple times while deserializing a
  property. This will happen if a child counter falls behind,
  for example in steps 2 and 3.

  During an increment of a parent node, all child nodes values are incremented
  to match that of the parent, for example in step 4.
  """

  def __init__(self):
    self.__counter = 0
    self.__sub_counters = collections.defaultdict(_NestedCounter)

  def get(self, parts=None):
    if parts:
      return self.__sub_counters[parts[0]].get(parts[1:])
    if self.__is_parent_node():
      return max(v.get() for v in self.__sub_counters.itervalues())
    return self.__counter

  def increment(self, parts=None):
    if parts:
      self.__make_parent_node()
      return self.__sub_counters[parts[0]].increment(parts[1:])
    if self.__is_parent_node():
      # Move all children forward
      value = self.get() + 1
      self._set(value)
      return value
    self.__counter += 1
    return self.__counter

  def _set(self, value):
    """Updates all descendants to a specified value."""
    if self.__is_parent_node():
      for child in self.__sub_counters.itervalues():
        child._set(value)
    else:
      self.__counter = value

  def _absolute_counter(self):
    # Used only for testing.
    return self.__counter

  def __is_parent_node(self):
    return self.__counter == -1

  def __make_parent_node(self):
    self.__counter = -1


class ModelAttribute(object):
  """A Base class signifying the presence of a _fix_up() method."""

  def _fix_up(self, cls, code_name):
    pass


class _BaseValue(_NotEqualMixin):
  """A marker object wrapping a 'base type' value.

  This is used to be able to tell whether ent._values[name] is a
  user value (i.e. of a type that the Python code understands) or a
  base value (i.e of a type that serialization understands).
  User values are unwrapped; base values are wrapped in a
  _BaseValue instance.
  """

  __slots__ = ['b_val']

  def __init__(self, b_val):
    """Constructor.  Argument is the base value to be wrapped."""
    assert b_val is not None, "Cannot wrap None"
    assert not isinstance(b_val, list), repr(b_val)
    self.b_val = b_val

  def __repr__(self):
    return '_BaseValue(%r)' % (self.b_val,)

  def __eq__(self, other):
    if not isinstance(other, _BaseValue):
      return NotImplemented
    return self.b_val == other.b_val

  def __hash__(self):
    raise TypeError('_BaseValue is not immutable')

# TEMP REMOVE
#
# def _unpack_user(v):
#   """Internal helper to unpack a User value from a protocol buffer."""
#   uv = v.uservalue()
#   email = unicode(uv.email().decode('utf-8'))
#   auth_domain = unicode(uv.auth_domain().decode('utf-8'))
#   obfuscated_gaiaid = uv.obfuscated_gaiaid().decode('utf-8')
#   obfuscated_gaiaid = unicode(obfuscated_gaiaid)
#
#   federated_identity = None
#   if uv.has_federated_identity():
#     federated_identity = unicode(
#         uv.federated_identity().decode('utf-8'))
#
#   value = users.User(email=email,
#                      _auth_domain=auth_domain,
#                      _user_id=obfuscated_gaiaid,
#                      federated_identity=federated_identity)
#   return value



def get_multi_async(keys, **ctx_options):
  """Fetches a sequence of keys.

  Args:
    keys: A sequence of keys.
    **ctx_options: Context options.

  Returns:
    A list of futures.
  """
  return [key.get_async(**ctx_options) for key in keys]


def get_multi(keys, **ctx_options):
  """Fetches a sequence of keys.

  Args:
    keys: A sequence of keys.
    **ctx_options: Context options.

  Returns:
    A list whose items are either a Model instance or None if the key wasn't
    found.
  """
  return [future.get_result()
          for future in get_multi_async(keys, **ctx_options)]


def put_multi_async(entities, **ctx_options):
  """Stores a sequence of Model instances.

  Args:
    entities: A sequence of Model instances.
    **ctx_options: Context options.

  Returns:
    A list of futures.
  """
  return [entity.put_async(**ctx_options) for entity in entities]


def put_multi(entities, **ctx_options):
  """Stores a sequence of Model instances.

  Args:
    entities: A sequence of Model instances.
    **ctx_options: Context options.

  Returns:
    A list with the stored keys.
  """
  return [future.get_result()
          for future in put_multi_async(entities, **ctx_options)]


def delete_multi_async(keys, **ctx_options):
  """Deletes a sequence of keys.

  Args:
    keys: A sequence of keys.
    **ctx_options: Context options.

  Returns:
    A list of futures.
  """
  return [key.delete_async(**ctx_options) for key in keys]


def delete_multi(keys, **ctx_options):
  """Deletes a sequence of keys.

  Args:
    keys: A sequence of keys.
    **ctx_options: Context options.

  Returns:
    A list whose items are all None, one per deleted key.
  """
  return [future.get_result()
          for future in delete_multi_async(keys, **ctx_options)]


def ValidateString(value,
                   name='unused',
                   exception=BadValueError,
                   max_len=1500,
                   empty_ok=False):
  """Raises an exception if value is not a valid string or a subclass thereof.

  A string is valid if it's not empty, no more than _MAX_STRING_LENGTH bytes,
  and not a Blob. The exception type can be specified with the exception
  argument; it defaults to BadValueError.

  Args:
    value: the value to validate.
    name: the name of this value; used in the exception message.
    exception: the type of exception to raise.
    max_len: the maximum allowed length, in bytes.
    empty_ok: allow empty value.
  """
  if value is None and empty_ok:
    return
  #if not isinstance(value, basestring) or isinstance(value, Blob):
  if not isinstance(value, basestring):
    raise exception('%s should be a string; received %s:' %
                    (name, value,))
  if not value and not empty_ok:
    raise exception('%s must not be empty.' % name)

  if len(value.encode('utf-8')) > max_len:
    raise exception('%s must be under %d bytes.' % (name, max_len))



__all__ = core_utils.build_mod_all_list(sys.modules[__name__])
# TEMP REMOVE
# def get_indexes_async(**ctx_options):
#   """Get a data structure representing the configured indexes.
#
#   Args:
#     **ctx_options: Context options.
#
#   Returns:
#     A future.
#   """
#   from . import tasklets
#   ctx = tasklets.get_context()
#   return ctx.get_indexes(**ctx_options)
#
#
# def get_indexes(**ctx_options):
#   """Get a data structure representing the configured indexes.
#
#   Args:
#     **ctx_options: Context options.
#
#   Returns:
#     A list of Index objects.
#   """
#   return get_indexes_async(**ctx_options).get_result()
