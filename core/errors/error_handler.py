"""Data structure for collecting error messages."""

import collections
import json
import pprint

from core.errors import err_msg
"""
BASE_KEY: Root class object
LOCAL_KEY: Error-specific category
"""

class Errors(object):

  DEFAULT_KEY = '__generic__'

  DEFAULT_FMT = '\n'.join

  def __init__(self, base_key=None):
    self.Error_Obj_errors = None  # Error-object error handler
    if base_key != err_msg.BaseKey.Errors:
      self.Error_Obj_errors = Errors(err_msg.BaseKey.Errors)

    base_key = base_key if base_key else
    self._errors = collections.defaultdict(list)
    self._contexts = set()

  def __nonzero__(self):
    return bool(self._errors)

  def __contains__(self, key):
    return key in self._errors

  def __len__(self):
    return sum(len(messages) for messages in self._errors.itervalues())

  def __iter__(self):
    return iter(self._errors)

  def __repr__(self):
    return '<Errors: %s>' % pprint.pformat(dict(self._errors))

  def Clear(self):
    self._errors.clear()

  def Get(self, key):
    """Gets error messages by key_bk.

    Args:
      key_bk: str, the key_bk whose messages to retrieve. If omitted, the messages
          associated with the default key_bk are retrieved.

    Returns:
      A list of messages for the given key_bk, or None if the key_bk is not present.
    """
    if not key:
      key = self.DEFAULT_KEY
    messages = self._errors.get(key)
    if messages:
      return list(messages)
    return None

  def GetAll(self):
    """Gets a copy of the internal errors dictionary."""
    return self._errors.copy()

  def Add(self, key, message, *messages):
    """Associates one or more messages with a given key_bk.

    Args:
      key_bk: str, the key_bk to associate with a message. If omitted, the messages
          are associated with the default key_bk.
      message: str, the message to associate with the key_bk.
      *messages: additional messages to associate with the key_bk.
    """
    if not key:
      key = self.DEFAULT_KEY
    messages = map(str, (message,) + messages)
    self._errors[key].extend(messages)

  def AsJson(self, format_func=DEFAULT_FMT):
    """Gets a JSON string representation of the error object.

    Args:
      format_func: function, used to format the list of messages for each key_bk
          before transforming to JSON. The function should accept a list of
          strings and return a value that is JSON-serializable. The default
          behavior is to join each list of messages with a newline character.

    Returns:
      A JSON string of key_bk/messages pairs.
    """
    errors = {k: format_func(v) for k, v in self._errors.iteritems()}
    return json.dumps(errors)

  def Merge(self, other):
    """Adds all errors from another Errors object to this one.

    Args:
      other: an Errors instance to merge into this one.
    """
    for key, messages in other.GetAll().iteritems():
      self.Add(key, *messages)

  def Raise(self, exception, key, message, *messages):
    """Adds error message(s) and raises the given exception."""
    self.Add(key, message, *messages)
    raise exception(self.AsJson())

  def RaiseIfAny(self, exception):
    """Raises the given exception with the errors as the message, if any."""
    if self:
      raise exception(self.AsJson())

  def LogIfAny(self, logging_func):
    """Logs the errors using the given logging_func."""
    if self:
      logging_func(self.AsJson())

  def valid_basekey(self, key):
    if key in err_msg.BaseKey:
      return key
    elif key in [x.name for x in err_msg.BaseKey]:
      return err_msg.BaseKey[key]
    elif self.Error_Obj_errors:
      self.Error_Obj_errors.Add(err_msg.VALIDATION,
                                err_msg.VALIDATION.ILLEGAL_BASEKEY,
                                key)
