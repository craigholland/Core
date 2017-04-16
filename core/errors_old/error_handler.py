"""Data structure for collecting error messages."""

import collections
import copy
import json
import pprint

from core.utils import file_util
from core._system.constants import *
from core.errors_old.err_msg_utils import errmsg

__all__ = [
  #  Error-related classes/instances
  'ErrorMsgManager',  # Error Message Management Class
  'ErrMsg',           # Instance of ErrorMsgManager Class
  'Errors',           # Error-handling Class
]

"""
BASE_KEY: Root class object
LOCAL_KEY: Error-specific category
MESSAGE_KEY: Abbr. Error Description
"""


def _repr_(title, keys=None):
  if keys:
    return '{0}<keys: {1}>'.format(title, (', '.join(keys)))
  else:
    return title

class ErrorMsgManager(object):
  """Collects and organizes error messages into object structure.
  Crawls through errors_old.err_msg directory and imports each file
  as a base_key.
  
  Each All-Cap property in each file is imported as a local_key (sub category)
    
  Usage:
  mgr = ErrorMsgManager()
  >>> mgr = ErrorMsgManager()
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
  BASE1.LOCAL2.MSGKEY1 <object>
  >>> mgr.BASE1.LOCAL2.MSGKEY1.message
  This message has no args'
  >>> mgr.BASE1.LOCAL2.MSGKEY1.argcount
  0
  >>> mgr.BASE1.LOCAL2.MSGKEY2.message
  This message has one arg: %s
  >>> mgr.BASE1.LOCAL2.MSGKEY1.argcount
  1
  >>> mgr.BASE1.LOCAL2.MSGKEY1.comps
  ['BASE1', 'LOCAL2', 'MSGKEY1']
  >>> type(mgr.BASE1.LOCAL2.MSGKEY1)
  <class 'core.errors_old.error_handler.MessageKey'>
  >>> type(mgr.BASE1.LOCAL2)
  <class 'core.errors_old.error_handler.LocalKey'>
  >>> type(mgr.BASE1)
  <class 'core.errors_old.error_handler.BaseKey'>
  >>> type(mgr)
  <class 'core.errors_old.error_handler.ErrorMsgManager'>
  """

  class ErrorKey(object):
    """Base Key object used to create BaseKey, LocalKey, and MessageKey objects."""
    _DEFAULT_BASEKEY, _DEFAULT_LOCALKEY, _DEFAULT_MSGKEY = ERRORKEY_SYSTEM_DEFAULTKEYS

    def __init__(self, **kwargs):
      self._comps = None
      for k, v in kwargs.iteritems():
        setattr(self, k, v)

    def __repr__(self):
      if hasattr(self, 'name') and hasattr(self, 'keys'):
        return _repr_(self.name, self.keys)
      elif hasattr(self, '_location'):
        return _repr_(self._location)
      else:
        return str(self)

    @property
    def comps(self):
      return self._comps

  def _keyGen(self, key_type, desc, path, name=None, keys=None):
    if key_type == ERRORKEY_DEFAULTKEYS[0]:
      class BaseKey(self.ErrorKey):
        pass
      return BaseKey(desc=desc, path=path, name=name, keys=keys)

    elif key_type == ERRORKEY_DEFAULTKEYS[1]:
      class LocalKey(self.ErrorKey):
        pass
      return LocalKey(desc=desc, path=path, name=name, keys=keys)

    elif key_type == ERRORKEY_DEFAULTKEYS[2]:
      class MessageKey(self.ErrorKey):
        def __init__(self, **kwargs):
          super(MessageKey, self).__init__(**kwargs)
          self.argcount = self.message.count('%s') if hasattr(
            self, 'message') else 0
      return MessageKey(message=desc, _location=path)

  def __init__(self):
    # Read core.errors_old.err_msg directory; Count each file as a BaseKey
    location = file_util.SitRep(__file__)
    msg_path = location.rel_thisdir+'/err_msg'
    self.as_list = file_util.searchDirectory(msg_path)
    self.base = __import__(msg_path.replace('/', '.'),
                           fromlist=self.as_list)

    # Ensure 'system.py' file is there.
    system_check = ERRORKEY_SYSTEM_DEFAULTKEYS[0] in [x.upper() for x in
                                                      self.as_list]
    if system_check:
      # Iterate through each BaseKey
      for base_key in self.as_list:
        # Import base_key
        base_data = getattr(self.base, base_key)
        desc, loc = base_data.__doc__, base_data.LOCATION
        local_keys = [x for x in dir(base_data) if not x.startswith('_') and
                      x == x.upper() and x.lower() != 'location']

        # Add default LocalKey (if not already there)
        if ERRORKEY_SYSTEM_DEFAULTKEYS[1] not in local_keys:
          local_keys.append(ERRORKEY_SYSTEM_DEFAULTKEYS[1])

        # Create BaseKey Object
        basekey_obj = self._keyGen(ERRORKEY_DEFAULTKEYS[0], desc, location, base_key.upper(), local_keys)
        setattr(self, base_key.upper(), basekey_obj)
        setattr(getattr(self, base_key.upper()), '_comps', [base_key.upper()])

        # Iterate through each local key of the BaseKey
        for local_key in local_keys:
          # Import local key data
          if local_key == ERRORKEY_SYSTEM_DEFAULTKEYS[1] and not hasattr(base_data, local_key):
            desc = 'Default local_key for {0} Object.'.format(base_key.upper())
            # loc = previously assigned loc from base
            messages = []
            message_keys = []
          else:
            local_key_data = getattr(base_data, local_key)
            desc, loc = local_key_data.desc, local_key_data.location
            messages = local_key_data.messages
            message_keys = [x.key for x in messages]

          # Add default MessageKey (if not already there)
          if ERRORKEY_SYSTEM_DEFAULTKEYS[2] not in message_keys:
            message_keys.append(ERRORKEY_SYSTEM_DEFAULTKEYS[2])
            messages.append(errmsg(key=ERRORKEY_SYSTEM_DEFAULTKEYS[2],
                                   value='Default MessageKey for {0}.{1} base/'
                                         'localkey'.format(base_key.upper(),
                                                           local_key)))

          # Create LocalKey Object
          localkey_obj = self._keyGen(ERRORKEY_DEFAULTKEYS[1], desc, loc, local_key, message_keys)
          setattr(basekey_obj, local_key, localkey_obj)
          setattr(getattr(basekey_obj, local_key), '_comps', [base_key.upper(), local_key])

          # Iterate through each message of the LocalKey
          for message in messages:
            location = '.'.join([base_key.upper(), local_key, message.key])

            # Create MessageKey Object
            msg_obj = self._keyGen(ERRORKEY_DEFAULTKEYS[2], message.value, location)
            setattr(localkey_obj, message.key, msg_obj)
            setattr(getattr(localkey_obj, message.key), '_comps', [base_key.upper(), local_key, message.key])

      self.as_list = [x.upper() for x in self.as_list]
    else:
      print 'CRITICAL FAILURE!!! MISSING SYSTEM.PY FILE IN "core.errors_old.err_msg"'
      print 'Exiting...'
      sys.exit(0)

  def __repr__(self):
    return _repr_('ErrorMsgManager', self.as_list)

  def _dummyMsgKey(self):
    return self._keyGen('msgkey', '', '')

  def _defaultKey(self, key=None, errors=None, **defaults):
    """Augments 'lazy' keychain with default settings.
    Args:
        key (optional): ErrorKey subclass to be built on.
        errors: error_handler.Errors object
        defaults: dict, default key settings for Object    
    """

    write_error = errors is not None

    extra = list(set(defaults.keys()) - set(ERRORKEY_DEFAULTKEYS))
    if extra and write_error:
        errors.Add(ErrMsg.ERROR.VALIDATION.UNEXPECTED_DEFAULTKEY, extra)
    keys = []
    for i in xrange(3):
      if ERRORKEY_DEFAULTKEYS[i] in defaults.keys():
        keys.append(defaults[ERRORKEY_DEFAULTKEYS[i]])
      else:
        keys.append(ERRORKEY_SYSTEM_DEFAULTKEYS[i])

    if self._validMessageKey(key):
      return key

    elif key == self or key is None:
      return self._defaultKey(getattr(ErrMsg, keys[0]), errors, **defaults)

    elif self._validateKey(key):
      if keys[1] in key.keys:
        return self._defaultKey(getattr(key, keys[1]), errors, **defaults)
      if keys[2] in key.keys:
        return self._defaultKey(getattr(key, keys[2]), errors, **defaults)

    elif write_error:
      errors.Add(ErrMsg.ERROR.VALIDATION.INVALIDKEY, key)


  def _validMessageKey(self, key, errors=None):
    testkey = self._dummyMsgKey()
    if self._validateKey(key) and type(key).__name__ == type(testkey).__name__:
      return True
    elif errors is not None:
      try:
        errors.Add(ErrMsg.ERROR.VALIDATION.INVALIDKEY, str(key))
      except Exception, e:
        errors.Add(ErrMsg.ERROR.VALIDATION.UNKNOWN, e)
    return False

  def getKeyFromString(self, key_str, errors=None):
    """convert dot-based string into Key."""
    if key_str:
      comps = key_str.split('.')
      new_key = self
      for key in comps:
        if hasattr(new_key, key):
          new_key=getattr(new_key, key)
        elif isinstance(errors, Errors):
          errors.Add(ErrMsg.ERROR.VALIDATION.INVALIDKEY, key)
          return None
        else:
          return None
      return self._defaultKey(new_key)
    else:
      return None

  def _validateKey(self, key):
    return issubclass(key.__class__, self.ErrorKey)

  @property
  def all(self):
      all_messages = collections.OrderedDict()
      for basekey in sorted(self.as_list):
          base = getattr(self, basekey)
          for localkey in sorted(base.keys):
              local = getattr(base, localkey)
              for msgkey in sorted(local.keys):
                  msg = getattr(local, msgkey).message
                  keychain = self.getKeyFromString('.'.join([basekey, localkey, msgkey]))
                  all_messages[str(keychain)] = msg
      return all_messages




