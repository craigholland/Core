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
MessageKeyType = None  # Dynamically set by ErrorMsgManager._keyGen()

def _str_(title, keys=None):
  if keys:
    return '{0}<keys: {1}>'.format(title, (', '.join(keys)))
  else:
    return title

class ErrorMsgManager(object):
  """Collects and organizes error messages into object structure.
  Crawls through errors.err_msg directory and imports each file
  as a base_key.
  
  Each All-Cap property in each file is imported as a local_key (sub category)
    
  Usage:
  mgr = ErrorMsgManager()
  >>> mgr
  ErrorMsgManager<keys: BASE1, BASE2, BASE3>
  >>> mgr.keys
  ['BASE1', 'BASE2', 'BASE3']
  >>> mgr.BASE1
  BASE1<keys: LOCAL1, LOCAL2, LOCAL3>
  >>> mgr.BASE1.keys
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
  >>> type(mgr.BASE1.LOCAL2.MSGKEY1)
  <class 'core.errors.error_handler.MessageKey'>
  >>> type(mgr.BASE1.LOCAL2)
  <class 'core.errors.error_handler.LocalKey'>
  >>> type(mgr.BASE1)
  <class 'core.errors.error_handler.BaseKey'>
  >>> type(mgr)
  <class 'core.errors.error_handler.ErrorMsgManager'>
  """

  class ErrorKey(object):
    """Base Key object used to create BaseKey, LocalKey, and MessageKey objects."""

    def __init__(self, **kwargs):
      for k, v in kwargs.iteritems():
        setattr(self, k, v)
    def __str__(self):
      if hasattr(self, 'name') and hasattr(self, 'keys'):
        return _str_(self.name, self.keys)
      elif hasattr(self, '_location'):
        return _str_(self._location)
      else:
        return str(self)

  def _keyGen(self, key_type, desc, path, name=None, keys=None):
    if key_type == 'Base':
      class BaseKey(self.ErrorKey):
        pass
      return BaseKey(desc=desc, path=path, name=name, keys=keys)

    elif key_type =='Local':
      class LocalKey(self.ErrorKey):
        pass
      return LocalKey(desc=desc, path=path, name=name, keys=keys)

    elif key_type == 'Message':
      class MessageKey(self.ErrorKey):
        def __init__(self, **kwargs):
          super(MessageKey, self).__init__(**kwargs)
          self.argcount = self.message.count('%s') if hasattr(
            self, 'message') else 0
      msg = MessageKey(message=desc, _location=path)
      if not globals()['MessageKeyType']:
        globals()['MessageKeyType'] = type(msg)
      return msg

  def __init__(self):

    # Read core.errors.err_msg directory; Count each file as a BaseKey
    location = file_util.SitRep(__file__)
    msg_path = location.rel_thisdir+'/err_msg'
    self.as_list = file_util.searchDirectory(msg_path)
    self.base = __import__(msg_path.replace('/', '.'),
                           fromlist=self.as_list)

    # Iterate through each BaseKey
    for base_key in self.as_list:
      # Import base_key data
      base_data = getattr(self.base, base_key)
      desc, loc = base_data.__doc__, base_data.LOCATION
      local_keys = [x for x in dir(base_data) if not x.startswith('_') and
                    x == x.upper() and x.lower() != 'location']

      # Create BaseKey Object
      basekey_obj = self._keyGen('Base', desc, location, base_key.upper(), local_keys)
      setattr(self, base_key.upper(), basekey_obj)

      # Iterate through each local key of the BaseKey
      for local_key in local_keys:
        # Import local key data
        local_key_data = getattr(base_data, local_key)
        desc, loc = local_key_data.desc, local_key_data.location
        message_keys = [x.key for x in local_key_data.messages]

        # Create LocalKey Object
        localkey_obj = self._keyGen('Local', desc, loc, local_key, message_keys)
        setattr(basekey_obj, local_key, localkey_obj)

        # Iterate through each message of the LocalKey
        for message in local_key_data.messages:
          location = '.'.join([base_key.upper(), local_key, message.key])

          # Create MessageKey Object
          msg_obj = self._keyGen('Message', message.value, location)
          setattr(localkey_obj, message.key, msg_obj)

    self.as_list = [x.upper() for x in self.as_list]

  def __str__(self):
    return _str_('ErrorMsgManager', self.as_list)
ErrMsg = ErrorMsgManager()

class Errors(object):
  _DEFAULT_BASEKEY = 'ERROR'
  _DEFAULT_LOCALKEY = 'GENERIC'
  _DEFAULT_MSGKEY = 'GENERICKEY'

  DEFAULT_FMT = '\n'.join

  def __init__(self):
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

  def _validateKey(self, key):
    if type(key) == MessageKeyType:
      self.basekey, self.localkey, self.msgkey = str(key).split('.')
      self.message, self.argcount = key.message, key.argcount
      return True
    else:
      key = ErrorMsgManager()
      for sub_key in [self._DEFAULT_BASEKEY, self._DEFAULT_LOCALKEY, self._DEFAULT_MSGKEY]:
        key = getattr(key, sub_key)
        self._validateKey(key)
      return False

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

  def Add(self, key, *messages):
    """Associates one or more messages with a given key_bk.

    Args:
      key_bk: str, the key_bk to associate with a message. If omitted, the messages
          are associated with the default key_bk.
      message: str, the message to associate with the key_bk.
      *messages: additional messages to associate with the key_bk.
    """
    if self._validateKey(key):

      print 'adding key'

      # messages = map(str, (message,) + messages)
      # self._errors[key].extend(messages)
    else:
      print 'error - bad key'

    print 'Base: {0}; Local: {1}; Msg: {2}'.format(self.basekey, self.localkey, self.msgkey)
    print 'Message: {0} (Argcount: {1})'.format(self.message, self.argcount)

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

__all__ = ['ErrorMsgManager', 'ErrMsg', 'Errors', 'MessageKey']
