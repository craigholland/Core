"""Data structure for collecting error messages."""

import collections
import json
import pprint

from core.utils import file_util
from core._system.constants import *

"""
BASE_KEY: Root class object
LOCAL_KEY: Error-specific category
MESSAGE_KEY: Abbr. Error Description
"""


class ErrorMsgManager(object):
  """Collects and organizes error messages into object structure.
  Crawls through errors.err_msg directory and imports each file
  as a base_key.
  
  Each All-Cap property in each file is imported as a local_key
    
  Usage:
  mgr = ErrorMsgManager()
  >>> mgr
  ErrorMsgManager<keys: BASE1, BASE2, BASE3>
  >>> mgr.as_list
  ['BASE1', 'BASE2', 'BASE3']
  >>> mgr.BASE1
  BASE1<keys: LOCAL1, LOCAL2, LOCAL3>
  >>> mgr.BASE1.as_list
  ['LOCAL1', 'LOCAL2', 'LOCAL3']
  >>> mgr.BASE1.LOCAL2
  LOCAL2<keys: MSGKEY1, MSGKEY2>
  >>> mgr.BASE1.LOCAL2.MSGKEY1
  This message has no args'
  >>> mgr.BASE1.LOCAL2.MSGKEY1.argcount
  0
  >>> mgr.BASE1.LOCAL2.MSGKEY2
  This message has one arg: %s
  >>> mgr.BASE1.LOCAL2.MSGKEY1.argcount
  1
  
  """
  def _repr_(self, title, keys):
    return '{0}<keys: {1}>'.format(title, (', '.join(keys)))

  def _dummy_object(cls, desc, location, title, keys):

    if desc and location:
      class dummy(object):
        def __init__(self, **kwargs):
          for k, v in kwargs.iteritems():
            setattr(self, k, v)
        def __repr__(self):
          return cls._repr_(title, keys)
        @property
        def as_list(self):
          return keys
      return dummy(desc=desc, location=location)

    else:
      class dummy(object):
        def __init__(self, location, msg):
          self._location = location
          self.message = msg
          self.argcount = msg.count('%s')
        def __repr__(self):
          return self._location
      return dummy(location, title)

  def __init__(self):
    location = file_util.SitRep(__file__)
    msg_path = location.rel_thisdir+'/err_msg'
    self.as_list = file_util.searchDirectory(msg_path)

    self.base = __import__(msg_path.replace('/', '.'),
                           fromlist=self.as_list)
    for base_key in self.as_list:
      # Import base_key data
      base_data = getattr(self.base, base_key)
      desc, loc = base_data.__doc__, base_data.LOCATION
      local_keys = [x for x in dir(base_data) if not x.startswith('_') and
                    x == x.upper() and x.lower() != 'location']

      setattr(self, base_key.upper(),
              self._dummy_object(desc, location, base_key.upper(), local_keys))
      basekey_obj = getattr(self, base_key.upper())
      for local_key in local_keys:
        local_key_data = getattr(base_data, local_key)
        desc, loc = local_key_data.desc, local_key_data.location
        message_keys = [x.key for x in local_key_data.messages]
        setattr(basekey_obj, local_key,
                self._dummy_object(desc, loc, local_key, message_keys))
        localkey_obj = getattr(basekey_obj, local_key)
        for message in local_key_data.messages:
          location = '.'.join([base_key.upper(), local_key, message.key])
          setattr(localkey_obj, message.key,
                  self._dummy_object(None, location, message.value, None))
    self.as_list = [x.upper() for x in self.as_list]

  def __repr__(self):
    return self._repr_('ErrorMsgManager', self.as_list)
ErrMsg = ErrorMsgManager()


class Errors(object):

  DEFAULT_KEY = '__generic__'

  DEFAULT_FMT = '\n'.join

  def __init__(self):
    _locals = collections.defaultdict(list)
    self._errors = collections.defaultdict(type(_locals))
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