ErrMsg = ErrorMsgManager()

class Errors(object):
  DEFAULT_FMT = '\n'.join

  def __init__(self):
    self._errors = {}

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

  @property
  def count(self):
    return sum(len(x) for x in self.condensed.values())

  @property
  def condensed(self):
    """Condenses nested dict to single dict."""
    condensed = {}
    key_format = '{0}_{1}_{2}'
    for basekey, basevalue in sorted(self._errors.iteritems()):
      for localkey, localvalue in sorted(basevalue.iteritems()):
        for msgkey, msglist in sorted(localvalue.iteritems()):
          new_key = key_format.format(basekey, localkey, msgkey)
          condensed[new_key] = msglist
    return condensed

  @property
  def consists_of(self):
    d = collections.defaultdict(list)
    for basekey, basevalue in sorted(self._errors.iteritems()):
      d[ERRORKEY_DEFAULTKEYS[0]].append(basekey)
      for localkey, localvalue in sorted(basevalue.iteritems()):
        d[ERRORKEY_DEFAULTKEYS[1]].append('.'.join([basekey, localkey]))
        for msgkey, _ in sorted(localvalue.iteritems()):
          d[ERRORKEY_DEFAULTKEYS[2]].append('.'.join([basekey, localkey, msgkey]))
    return dict(d)

  @property
  def display(self):
    d = ''
    for basekey, basevalue in sorted(self._errors.iteritems()):
      d += basekey + '\n'
      for localkey, localvalue in sorted(basevalue.iteritems()):
        d += ' ' * 4 + localkey + '\n'
        for msgkey, msglist in sorted(localvalue.iteritems()):
          temp_list = copy.copy(msglist)
          first_msg = temp_list.pop(0)
          d += '{0}{1}: {2}'.format(' ' * 10, msgkey, first_msg) + '\n'
          for msg in temp_list:
            d += ' ' * (12 + len(msgkey)) + msg + '\n'
          d += '\n'
    return d

  def _keychainExists(self, key, create_new=False):
    """Confirms if key already exists in error dictionary.
    Args:
        key, an ErrorKey subclass, key to be searched.
        create_new: bool, if key doesn't exist in error, create new one.
    """
    if ErrMsg._validateKey(key):
      curr_dict = self._errors

      for i, comp in enumerate(str(key).split('.')):
        create_type = dict if i < 2 else list
        if comp in curr_dict.keys():
          curr_dict = curr_dict[comp]
        else:
          if create_new:
            curr_dict[comp] = create_type()
            curr_dict = curr_dict[comp]
          else:
            return False
      return True

  def isError(self, obj):
    return isinstance(obj, Errors) or issubclass(obj, Errors)

  def Clear(self):
    self._errors = {}


  def Get(self, key):
    """Gets error messages by key_bk.

    Args:
      key_bk: str, the key_bk whose messages to retrieve. If omitted, the messages
          associated with the default key_bk are retrieved.

    Returns:
      A list of messages for the given key_bk, or None if the key_bk is not present.
    """
    if not key:
      key = ERRORKEY_SYSTEM_DEFAULTKEYS[0]
    messages = self._errors.get(key)
    if messages:
      return list(messages)
    return None

  def GetAll(self):
    """Gets a copy of the internal errors_old dictionary."""
    return self._errors.copy()

  def Add(self, key, *messages):
    """Associates one or more messages with a given key_bk.

    Args:
      key_bk: str, the key_bk to associate with a message. If omitted, the messages
          are associated with the default key_bk.
      message: str, the message to associate with the key_bk.
      *messages: additional messages to associate with the key_bk.
    """
    if ErrMsg._validMessageKey(key):
      if not self._keychainExists(key):
        self._keychainExists(key, True)

      basekey, localkey, msgkey = str(key).split('.')

      if key.argcount == len(messages):
        self.message = key.message % messages
        self._errors[basekey][localkey][msgkey].append(self.message)

      else:
        self.Add(ErrMsg.ERROR.ADD.INVALID_MSGFORMAT, key.message, messages)
    elif ErrMsg._validateKey(key):
      # Assume GENERIC status
      temp_error = Errors()
      key = ErrMsg._defaultKey(key, temp_error)
      if temp_error:
        pass
      else:
        self.Add(key, messages)
    else:
      self.Add(ErrMsg.ERROR.ADD.INVALID_ERRORKEY, key.message, messages)

  def AsJson(self):
    """Gets a JSON string representation of the error object.

    Args:
      format_func: function, used to format the list of messages for each key_bk
          before transforming to JSON. The function should accept a list of
          strings and return a value that is JSON-serializable. The default
          behavior is to join each list of messages with a newline character.

    Returns:
      A JSON string of key_bk/messages pairs.
    """

    return json.dumps(self._errors)

  def Merge(self, other):
    """Adds all errors_old from another Errors object to this one.

    Args:
      other: an Errors instance to merge into this one.
    """
    if self.isError(other):
      for basekey, basevalue in other._errors.iteritems():
        for localkey, localvalue in basevalue.iteritems():
          for msgkey, msglist in localvalue.iteritems():
            keychain = ErrMsg.getKeyFromString('.'.join([basekey, localkey,
                                                         msgkey]))

            # Use keychainExists flag to create chain in self if it doesn't
            # already exist.
            self._keychainExists(keychain, True)
            for msg in msglist:
              self._errors[basekey][localkey][msgkey].append(msg)

  def Raise(self, exception, key, message, *messages):
    """Adds error message(s) and raises the given exception."""
    self.Add(key, message, *messages)
    raise exception(self.AsJson())

  def RaiseIfAny(self, exception):
    """Raises the given exception with the errors_old as the message, if any."""
    if self:
      raise exception(self.AsJson())

  def LogIfAny(self, logging_func):
    """Logs the errors_old using the given logging_func."""
    if self:
      logging_func(self.AsJson())
