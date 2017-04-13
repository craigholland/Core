"""Data structure for collecting error messages."""

import collections
import copy
import json
import pprint

from core.utils import file_util
from core._system.constants import *
from core.errors_test.err_msg_utils import LocalKey, errmsg
from core.errors_test import error_handler_utils

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

_ERRMSG_LOCATION = '/err_msg'

def _repr_(title, keys=None):
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
  <class 'core.errors.error_handler.MessageKey'>
  >>> type(mgr.BASE1.LOCAL2)
  <class 'core.errors.error_handler.LocalKey'>
  >>> type(mgr.BASE1)
  <class 'core.errors.error_handler.BaseKey'>
  >>> type(mgr)
  <class 'core.errors.error_handler.ErrorMsgManager'>
  """

  def __repr__(self):
    title = 'ErrorMsgManager'
    comps = []
    if self._comps:
      for comp in self._comps:
        comps.append(comp)
    return '{0}<keys: {1}>'.format(title, '.'.join(comps))


  def _import_basekey(self, page_module, basekey_filename):
    """Imports err_msg/<all files> as BaseKey objects.
    
    Args:
        page_module: __import__ module of core.errors.err_msg
        basekey_filename: str, name of target file.
        
    Returns:
        basekey_obj: obj, New BaseKey object.
        lcl_keys: list, List of name/LocalKey Message pairs.
    """

    basepage_obj = getattr(page_module, basekey_filename)
    basekey = basekey_filename.capitalize()
    base_dict = error_handler_utils._getErrmsgData(basepage_obj)
    attr, lcl_keys = base_dict['attributes'], base_dict['local_keys']

    # Create BaseKey Object and its attributes
    basekey_dict = dict((k, v) for k, v in [x for x in attr])
    basekey_dict['_comps'] = [basekey]
    basekey_dict['_keys'] = [k.capitalize() for k, _ in lcl_keys] or []
    basekey_obj = type('BaseKey', (object,), basekey_dict)

    # set __repr__ method for basekey_obj
    setattr(basekey_obj, '__repr__', self.__repr__)

    # Assign BaseKey object to ErrMsg (self)
    setattr(self, basekey, basekey_obj)

    return basekey_obj, lcl_keys

  def _import_localkey(self, basekey_obj, lcl):
    """Imports LocalKey Messages from BaseKey as LocalKey objects.

      Args:
          basekey_obj: ErrMsg.BaseKey object
          lcl: tuple(str, LocalKey Message).

      Returns:
          localkey_obj: obj, New LocalKey object.
          msgkey_list: list, List of MessageKey messages.
      """
    lclkey_name, lclmsg = lcl
    desc, loc, msgkey_list = (lclmsg.desc, lclmsg.location, lclmsg.messages)

    # Create LocalKey Object and its attributes.
    local_dict = {
      'description': desc,
      'location': loc,
      '_comps': [basekey_obj._comps[0], lclkey_name.capitalize()],
      '_keys': [message.key.capitalize() for message in msgkey_list]
    }
    localkey_obj = type('LocalKey', (object,), local_dict)

    # set __repr__ method for localkey_obj
    setattr(localkey_obj, '__repr__', self.__repr__)

    # Assign LocalKey object to BaseKey.
    setattr(basekey_obj, lclkey_name.capitalize(), localkey_obj)

    return localkey_obj, msgkey_list

  def _import_messagekeys(self, local_obj, msg_obj):
    """Imports MsgKey Messages from LocalKey as MsgKey objects.

      Args:
          local_obj: ErrMsg.BaseKey object
          msg_obj: obj, name/LocalKey Message pairs.      
      """
    msgkey, message = msg_obj.key, msg_obj.value

    # Create MessageKey Object and its attributes.
    msg_dict = {'message': message,
                'argcount': message.count('%s'),
                '_comps': local_obj._comps + [msgkey]}
    msgkey_obj = type('MessageKey', (object,), msg_dict)

    # set __repr__ method for msgkey_obj
    setattr(msgkey_obj, '__repr__', self.__repr__)

    # Assign it to LocalKey.
    setattr(local_obj, msgkey.capitalize(), msgkey_obj)


  def __init__(self):
    # Determine relative path to ERRMSG directory
    location = file_util.SitRep(__file__)
    msg_path = (location.rel_thisdir + _ERRMSG_LOCATION).replace('/', '.')

    # Read ERRMSG directory; Count each file as a BaseKey
    basekey_list = file_util.searchDirectory(msg_path)  # List of file names in /err_msg folder
    self._keys = [x.capitalize() for x in basekey_list]
    errmsg_mod = __import__(msg_path, fromlist=basekey_list)  #import module: core.errors.err_msg

    # Ensure 'system.py' file is there.
    system_check = ERRORKEY_SYSTEM_DEFAULTKEYS[0] in [x.upper() for x in basekey_list]
    if system_check:
      # Iterate through each file
      for basekey in basekey_list:
        self._comps = None  # Keeps track of Basekey, LocalKey, MsgKey components.
        basekey_obj, localkey_list = self._import_basekey(errmsg_mod, basekey)

        # If Default Local not in localkey_list, append a default LocalKey
        localkey_list = error_handler_utils._check_LocalKeyDefault(basekey_obj, localkey_list)

        # Convert LocalKey Messages to Objects:
        for local_keymsg in localkey_list:
          lclkey_obj, msgkey_list = self._import_localkey(basekey_obj, local_keymsg)

          # If Default MessageKey not in msgkey_list, append a default MsgKey
          msgkey_list = error_handler_utils._check_MsgKeyDefault(lclkey_obj, msgkey_list)

          # Convert MessageKey Messages to Objects:
          for msg in msgkey_list:
            self._import_messagekeys(lclkey_obj, msg)
    else:
      print CRITICALFAIL_MSG
      sys.exit(0)


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
    """Adds all errors from another Errors object to this one.

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
    """Raises the given exception with the errors as the message, if any."""
    if self:
      raise exception(self.AsJson())

  def LogIfAny(self, logging_func):
    """Logs the errors using the given logging_func."""
    if self:
      logging_func(self.AsJson())
