"""Data structure for collecting error messages."""

import collections
import copy
import inspect
import json
import pprint

from core.utils import file_util
from core._system.constants import *
from core.errors.err_msg_utils import LocalKey, msgkey
from core.errors import error_handler_utils as util

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

def _repr_(slf):
  title = 'ErrorMsgManager'
  func = lambda s, v: ', '.join(getattr(s, v) or [] if hasattr(s, v) else [])
  key_list = func(slf, '_keys')
  comps = func(slf, '_comps')

  return '<{0} (comp: [{1}];keys: [{2}])>'.format(title, comps, key_list)

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

  def __repr__(self):
    return _repr_(self)


  def _import_basekey(self, page_module, basekey):
    """Imports err_msg/<all files> as BaseKey objects.
    
    Args:
        page_module: __import__ module of core.errors_old.err_msg
        basekey: str, name of target file.
        
    Returns:
        basekey_obj: obj, New BaseKey object.
        lcl_keys: list, List of name/LocalKey Message pairs.
    """

    basepage_obj = getattr(page_module, basekey.lower())
    raw_dict = util._getErrmsgData(basepage_obj)

    attr, lcl_keys = raw_dict['attributes'], raw_dict['local_keys']

    basekey_dict = dict([(k, v) for k, v in attr] +   # Load all Attributes
                        zip(['_keys', '_comps'],
                            [[k[0].capitalize() for k in lcl_keys] or [], # local_keys
                             [basekey]]))                                 # components

    Basekey = self._BaseKey__class()  # Dynamically created in _createErrorMsgKeys()
    Basekey._load(basekey_dict)

    # Assign BaseKey object to ErrMsg (self)
    setattr(self, basekey, Basekey)

    return Basekey, lcl_keys

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

    # Aggregate attributes into a dict.
    local_dict = {
      'description': lclmsg.desc,
      'location': lclmsg.location,
      '_comps': [basekey_obj._comps[0], lclkey_name.capitalize()],
      '_keys': [message.key.capitalize() for message in lclmsg.messages]
    }

    # Create LocalKey Object and load its attributes.
    localkey_obj = self._LocalKey__class() # Dynamically created in _createErrorMsgKeys()
    localkey_obj._load(local_dict)

    # Assign LocalKey object to BaseKey.
    setattr(basekey_obj, lclkey_name.capitalize(), localkey_obj)

    return localkey_obj, lclmsg.messages

  def _import_messagekeys(self, local_obj, msg_obj):
    """Imports MsgKey Messages from LocalKey as MsgKey objects.

      Args:
          local_obj: ErrMsg.BaseKey object
          msg_obj: obj, name/LocalKey Message pairs.      
      """

    # Aggregate MsgKey attributes into a dict.
    msg_dict = {'message': msg_obj.value,
                'argcount': msg_obj.value.count('%s'),
                '_comps': local_obj._comps + [msg_obj.key]}

    # Create MessageKey Object and load its attributes
    msgkey_obj = self._MsgKey__class()  # Dynamically created in _createErrorMsgKeys()
    msgkey_obj._load(msg_dict)


    # Assign it to parent LocalKey.
    setattr(local_obj, msg_obj.key.capitalize(), msgkey_obj)

  def _createErrorMsgKeys(self):
    base_error_class = util.createBasicClass('BaseErrorKey')
    setattr(base_error_class, '__repr__', _repr_)
    setattr(base_error_class, '_load',
            lambda self, dict: util.dictToInstance(self, dict))

    for key in ['BaseKey', 'LocalKey', 'MsgKey']:
      setattr(self, '_{0}__class'.format(key),
              util.createBasicClass(key, (base_error_class,)))

  def _validateInput(self, default_keys):
    sys_default_keys = ERRORKEY_SYSTEM_DEFAULTKEYS
    err, comps = self, None
    if isinstance(default_keys, list):

      use_sysdefaults = False
      for i, key in enumerate(default_keys):
        key = key if not use_sysdefaults else sys_default_keys[i]
        if hasattr(err, key):
          err = getattr(err, key)
        else:
          use_sysdefaults = True
          err = getattr(err, sys_default_keys[i])
      comps = err._comps

    elif isinstance(default_keys, dict):
      for i, keyword in enumerate(ERRORKEY_DEFAULTKEYS):
        if keyword in default_keys.keys():
          if hasattr(err, default_keys[keyword]):
            err = getattr(err, default_keys[keyword])
          else:
            err = getattr(err, ERRORKEY_SYSTEM_DEFAULTKEYS[i])
      comps = err._comps
    else:
      comps = list(ERRORKEY_SYSTEM_DEFAULTKEYS)

    self.default_keys = comps


  def __init__(self, error_keys=None):
    self._validateInput(error_keys)
    # Determine relative path to ERRMSG directory

    location = file_util.SitRep(__file__)
    msg_path = (location.rel_thisdir + _ERRMSG_LOCATION).replace('/', '.')

    # Read ERRMSG directory; Count each file as a BaseKey
    self._keys = [x.capitalize() for x in file_util.searchDirectory(msg_path)]  # List of file names in /err_msg folder
    errmsg_mod = __import__(msg_path, fromlist=[x.lower() for x in self._keys])  #import module: core.errors_old.err_msg

    # Ensure 'system.py' file is there.
    system_check = ERRORKEY_SYSTEM_DEFAULTKEYS[0].lower() in [x.lower() for x in self._keys]
    if system_check:
      self._createErrorMsgKeys()
      # Iterate through each file
      for basekey in self._keys:
        self._comps = None  # Keeps track of Basekey, LocalKey, MsgKey components.

        # Create BaseKey.
        basekey_obj, localkey_list = self._import_basekey(errmsg_mod, basekey)

        # If Default Local not in localkey_list, append a default LocalKey
        localkey_list = util._check_LocalKeyDefault(basekey_obj, localkey_list)

        # Convert LocalKey Messages to Objects:
        for local_keymsg in localkey_list:
          lclkey_obj, msgkey_list = self._import_localkey(basekey_obj, local_keymsg)

          # If Default MessageKey not in msgkey_list, append a default MsgKey
          msgkey_list = util._check_MsgKeyDefault(lclkey_obj, msgkey_list)

          # Convert MessageKey Messages to Objects:
          for msg in msgkey_list:
            self._import_messagekeys(lclkey_obj, msg)
    else:
      print CRITICALFAIL_MSG
      sys.exit(0)

  def getKeyFromString(self, key_str, errors=None, add_default=True):
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

      # if key_str is only a partial keychain, add default keys to complete it.
      if len(comps) < 3 and add_default:
        return self._defaultKeyChain(new_key, errors)
      else:
        return new_key
    else:
      return self


  def _defaultKeyChain(self, key=None, errors=None):

    # Get list of components of key (if any)
    key_class_types = [self._BaseKey__class, self._LocalKey__class,
                       self._MsgKey__class, ErrorMsgManager]
    chain = (key._comps if any(
      [isinstance(key, cls) for cls in key_class_types]) else None) or []

    chain += self.default_keys[len(chain):]
    return self.getKeyFromString('.'.join(chain))


  def _validateKey(self, key, cls = None):
    """"Verify that key is an instance of some ErrorKey or ErrMsgManager class."""

    key_class_types = [self._BaseKey__class, self._LocalKey__class,
                       self._MsgKey__class, ErrorMsgManager]

    if cls:
      if inspect.isclass(cls) and cls in key_class_types:
        classes = [key]
      else:
        return None
    else:
      classes = key_class_types
    return any([isinstance(key, cls) for cls in classes])


  def isValidKey(self, key, cls=None, errors=None):
    isvalid = self._validateKey(key, cls)

    if isvalid is None:
      pass
      # Provided cls not legal
    else:
      return isvalid


  @property
  def all(self):
      all_messages = collections.OrderedDict()
      for basekey in sorted(self._keys):
          base = getattr(self, basekey)
          for localkey in sorted(base._keys):
              local = getattr(base, localkey)
              for msgkey in sorted(local._keys):
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
