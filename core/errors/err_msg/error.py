"""Error categories and messages specific to the Error Object."""

from core.errors.err_msg_utils import *
"""
error_handler.ErrorMsgManager (ErrMsg) creates unique BaseKey object
    from this file (error.py (file) --> Error (object)

The doc_string at the top of this file becomes the description of the 
    Error object.
    
Each property in ALL-CAPS is converted to a BaseKey property.

Each property starting with underscore is ignored by the ErrMsg import 
    process and is only locally-used.
    
Each LocalKey Message object is added as a child object of the BaseKey.
    Ex: 
        error.py file contains a LocalKey Message class named, 'Generic'.
        ErrMsg imports it in and converts it to a child object of the Error BaseKey.
        Each msgkey in LocalKey.messages is converted to a child class of
            the LocalKey object.
        Therefore, this page contains Generic, Validation, and Add classes, this
            results in: ErrMsg.Error.description (property; __doc__ of this file)
                        ErrMsg.Error.location    (property)
                        ErrMsg.Error.Generic     (LocalKey Message Class --> Object)
                        ErrMsg.Error.Validation  (LocalKey Message Class --> Object)
                        ErrMsg.Error.Add         (LocalKey Message Class --> Object)
                        ErrMsg.Error.Generic.DefaultKey (ErrMsg Message Class --> Object)
                        
"""

# BaseKey Properties
LOCATION = 'core.errors_old.error_handler'
_local_location = LOCATION + '.Errors'

"""
LocalKey Template:

xx_localkey_name_xx = LocalKey(
    desc = '',
    location = _local_location,
    messages = [
        errmsg('xx_msgkey_xx', 'xx_message')
    ]
)
"""

Generic = LocalKey(
    desc='Generic LocalKey for Error BaseKey Object.',
    location = _local_location,
    messages = [
        errmsg('GENERICKEY', 'This key not to be used in messaging.'),
        errmsg('UNKNOWN_ERRORKEY', 'Encountered unexpected key: %s'),
        errmsg('DEFAULTKEY', 'Generic Error Message'),
        errmsg('UNEXPECTED_DEFAULT', 'Encountered unexpected default key(s): %s')
    ]
)

Validation = LocalKey(
    desc = 'Validation-related LocalKey for Error BaseKey Object.',
    location = _local_location,
    messages = [
        errmsg('UNKNOWN', 'An unknown error has caused an exception: %s'),
        errmsg('INVALIDKEY', 'Encountered invalid error key: %s'),
    ]
)


Add = LocalKey(
    desc = 'Errors.Add()-related LocalKey for Error BaseKey Object.',
    location = _local_location,
    messages = [
        errmsg('INVALID_MSGFORMAT', 'Incorrect number of message arguments included with '
                                    'message.  Original message: %s; Args: %s'),
        errmsg('INVALID_ERRORKEY', 'Invalid ErrorKey included with message.  Original '
                                   'message: %s; Args: %s')
    ]
)
